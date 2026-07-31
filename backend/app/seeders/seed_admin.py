"""Seed the initial admin user.

Run directly (idempotent):

    .venv/Scripts/python -m app.seeders.seed_admin

Credentials:
    email:    admin@marketmind.ai
    password: Admin@123

The password is stored hashed (bcrypt). The admin user is created only
if no user with that email exists yet, so re-running is safe.
"""
import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.role import Role
from app.models.user import User

logger = logging.getLogger("market_mind_ai.seeders")

ADMIN_EMAIL = "admin@marketmind.ai"
ADMIN_PASSWORD = "Admin@123"
ADMIN_FULL_NAME = "Market Mind Admin"
ADMIN_ROLE_NAME = "admin"


async def seed_admin(db: AsyncSession) -> None:
    """Create the admin user with the admin role if it does not exist."""
    existing = await db.scalar(select(User).where(User.email == ADMIN_EMAIL))
    if existing is not None:
        logger.info("Admin user %r already exists, skipping", ADMIN_EMAIL)
        return

    role = await db.scalar(select(Role).where(Role.name == ADMIN_ROLE_NAME))
    if role is None:
        logger.error(
            "Role %r not found; run seed_roles first", ADMIN_ROLE_NAME
        )
        raise RuntimeError(
            f"Role {ADMIN_ROLE_NAME!r} missing — run seed_roles before seed_admin"
        )

    admin = User(
        email=ADMIN_EMAIL,
        full_name=ADMIN_FULL_NAME,
        hashed_password=hash_password(ADMIN_PASSWORD),
        is_active=True,
        role_id=role.id,
    )
    db.add(admin)
    await db.commit()
    logger.info("Created admin user %r with role %r", ADMIN_EMAIL, ADMIN_ROLE_NAME)


async def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    async with SessionLocal() as session:
        await seed_admin(session)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
