from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import List
from crud import (create_session, get_active_session, get_session_by_id, update_session_status)
from schemas import (SessionCreate, SessionResponse, SessionStatusUpdate)

router = APIRouter(prefix="/sessions", tags=['Управление сессиями заказа'])

# POST /sessions
@router.post('/', response_model=SessionResponse, status_code=201)
async def creare_new_session(session_data: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await create_session(db, session_data)
    return session

# GET /sessions
@router.get('/', response_model=List[SessionResponse])
async def list_active_session(db: AsyncSession = Depends(get_db),):
    sessions = await get_active_session(db)
    return sessions

# GET /sessions/{session_id}
@router.get('/{session_id}', response_model=SessionResponse)
async def get_session_detail(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await get_session_by_id(db, session_id)
    from sqlalchemy import select
    from models import MenuItem
    result = await db.execute(
        select(MenuItem).where(MenuItem.session_id == session_id)
    )
    session.menu_items = result.scalars().all()
    return session

# PATCH /session/{session_id}/status
@router.patch('/{session_id}/status', response_model=SessionResponse)
async def change_session_status(
    session_id: int,
    status_data: SessionStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    session = await update_session_status(db, session_id, status_data.status)
    from sqlalchemy import select
    from models import MenuItem
    result = await db.execute(
        select(MenuItem).where(MenuItem.session_id == session_id)
    )
    session.menu_items = result.scalars().all()
    return session
