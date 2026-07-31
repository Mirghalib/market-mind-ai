"""Reusable role requirement dependency.

Usage:
    @router.get("/admin/dashboard")
    async def admin_dashboard(
        current_user: Annotated[User, Depends(get_current_user)],
        _: Annotated[None, Depends(RequireRole("admin"))],
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


def RequireRole(role_name: str):
    """Return a dependency that rejects the request unless the caller's
    role matches ``role_name``.

    Composes with get_current_user so endpoints only need one extra
    dependency, and the role check is performed through
    AuthorizationService (single source of truth).
    """
    async def _check_role(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        authz = AuthorizationService(db)
        if not await authz.user_has_role(current_user, role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {role_name}",
            )

    return _check_role
