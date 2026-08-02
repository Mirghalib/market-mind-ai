"""Authorization domain logic: role/permission resolution and policy.

Centralizes RBAC rules so every consumer (dependencies, admin APIs,
seeders) reads permissions from the same place. The permission lists
below define the fixed RBAC policy for this application.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User

# Canonical permission names. Kept as constants so typos fail at
# import time instead of silently granting the wrong check.
PERM_CREATE_STRATEGY = "create_strategy"
PERM_VIEW_STRATEGY = "view_strategy"
PERM_DELETE_STRATEGY = "delete_strategy"
PERM_MANAGE_USERS = "manage_users"
PERM_VIEW_ANALYTICS = "view_analytics"
PERM_MANAGE_ROLES = "manage_roles"
PERM_MANAGE_PERMISSIONS = "manage_permissions"
PERM_EXPORT_STRATEGY = "export_strategy"
PERM_VIEW_HISTORY = "view_history"
PERM_UPDATE_PROFILE = "update_profile"

ALL_PERMISSIONS: tuple[str, ...] = (
    PERM_CREATE_STRATEGY,
    PERM_VIEW_STRATEGY,
    PERM_DELETE_STRATEGY,
    PERM_MANAGE_USERS,
    PERM_VIEW_ANALYTICS,
    PERM_MANAGE_ROLES,
    PERM_MANAGE_PERMISSIONS,
    PERM_EXPORT_STRATEGY,
    PERM_VIEW_HISTORY,
    PERM_UPDATE_PROFILE,
)

# Fixed role -> permission mapping.
#   admin: everything
#   user:  self-service capabilities only
ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "admin": ALL_PERMISSIONS,
    "user": (
        PERM_CREATE_STRATEGY,
        PERM_VIEW_STRATEGY,
        PERM_EXPORT_STRATEGY,
        PERM_VIEW_HISTORY,
        PERM_UPDATE_PROFILE,
    ),
}


class AuthorizationService:
    """Loads roles, permissions and per-role permission names from the DB."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def get_permission_by_name(self, name: str) -> Permission | None:
        result = await self.db.execute(
            select(Permission).where(Permission.name == name)
        )
        return result.scalar_one_or_none()

    async def get_user_permissions(self, user: User) -> set[str]:
        """Names of all permissions granted to the user's role."""
        role = await self._resolve_role(user)
        if role is None:
            return set()
        result = await self.db.execute(
            select(Permission.name).join(
                RolePermission, RolePermission.permission_id == Permission.id
            ).where(RolePermission.role_id == role.id)
        )
        return set(result.scalars().all())

    async def _resolve_role(self, user: User) -> Role | None:
        """Load role via the relationship, falling back to a query."""
        if user.role is not None:
            return user.role
        if user.role_id is None:
            return None
        result = await self.db.execute(
            select(Role).where(Role.id == user.role_id)
        )
        return result.scalar_one_or_none()

    async def user_has_role(self, user: User, role_name: str) -> bool:
        role = await self._resolve_role(user)
        return role is not None and role.name == role_name

    async def user_has_permission(self, user: User, permission: str) -> bool:
        return permission in await self.get_user_permissions(user)
