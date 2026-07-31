"""End-to-end tests for the generation history endpoints."""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation_history import GenerationHistory, GenerationStatus
from app.models.marketing_strategy import MarketingStrategy, StrategyStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService

USER_PAYLOAD = {
    "email": "history@example.com",
    "password": "supersecret",
    "full_name": "History Tester",
}


async def _register_user(session: AsyncSession) -> User:
    return await UserService(session).register(UserCreate(**USER_PAYLOAD))


async def _create_strategy_with_history(
    session: AsyncSession, user: User, *, count: int = 3
) -> tuple[Project, MarketingStrategy, list[GenerationHistory]]:
    """Seed a user-owned project, strategy and N history records."""
    project = Project(user_id=user.id, name="History Project")
    session.add(project)
    await session.flush()

    strategy = MarketingStrategy(
        project_id=project.id,
        name="Launch Strategy",
        status=StrategyStatus.COMPLETED,
    )
    session.add(strategy)
    await session.flush()

    records = [
        GenerationHistory(
            strategy_id=strategy.id,
            model_used=f"mock-model-{i}",
            status=GenerationStatus.SUCCESS,
            latency_ms=12.5 * i,
        )
        for i in range(count)
    ]
    session.add_all(records)
    await session.commit()
    return project, strategy, records


@pytest.mark.asyncio
async def test_list_requires_auth(app_client) -> None:
    response = await app_client.get("/generation-history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_returns_paginated_records(app_client, db_session) -> None:
    user = await _register_user(db_session)
    await _create_strategy_with_history(db_session, user, count=5)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.get(
        "/generation-history?limit=2&offset=0", headers=headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["has_more"] is True
    assert len(body["items"]) == 2
    assert all(item["model_used"].startswith("mock-model-") for item in body["items"])


@pytest.mark.asyncio
async def test_list_filter_by_strategy(app_client, db_session) -> None:
    user = await _register_user(db_session)
    _, strategy, records = await _create_strategy_with_history(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.get(
        f"/generation-history?strategy_id={strategy.id}", headers=headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == len(records)
    assert all(item["strategy_id"] == str(strategy.id) for item in body["items"])


@pytest.mark.asyncio
async def test_get_record(app_client, db_session) -> None:
    user = await _register_user(db_session)
    _, _, records = await _create_strategy_with_history(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.get(
        f"/generation-history/{records[0].id}", headers=headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(records[0].id)
    assert body["status"] == "success"
    assert body["model_used"] == records[0].model_used


@pytest.mark.asyncio
async def test_get_missing_record(app_client, db_session) -> None:
    user = await _register_user(db_session)
    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.get(
        f"/generation-history/{uuid.uuid4()}", headers=headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_record(app_client, db_session) -> None:
    user = await _register_user(db_session)
    _, _, records = await _create_strategy_with_history(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.delete(
        f"/generation-history/{records[0].id}", headers=headers
    )
    assert response.status_code == 204

    # Deleted record is gone from the list
    list_response = await app_client.get("/generation-history", headers=headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == len(records) - 1
    assert all(item["id"] != str(records[0].id) for item in body["items"])


@pytest.mark.asyncio
async def test_delete_missing_record(app_client, db_session) -> None:
    user = await _register_user(db_session)
    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await app_client.delete(
        f"/generation-history/{uuid.uuid4()}", headers=headers
    )
    assert response.status_code == 404
