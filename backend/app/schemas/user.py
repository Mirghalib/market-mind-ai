"""Pydantic schemas for the User entity."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class UserUpdateProfile(BaseModel):
    """Editable profile fields for PUT /dashboard/profile."""

    full_name: str | None = Field(default=None, max_length=255)


class ChangePasswordRequest(BaseModel):
    """Payload for POST /dashboard/change-password."""

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
