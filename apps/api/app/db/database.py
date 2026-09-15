"""AEGIS - Local SQLite & Async Engine Setup"""
import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "aegis.db")).replace("\\", "/")
LOCAL_DB_URL = f"sqlite+aiosqlite:///{SQLITE_PATH}"

engine = create_async_engine(
    LOCAL_DB_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
