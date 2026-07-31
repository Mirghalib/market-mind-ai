"""Export domain logic: render a strategy and persist the export record.

Dependencies: database session + renderer registry only. Raises plain
exceptions; the API layer translates them into HTTP errors.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import Export, ExportFormat, ExportStatus
from app.models.marketing_strategy import MarketingStrategy
from app.schemas.export import ExportCreateRequest
from app.services.export.renderers import RenderedExport, get_renderer


class StrategyNotFoundError(Exception):
    """Raised when the strategy being exported does not exist."""


class UnsupportedExportFormatError(Exception):
    """Raised when no renderer is registered for the requested format."""


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
            file_key=f"strategies/{strategy.id}/{request.format.value}",
        )
        self.db.add(export)
        await self.db.commit()
        await self.db.refresh(export)
        return export, rendered

    async def _get_strategy(self, strategy_id: uuid.UUID) -> MarketingStrategy | None:
        result = await self.db.execute(
            select(MarketingStrategy).where(MarketingStrategy.id == strategy_id)
        )
        return result.scalar_one_or_none()
