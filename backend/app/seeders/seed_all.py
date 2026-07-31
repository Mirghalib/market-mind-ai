"""Seed the complete RBAC baseline in dependency order.

Run once:

    .venv/Scripts/python -m app.seeders.seed_all

Runs seed_roles, then seed_permissions, then seed_admin. Every step is
idempotent, so the whole command is safe to re-run.
"""
import asyncio
import logging
import sys
from pathlib import Path

from app.database.session import SessionLocal
from app.seeders.seed_admin import seed_admin
from app.seeders.seed_permissions import seed_permissions
from app.seeders.seed_roles import seed_roles

logger = logging.getLogger("market_mind_ai.seeders")


async def seed_all() -> None:
    async with SessionLocal() as session:
        await seed_roles(session)
        await seed_permissions(session)
        await seed_admin(session)


async def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    await seed_all()
    logger.info("Seeding complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
