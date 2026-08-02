"""Strategy export endpoint: render a strategy as a downloadable file."""
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.export import Export
from app.models.share_link import ShareLink
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
    except RuntimeError as exc:
        # Renderer dependency missing (e.g. reportlab/python-pptx) —
        # surface a helpful message instead of a bare 500.
        logger.exception("Renderer error exporting strategy=%s", payload.strategy_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc) or "Export failed",
        )
    except Exception:
        logger.exception("Unexpected error exporting strategy=%s", payload.strategy_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed. Please try again or contact support.",
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

    if not export.file_url or not export.file_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file is missing",
        )

    # Resolve the persisted file so it can be attached to the email.
    attachment_path = Path(settings.EXPORT_DIR) / export.file_key
    if not attachment_path.is_file():
        attachment_path = None

    # Marketing score for the branded email badge.
    marketing_score = None
    content = export.strategy.content if export.strategy else None
    if isinstance(content, dict):
        score = (content.get("marketingScore") or {}).get("overall")
        try:
            marketing_score = int(score)
        except (TypeError, ValueError):
            marketing_score = None

    # Create a short-lived share link for the "view in browser" button.
    share_url = None
    try:
        share, share_url = await service.create_share_link(
            export, current_user, expires_in_days=7
        )
    except Exception:  # noqa: BLE001
        logger.warning("Could not create share link for email export %s", export_id)

    email_service = EmailService()
    try:
        email_service.send_report_email(
            to_email=payload.to_email,
            business_name=export.strategy.name if export.strategy else "your strategy",
            public_url=export.file_url,
            summary=_email_summary(export),
            marketing_score=marketing_score,
            recipient_name=payload.recipient_name,
            share_url=share_url,
            attachment_path=attachment_path,
            attachment_display_name=(
                f"{export.strategy.name if export.strategy else 'strategy'}."
                f"{export.format.value}"
            ),
        )
    except EmailNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery is not configured on this server. "
            "Please add SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD and "
            "SMTP_FROM to the server's .env file.",
        )
    except EmailSendError as exc:
        logger.exception("Email delivery failed for export=%s", export_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    return {"message": f"Report sent to {payload.to_email}"}


@router.post(
    "/export/{export_id}/share",
    status_code=status.HTTP_201_CREATED,
    summary="Create a secure share link for an export",
)
async def share_export(
    export_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
    expires_in_days: int = Query(default=7, ge=1, le=30),
) -> dict:
    """Create a secure, expiring link that opens the exported report."""
    service = ExportService(db)
    try:
        export = await service.get_user_export(export_id, current_user)
    except ExportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    share, url = await service.create_share_link(
        export, current_user, expires_in_days=expires_in_days
    )
    return {
        "id": str(share.id),
        "token": share.token,
        "url": url,
        "expires_at": share.expires_at.isoformat() if share.expires_at else None,
    }


@router.get(
    "/export/{export_id}/shares",
    summary="List share links for an export",
)
async def list_shares(
    export_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> dict:
    """Return active share links for an export owned by the current user."""
    service = ExportService(db)
    try:
        export = await service.get_user_export(export_id, current_user)
    except ExportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    links = await service.list_share_links(export)
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return {
        "items": [
            {
                "id": str(link.id),
                "token": link.token,
                "url": f"{base}/api/v1/s/{link.token}",
                "created_at": link.created_at.isoformat() if link.created_at else None,
                "expires_at": link.expires_at.isoformat() if link.expires_at else None,
                "download_count": link.download_count,
                "is_active": link.is_active,
            }
            for link in links
        ]
    }


@router.delete(
    "/export/{export_id}/shares/{share_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a share link",
)
async def revoke_share(
    export_id: uuid.UUID,
    share_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> None:
    """Revoke a share link for an export owned by the current user."""
    service = ExportService(db)
    try:
        export = await service.get_user_export(export_id, current_user)
    except ExportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )
    revoked = await service.revoke_share_link(share_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found",
        )


@router.get(
    "/s/{token}",
    summary="Open a shared report (public)",
)
async def open_shared_report(
    token: str,
    db: DbDep,
) -> FileResponse:
    """Public, token-based access to a shared export file.

    The link works without authentication so stakeholders can open the
    report; the unguessable token is the security boundary. Expired,
    revoked, or missing links return a helpful 404/410 message instead
    of crashing.
    """
    share = await _resolve_share(db, token)

    if not share.export or not share.export.file_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The shared report file is missing.",
        )

    file_path = Path(settings.EXPORT_DIR) / share.export.file_key
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The shared report file is missing.",
        )

    share.download_count += 1
    await db.commit()

    return FileResponse(
        path=str(file_path),
        filename=(
            f"{share.export.strategy.name if share.export.strategy else 'report'}-"
            f"shared.{file_path.suffix.lstrip('.')}"
        ),
        media_type="application/octet-stream",
    )


async def _resolve_share(db: AsyncSession, token: str) -> ShareLink:
    """Load a share link and enforce active/not-expired rules."""
    result = await db.execute(
        select(ShareLink)
        .options(
            selectinload(ShareLink.export).selectinload(Export.strategy)
        )
        .where(ShareLink.token == token)
    )
    share = result.scalar_one_or_none()

    if share is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This share link does not exist or has been revoked.",
        )
    if not share.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This share link has been revoked.",
        )
    if share.expires_at is not None:
        expiry = share.expires_at
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This share link has expired.",
            )
    return share


@router.get(
    "/s/{token}/preview",
    summary="Branded HTML preview of a shared report (public)",
    responses={
        200: {"content": {"text/html": {}}, "description": "Branded preview page"},
        404: {"description": "Share link not found"},
        410: {"description": "Share link revoked or expired"},
    },
)
async def shared_report_preview(
    token: str,
    db: DbDep,
) -> Response:
    """Render a professional, responsive preview page for a share link."""
    from app.services.export.share_preview import render_share_preview

    share = await _resolve_share(db, token)
    html = render_share_preview(share, token)
    return Response(
        content=html,
        media_type="text/html; charset=utf-8",
    )


@router.get(
    "/s/{token}/download",
    summary="Download a shared report in a chosen format (public)",
)
async def shared_report_download(
    token: str,
    db: DbDep,
    format: str = Query(default="pdf", pattern="^(pdf|docx|pptx|markdown|html|json)$"),
) -> Response:
    """Stream the shared strategy re-rendered in the requested format."""
    from app.models.export import ExportFormat
    from app.services.export.renderers import get_renderer

    share = await _resolve_share(db, token)
    if not share.export or not share.export.strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The shared report is missing.",
        )

    try:
        rendered = get_renderer(ExportFormat(format)).render(share.export.strategy)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc) or "Export failed",
        )

    share.download_count += 1
    await db.commit()

    filename = (
        f"{share.export.strategy.name or 'report'}-"
        f"{format}.{rendered.file_extension}"
    )
    return Response(
        content=rendered.content,
        media_type=rendered.media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _email_summary(export) -> str:
    """Build a short summary line from the strategy content for the email."""
    content = export.strategy.content if export.strategy else None
    if not isinstance(content, dict):
        return ""
    summary = content.get("executiveSummary") or {}
    text = summary.get("summary") if isinstance(summary, dict) else ""
    if text:
        return str(text)[:300]
    sections = content.get("sections")
    if isinstance(sections, list) and sections:
        return str(sections[0].get("content", ""))[:300]
    return ""
