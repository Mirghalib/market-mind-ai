"""Probe database connectivity and table existence."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.database.session import engine  # noqa: E402


async def main() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
        result = await conn.execute(text("SELECT id, email FROM users"))
        for row in result.fetchall():
            print(row[0], row[1])


asyncio.run(main())
