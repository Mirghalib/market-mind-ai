"""End-to-end tests for invitations, share links and admin user management."""
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invitation import Invitation
from app.models.marketing_strategy import MarketingStrategy, StrategyStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.export_service import ExportService
from app.services.user_service import UserService

USER_PAYLOAD = {
    "email": "admin-flow@example.com",
    "password": "supersecret",
    "full_name": "Flow Tester",
}


async def _register_user(session: AsyncSession) -> User:
    return await UserService(session).register(UserCreate(**USER_PAYLOAD))


async def _login(client, email=USER_PAYLOAD["email"], password="supersecret"):
    response = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _admin_login(client):
    response = await client.post(
        "/auth/login",
        json={"email": "admin@marketmind.ai", "password": "Admin@123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _create_strategy(session: AsyncSession, user: User) -> MarketingStrategy:
    project = Project(user_id=user.id, name="Share Project")
    session.add(project)
    await session.flush()
    strategy = MarketingStrategy(
        project_id=project.id,
        name="Share Strategy",
        target_audience="Founders",
        goals=["Grow"],
        content={"summary": "A", "sections": [{"title": "Overview", "content": "B"}]},
        status=StrategyStatus.COMPLETED,
    )
    session.add(strategy)
    await session.commit()
    return strategy


# --- Share links -----------------------------------------------------------


@pytest.mark.asyncio
async def test_share_link_flow(app_client, db_session) -> None:
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)
    headers = await _login(app_client)

    # Create an export.
    created = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "json"},
        headers=headers,
    )
    assert created.status_code == 200

    from sqlalchemy import select

    from app.models.export import Export

    export_id = (await db_session.execute(select(Export).limit(1))).scalar_one().id

    # Create a share link.
    share = await app_client.post(
        f"/export/{export_id}/share", params={"expires_in_days": 7}, headers=headers
    )
    assert share.status_code == 201
    body = share.json()
    assert body["token"]
    assert body["url"].endswith(f"/api/v1/s/{body['token']}")

    # Open the shared report (public, no auth).
    opened = await app_client.get(f"/s/{body['token']}")
    assert opened.status_code == 200
    assert len(opened.content) > 0

    # List shares.
    listing = await app_client.get(f"/export/{export_id}/shares", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["items"][0]["token"] == body["token"]

    # Revoke the share.
    share_id = listing.json()["items"][0]["id"]
    revoked = await app_client.delete(
        f"/export/{export_id}/shares/{share_id}", headers=headers
    )
    assert revoked.status_code == 204

    # Now opening returns 410.
    opened = await app_client.get(f"/s/{body['token']}")
    assert opened.status_code == 410


@pytest.mark.asyncio
async def test_share_link_requires_owner(app_client, db_session) -> None:
    user = await _register_user(db_session)
    strategy = await _create_strategy(db_session, user)
    headers = await _login(app_client)

    created = await app_client.post(
        "/export",
        json={"strategy_id": str(strategy.id), "format": "json"},
        headers=headers,
    )
    assert created.status_code == 200

    from sqlalchemy import select

    from app.models.export import Export

    export_id = (await db_session.execute(select(Export).limit(1))).scalar_one().id

    # A second user cannot create a share for someone else's export.
    second = await app_client.post(
        "/auth/register",
        json={"email": "other-share@example.com", "password": "supersecret"},
    )
    assert second.status_code in (200, 201)
    headers2 = await _login(app_client, "other-share@example.com")
    share = await app_client.post(f"/export/{export_id}/share", headers=headers2)
    assert share.status_code == 404


# --- Invitations -----------------------------------------------------------


@pytest.mark.asyncio
async def test_invitation_flow(seeded_app_client, db_session) -> None:
    admin_headers = await _admin_login(seeded_app_client)

    email = f"invite-{uuid.uuid4().hex[:8]}@example.com"
    invite = await seeded_app_client.post(
        "/admin/invitations",
        json={"email": email, "full_name": "Invitee", "role_name": "user"},
        headers=admin_headers,
    )
    assert invite.status_code == 201, invite.text
    token = invite.json()["accept_url"].split("token=")[1]

    # Validate.
    validation = await seeded_app_client.get(f"/invitations/validate?token={token}")
    assert validation.status_code == 200
    assert validation.json()["email"] == email

    # Accept.
    accepted = await seeded_app_client.post(
        "/invitations/accept",
        json={"token": token, "full_name": "Invitee", "password": "Invite@123"},
    )
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["email"] == email
    assert accepted.json()["is_email_verified"] is True

    # The invitee can log in.
    login = await seeded_app_client.post(
        "/auth/login", json={"email": email, "password": "Invite@123"}
    )
    assert login.status_code == 200

    # Using the token again returns 410.
    again = await seeded_app_client.post(
        "/invitations/accept",
        json={"token": token, "full_name": "Invitee", "password": "Invite@123"},
    )
    assert again.status_code == 410


@pytest.mark.asyncio
async def test_invitation_duplicate_email(seeded_app_client, db_session) -> None:
    admin_headers = await _admin_login(seeded_app_client)
    email = "dup@example.com"

    first = await seeded_app_client.post(
        "/admin/invitations",
        json={"email": email, "full_name": "Dup", "role_name": "user"},
        headers=admin_headers,
    )
    assert first.status_code == 201

    second = await seeded_app_client.post(
        "/admin/invitations",
        json={"email": email, "full_name": "Dup", "role_name": "user"},
        headers=admin_headers,
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_invitation_expired(seeded_app_client, db_session) -> None:
    """An expired invitation returns a clear 410."""
    admin_headers = await _admin_login(seeded_app_client)
    email = f"expired-{uuid.uuid4().hex[:8]}@example.com"
    invite = await seeded_app_client.post(
        "/admin/invitations",
        json={"email": email, "full_name": "Exp", "role_name": "user"},
        headers=admin_headers,
    )
    assert invite.status_code == 201
    token = invite.json()["accept_url"].split("token=")[1]

    # Force expiry.
    from datetime import datetime, timedelta, timezone

    invitation = await db_session.scalar(
        select(Invitation).where(Invitation.email == email)
    )
    invitation.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    await db_session.commit()

    validation = await seeded_app_client.get(f"/invitations/validate?token={token}")
    assert validation.status_code == 410
    assert "expired" in validation.json()["detail"].lower()


# --- Admin user management --------------------------------------------------


@pytest.mark.asyncio
async def test_admin_create_update_block_delete(seeded_app_client, db_session) -> None:
    admin_headers = await _admin_login(seeded_app_client)

    email = f"managed-{uuid.uuid4().hex[:8]}@example.com"
    created = await seeded_app_client.post(
        "/admin/users",
        json={
            "email": email,
            "password": "Managed@123",
            "full_name": "Managed",
            "role_name": "user",
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]

    # Update role + name.
    updated = await seeded_app_client.patch(
        f"/admin/users/{user_id}",
        json={"full_name": "Managed Two"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Managed Two"

    # Block then unblock.
    blocked = await seeded_app_client.patch(
        f"/admin/users/{user_id}", json={"is_active": False}, headers=admin_headers
    )
    assert blocked.status_code == 200 and blocked.json()["is_active"] is False

    # Blocked user cannot log in.
    login = await seeded_app_client.post(
        "/auth/login", json={"email": email, "password": "Managed@123"}
    )
    assert login.status_code == 401

    unblocked = await seeded_app_client.patch(
        f"/admin/users/{user_id}", json={"is_active": True}, headers=admin_headers
    )
    assert unblocked.status_code == 200 and unblocked.json()["is_active"] is True

    # Reset password.
    reset = await seeded_app_client.post(
        f"/admin/users/{user_id}/reset-password",
        json={"new_password": "NewPass@123"},
        headers=admin_headers,
    )
    assert reset.status_code == 200

    # Verify email.
    verified = await seeded_app_client.post(
        f"/admin/users/{user_id}/verify-email", headers=admin_headers
    )
    assert verified.status_code == 200

    # Search finds the user.
    listing = await seeded_app_client.get(
        "/admin/users", params={"search": email}, headers=admin_headers
    )
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    # Delete (soft) then restore.
    deleted = await seeded_app_client.delete(
        f"/admin/users/{user_id}", headers=admin_headers
    )
    assert deleted.status_code == 204

    restored = await seeded_app_client.post(
        f"/admin/users/{user_id}/restore", headers=admin_headers
    )
    assert restored.status_code == 200
