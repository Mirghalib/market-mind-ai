"""pytest fixtures.

The app_client fixture wires the app to an in-memory SQLite database
(via aiosqlite) so tests exercise real persistence without needing
PostgreSQL.
"""
from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from main import create_app

_test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture
async def app_client() -> AsyncIterator[AsyncClient]:
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://test{settings.API_V1_STR}",
    ) as client:
        yield client

    app.dependency_overrides.clear()

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncIterator[AsyncSession]:
    """Yield a fresh session for each request (in-memory SQLite)."""
    async with _TestSessionLocal() as session:
        yield session
