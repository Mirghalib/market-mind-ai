"""Strategy export endpoint: render a strategy as a downloadable file."""
import logging
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.export import (
    ExportCreateRequest,
    ExportEmailRequest,
    ExportPage,
    ExportRead,
)
from app.services.email_service import (
    EmailNotConfiguredError,
    EmailSendError,
    EmailService,
)
from app.services.export_service import (
    ExportNotFoundError,
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

    The rendered file is also persisted to disk and recorded in the
    ``exports`` table so it can be listed on the History page and
    re-downloaded via ``GET /export/{id}``.
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


@router.get(
    "/export/list",
    response_model=ExportPage,
    summary="List the current user's exports",
)
async def list_exports(
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
    strategy_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ExportPage:
    """Return the exports owned by the current user, newest first.

    Scoped to the authenticated user via ``ExportService.list_exports``.
    """
    service = ExportService(db)
    items, total = await service.list_exports(
        current_user,
        strategy_id=strategy_id,
        limit=limit,
        offset=offset,
    )

    def _to_read(export) -> ExportRead:
        return ExportRead(
            id=export.id,
            strategy_id=export.strategy_id,
            format=export.format,
            file_key=export.file_key,
            file_url=export.file_url,
            status=export.status,
            created_at=export.created_at,
            updated_at=export.updated_at,
            strategy_name=export.strategy.name if export.strategy else None,
        )

    return ExportPage(
        items=[_to_read(e) for e in items],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
    )


@router.get(
    "/export/{export_id}",
    summary="Download a previously exported file",
)
async def download_export(
    export_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> FileResponse:
    """Re-download a saved export owned by the current user."""
    service = ExportService(db)
    try:
        export = await service.get_user_export(export_id, current_user)
    except ExportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )

    if not export.file_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file is missing",
        )

    file_path = Path(settings.EXPORT_DIR) / export.file_key
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file is missing",
        )

    return FileResponse(
        path=str(file_path),
        filename=f"{export.strategy.name or 'strategy'}-{export.format.value}.{file_path.suffix.lstrip('.')}",
        media_type="application/octet-stream",
    )


@router.post(
    "/export/{export_id}/email",
    status_code=status.HTTP_200_OK,
    summary="Email a report to a recipient",
)
async def email_export(
    export_id: uuid.UUID,
    payload: ExportEmailRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> dict[str, str]:
    """Email a link to the exported report.

    Requires a persisted export (any format) owned by the current user.
    When SMTP is not configured, returns 503 with a clear message.
    """
    service = ExportService(db)
    try:
        export = await service.get_user_export(export_id, current_user)
    except ExportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )

    if not export.file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file is missing",
        )

    email_service = EmailService()
    try:
        email_service.send_report_email(
            to_email=payload.to_email,
            business_name=export.strategy.name if export.strategy else "your strategy",
            public_url=export.file_url,
        )
    except EmailNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery is not configured on this server.",
        )
    except EmailSendError as exc:
        logger.exception("Email delivery failed for export=%s", export_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    return {"message": f"Report sent to {payload.to_email}"}
