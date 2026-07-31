"""Seed the permission catalog and assign permissions to roles.

Run directly (idempotent):

    .venv/Scripts/python -m app.seeders.seed_permissions

Permission names are defined once in AuthorizationService and mirrored
here for the catalog. Assignments follow the fixed RBAC policy:
admin = all permissions, user = self-service subset.
"""
import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.services.authorization_service import (
    ALL_PERMISSIONS,
    ROLE_PERMISSIONS,
)

logger = logging.getLogger("market_mind_ai.seeders")

PERMISSION_DESCRIPTIONS = {
    "create_strategy": "Generate a new AI marketing strategy",
    "view_strategy": "View a marketing strategy",
    "delete_strategy": "Delete a marketing strategy",
    "manage_users": "List and manage user accounts",
    "view_analytics": "View platform analytics",
    "manage_roles": "Create and edit roles",
    "manage_permissions": "Assign permissions to roles",
    "export_strategy": "Export a strategy as a file",
    "view_history": "View generation history",
    "update_profile": "Update the own profile",
}


async def seed_permissions(db: AsyncSession) -> None:
    """Create missing permissions and grant them per the role policy."""
    # 1. Create any missing permission rows.
    permission_ids: dict[str, object] = {}
    for name in ALL_PERMISSIONS:
        existing = await db.scalar(
            select(Permission).where(Permission.name == name)
        )
        if existing is not None:
            permission_ids[name] = existing.id
            continue
        permission = Permission(
            name=name, description=PERMISSION_DESCRIPTIONS.get(name)
        )
        db.add(permission)
        await db.flush()
        permission_ids[name] = permission.id
        logger.info("Created permission %r", name)
    await db.commit()

    # 2. Assign permissions to each role per the policy.
    for role_name, permission_names in ROLE_PERMISSIONS.items():
        role = await db.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            logger.warning("Role %r missing; run seed_roles first", role_name)
            continue
        for permission_name in permission_names:
            exists = await db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission_ids[permission_name],
                )
            )
            if exists is not None:
                continue
            db.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission_ids[permission_name],
                )
            )
            logger.info(
                "Granted %r to %r", permission_name, role_name
            )
    await db.commit()


async def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    async with SessionLocal() as session:
        await seed_permissions(session)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
