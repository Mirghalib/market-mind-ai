"""Tests for the admin analytics payload (charts, stats, activity feed)."""
import uuid

import pytest
from sqlalchemy import select

from app.models.export import Export, ExportFormat, ExportStatus
from app.models.generation_history import GenerationHistory
from app.models.marketing_strategy import MarketingStrategy, StrategyStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService


async def _create_user(session, email):
    return await UserService(session).register(
        UserCreate(email=email, password="supersecret", full_name=email.split("@")[0])
    )


async def _admin_login(client):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@marketmind.ai", "password": "Admin@123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _make_strategy(session, user, name):
    project = Project(user_id=user.id, name=name)
    session.add(project)
    await session.flush()
    strategy = MarketingStrategy(
        project_id=project.id,
        name=name,
        status=StrategyStatus.COMPLETED,
        content={"summary": "x"},
    )
    session.add(strategy)
    await session.commit()
    return strategy


@pytest.mark.asyncio
async def test_admin_analytics_payload(seeded_app_client, db_session) -> None:
    user = await _create_user(db_session, f"ana-{uuid.uuid4().hex[:8]}@example.com")
    strategy = await _make_strategy(db_session, user, "Analytics Strategy")

    # One completed export in pdf format.
    db_session.add(
        Export(
            strategy_id=strategy.id,
            format=ExportFormat.PDF,
            status=ExportStatus.COMPLETED,
        )
    )
    await db_session.commit()

    headers = await _admin_login(seeded_app_client)
    response = await seeded_app_client.get("/admin/analytics", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()

    # Stat cards.
    assert body["stats"]["total_users"] >= 2  # admin + created user
    assert body["stats"]["total_strategies"] >= 1
    assert body["stats"]["total_exports"] >= 1

    # Chart series all present and correctly shaped.
    assert body["strategy_trend"] and len(body["strategy_trend"]) == 30
    assert body["strategy_trend"][0]["label"]
    assert "value" in body["strategy_trend"][0]

    formats = {item["label"]: item["value"] for item in body["export_formats"]}
    assert formats.get("pdf", 0) >= 1

    statuses = {item["label"]: item["value"] for item in body["user_status"]}
    assert statuses["Active"] >= 2
    assert statuses["Blocked"] >= 0

    assert body["top_users"] and body["top_users"][0]["value"] >= 1
    assert body["monthly_registrations"] and len(body["monthly_registrations"]) == 12
    success = {item["label"]: item["value"] for item in body["strategy_success"]}
    assert success.get("completed", 0) >= 1
    assert "ai_requests_today" in body

    # Activity feed includes the seeded events.
    types = {event["type"] for event in body["recent_activity"]}
    assert "user_registered" in types
    assert "strategy_generated" in types
    assert "export_created" in types


@pytest.mark.asyncio
async def test_admin_analytics_requires_admin(seeded_app_client, db_session) -> None:
    user = await _create_user(db_session, "plain-user@example.com")
    login = await seeded_app_client.post(
        "/auth/login", json={"email": user.email, "password": "supersecret"}
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await seeded_app_client.get("/admin/analytics", headers=headers)
    assert response.status_code == 403
