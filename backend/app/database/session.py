"""Async database engine and session factory."""
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    # Recycle connections before the transaction-mode pooler (pgbouncer)
    # drops idle ones (~60s) so we never hand out a closed connection.
    pool_pre_ping=True,
    pool_recycle=45,
    pool_size=10,
    max_overflow=10,
    # Supabase's transaction-mode pooler does not support asyncpg
    # prepared statements, so they must be disabled here.
    connect_args={"statement_cache_size": 0},
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a database session and
    always closes it afterwards."""
    async with SessionLocal() as session:
        yield session
