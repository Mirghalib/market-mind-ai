"""Strategy export endpoint: render a strategy as a downloadable file."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.export import ExportCreateRequest
from app.services.export_service import (
    ExportService,
    StrategyNotFoundError,
    UnsupportedExportFormatError,
)

router = APIRouter()

logger = logging.getLogger("market_mind_ai.export")

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/export",
    status_code=status.HTTP_200_OK,
    summary="Export a strategy as a file",
    responses={
        200: {"content": {"application/json": {}}, "description": "The exported file"},
        404: {"description": "Strategy not found"},
    },
)
async def export_strategy(
    payload: ExportCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> Response:
    """Render the strategy in the requested format and stream it back.

    The response is an attachment download. Currently only JSON is
    implemented; PDF, DOCX, Markdown and HTML are on the roadmap and
    are selected through the same ``format`` field.
    """
    service = ExportService(db)
    try:
        export, rendered = await service.export_strategy(payload)
    except StrategyNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    except UnsupportedExportFormatError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format: {payload.format.value}",
        )
    except Exception:
        logger.exception("Unexpected error exporting strategy=%s", payload.strategy_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed",
        )

    filename = f"strategy-{export.id}.{rendered.file_extension}"
    return Response(
        content=rendered.content,
        media_type=rendered.media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
