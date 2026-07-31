"""Seed the two fixed application roles: admin and user.

Run directly (idempotent — safe to run repeatedly):

    .venv/Scripts/python -m app.seeders.seed_roles

This module also exposes the shared async session bootstrap used by all
seeder scripts.
"""
import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal
from app.models.role import Role

logger = logging.getLogger("market_mind_ai.seeders")

# (name, description) for the fixed roles. Role names are the source of
# truth for frontend routing ("admin" -> /admin/dashboard, else /dashboard).
ROLES = (
    ("admin", "Full access to all system capabilities"),
    ("user", "Self-service access to strategies, exports and profile"),
)


def _bootstrap() -> None:
    """Make ``app`` importable when run as ``python -m app.seeders.X``."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


async def seed_roles(db: AsyncSession) -> None:
    """Create the admin and user roles if they do not exist."""
    for name, description in ROLES:
        existing = await db.scalar(select(Role).where(Role.name == name))
        if existing is not None:
            logger.info("Role %r already exists, skipping", name)
            continue
        db.add(Role(name=name, description=description))
        logger.info("Created role %r", name)
    await db.commit()


async def main() -> None:
    _bootstrap()
    async with SessionLocal() as session:
        await seed_roles(session)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
