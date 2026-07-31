"""Tests for the AI strategy generation endpoint."""
import pytest

VALID_PAYLOAD = {
    "project_name": "Launchpad",
    "industry": "SaaS",
    "target_audience": "Startup founders",
    "goals": ["Increase signups", "Improve retention"],
}


@pytest.mark.asyncio
async def test_generate_success(app_client) -> None:
    response = await app_client.post("/generate", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["strategy_id"]
    assert body["model_used"].startswith("mock-")
    assert body["summary"]
    assert len(body["sections"]) >= 3
    assert all(s["title"] and s["content"] for s in body["sections"])


@pytest.mark.asyncio
async def test_generate_validates_request(app_client) -> None:
    # Missing required field
    response = await app_client.post(
        "/generate",
        json={"industry": "SaaS", "target_audience": "x", "goals": ["y"]},
    )
    assert response.status_code == 422

    # Empty goals list
    response = await app_client.post(
        "/generate",
        json={**VALID_PAYLOAD, "goals": []},
    )
    assert response.status_code == 422

    # Invalid tone
    response = await app_client.post(
        "/generate",
        json={**VALID_PAYLOAD, "tone": "aggressive"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_tone_choices(app_client) -> None:
    for tone in ("professional", "friendly", "persuasive"):
        response = await app_client.post(
            "/generate", json={**VALID_PAYLOAD, "tone": tone}
        )
        assert response.status_code == 200
        assert tone in response.json()["summary"]
