"""Profile image handling: validation, storage and URL building.

Uploaded files are stored under ``uploads/profile_images/`` with a
UUID-based filename. Only the relative path (e.g.
``uploads/profile_images/<uuid>.jpg``) is persisted in the database;
the public URL is derived at response time from PUBLIC_BASE_URL.
"""
import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

logger = logging.getLogger("market_mind_ai.profile_image")

MAX_SIZE = settings.UPLOAD_MAX_SIZE
ALLOWED_TYPES = settings.PROFILE_IMAGE_ALLOWED_TYPES
IMAGE_DIR = Path(settings.PROFILE_IMAGE_DIR)


class ProfileImageError(Exception):
    """Base error for profile image failures."""


class UnsupportedImageTypeError(ProfileImageError):
    """Raised when the file extension or MIME type is not allowed."""


class ImageTooLargeError(ProfileImageError):
    """Raised when the uploaded file exceeds UPLOAD_MAX_SIZE."""


def _ensure_upload_dir() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def _validate(filename: str, content_type: str | None) -> str:
    """Return the canonical extension for a valid image, else raise."""
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_TYPES:
        raise UnsupportedImageTypeError(
            "Unsupported image type; allowed: jpg, jpeg, png, webp"
        )
    if content_type not in ALLOWED_TYPES.values():
        raise UnsupportedImageTypeError(
            f"Unsupported content type: {content_type or 'unknown'}"
        )
    return ext


async def save_profile_image(file: UploadFile) -> str:
    """Validate and persist an uploaded image, returning its relative path.

    The whole payload is read in-memory so its size can be enforced
    (5 MB cap). The relative path is what callers store in the User row.
    """
    try:
        ext = _validate(file.filename or "", file.content_type)
    except UnsupportedImageTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File too large; maximum size is {MAX_SIZE // (1024 * 1024)} MB",
        )

    _ensure_upload_dir()
    filename = f"{uuid.uuid4().hex}.{ext}"
    # uuid-hex guarantees a collision-free unique name.
    relative_path = f"{settings.PROFILE_IMAGE_DIR}/{filename}"
    destination = IMAGE_DIR / filename

    try:
        destination.write_bytes(content)
    except OSError:
        logger.exception("Failed to write profile image %s", destination)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save profile image",
        ) from None

    logger.info("Saved profile image %s (%d bytes)", relative_path, len(content))
    return relative_path


def delete_profile_image(relative_path: str | None) -> None:
    """Remove a previously stored image (best-effort, on replace)."""
    if not relative_path:
        return
    path = Path(relative_path)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        logger.warning("Could not remove old profile image %s", relative_path)


def profile_image_url(relative_path: str | None) -> str | None:
    """Convert a stored relative path into a publicly reachable URL."""
    if not relative_path:
        return None
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return f"{base}/{relative_path}"
