"""Admin domain logic: dashboard aggregates, user and strategy management."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.export import Export
from app.models.generation_history import GenerationHistory
from app.models.marketing_strategy import MarketingStrategy
from app.models.project import Project
from app.models.role import Role
from app.models.user import User


class UserNotFoundError(Exception):
    """Raised when an admin operation targets a missing user."""


class AdminService:
    """Read/aggregate user management for the admin dashboard."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # --- Dashboard stats ---------------------------------------------------

    async def dashboard_stats(self) -> dict[str, int]:
        total_users = await self.db.scalar(
            select(func.count(User.id)).where(User.deleted_at.is_(None))
        )
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

    # --- User listing ------------------------------------------------------

    async def list_users(
        self,
        *,
        search: str | None = None,
        role: str | None = None,
        status: str | None = None,
        verified: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """Return (users, total) with search/filter/pagination/sorting.

        Only non-deleted users are returned; the admin can restore
        soft-deleted users via ``restore_user``.
        """
        filters = [User.deleted_at.is_(None)]
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(User.email).like(pattern),
                    func.lower(User.full_name).like(pattern),
                )
            )
        if role:
            filters.append(User.role.has(Role.name == role))
        if status == "blocked":
            filters.append(User.is_active.is_(False))
        elif status == "active":
            filters.append(User.is_active.is_(True))
        if verified == "verified":
            filters.append(User.is_email_verified.is_(True))
        elif verified == "unverified":
            filters.append(User.is_email_verified.is_(False))

        total = await self.db.scalar(
            select(func.count(User.id)).where(*filters)
        )

        column = getattr(User, sort_by, User.created_at)
        order = column.desc() if sort_dir == "desc" else column.asc()

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(*filters)
            .order_by(order, User.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), total or 0

    async def get_user(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    async def user_aggregates(self, user_id: uuid.UUID) -> dict:
        """Per-user counts (strategies, exports, projects, storage)."""
        total_strategies = await self.db.scalar(
            select(func.count(MarketingStrategy.id))
            .join(MarketingStrategy.project)
            .where(MarketingStrategy.project.has(user_id=user_id))
        )
        total_exports = await self.db.scalar(
            select(func.count(Export.id))
            .join(Export.strategy)
            .join(MarketingStrategy.project)
            .where(MarketingStrategy.project.has(user_id=user_id))
        )
        total_projects = await self.db.scalar(
            select(func.count(Project.id)).where(Project.user_id == user_id)
        )
        # Approximate storage used: sum of export file sizes on disk.
        storage_used = 0
        exports = await self.db.execute(
            select(Export).where(
                Export.strategy_id.in_(
                    select(MarketingStrategy.id).join(MarketingStrategy.project).where(
                        MarketingStrategy.project.has(user_id=user_id)
                    )
                )
            )
        )
        from pathlib import Path

        from app.core.config import settings

        for export in exports.scalars().all():
            if export.file_key:
                path = Path(settings.EXPORT_DIR) / export.file_key
                try:
                    if path.is_file():
                        storage_used += path.stat().st_size
                except OSError:
                    continue
        return {
            "total_strategies": total_strategies or 0,
            "total_exports": total_exports or 0,
            "total_projects": total_projects or 0,
            "storage_used": storage_used,
        }

    async def get_user_detail(self, user_id: uuid.UUID) -> dict:
        """Per-user aggregates for the admin panel."""
        return await self.user_aggregates(user_id)

    # --- User management ---------------------------------------------------

    async def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None,
        role_name: str,
    ) -> User:
        """Create a user directly (admin action)."""
        from app.services.user_service import EmailAlreadyRegisteredError

        existing = await self.db.scalar(
            select(User).where(func.lower(User.email) == email.lower())
        )
        if existing is not None:
            raise EmailAlreadyRegisteredError(email)
        role = await self.db.scalar(select(Role).where(Role.name == role_name))
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hash_password(password),
            is_active=True,
            is_email_verified=False,
            role_id=role.id if role else None,
        )
        self.db.add(user)
        await self.db.commit()
        return await self.get_user(user.id)

    async def update_user(
        self,
        user_id: uuid.UUID,
        *,
        full_name: str | None = None,
        role_name: str | None = None,
        is_active: bool | None = None,
        is_email_verified: bool | None = None,
    ) -> User:
        user = await self.get_user(user_id)
        if full_name is not None:
            user.full_name = full_name
        if role_name is not None:
            role = await self.db.scalar(select(Role).where(Role.name == role_name))
            user.role_id = role.id if role else None
        if is_active is not None:
            user.is_active = is_active
        if is_email_verified is not None:
            user.is_email_verified = is_email_verified
            if is_email_verified and user.email_verified_at is None:
                user.email_verified_at = datetime.now(timezone.utc)
            elif not is_email_verified:
                user.email_verified_at = None
        await self.db.commit()
        return await self.get_user(user_id)

    async def set_user_active(self, user_id: uuid.UUID, is_active: bool) -> User:
        return await self.update_user(user_id, is_active=is_active)

    async def reset_password(self, user_id: uuid.UUID, new_password: str) -> User:
        user = await self.get_user(user_id)
        user.hashed_password = hash_password(new_password)
        await self.db.commit()
        return await self.get_user(user_id)

    async def verify_email(self, user_id: uuid.UUID) -> User:
        user = await self.get_user(user_id)
        user.is_email_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        await self.db.commit()
        return await self.get_user(user_id)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Soft-delete a user (restorable)."""
        user = await self.db.get(User, user_id)
        if user is None:
            return False
        user.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def restore_user(self, user_id: uuid.UUID) -> User | None:
        """Restore a soft-deleted user."""
        user = await self.db.get(User, user_id)
        if user is None or user.deleted_at is None:
            return None
        user.deleted_at = None
        await self.db.commit()
        return await self.get_user(user_id)

    # --- Strategies --------------------------------------------------------

    async def list_strategies(self) -> list[MarketingStrategy]:
        result = await self.db.execute(
            select(MarketingStrategy).order_by(MarketingStrategy.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_strategy(self, strategy_id: uuid.UUID) -> bool:
        strategy = await self.db.get(MarketingStrategy, strategy_id)
        if strategy is None:
            return False
        await self.db.delete(strategy)
        await self.db.commit()
        return True
