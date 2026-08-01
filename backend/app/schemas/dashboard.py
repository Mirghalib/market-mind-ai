"""Pydantic schemas for admin and user dashboards."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.user import UserRead


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None


class AdminDashboardStats(BaseModel):
    """Aggregates shown on the admin dashboard."""

    total_users: int
    total_strategies: int
    total_generations: int
    total_exports: int


class AdminUserItem(UserRead):
    """A user row with per-user aggregates for the admin panel."""

    total_strategies: int = 0
    total_exports: int = 0
    total_projects: int = 0
    storage_used: int = 0


class AdminUsersResponse(BaseModel):
    items: list[AdminUserItem]
    total: int
    limit: int
    offset: int
    has_more: bool


class AdminUserUpdate(BaseModel):
    """Editable fields for admin user management."""

    full_name: str | None = Field(default=None, max_length=255)
    role_name: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    is_email_verified: bool | None = None


class AdminUserCreate(BaseModel):
    """Direct user creation by an admin."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    role_name: str = "user"


class AdminUserResetPassword(BaseModel):
    """New password set by an admin on behalf of a user."""

    new_password: str = Field(min_length=8, max_length=128)


class InviteCreateRequest(BaseModel):
    """Payload for inviting a new user by email."""

    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    role_name: str = "user"


class InviteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role_name: str
    invited_by: uuid.UUID | None
    expires_at: datetime
    accepted_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class UserDashboardStats(BaseModel):
    """Aggregates shown on the user dashboard."""

    total_strategies: int
    total_generations: int
    total_exports: int
    latest_strategy: "StrategySummary | None" = None


class StrategySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    status: str
    created_at: datetime


class StrategyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    target_audience: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class AdminStrategiesResponse(BaseModel):
    items: list[StrategyRead]
    total: int


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str | None
    role_name: str | None
    is_active: bool
    profile_image: str | None
    created_at: datetime
