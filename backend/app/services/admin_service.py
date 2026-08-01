"""Admin domain logic: dashboard aggregates, user and strategy management."""
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_password
from app.models.export import Export
from app.models.generation_history import GenerationHistory
from app.models.invitation import Invitation
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

    async def active_users_count(self) -> int:
        return (
            await self.db.scalar(
                select(func.count(User.id)).where(
                    User.deleted_at.is_(None), User.is_active.is_(True)
                )
            )
            or 0
        )

    async def blocked_users_count(self) -> int:
        return (
            await self.db.scalar(
                select(func.count(User.id)).where(
                    User.deleted_at.is_(None), User.is_active.is_(False)
                )
            )
            or 0
        )

    async def pending_verification_count(self) -> int:
        return (
            await self.db.scalar(
                select(func.count(User.id)).where(
                    User.deleted_at.is_(None), User.is_email_verified.is_(False)
                )
            )
            or 0
        )

    # --- Platform analytics ------------------------------------------------

    async def platform_analytics(self) -> dict:
        """One-shot payload backing the admin analytics dashboard.

        Every series is computed from real database rows — there is no
        mock data anywhere in this method.
        """
        stats = await self.dashboard_stats()
        active_users = await self.active_users_count()
        blocked_users = await self.blocked_users_count()
        pending_verification = await self.pending_verification_count()

        # Today's AI request count (UTC day).
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        ai_requests_today = (
            await self.db.scalar(
                select(func.count(GenerationHistory.id)).where(
                    GenerationHistory.created_at >= today
                )
            )
            or 0
        )

        return {
            "stats": stats,
            "growth": await self._growth(),
            "strategy_trend": await self._strategy_trend(),
            "export_formats": await self._export_formats(),
            "user_status": [
                {"label": "Active", "value": active_users},
                {"label": "Blocked", "value": blocked_users},
                {"label": "Pending Verification", "value": pending_verification},
            ],
            "top_users": await self._top_users(),
            "monthly_registrations": await self._monthly_registrations(),
            "strategy_success": await self._strategy_success(),
            "ai_requests_today": ai_requests_today,
            "recent_activity": await self._recent_activity(),
            "latest_users": await self.latest_users(limit=6),
        }

    async def latest_users(self, limit: int = 6) -> list[dict]:
        """Newest registered users, with per-user aggregates."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        items = []
        for user in result.scalars().all():
            agg = await self.user_aggregates(user.id)
            items.append(
                {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "role_name": user.role_name,
                    "profile_image": user.profile_image,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "last_login_at": user.last_login_at,
                    "is_email_verified": user.is_email_verified,
                    "email_verified_at": user.email_verified_at,
                    "total_strategies": agg.get("total_strategies", 0),
                    "total_exports": agg.get("total_exports", 0),
                    "total_projects": agg.get("total_projects", 0),
                    "storage_used": agg.get("storage_used", 0),
                }
            )
        return items

    async def _growth(self) -> dict[str, float | None]:
        """30-day % change for the headline cards.

        Compares the trailing 30 days against the previous 30 days so
        every delta chip is computed from real rows. Returns None when
        there is no prior-period data to compare against.
        """
        now = datetime.now(timezone.utc)
        period = timedelta(days=30)
        this_start = now - period
        prev_start = now - 2 * period

        async def delta_between(model, column, status_filter=None):
            prev = await self.db.scalar(
                select(func.count(model.id)).where(
                    column >= prev_start,
                    column < this_start,
                    *(status_filter or []),
                )
            )
            curr = await self.db.scalar(
                select(func.count(model.id)).where(
                    column >= this_start,
                    *(status_filter or []),
                )
            )
            prev = prev or 0
            curr = curr or 0
            if prev <= 0:
                return None if curr == 0 else 100.0
            return round(((curr - prev) / prev) * 100, 1)

        return {
            "total_users": await delta_between(User, User.created_at),
            "active_users": await delta_between(
                User, User.created_at, [User.is_active.is_(True)]
            ),
            "blocked_users": await delta_between(
                User, User.created_at, [User.is_active.is_(False)]
            ),
            "total_strategies": await delta_between(
                MarketingStrategy, MarketingStrategy.created_at
            ),
            "total_exports": await delta_between(Export, Export.created_at),
            "ai_requests_today": await delta_between(
                GenerationHistory, GenerationHistory.created_at
            ),
        }

    async def _strategy_trend(self) -> list[dict]:
        """Strategies created per day over the last 30 days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=29)
        cutoff = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
        rows = await self.db.execute(
            select(
                func.date(MarketingStrategy.created_at).label("day"),
                func.count(MarketingStrategy.id),
            )
            .where(MarketingStrategy.created_at >= cutoff)
            .group_by("day")
            .order_by("day")
        )
        buckets = defaultdict(int)
        for day, count in rows.all():
            buckets[str(day)] = count
        series = []
        cursor = cutoff
        for _ in range(30):
            key = cursor.date().isoformat()
            series.append({"label": key, "value": buckets.get(key, 0)})
            cursor += timedelta(days=1)
        return series

    async def _export_formats(self) -> list[dict]:
        """Export counts grouped by format (pdf/docx/pptx/markdown/html/json)."""
        rows = await self.db.execute(
            select(Export.format, func.count(Export.id)).group_by(Export.format)
        )
        by_format = {row[0].value: row[1] for row in rows.all()}
        return [
            {"label": fmt, "value": by_format.get(fmt, 0)}
            for fmt in ("pdf", "docx", "pptx", "markdown", "html", "json")
        ]

    async def _top_users(self) -> list[dict]:
        """Top 10 users by strategy count."""
        rows = await self.db.execute(
            select(
                func.coalesce(User.full_name, User.email).label("name"),
                func.count(MarketingStrategy.id),
            )
            .select_from(MarketingStrategy)
            .join(MarketingStrategy.project)
            .join(Project.user)
            .where(User.deleted_at.is_(None))
            .group_by(User.id)
            .order_by(func.count(MarketingStrategy.id).desc())
            .limit(10)
        )
        return [{"label": name, "value": count} for name, count in rows.all()]

    async def _monthly_registrations(self) -> list[dict]:
        """New users per month for the last 12 months.

        Grouping happens in Python (not SQL) so the same query works on
        both Postgres and SQLite — ``strftime`` is SQLite-only and
        ``date_trunc`` is Postgres-only.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=365)
        rows = await self.db.execute(
            select(User.created_at)
            .where(
                User.created_at >= cutoff,
                User.deleted_at.is_(None),
            )
        )
        buckets = defaultdict(int)
        for (created_at,) in rows.all():
            if created_at is None:
                continue
            buckets[created_at.strftime("%Y-%m")] += 1

        series = []
        for i in range(11, -1, -1):
            month_date = now.replace(day=1) - timedelta(days=31 * i)
            key = month_date.strftime("%Y-%m")
            label = month_date.strftime("%b %Y")
            series.append({"label": label, "value": buckets.get(key, 0)})
        return series

    async def _strategy_success(self) -> list[dict]:
        """Strategy status distribution (completed/failed/draft/generating)."""
        rows = await self.db.execute(
            select(MarketingStrategy.status, func.count(MarketingStrategy.id)).group_by(
                MarketingStrategy.status
            )
        )
        by_status = {row[0].value: row[1] for row in rows.all()}
        return [
            {"label": status, "value": by_status.get(status, 0)}
            for status in ("completed", "failed", "draft", "generating")
        ]

    async def _recent_activity(self, limit: int = 20) -> list[dict]:
        """A merged, newest-first feed of platform events."""
        events: list[dict] = []

        for user in (
            await self.db.execute(
                select(User)
                .where(User.deleted_at.is_(None))
                .order_by(User.created_at.desc())
                .limit(limit)
            )
        ).scalars().all():
            events.append(
                {
                    "type": "user_registered",
                    "message": f"{user.full_name or user.email} registered",
                    "created_at": user.created_at,
                }
            )

        for strategy in (
            await self.db.execute(
                select(MarketingStrategy)
                .order_by(MarketingStrategy.created_at.desc())
                .limit(limit)
            )
        ).scalars().all():
            events.append(
                {
                    "type": "strategy_generated",
                    "message": f"Strategy generated for {strategy.name}",
                    "created_at": strategy.created_at,
                }
            )

        for export in (
            await self.db.execute(
                select(Export).order_by(Export.created_at.desc()).limit(limit)
            )
        ).scalars().all():
            events.append(
                {
                    "type": "export_created",
                    "message": (
                        f"{export.format.value.upper()} export created"
                    ),
                    "created_at": export.created_at,
                }
            )

        for invitation in (
            await self.db.execute(
                select(Invitation).order_by(Invitation.created_at.desc()).limit(limit)
            )
        ).scalars().all():
            if invitation.accepted_at:
                events.append(
                    {
                        "type": "invitation_accepted",
                        "message": f"{invitation.email} accepted the invitation",
                        "created_at": invitation.accepted_at,
                    }
                )

        # Email sends are recorded as exports via the email action; nothing
        # else in the schema tracks a discrete "email sent" event, so we
        # derive that event from share/email-capable exports here.
        share_rows = await self.db.execute(
            select(Export).where(Export.file_url.is_not(None)).limit(limit)
        )
        for export in share_rows.scalars().all():
            events.append(
                {
                    "type": "email_sent",
                    "message": f"Report emailed for strategy {export.strategy_id}",
                    "created_at": export.updated_at,
                }
            )

        events.sort(key=lambda e: e["created_at"], reverse=True)
        return events[:limit]

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

    # --- Exports (admin) ---------------------------------------------------

    async def list_all_exports(
        self,
        *,
        search: str | None = None,
        export_format: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_dir: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """Return (rows, total) of every export across all users.

        Rows are joined through strategy -> project -> user so the admin
        history page can show the owning user, strategy title, format,
        status and (where available) the file size on disk.
        """
        filters = []
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(User.email).like(pattern),
                    func.lower(User.full_name).like(pattern),
                    func.lower(MarketingStrategy.name).like(pattern),
                )
            )
        if export_format:
            filters.append(Export.format == export_format)
        if date_from is not None:
            filters.append(Export.created_at >= date_from)
        if date_to is not None:
            filters.append(Export.created_at <= date_to)

        base = (
            select(Export)
            .join(Export.strategy)
            .join(MarketingStrategy.project)
            .join(Project.user)
            .options(
                selectinload(Export.strategy).selectinload(
                    MarketingStrategy.project
                ).selectinload(Project.user)
            )
        )
        total = await self.db.scalar(
            select(func.count(Export.id)).join(Export.strategy).join(
                MarketingStrategy.project
            ).join(Project.user).where(*filters)
        )

        column = Export.created_at
        order = column.desc() if sort_dir == "desc" else column.asc()
        result = await self.db.execute(
            base.where(*filters).order_by(order, Export.id.desc()).limit(limit).offset(offset)
        )
        exports = list(result.scalars().all())

        rows = []
        for export in exports:
            user = (
                export.strategy.project.user
                if export.strategy and export.strategy.project
                else None
            )
            rows.append(
                {
                    "id": export.id,
                    "strategy_id": export.strategy_id,
                    "strategy_name": export.strategy.name if export.strategy else None,
                    "format": export.format.value,
                    "status": export.status.value,
                    "file_key": export.file_key,
                    "file_url": export.file_url,
                    "file_size": self._export_file_size(export),
                    "created_at": export.created_at,
                    "user_id": user.id if user else None,
                    "user_name": user.full_name if user else None,
                    "user_email": user.email if user else None,
                }
            )
        return rows, total or 0

    @staticmethod
    def _export_file_size(export: Export) -> int | None:
        """Byte size of the rendered file on disk, if present."""
        if not export.file_key:
            return None
        path = Path(settings.EXPORT_DIR) / export.file_key
        try:
            if path.is_file():
                return path.stat().st_size
        except OSError:
            return None
        return None

    async def get_export_for_admin(self, export_id: uuid.UUID) -> Export | None:
        """Load a single export regardless of owner (admin only)."""
        result = await self.db.execute(
            select(Export)
            .join(Export.strategy)
            .options(selectinload(Export.strategy))
            .where(Export.id == export_id)
        )
        return result.scalar_one_or_none()

    async def delete_export(self, export_id: uuid.UUID) -> bool:
        """Permanently delete an export record and its file on disk."""
        export = await self.db.get(Export, export_id)
        if export is None:
            return False
        if export.file_key:
            path = Path(settings.EXPORT_DIR) / export.file_key
            try:
                if path.is_file():
                    path.unlink()
            except OSError:
                pass
        await self.db.delete(export)
        await self.db.commit()
        return True
