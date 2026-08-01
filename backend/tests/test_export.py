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
        "pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".pptx",
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
    # Files are persisted under <strategy_id>/<export_id>.<ext> relative
    # to the export directory, and the public URL is populated.
    assert exports[0].file_key.endswith(".json")
    assert str(strategy.id) in exports[0].file_key
    assert exports[0].file_url.endswith(f"/uploads/exports/{exports[0].file_key}")


@pytest.mark.asyncio
async def test_export_list_and_download(app_client, db_session) -> None:
    """The list endpoint returns owned exports and download re-serves the file."""
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create two exports.
    for fmt in ("json", "pdf"):
        response = await app_client.post(
            "/export",
            json={"strategy_id": str(strategy.id), "format": fmt},
            headers=headers,
        )
        assert response.status_code == 200

    # List.
    listing = await app_client.get("/dashboard/exports", headers=headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 2
    assert {item["format"] for item in body["items"]} == {"json", "pdf"}
    assert all(item["strategy_name"] == "Launch Strategy" for item in body["items"])
    export_id = body["items"][0]["id"]

    # Download re-serves the saved file.
    download = await app_client.get(f"/export/{export_id}", headers=headers)
    assert download.status_code == 200
    assert len(download.content) > 0
    assert "attachment" in download.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_export_list_scoped_to_user(app_client, db_session) -> None:
    """Another user cannot see or download this user's exports."""
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "json"},
        headers=headers,
    )
    assert created.status_code == 200

    # Register a second user.
    second = await app_client.post(
        "/auth/register",
        json={"email": "other@example.com", "password": "supersecret"},
    )
    assert second.status_code in (200, 201)
    login2 = await app_client.post(
        "/auth/login",
        json={"email": "other@example.com", "password": "supersecret"},
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    listing = await app_client.get("/dashboard/exports", headers=headers2)
    assert listing.status_code == 200
    assert listing.json()["total"] == 0

    from sqlalchemy import select

    from app.models.export import Export

    export_id = (
        await db_session.execute(select(Export).limit(1))
    ).scalar_one().id
    download = await app_client.get(f"/export/{export_id}", headers=headers2)
    assert download.status_code == 404


@pytest.mark.asyncio
async def test_email_export_unconfigured(app_client, db_session, monkeypatch) -> None:
    """Without SMTP config, the email endpoint returns a clear 503."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "SMTP_HOST", "")
    monkeypatch.setattr(settings, "SMTP_FROM", "")

    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "pdf"},
        headers=headers,
    )
    assert created.status_code == 200

    from sqlalchemy import select

    from app.models.export import Export

    export_id = (
        await db_session.execute(select(Export).limit(1))
    ).scalar_one().id

    response = await app_client.post(
        f"/export/{export_id}/email",
        json={"to_email": "recipient@example.com"},
        headers=headers,
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_email_export_sends_when_configured(
    app_client, db_session, monkeypatch
) -> None:
    """With SMTP configured, the endpoint delegates to EmailService."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test.com")
    monkeypatch.setattr(settings, "SMTP_FROM", "reports@test.com")

    sent = {}

    class FakeEmailService:
        def __init__(self):
            pass

        def send_report_email(self, **kwargs):
            sent.update(kwargs)

    import app.api.endpoints.export as export_module

    export_module.EmailService = FakeEmailService

    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)

    login = await app_client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "pdf"},
        headers=headers,
    )
    assert created.status_code == 200

    from sqlalchemy import select

    from app.models.export import Export

    export_id = (
        await db_session.execute(select(Export).limit(1))
    ).scalar_one().id

    response = await app_client.post(
        f"/export/{export_id}/email",
        json={"to_email": "recipient@example.com"},
        headers=headers,
    )
    assert response.status_code == 200
    assert sent["to_email"] == "recipient@example.com"
    assert "uploads/exports" in sent["public_url"]


@pytest.mark.asyncio
async def test_pdf_report_renders_full_strategy(app_client, db_session) -> None:
    """The professional PDF renderer produces a valid, non-trivial PDF."""
    from app.services.export.renderers import PdfRenderer

    user = await _register_user(db_session)
    strategy = await _create_strategy(
        db_session,
        user,
        content={
            "executiveSummary": {"summary": "S", "highlights": ["H"], "ask": "A"},
            "marketingScore": {"overall": 74, "breakdown": [], "benchmark": "", "summary": ""},
            "marketOverview": {"summary": "M", "marketTrends": [], "targetMarketSize": "X", "growthRate": "", "keyDrivers": [], "marketRisks": []},
            "socialMediaStrategy": {"summary": "S", "platforms": [], "communityManagement": [], "performanceMetrics": []},
            "implementationRoadmap": {"summary": "R", "phases": []},
            "weeklyMilestones": {"summary": "W", "weeks": []},
            "estimatedROI": {"summary": "R", "assumptions": [], "projections": [], "paybackPeriod": "", "methodology": ""},
            "riskMitigation": {"summary": "R", "risks": []},
            "finalRecommendations": {"summary": "F", "priorities": [], "quickWins": [], "longTermInvestments": [], "successCriteria": [], "closingStatement": ""},
        },
    )
    rendered = PdfRenderer().render(strategy)
    assert rendered.content[:4] == b"%PDF"
    assert len(rendered.content) > 5000


async def _create_strategy(
    session: AsyncSession,
    user: User,
    *,
    name: str = "Launch Strategy",
    content: dict | None = None,
) -> MarketingStrategy:
    project = Project(user_id=user.id, name="Export Project")
    session.add(project)
    await session.flush()

    strategy = MarketingStrategy(
        project_id=project.id,
        name=name,
        target_audience="Startup founders",
        goals=["Grow signups"],
        content=content or STRATEGY_CONTENT,
        status=StrategyStatus.COMPLETED,
    )
    session.add(strategy)
    await session.commit()
    return strategy
