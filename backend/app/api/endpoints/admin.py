"""Admin dashboard endpoints — restricted to the admin role."""
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission_checker import RequirePermission
from app.dependencies.role_checker import RequireRole
from app.models.role import Role
from app.models.user import User
from app.schemas.dashboard import (
    AdminAnalytics,
    AdminDashboardStats,
    AdminExportItem,
    AdminExportsResponse,
    AdminStrategiesResponse,
    AdminUserCreate,
    AdminUserItem,
    AdminUserResetPassword,
    AdminUserUpdate,
    AdminUsersResponse,
    InviteCreateRequest,
)
from app.schemas.user import UserRead
from app.services.admin_service import AdminService, UserNotFoundError
from app.services.email_service import (
    EmailNotConfiguredError,
    EmailService,
)
from app.services.invitation_service import (
    DuplicateInviteError,
    InvitationService,
)
from app.services.user_service import EmailAlreadyRegisteredError

router = APIRouter()

logger = logging.getLogger("market_mind_ai.admin")

DbDep = Annotated[AsyncSession, Depends(get_db)]

# Reusable authorization: every admin endpoint requires the caller to
# hold the "admin" role AND the matching permission.
AdminRole = Annotated[None, Depends(RequireRole("admin"))]
ManageUsers = Annotated[None, Depends(RequirePermission("manage_users"))]
ManageStrategies = Annotated[None, Depends(RequirePermission("delete_strategy"))]
ViewAnalytics = Annotated[None, Depends(RequirePermission("view_analytics"))]


def _to_admin_item(user: User, aggregates: dict) -> AdminUserItem:
    return AdminUserItem(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role_name=user.role_name,
        profile_image=user.profile_image,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        is_email_verified=user.is_email_verified,
        email_verified_at=user.email_verified_at,
        total_strategies=aggregates.get("total_strategies", 0),
        total_exports=aggregates.get("total_exports", 0),
        total_projects=aggregates.get("total_projects", 0),
        storage_used=aggregates.get("storage_used", 0),
    )


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
    summary="List all users with search/filter/pagination/sort",
)
async def admin_list_users(
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    status: str | None = Query(default=None, description="active|blocked"),
    verified: str | None = Query(default=None, description="verified|unverified"),
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminUsersResponse:
    """Return all users (admin only) with aggregates per user."""
    service = AdminService(db)
    users, total = await service.list_users(
        search=search,
        role=role,
        status=status,
        verified=verified,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
    items = []
    for user in users:
        agg = await service.user_aggregates(user.id)
        items.append(_to_admin_item(user, agg))
    return AdminUsersResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
    )


@router.get(
    "/users/{user_id}",
    summary="Get a user with per-user aggregates",
)
async def admin_get_user(
    user_id: uuid.UUID,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> dict:
    """Return a user's profile plus strategy/export counts (admin only)."""
    service = AdminService(db)
    try:
        user = await service.get_user(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    detail = await service.user_aggregates(user_id)
    return {
        **_to_admin_item(user, detail).model_dump(),
    }


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=AdminUserItem,
    summary="Create a user directly",
)
async def admin_create_user(
    payload: AdminUserCreate,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> AdminUserItem:
    """Create a user account directly (admin only)."""
    service = AdminService(db)
    try:
        user = await service.create_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role_name=payload.role_name,
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    agg = await service.user_aggregates(user.id)
    return _to_admin_item(user, agg)


@router.patch(
    "/users/{user_id}",
    response_model=AdminUserItem,
    summary="Edit a user (name, role, status, verification)",
)
async def admin_update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> AdminUserItem:
    """Update a user's editable fields (admin only)."""
    if current_user.id == user_id:
        if payload.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admins cannot block their own account",
            )
        if payload.role_name is not None and payload.role_name != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admins cannot change their own role",
            )
    service = AdminService(db)
    try:
        user = await service.update_user(
            user_id,
            full_name=payload.full_name,
            role_name=payload.role_name,
            is_active=payload.is_active,
            is_email_verified=payload.is_email_verified,
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    agg = await service.user_aggregates(user.id)
    return _to_admin_item(user, agg)


@router.post(
    "/users/{user_id}/reset-password",
    summary="Reset a user's password",
)
async def admin_reset_password(
    user_id: uuid.UUID,
    payload: AdminUserResetPassword,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> dict[str, str]:
    """Set a new password for a user (admin only)."""
    service = AdminService(db)
    try:
        user = await service.reset_password(user_id, payload.new_password)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": f"Password reset for {user.email}"}


@router.post(
    "/users/{user_id}/verify-email",
    summary="Mark a user's email as verified",
)
async def admin_verify_email(
    user_id: uuid.UUID,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> dict[str, str]:
    """Mark a user's email as verified (admin only)."""
    service = AdminService(db)
    try:
        await service.verify_email(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": "Email marked as verified"}


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (soft delete)",
)
async def admin_delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> None:
    """Soft-delete a user account (admin only)."""
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


# Legacy alias: the original admin API used /admin/user/{id} (singular).
@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (legacy route)",
    include_in_schema=False,
)
async def admin_delete_user_legacy(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> None:
    """Backward-compatible alias for the old /admin/user/{id} path."""
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


@router.post(
    "/users/{user_id}/restore",
    response_model=AdminUserItem,
    summary="Restore a soft-deleted user",
)
async def admin_restore_user(
    user_id: uuid.UUID,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> AdminUserItem:
    """Restore a soft-deleted user (admin only)."""
    service = AdminService(db)
    user = await service.restore_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not deleted",
        )
    agg = await service.user_aggregates(user.id)
    return _to_admin_item(user, agg)


@router.get(
    "/roles",
    summary="List available roles for the invite/edit forms",
)
async def admin_list_roles(
    _: AdminRole,
    db: DbDep,
) -> dict:
    """Return the fixed application roles (admin only)."""
    roles = await db.execute(select(Role).order_by(Role.name))
    return {"items": [{"name": r.name, "id": str(r.id)} for r in roles.scalars().all()]}


# --- Invitations ---------------------------------------------------------


@router.post(
    "/invitations",
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user by email",
)
async def admin_invite_user(
    payload: InviteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> dict:
    """Create an invitation, email the link, and store the token hash."""
    service = InvitationService(db)
    try:
        invitation, raw_token = await service.create_invitation(
            email=payload.email,
            full_name=payload.full_name,
            role_name=payload.role_name,
            invited_by=current_user.id,
        )
    except DuplicateInviteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    accept_url = (
        f"{settings.PUBLIC_BASE_URL.rstrip('/')}/accept-invite?token={raw_token}"
    )
    email_service = EmailService()
    if email_service.is_configured():
        try:
            email_service.send_invitation_email(
                to_email=invitation.email,
                full_name=invitation.full_name,
                accept_url=accept_url,
                invited_by=current_user.full_name or current_user.email,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Invitation email to %s could not be delivered: %s",
                invitation.email,
                exc,
            )
    else:
        logger.info(
            "SMTP not configured; invitation link for %s: %s",
            invitation.email,
            accept_url,
        )

    return {
        "id": str(invitation.id),
        "email": invitation.email,
        "role_name": invitation.role_name,
        "expires_at": invitation.expires_at.isoformat(),
        "accept_url": accept_url,
        "message": (
            f"Invitation created for {invitation.email}. "
            + (
                "Invitation email sent."
                if email_service.is_configured()
                else "SMTP is not configured — share the accept link manually."
            )
        ),
    }


@router.get(
    "/invitations",
    summary="List invitations",
)
async def admin_list_invitations(
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> dict:
    """Return all invitations (admin only)."""
    service = InvitationService(db)
    invitations = await service.list_invitations()
    return {
        "items": [
            {
                "id": str(inv.id),
                "email": inv.email,
                "full_name": inv.full_name,
                "role_name": inv.role_name,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
                "accepted_at": inv.accepted_at.isoformat() if inv.accepted_at else None,
                "revoked_at": inv.revoked_at.isoformat() if inv.revoked_at else None,
                "status": (
                    "accepted"
                    if inv.is_accepted
                    else "revoked"
                    if inv.is_revoked
                    else "expired"
                    if inv.is_expired
                    else "pending"
                ),
            }
            for inv in invitations
        ]
    }


@router.delete(
    "/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an invitation",
)
async def admin_revoke_invitation(
    invitation_id: uuid.UUID,
    _: AdminRole,
    __: ManageUsers,
    db: DbDep,
) -> None:
    """Revoke a pending invitation (admin only)."""
    revoked = await InvitationService(db).revoke_invitation(invitation_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )


# --- Strategies ----------------------------------------------------------


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
    response_model=AdminAnalytics,
    summary="Platform analytics aggregates",
)
async def admin_analytics(
    _: AdminRole,
    __: ViewAnalytics,
    db: DbDep,
) -> AdminAnalytics:
    """Return the full platform analytics payload (admin only).

    Includes stat cards, every chart series (strategies over time,
    export formats, user status, top users, monthly registrations,
    strategy success) and a merged recent-activity feed. All values
    come from real database rows.
    """
    payload = await AdminService(db).platform_analytics()
    return AdminAnalytics(**payload)


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


# --- Exports (admin) -------------------------------------------------------


@router.get(
    "/exports",
    response_model=AdminExportsResponse,
    summary="List every export across all users",
)
async def admin_list_exports(
    _: AdminRole,
    __: ViewAnalytics,
    db: DbDep,
    search: str | None = Query(default=None),
    export_format: str | None = Query(default=None, description="pdf|docx|pptx|markdown|html|json"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminExportsResponse:
    """Return every export on the platform, newest first (admin only)."""
    service = AdminService(db)
    rows, total = await service.list_all_exports(
        search=search,
        export_format=export_format,
        date_from=date_from,
        date_to=date_to,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
    return AdminExportsResponse(
        items=[AdminExportItem(**row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(rows) < total,
    )


@router.get(
    "/exports/{export_id}/download",
    summary="Download any export file (admin only)",
)
async def admin_download_export(
    export_id: uuid.UUID,
    _: AdminRole,
    __: ViewAnalytics,
    db: DbDep,
) -> FileResponse:
    """Stream the rendered file for any export on the platform."""
    service = AdminService(db)
    export = await service.get_export_for_admin(export_id)
    if export is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    if not export.file_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file is missing",
        )
    file_path = Path(settings.EXPORT_DIR) / export.file_key
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file is missing",
        )
    name = export.strategy.name if export.strategy else "strategy"
    return FileResponse(
        path=str(file_path),
        filename=f"{name}-{export.format.value}.{file_path.suffix.lstrip('.')}",
        media_type="application/octet-stream",
    )


@router.delete(
    "/exports/{export_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete an export (admin only)",
)
async def admin_delete_export(
    export_id: uuid.UUID,
    _: AdminRole,
    __: ViewAnalytics,
    db: DbDep,
) -> None:
    """Permanently delete an export record and its file on disk."""
    deleted = await AdminService(db).delete_export(export_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
