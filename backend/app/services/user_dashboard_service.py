"""User dashboard domain logic: profile update and personal aggregates."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import Export
from app.models.generation_history import GenerationHistory
from app.models.marketing_strategy import MarketingStrategy
from app.models.user import User
from app.schemas.user import UserUpdateProfile


class UserDashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def dashboard_stats(self, user: User) -> dict:
        """Counts scoped to the current user via their projects."""
        total_strategies = await self.db.scalar(
            select(func.count(MarketingStrategy.id))
            .join(MarketingStrategy.project)
            .where(MarketingStrategy.project.has(user_id=user.id))
        )
        total_generations = await self.db.scalar(
            select(func.count(GenerationHistory.id))
            .join(GenerationHistory.strategy)
            .join(MarketingStrategy.project)
            .where(MarketingStrategy.project.has(user_id=user.id))
        )
        total_exports = await self.db.scalar(
            select(func.count(Export.id))
            .join(Export.strategy)
            .join(MarketingStrategy.project)
            .where(MarketingStrategy.project.has(user_id=user.id))
        )
        latest = await self.db.scalar(
            select(MarketingStrategy)
            .join(MarketingStrategy.project)
            .where(MarketingStrategy.project.has(user_id=user.id))
            .order_by(MarketingStrategy.created_at.desc())
            .limit(1)
        )
        return {
            "total_strategies": total_strategies or 0,
            "total_generations": total_generations or 0,
            "total_exports": total_exports or 0,
            "latest_strategy": latest,
        }

    async def update_profile(
        self, user: User, data: UserUpdateProfile
    ) -> User:
        user.full_name = data.full_name
        await self.db.commit()
        await self.db.refresh(user)
        return user
