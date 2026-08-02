"""pytest fixtures.

The app_client fixture wires the app to an in-memory SQLite database
(via aiosqlite) so tests exercise real persistence without needing
PostgreSQL.

Provider API keys are cleared for the whole test session so endpoint
tests deterministically exercise the deterministic mock generation
path instead of consuming live LLM tokens.
"""
from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from main import create_app

# Never hit a live LLM provider from the endpoint test suite.
settings.AI_API_KEY = ""

# The endpoint tests exercise the deterministic mock generation path
# (offline/demo behavior), so the fallback must be enabled.
settings.AI_FALLBACK_TO_MOCK = True

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


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Yield a direct session for seeding test data (same in-memory DB)."""
    async with _TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def seeded_db_session() -> AsyncIterator[AsyncSession]:
    """DB session with the RBAC baseline seeded (roles, permissions, admin)."""
    from app.seeders.seed_roles import seed_roles
    from app.seeders.seed_permissions import seed_permissions
    from app.seeders.seed_admin import seed_admin

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSessionLocal() as session:
        await seed_roles(session)
        await seed_permissions(session)
        await seed_admin(session)
        yield session


@pytest_asyncio.fixture
async def seeded_app_client(seeded_db_session) -> AsyncIterator[AsyncClient]:
    """App client whose dependency override shares the seeded in-memory DB."""
    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://test{settings.API_V1_STR}",
    ) as client:
        yield client

    app.dependency_overrides.clear()


async def _override_get_db() -> AsyncIterator[AsyncSession]:
    """Yield a fresh session for each request (in-memory SQLite)."""
    async with _TestSessionLocal() as session:
        yield session
