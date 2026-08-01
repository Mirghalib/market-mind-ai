"""Tests for the AI strategy generation endpoint."""
import pytest

VALID_PAYLOAD = {
    "project_name": "Launchpad",
    "industry": "SaaS",
    "target_audience": "Startup founders",
    "goals": ["Increase signups", "Improve retention"],
}


async def _authed_headers(client) -> dict[str, str]:
    """Register a throwaway user and return Bearer headers."""
    await client.post(
        "/auth/register",
        json={"email": "gen@example.com", "password": "supersecret"},
    )
    login = await client.post(
        "/auth/login",
        json={"email": "gen@example.com", "password": "supersecret"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_generate_requires_auth(app_client) -> None:
    response = await app_client.post("/generate", json=VALID_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_generate_success(app_client) -> None:
    headers = await _authed_headers(app_client)
    response = await app_client.post("/generate", json=VALID_PAYLOAD, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["strategy_id"]
    assert body["model_used"]
    assert body["summary"]
    assert len(body["sections"]) >= 3
    assert all(s["title"] and s["content"] for s in body["sections"])
    # The full structured payload is included for the report generators.
    assert body["content"]
    assert "marketingScore" in body["content"]
    assert "implementationRoadmap" in body["content"]
    assert "estimatedROI" in body["content"]


@pytest.mark.asyncio
async def test_generate_validates_request(app_client) -> None:
    headers = await _authed_headers(app_client)
    # Missing required field
    response = await app_client.post(
        "/generate",
        json={"industry": "SaaS", "target_audience": "x", "goals": ["y"]},
        headers=headers,
    )
    assert response.status_code == 422

    # Empty goals list
    response = await app_client.post(
        "/generate",
        json={**VALID_PAYLOAD, "goals": []},
        headers=headers,
    )
    assert response.status_code == 422

    # Invalid tone
    response = await app_client.post(
        "/generate",
        json={**VALID_PAYLOAD, "tone": "aggressive"},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_tone_choices(app_client) -> None:
    headers = await _authed_headers(app_client)
    for tone in ("professional", "friendly", "persuasive"):
        response = await app_client.post(
            "/generate",
            json={**VALID_PAYLOAD, "tone": tone},
            headers=headers,
        )
        assert response.status_code == 200
        assert tone in response.json()["summary"]


@pytest.mark.asyncio
async def test_generate_persists_strategy_and_history(app_client, db_session) -> None:
    """A successful generation creates project/strategy/history rows."""
    from sqlalchemy import select

    from app.models.generation_history import GenerationHistory
    from app.models.marketing_strategy import MarketingStrategy
    from app.models.project import Project

    headers = await _authed_headers(app_client)
    response = await app_client.post("/generate", json=VALID_PAYLOAD, headers=headers)
    assert response.status_code == 200
    strategy_id = response.json()["strategy_id"]

    strategies = (await db_session.execute(select(MarketingStrategy))).scalars().all()
    assert any(str(s.id) == strategy_id for s in strategies)

    projects = (await db_session.execute(select(Project))).scalars().all()
    assert len(projects) >= 1

    history = (await db_session.execute(select(GenerationHistory))).scalars().all()
    assert any(str(h.strategy_id) == strategy_id for h in history)
