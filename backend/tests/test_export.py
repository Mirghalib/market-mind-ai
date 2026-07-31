"""End-to-end tests for the strategy export endpoint."""
import json
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketing_strategy import MarketingStrategy, StrategyStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService

USER_PAYLOAD = {
    "email": "export@example.com",
    "password": "supersecret",
    "full_name": "Export Tester",
}

STRATEGY_CONTENT = {
    "summary": "A SaaS strategy",
    "sections": [{"title": "Overview", "content": "Launch fast"}],
}


async def _register_user(session: AsyncSession) -> User:
    return await UserService(session).register(UserCreate(**USER_PAYLOAD))


async def _create_strategy(
    session: AsyncSession, user: User, *, name: str = "Launch Strategy"
) -> MarketingStrategy:
    project = Project(user_id=user.id, name="Export Project")
    session.add(project)
    await session.flush()

    strategy = MarketingStrategy(
        project_id=project.id,
        name=name,
        target_audience="Startup founders",
        goals=["Grow signups"],
        content=STRATEGY_CONTENT,
        status=StrategyStatus.COMPLETED,
    )
    session.add(strategy)
    await session.commit()
    return strategy


@pytest.mark.asyncio
async def test_export_requires_auth(app_client) -> None:
    response = await app_client.post(
        "/export", json={"strategy_id": str(uuid.uuid4())}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_json_success(app_client, db_session) -> None:
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "json"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "attachment" in response.headers["content-disposition"]
    assert response.headers["content-disposition"].endswith('.json"')

    body = response.json()
    assert body["strategy_id"] == str(strategy.id)
    assert body["name"] == "Launch Strategy"
    assert body["content"] == STRATEGY_CONTENT
    assert body["status"] == "completed"


@pytest.mark.asyncio
async def test_export_unknown_strategy(app_client, db_session) -> None:
    user = await _register_user(db_session)
    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.post(
        "/export",
        json={"strategy_id": str(uuid.uuid4())},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Strategy not found"


@pytest.mark.asyncio
async def test_export_all_formats(app_client, db_session) -> None:
    """Every registered format renders a downloadable file."""
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    expected = {
        "json": ("application/json", ".json"),
        "markdown": ("text/markdown", ".md"),
        "html": ("text/html", ".html"),
        "pdf": ("application/pdf", ".pdf"),
        "docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".docx",
        ),
    }
    for fmt, (media_type, ext) in expected.items():
        response = await app_client.post(
            "/export",
            json={"strategy_id": str(strategy.id), "format": fmt},
            headers=headers,
        )
        assert response.status_code == 200, fmt
        assert response.headers["content-type"].startswith(media_type), fmt
        assert "attachment" in response.headers["content-disposition"], fmt
        assert response.headers["content-disposition"].endswith(f'{ext}"'), fmt
        assert len(response.content) > 0, fmt


@pytest.mark.asyncio
async def test_export_invalid_format(app_client, db_session) -> None:
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Valid enum value but no renderer registered yet
    response = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "xlsx"},
        headers=headers,
    )
    assert response.status_code == 422  # not a valid enum value


@pytest.mark.asyncio
async def test_export_invalid_payload(app_client, db_session) -> None:
    user = await _register_user(db_session)
    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Unknown enum value -> 422 from validation
    response = await app_client.post(
        "/export",
        json={"strategy_id": str(uuid.uuid4()), "format": "xlsx"},
        headers=headers,
    )
    assert response.status_code == 422

    # Missing strategy_id -> 422 from validation
    response = await app_client.post(
        "/export",
        json={"format": "json"},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_export_records_persisted(app_client, db_session) -> None:
    """A successful export persists a completed Export row."""
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "json"},
        headers=headers,
    )
    assert response.status_code == 200

    from sqlalchemy import select

    from app.models.export import Export

    result = await db_session.execute(select(Export))
    exports = result.scalars().all()
    assert len(exports) == 1
    assert exports[0].strategy_id == strategy.id
    assert exports[0].format.value == "json"
    assert exports[0].status.value == "completed"
    assert exports[0].file_key.startswith("strategies/")
