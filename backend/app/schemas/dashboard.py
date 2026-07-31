"""Pydantic schemas for admin and user dashboards."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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


class AdminUsersResponse(BaseModel):
    items: list[UserRead]
    total: int


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
