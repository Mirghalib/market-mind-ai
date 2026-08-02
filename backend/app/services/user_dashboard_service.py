"""User dashboard domain logic: profile update and personal aggregates."""
from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import Export
from app.models.generation_history import GenerationHistory
from app.models.marketing_strategy import MarketingStrategy
from app.models.user import User
from app.services.profile_image_service import (
    delete_profile_image,
    save_profile_image,
)


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
        self,
        user: User,
        *,
        full_name: str | None = None,
        profile_image: UploadFile | None = None,
    ) -> User:
        """Update profile fields; saves a new image and drops the old one."""
        if full_name is not None:
            user.full_name = full_name

        if profile_image is not None:
            new_path = await save_profile_image(profile_image)
            old_path = user.profile_image
            user.profile_image = new_path
            # Commit first so the DB never points at a missing file.
            await self.db.commit()
            await self.db.refresh(user)
            delete_profile_image(old_path)
            return user

        await self.db.commit()
        await self.db.refresh(user)
        return user
