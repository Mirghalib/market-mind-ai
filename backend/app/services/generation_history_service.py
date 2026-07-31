"""Generation history domain logic: listing, retrieval and deletion.

Dependencies: database session only. Raises plain exceptions; the API
layer translates them into HTTP errors.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation_history import GenerationHistory


class GenerationHistoryNotFoundError(Exception):
    """Raised when a generation history id does not exist."""


class GenerationHistoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self,
        *,
        strategy_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[GenerationHistory], int]:
        """Return (records, total_count) filtered by the given criteria.

        Records are ordered newest-first. ``total`` reflects the filter
        before pagination, so clients can render page metadata.
        """
        filters = []
        if strategy_id is not None:
            filters.append(GenerationHistory.strategy_id == strategy_id)

        total = await self.db.scalar(
            select(func.count(GenerationHistory.id)).where(*filters)
        )

        result = await self.db.execute(
            select(GenerationHistory)
            .where(*filters)
            .order_by(GenerationHistory.created_at.desc(), GenerationHistory.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), total or 0

    async def get(self, history_id: uuid.UUID) -> GenerationHistory:
        result = await self.db.execute(
            select(GenerationHistory).where(GenerationHistory.id == history_id)
        )
        record = result.scalar_one_or_none()
        if record is None:
            raise GenerationHistoryNotFoundError(history_id)
        return record

    async def delete(self, history_id: uuid.UUID) -> None:
        record = await self.get(history_id)
        await self.db.delete(record)
        await self.db.commit()
