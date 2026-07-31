"""Admin dashboard endpoints — restricted to the admin role."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission_checker import RequirePermission
from app.dependencies.role_checker import RequireRole
from app.models.user import User
from app.schemas.dashboard import (
    AdminDashboardStats,
    AdminStrategiesResponse,
    AdminUsersResponse,
)
from app.schemas.user import UserRead
from app.services.admin_service import AdminService

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]

# Reusable authorization: every admin endpoint requires the caller to
# hold the "admin" role AND the matching permission.
AdminRole = Annotated[None, Depends(RequireRole("admin"))]
ManageUsers = Annotated[None, Depends(RequirePermission("manage_users"))]
ManageStrategies = Annotated[None, Depends(RequirePermission("delete_strategy"))]
ViewAnalytics = Annotated[None, Depends(RequirePermission("view_analytics"))]


@router.get(
    "/dashboard",
    response_model=AdminDashboardStats,
    summary="Admin dashboard aggregates",
)
async def admin_dashboard(
    _: AdminRole,
    __: ViewAnalytics,
    db: DbDep,
) -> AdminDashboardStats:
    """Return platform-wide counts for the admin dashboard."""
    stats = await AdminService(db).dashboard_stats()
    return AdminDashboardStats(**stats)


@router.get(
    "/users",
    response_model=AdminUsersResponse,
    summary="List all users",
)
async def admin_list_users(
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> AdminUsersResponse:
    """Return all users (admin only)."""
    users = await AdminService(db).list_users()
    return AdminUsersResponse(items=users, total=len(users))


@router.get(
    "/strategies",
    response_model=AdminStrategiesResponse,
    summary="List all strategies",
)
async def admin_list_strategies(
    _: AdminRole,
    __: ManageStrategies,
    db: DbDep,
) -> AdminStrategiesResponse:
    """Return all strategies (admin only)."""
    strategies = await AdminService(db).list_strategies()
    return AdminStrategiesResponse(items=strategies, total=len(strategies))


@router.get(
    "/analytics",
    summary="Platform analytics placeholder",
)
async def admin_analytics(
    _: AdminRole,
    __: ViewAnalytics,
    db: DbDep,
) -> dict[str, int]:
    """Return analytics aggregates; extended with real charts later."""
    stats = await AdminService(db).dashboard_stats()
    return {"generations": stats["total_generations"], "exports": stats["total_exports"]}


@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def admin_delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> None:
    """Permanently delete a user account (admin only)."""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot delete their own account",
        )
    deleted = await AdminService(db).delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get(
    "/user/{user_id}",
    summary="Get a user with per-user aggregates",
)
async def admin_get_user(
    user_id: uuid.UUID,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> dict:
    """Return a user's profile plus strategy/export counts (admin only)."""
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    detail = await AdminService(db).get_user_detail(user_id)
    return {
        **UserRead.model_validate(user).model_dump(),
        **detail,
    }


@router.patch(
    "/user/{user_id}/status",
    response_model=UserRead,
    summary="Block or unblock a user",
)
async def admin_set_user_status(
    user_id: uuid.UUID,
    payload: dict[str, bool],
    current_user: Annotated[User, Depends(get_current_user)],
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> User:
    """Block (is_active=false) or unblock (is_active=true) a user."""
    is_active = payload.get("is_active")
    if not isinstance(is_active, bool):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'is_active' must be a boolean",
        )
    if current_user.id == user_id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot block their own account",
        )
    updated = await AdminService(db).set_user_active(user_id, is_active)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = await db.get(User, user_id)
    return user


@router.delete(
    "/strategy/{strategy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a strategy",
)
async def admin_delete_strategy(
    strategy_id: uuid.UUID,
    _: AdminRole,
    __: ManageStrategies,
    db: DbDep,
) -> None:
    """Permanently delete a marketing strategy (admin only)."""
    deleted = await AdminService(db).delete_strategy(strategy_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
