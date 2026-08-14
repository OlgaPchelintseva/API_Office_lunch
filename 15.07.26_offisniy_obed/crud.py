from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import User,Session, MenuItem, OrderItem
from schemas import UserCreate, SessionCreate, MenuItemCreate, OrderItemCreate, SessionStatus
from fastapi import HTTPException
from datetime import datetime


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    new_user = User(username = user_data.username, email = user_data.email)
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    return new_user

async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code = 404, detail = f'Пользователь с ID {user_id} не найден')
    return user

async def create_session(db: AsyncSession, session_data: SessionCreate) -> Session:
    if session_data.deadline <= datetime.now():
        raise HTTPException(status_code = 400, detail = 'Дедлайн должен быть строго в будущем')
    await get_user_by_id(db, session_data.creator_id)
    new_session = Session(
        creator_id = session_data.creator_id,
        restaurant_name = session_data.restaurant_name,
        deadline = session_data.deadline,
        status = SessionStatus.active
    )
    db.add(new_session)
    await db.flush()
    await db.refresh(new_session)
    return new_session

async def get_active_session(db: AsyncSession) -> list[Session]:
    result = await db.execute(select(Session).where(Session.status == SessionStatus.active))
    return  result.scalars().all()

async def get_session_by_id(db: AsyncSession, session_id: int) -> Session:
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code = 404, detail = f'Сессия с ID {session_id} не найдена')
    return session

async def update_session_status(db: AsyncSession, session_id: int, new_status: SessionStatus) -> Session:
    session = await get_session_by_id(db, session_id)
    if new_status == SessionStatus.ordered:
        result = await  db.execute(
            select(func.count(OrderItem.id))
            .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
            .where(MenuItem.session_id == session_id)
        )
        orders_count = result.scalar()
        if orders_count == 0:
            raise HTTPException(status_code = 400, detail = 'В заказе нет ни одной позиции')
    session.status = new_status
    await db.flush()
    await db.refresh(session)
    return session

# CRUD для меню
async def add_menu_item(db: AsyncSession, session_id: int, items: list[MenuItemCreate]) -> list[MenuItem]:
    session = await get_session_by_id(db, session_id)
    now = datetime.now()

    if session.status != SessionStatus.active:
        raise HTTPException(status_code=400, detail='Нельзя добавлять меню в неактивную сессию')
    if now >= session.deadline:
        raise HTTPException(status_code=400, detail='Дедлайн сессии уже наступил')

    created_items = []
    for item in items: 
        new_item = MenuItem(
            session_id = session_id,
            name = item.name,
            price = item.price,
        )
        db.add(new_item)
        created_items.append(new_item)
    
    await db.flush() # для получения id
    for item in created_items:
        await db.refresh(item)
    return created_items

# CRUD для заказов
async def get_menu_item_by_id(db: AsyncSession, menu_item_id: int) -> MenuItem:
    result = await db.execute(select(MenuItem).where(MenuItem.id == menu_item_id))
    item = result.scalar_one_or_none()
    if not item: 
        raise HTTPException(status_code=404, detail=f'Блюдо с id {menu_item_id} не найдено')
    return item

async def add_order_item(db: AsyncSession, data: OrderItemCreate) -> OrderItem: # функция для добавления блюда в заказ, либо для увеличения количества
    # проверяем существование пользователя, блюда в меню
    await get_user_by_id(db, data.user_id)
    menu_item = await get_menu_item_by_id(db, data.menu_item_id)
    session = await get_session_by_id(db, menu_item.session_id)
    
    if session.status != SessionStatus.active:
        raise HTTPException(status_code=400, detail='Нельзя добавлять меню в неактивную сессию')
    if datetime.now() >= session.deadline:
        raise HTTPException(status_code=400, detail='Дедлайн сессии истек')
    
    result = await db.execute(
        select(OrderItem)
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
        .where(
            OrderItem.user_id == data.user_id,
            OrderItem.menu_item_id == data.menu_item_id,
            MenuItem.session_id == menu_item.session_id
        )
    )

    existing_item = result.scalar_one_or_none()
    if existing_item:
        existing_item.quantity += data.quantity
        await db.flush()                # получаем id
        await db.refresh(existing_item) # обновляем
        return existing_item            # возвращаем результат
    else:
        new_order = OrderItem(
            user_id = data.user_id,
            menu_item_id = data.menu_item_id,
            quantity = data.quantity,
        )
        db.add(new_order)
        await db.flush()               
        await db.refresh(new_order) 
        return new_order           

# Удаление позиции в заказе
async def delete_order_item(db: AsyncSession, order_item_id: int) -> dict:
    # проверить на существование order_item_id, если нет - 404
    # если найден, получить сессию, чтобы проверить дедлайн (через MenuItem)
    # проверка - нельзя удалять после дедлайна
    # удаляем позицию (.delete -> flush -> return) (key: 'позиция удалена')

    # result = await db.execute(select(MenuItem).where(MenuItem.order_items == order_item_id)) - моя версия
    result = await db.execute(select(OrderItem).where(OrderItem.id == order_item_id))
    order_item = result.scalar_one_or_none()
    if not order_item:
        raise HTTPException(status_code=404, detail=f'Позиция заказа с id {order_item_id} не найдена')
    # получить сессию, чтобы проверить дедлайн
    menu_item = await get_menu_item_by_id(db, order_item.menu_item_id)
    session = await get_session_by_id(db, menu_item.session_id)
    # проверка - нельзя удалять после дедлайна
    if datetime.now() >= session.deadline:
        raise HTTPException(status_code=400, detail='Дедлайн сессии истек')
    # удаляем позицию
    db.delete(order_item)
    await db.flush()
    return {'detail': 'Позиция успешно удалена'}


    
