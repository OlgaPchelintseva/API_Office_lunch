from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(__file__), 'office_lunch.db')}" #вернет абсолютный путь корневой папки, тут будет искать в дальнеййшем наш файл

engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    connect_args = {"check_same_thread": False} # для возможности поключения из разных потоков
)

AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session: # cjplftv ctccb. lkz ntreotuj pfghjcf
        try: 
            yield session # создаем сессию в инпоинт
            await session.commit()
        except Exception:
            await session.rollback() # откатываем сессию
            raise
        finally:
            await session.close() # закрываем сессию

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)