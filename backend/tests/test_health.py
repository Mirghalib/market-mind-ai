"""Smoke tests for the health endpoint."""
import pytest


@pytest.mark.asyncio
async def test_health_check(app_client) -> None:
    response = await app_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] in {"ok", "unavailable"}


@pytest.mark.asyncio
async def test_request_id_header_present(app_client) -> None:
    response = await app_client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-request-id")
