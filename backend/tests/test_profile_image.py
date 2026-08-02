"""End-to-end tests for profile image uploads."""
import io
import uuid
from pathlib import Path

import pytest

from app.core.config import settings


async def _register_and_login(client, email: str | None = None) -> str:
    """Register a user with a unique email and return a token."""
    email = email or f"image-{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Image Tester"},
    )
    assert r.status_code == 201, r.text
    r = await client.post(
        "/auth/login",
        json={"email": email, "password": "supersecret"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _png_bytes(size: int = 1024) -> bytes:
    """Minimal-but-plausible PNG header + padding to size."""
    header = b"\x89PNG\r\n\x1a\n" + b"\x00" * (size - 8)
    return header[:size]


@pytest.mark.asyncio
async def test_upload_profile_image_success(seeded_app_client, tmp_path) -> None:
    token = await _register_and_login(seeded_app_client)

    files = {
        "profile_image": (
            "avatar.png",
            io.BytesIO(_png_bytes()),
            "image/png",
        )
    }
    response = await seeded_app_client.put(
        "/dashboard/profile",
        data={"full_name": "New Name"},
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "New Name"
    assert body["profile_image"].startswith(
        "http://localhost:8000/uploads/profile_images/"
    )

    # Relative path stored in the DB, file on disk with a UUID name
    relative = body["profile_image"].split("/uploads/", 1)[1]
    assert relative.startswith("profile_images/")
    assert relative.endswith(".png")
    path = Path("uploads") / relative
    assert path.is_file()
    uuid.UUID(path.stem)  # raises if not a valid UUID hex


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_type(seeded_app_client) -> None:
    token = await _register_and_login(seeded_app_client)

    response = await seeded_app_client.put(
        "/dashboard/profile",
        files={
            "profile_image": (
                "malware.exe",
                io.BytesIO(b"MZ\x90\x00"),
                "application/octet-stream",
            )
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_rejects_large_file(seeded_app_client) -> None:
    token = await _register_and_login(seeded_app_client)

    big = _png_bytes(settings.UPLOAD_MAX_SIZE + 1)
    response = await seeded_app_client.put(
        "/dashboard/profile",
        files={
            "profile_image": (
                "big.png",
                io.BytesIO(big),
                "image/png",
            )
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_replaces_and_deletes_old_image(
    seeded_app_client, tmp_path
) -> None:
    token = await _register_and_login(seeded_app_client)
    headers = {"Authorization": f"Bearer {token}"}

    first = await seeded_app_client.put(
        "/dashboard/profile",
        files={
            "profile_image": ("a.png", io.BytesIO(_png_bytes()), "image/png")
        },
        headers=headers,
    )
    assert first.status_code == 200
    first_path = first.json()["profile_image"].split("/uploads/", 1)[1]

    second = await seeded_app_client.put(
        "/dashboard/profile",
        files={
            "profile_image": ("b.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 16), "image/jpeg")
        },
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json()["profile_image"] != first.json()["profile_image"]

    # Old file should be gone, new file present
    assert not (Path("uploads") / first_path).exists()
    second_path = Path("uploads") / second.json()["profile_image"].split("/uploads/", 1)[1]
    assert second_path.exists()


@pytest.mark.asyncio
async def test_profile_get_returns_image_url(seeded_app_client) -> None:
    token = await _register_and_login(seeded_app_client)
    headers = {"Authorization": f"Bearer {token}"}

    await seeded_app_client.put(
        "/dashboard/profile",
        files={
            "profile_image": ("a.png", io.BytesIO(_png_bytes()), "image/png")
        },
        headers=headers,
    )

    response = await seeded_app_client.get("/dashboard/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["profile_image"].startswith(
        "http://localhost:8000/uploads/profile_images/"
    )


@pytest.mark.asyncio
async def test_uploaded_file_served_statically(seeded_app_client) -> None:
    """The /uploads mount serves the stored file."""
    from httpx import ASGITransport, AsyncClient

    from app.database.session import get_db
    from main import create_app

    token = await _register_and_login(seeded_app_client)

    upload = await seeded_app_client.put(
        "/dashboard/profile",
        files={
            "profile_image": ("a.png", io.BytesIO(_png_bytes()), "image/png")
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200
    url = upload.json()["profile_image"]
    relative = url.split("/uploads/", 1)[1]

    # Build a fresh app (same in-memory DB override) with a base URL that
    # does NOT include /api/v1, so the /uploads mount is reachable.
    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/uploads/{relative}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")


async def _override_get_db():
    """Yield a fresh session from the shared in-memory test engine."""
    from tests.conftest import _TestSessionLocal

    async with _TestSessionLocal() as session:
        yield session
