"""Admin domain logic: dashboard aggregates, user and strategy management."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.export import Export
from app.models.generation_history import GenerationHistory
from app.models.marketing_strategy import MarketingStrategy
from app.models.user import User


class AdminService:
    """Read-only aggregates and deletions for the admin dashboard."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def dashboard_stats(self) -> dict[str, int]:
        total_users = await self.db.scalar(select(func.count(User.id)))
        total_strategies = await self.db.scalar(
            select(func.count(MarketingStrategy.id))
        )
        total_generations = await self.db.scalar(
            select(func.count(GenerationHistory.id))
        )
        total_exports = await self.db.scalar(select(func.count(Export.id)))
        return {
            "total_users": total_users or 0,
            "total_strategies": total_strategies or 0,
            "total_generations": total_generations or 0,
            "total_exports": total_exports or 0,
        }

    async def list_users(self) -> list[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_strategies(self) -> list[MarketingStrategy]:
        result = await self.db.execute(
            select(MarketingStrategy).order_by(MarketingStrategy.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        user = await self.db.get(User, user_id)
        if user is None:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def delete_strategy(self, strategy_id: uuid.UUID) -> bool:
        strategy = await self.db.get(MarketingStrategy, strategy_id)
        if strategy is None:
            return False
        await self.db.delete(strategy)
        await self.db.commit()
        return True
