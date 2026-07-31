"""Tests for reusable middleware: logging, CORS, error handling, timing."""
import logging

import pytest
from fastapi import APIRouter, Depends
from httpx import ASGITransport, AsyncClient

from app.database.session import get_db


@pytest.mark.asyncio
async def test_request_logging_writes_access_line(app_client, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="market_mind_ai.access"):
        response = await app_client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")

    records = [r for r in caplog.records if r.name == "market_mind_ai.access"]
    assert len(records) == 1
    assert records[0].message == "GET /api/v1/health -> 200 from 127.0.0.1"
    assert records[0].request_id == response.headers["x-request-id"]
    assert records[0].duration_ms >= 0


@pytest.mark.asyncio
async def test_request_logging_tracks_error_responses(app_client, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="market_mind_ai.access"):
        response = await app_client.get("/generation-history")

    assert response.status_code == 401
    records = [r for r in caplog.records if r.name == "market_mind_ai.access"]
    assert len(records) == 1
    assert "-> 401" in records[0].message


@pytest.mark.asyncio
async def test_cors_preflight(app_client) -> None:
    response = await app_client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "GET" in response.headers["access-control-allow-methods"]


@pytest.mark.asyncio
async def test_cors_allowed_origin_header(app_client) -> None:
    response = await app_client.get(
        "/health", headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_cors_disallowed_origin(app_client) -> None:
    response = await app_client.get(
        "/health", headers={"Origin": "http://evil.example.com"}
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.asyncio
async def test_request_id_propagates(app_client) -> None:
    response = await app_client.get(
        "/health", headers={"X-Request-ID": "test-request-123"}
    )
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request-123"


@pytest.mark.asyncio
async def test_unhandled_error_returns_json_500() -> None:
    """A route that raises an unhandled exception gets a clean JSON 500."""

    async def boom() -> None:
        raise RuntimeError("boom")

    router = APIRouter()
    router.add_api_route("/boom", boom, methods=["GET"])

    # Mount on a fresh app to avoid polluting the shared one
    from main import create_app

    test_app = create_app()
    test_app.include_router(router)

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.get("/boom")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Internal server error"}
