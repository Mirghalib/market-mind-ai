"""End-to-end tests for the RBAC architecture."""
import uuid

import pytest
from sqlalchemy import select

from app.models.role import Role
from app.models.user import User


async def _login(client, email: str, password: str) -> str:
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Seeding ---


@pytest.mark.asyncio
async def test_seeder_creates_roles_permissions_admin(seeded_db_session) -> None:
    roles = (await seeded_db_session.execute(select(Role))).scalars().all()
    names = {r.name for r in roles}
    assert names == {"admin", "user"}

    from app.models.permission import Permission

    perms = (await seeded_db_session.execute(select(Permission))).scalars().all()
    perm_names = {p.name for p in perms}
    assert "manage_users" in perm_names
    assert "view_analytics" in perm_names

    admin = await seeded_db_session.scalar(
        select(User).where(User.email == "admin@marketmind.ai")
    )
    assert admin is not None
    assert admin.role_name == "admin"

    # Idempotent: re-running the seeder must not duplicate rows
    from app.seeders.seed_roles import seed_roles
    from app.seeders.seed_permissions import seed_permissions
    from app.seeders.seed_admin import seed_admin

    await seed_roles(seeded_db_session)
    await seed_permissions(seeded_db_session)
    await seed_admin(seeded_db_session)

    roles2 = (await seeded_db_session.execute(select(Role))).scalars().all()
    assert len(roles2) == 2


@pytest.mark.asyncio
async def test_admin_role_has_all_permissions(seeded_db_session) -> None:
    from app.models.permission import Permission
    from app.models.role_permission import RolePermission
    from app.services.authorization_service import ALL_PERMISSIONS

    admin = await seeded_db_session.scalar(
        select(Role).where(Role.name == "admin")
    )
    result = await seeded_db_session.execute(
        select(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == admin.id)
    )
    granted = set(result.scalars().all())
    assert granted == set(ALL_PERMISSIONS)


# --- JWT claims ---


@pytest.mark.asyncio
async def test_jwt_contains_user_id_email_role(seeded_app_client) -> None:
    token = await _login(
        seeded_app_client, "admin@marketmind.ai", "Admin@123"
    )
    from jose import jwt as pyjwt

    from app.core.config import settings

    payload = pyjwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["role"] == "admin"
    assert payload["email"] == "admin@marketmind.ai"
    assert payload["user_id"]


# --- Authorization enforcement ---


@pytest.mark.asyncio
async def test_admin_dashboard_requires_admin_role(seeded_app_client) -> None:
    # Unauthenticated
    response = await seeded_app_client.get("/admin/dashboard")
    assert response.status_code == 401

    # Regular user lacks the admin role -> 403
    await seeded_app_client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    user_token = await _login(seeded_app_client, "user@example.com", "supersecret")
    response = await seeded_app_client.get(
        "/admin/dashboard", headers=_auth(user_token)
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_dashboard_ok_for_admin(seeded_app_client) -> None:
    admin_token = await _login(seeded_app_client, "admin@marketmind.ai", "Admin@123")
    response = await seeded_app_client.get(
        "/admin/dashboard", headers=_auth(admin_token)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_users"] >= 1
    assert "total_strategies" in body


@pytest.mark.asyncio
async def test_admin_list_users_permission(seeded_app_client) -> None:
    admin_token = await _login(seeded_app_client, "admin@marketmind.ai", "Admin@123")
    response = await seeded_app_client.get(
        "/admin/users", headers=_auth(admin_token)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(u["email"] == "admin@marketmind.ai" for u in body["items"])
    assert "role_name" in body["items"][0]


@pytest.mark.asyncio
async def test_admin_cannot_delete_self(seeded_app_client) -> None:
    admin_token = await _login(seeded_app_client, "admin@marketmind.ai", "Admin@123")
    me = await seeded_app_client.get("/auth/me", headers=_auth(admin_token))
    my_id = me.json()["id"]
    response = await seeded_app_client.delete(
        f"/admin/user/{my_id}", headers=_auth(admin_token)
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_delete_user(seeded_app_client) -> None:
    await seeded_app_client.post(
        "/auth/register",
        json={"email": "doomed@example.com", "password": "supersecret"},
    )
    admin_token = await _login(seeded_app_client, "admin@marketmind.ai", "Admin@123")
    listing = await seeded_app_client.get(
        "/admin/users", headers=_auth(admin_token)
    )
    doomed = next(
        u for u in listing.json()["items"] if u["email"] == "doomed@example.com"
    )
    response = await seeded_app_client.delete(
        f"/admin/user/{doomed['id']}", headers=_auth(admin_token)
    )
    assert response.status_code == 204


# --- User dashboard ---


@pytest.mark.asyncio
async def test_user_dashboard_and_profile(seeded_app_client) -> None:
    await seeded_app_client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "supersecret"},
    )
    token = await _login(seeded_app_client, "user@example.com", "supersecret")

    dash = await seeded_app_client.get("/dashboard/dashboard", headers=_auth(token))
    assert dash.status_code == 200
    assert "total_strategies" in dash.json()

    profile = await seeded_app_client.get("/dashboard/profile", headers=_auth(token))
    assert profile.status_code == 200
    assert profile.json()["email"] == "user@example.com"
    assert profile.json()["role_name"] == "user"


@pytest.mark.asyncio
async def test_user_can_update_profile(seeded_app_client) -> None:
    await seeded_app_client.post(
        "/auth/register",
        json={"email": "updater@example.com", "password": "supersecret"},
    )
    token = await _login(seeded_app_client, "updater@example.com", "supersecret")

    response = await seeded_app_client.put(
        "/dashboard/profile",
        json={"full_name": "New Name"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name"


@pytest.mark.asyncio
async def test_user_generate_and_history(seeded_app_client) -> None:
    await seeded_app_client.post(
        "/auth/register",
        json={"email": "creator@example.com", "password": "supersecret"},
    )
    token = await _login(seeded_app_client, "creator@example.com", "supersecret")

    gen = await seeded_app_client.post(
        "/dashboard/generate",
        json={
            "project_name": "Launchpad",
            "industry": "SaaS",
            "target_audience": "Founders",
            "goals": ["Grow"],
        },
        headers=_auth(token),
    )
    assert gen.status_code == 200
    assert gen.json()["strategy_id"]

    history = await seeded_app_client.get(
        "/dashboard/history", headers=_auth(token)
    )
    assert history.status_code == 200
    assert history.json()["total"] >= 0


@pytest.mark.asyncio
async def test_user_export_permission(seeded_app_client) -> None:
    await seeded_app_client.post(
        "/auth/register",
        json={"email": "exporter@example.com", "password": "supersecret"},
    )
    token = await _login(seeded_app_client, "exporter@example.com", "supersecret")

    response = await seeded_app_client.post(
        "/dashboard/export",
        json={"strategy_id": str(uuid.uuid4()), "format": "json"},
        headers=_auth(token),
    )
    # Export permission is granted to "user"; missing strategy -> 404
    assert response.status_code == 404
