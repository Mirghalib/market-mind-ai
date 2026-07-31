"""pytest fixtures.

The app_client fixture overrides the get_db dependency so tests never
touch a real database.
"""
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.database.session import get_db
from main import create_app


@pytest_asyncio.fixture
async def app_client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://test{settings.API_V1_STR}",
    ) as client:
        yield client

    app.dependency_overrides.clear()


async def _override_get_db() -> AsyncIterator[None]:
    """Stub database dependency for tests (no DB access)."""
    yield None
