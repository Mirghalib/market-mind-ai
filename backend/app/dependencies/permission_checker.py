"""Reusable permission requirement dependency.

Usage:
    @router.get("/admin/users")
    async def list_users(
        current_user: Annotated[User, Depends(get_current_user)],
        _: Annotated[None, Depends(RequirePermission("manage_users"))],
    ):
        ...
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.authorization_service import AuthorizationService


def RequirePermission(permission_name: str):
    """Return a dependency that rejects the request unless the caller's
    role grants ``permission_name``.

    Composes with get_current_user; the check reads the role's granted
    permissions from the database via AuthorizationService.
    """
    async def _check_permission(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        authz = AuthorizationService(db)
        if not await authz.user_has_permission(current_user, permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_name}",
            )

    return _check_permission
