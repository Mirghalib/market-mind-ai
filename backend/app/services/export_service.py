"""Export domain logic: render a strategy and persist the export record.

Dependencies: database session + renderer registry only. Raises plain
exceptions; the API layer translates them into HTTP errors.
"""
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.export import Export, ExportFormat, ExportStatus
from app.models.marketing_strategy import MarketingStrategy
from app.models.project import Project
from app.models.user import User
from app.schemas.export import ExportCreateRequest
from app.services.export.renderers import RenderedExport, get_renderer


class StrategyNotFoundError(Exception):
    """Raised when the strategy being exported does not exist."""


class UnsupportedExportFormatError(Exception):
    """Raised when no renderer is registered for the requested format."""


class ExportNotFoundError(Exception):
    """Raised when an export record does not exist or is not owned."""


class ExportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def export_strategy(
        self, request: ExportCreateRequest
    ) -> tuple[Export, RenderedExport]:
        """Render ``request.strategy_id`` and persist an Export record.

        Returns the saved record and the rendered artifact. The caller
        is responsible for streaming the artifact to the client.
        """
        strategy = await self._get_strategy(request.strategy_id)
        if strategy is None:
            raise StrategyNotFoundError(request.strategy_id)

        try:
            renderer = get_renderer(request.format)
        except ValueError:
            raise UnsupportedExportFormatError(request.format) from None

        rendered = renderer.render(strategy)

        export = Export(
            strategy_id=strategy.id,
            format=request.format,
            status=ExportStatus.COMPLETED,
        )
        self.db.add(export)
        await self.db.flush()

        file_key, file_url = await self._persist_file(strategy, export, rendered)
        export.file_key = file_key
        export.file_url = file_url

        await self.db.commit()
        await self.db.refresh(export)
        return export, rendered

    async def list_exports(
        self,
        user: User,
        *,
        strategy_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Export], int]:
        """Return (exports, total) owned by ``user``, newest first.

        Ownership is enforced through ``strategy.project.user_id``.
        """
        filters = [MarketingStrategy.project.has(Project.user_id == user.id)]
        if strategy_id is not None:
            filters.append(Export.strategy_id == strategy_id)

        total = await self.db.scalar(
            select(func.count(Export.id))
            .join(Export.strategy)
            .where(*filters)
        )

        result = await self.db.execute(
            select(Export)
            .join(Export.strategy)
            .options(selectinload(Export.strategy))
            .where(*filters)
            .order_by(Export.created_at.desc(), Export.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), total or 0

    async def get_user_export(self, export_id: uuid.UUID, user: User) -> Export:
        """Load an export owned by ``user``, raising otherwise."""
        result = await self.db.execute(
            select(Export)
            .join(Export.strategy)
            .options(selectinload(Export.strategy))
            .where(
                Export.id == export_id,
                MarketingStrategy.project.has(Project.user_id == user.id),
            )
        )
        export = result.scalar_one_or_none()
        if export is None:
            raise ExportNotFoundError(export_id)
        return export

    async def _persist_file(
        self,
        strategy: MarketingStrategy,
        export: Export,
        rendered: RenderedExport,
    ) -> tuple[str, str]:
        """Write the rendered bytes to disk and return (file_key, file_url).

        Files land under ``<EXPORT_DIR>/<strategy_id>/<export_id>.<ext>``.
        ``file_key`` stores the path relative to the export directory root
        (i.e. ``<strategy_id>/<export_id>.<ext>``), matching the existing
        ``strategies/<strategy_id>/<format>`` convention while remaining
        unique per export record.
        """
        relative = Path(str(strategy.id)) / f"{export.id}.{rendered.file_extension}"
        destination = Path(settings.EXPORT_DIR) / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rendered.content)

        file_key = relative.as_posix()
        file_url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/uploads/exports/{file_key}"
        return file_key, file_url

    async def _get_strategy(self, strategy_id: uuid.UUID) -> MarketingStrategy | None:
        result = await self.db.execute(
            select(MarketingStrategy).where(MarketingStrategy.id == strategy_id)
        )
        return result.scalar_one_or_none()
