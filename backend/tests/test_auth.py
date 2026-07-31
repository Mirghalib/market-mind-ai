"""End-to-end tests for the authentication flow."""
import pytest


@pytest.mark.asyncio
async def test_register_success(app_client) -> None:
    response = await app_client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "supersecret",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["full_name"] == "Test User"
    assert body["is_active"] is True
    assert "password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email(app_client) -> None:
    payload = {
        "email": "dup@example.com",
        "password": "supersecret",
    }
    first = await app_client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await app_client.post("/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password_rejected(app_client) -> None:
    response = await app_client.post(
        "/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(app_client) -> None:
    await app_client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    response = await app_client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(app_client) -> None:
    await app_client.post(
        "/auth/register",
        json={"email": "badpw@example.com", "password": "supersecret"},
    )
    response = await app_client.post(
        "/auth/login",
        json={"email": "badpw@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(app_client) -> None:
    response = await app_client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "supersecret"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(app_client) -> None:
    await app_client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "supersecret"},
    )
    login = await app_client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": "supersecret"},
    )
    token = login.json()["access_token"]

    response = await app_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_me_without_token(app_client) -> None:
    response = await app_client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_garbage_token(app_client) -> None:
    response = await app_client.get(
        "/auth/me", headers={"Authorization": "Bearer not.a.jwt"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_oauth2_token_endpoint(app_client) -> None:
    """The OAuth2 form endpoint (Swagger Authorize) must also work."""
    await app_client.post(
        "/auth/register",
        json={"email": "form@example.com", "password": "supersecret"},
    )
    response = await app_client.post(
        "/auth/token",
        data={"username": "form@example.com", "password": "supersecret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
