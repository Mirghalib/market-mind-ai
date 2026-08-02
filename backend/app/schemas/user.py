"""Pydantic schemas for the User entity."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.functional_serializers import field_serializer

from app.core.config import settings


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    role_name: str | None
    profile_image: str | None
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
    is_email_verified: bool = False
    email_verified_at: datetime | None = None

    @field_serializer("profile_image")
    def _profile_image_url(self, value: str | None) -> str | None:
        """Expose the stored relative path as a publicly reachable URL."""
        if not value:
            return None
        if value.startswith(("http://", "https://")):
            return value
        base = settings.PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/{value}"


class UserUpdateProfile(BaseModel):
    """Editable profile fields for PUT /dashboard/profile."""

    full_name: str | None = Field(default=None, max_length=255)


class ChangePasswordRequest(BaseModel):
    """Payload for POST /dashboard/change-password."""

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
