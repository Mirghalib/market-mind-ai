"""User dashboard endpoints — authenticated users with self-service access.

Provides the /dashboard namespace for the frontend: profile, personal
stats, generation, history and export. All capabilities reuse the
existing services (UserDashboardService, StrategyGenerationService,
GenerationHistoryService, ExportService) so business logic is not
duplicated.
"""
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission_checker import RequirePermission
from app.models.user import User
from app.schemas.dashboard import ProfileResponse, UserDashboardStats
from app.schemas.export import ExportCreateRequest
from app.schemas.generation_history import GenerationHistoryPage
from app.schemas.strategy import StrategyGenerationRequest, StrategyGenerationResponse
from app.services.export_service import (
    ExportService,
    StrategyNotFoundError,
    UnsupportedExportFormatError,
)
from app.services.generation_history_service import (
    GenerationHistoryNotFoundError,
    GenerationHistoryService,
)
from app.services.generation_service import (
    GenerationError,
    GenerationQuotaExceededError,
    StrategyGenerationService,
)
from app.services.profile_image_service import profile_image_url
from app.services.user_dashboard_service import UserDashboardService

router = APIRouter()

logger = logging.getLogger("market_mind_ai.user_dashboard")

DbDep = Annotated[AsyncSession, Depends(get_db)]

# Permission gates reused across the user endpoints.
UpdateProfile = Annotated[None, Depends(RequirePermission("update_profile"))]
ViewHistory = Annotated[None, Depends(RequirePermission("view_history"))]
ExportStrategy = Annotated[None, Depends(RequirePermission("export_strategy"))]


@router.get(
    "/dashboard",
    response_model=UserDashboardStats,
    summary="User dashboard aggregates",
)
async def user_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> UserDashboardStats:
    """Return personal counts and the latest strategy."""
    stats = await UserDashboardService(db).dashboard_stats(current_user)
    return UserDashboardStats(**stats)


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get the own profile",
)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProfileResponse:
    """Return the authenticated user's profile (includes role)."""
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role_name=current_user.role_name,
        is_active=current_user.is_active,
        profile_image=profile_image_url(current_user.profile_image),
        created_at=current_user.created_at,
    )


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Update the own profile (multipart)",
)
async def update_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    _: UpdateProfile,
    db: DbDep,
    full_name: Annotated[str | None, Form(max_length=255)] = None,
    profile_image: Annotated[
        UploadFile | None, File(description="JPG/PNG/WEBP, max 5 MB")
    ] = None,
) -> ProfileResponse:
    """Update the own profile via multipart/form-data.

    Accepts an optional ``full_name`` and an optional ``profile_image``
    (jpg/jpeg/png/webp, max 5 MB). The image is stored under
    ``uploads/profile_images/`` and its relative path is saved on the
    user; the response returns the public image URL.
    """
    service = UserDashboardService(db)
    user = await service.update_profile(
        current_user,
        full_name=full_name,
        profile_image=profile_image,
    )
    return ProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role_name,
        is_active=user.is_active,
        profile_image=profile_image_url(user.profile_image),
        created_at=user.created_at,
    )


@router.post(
    "/generate",
    response_model=StrategyGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate an AI marketing strategy",
)
async def user_generate(
    request: StrategyGenerationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> StrategyGenerationResponse:
    """Generate a strategy (user role). Same service as POST /generate."""
    service = StrategyGenerationService()
    try:
        return await service.generate(request)
    except GenerationQuotaExceededError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI provider's rate limit was reached. Try again later.",
        )
    except GenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Strategy generation failed",
        )
    except Exception:
        logger.exception("Unexpected error in /dashboard/generate")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/history",
    response_model=GenerationHistoryPage,
    summary="List generation history",
)
async def user_history(
    current_user: Annotated[User, Depends(get_current_user)],
    _: ViewHistory,
    db: DbDep,
    limit: int = 20,
    offset: int = 0,
) -> GenerationHistoryPage:
    """Return the generation history (user role)."""
    service = GenerationHistoryService(db)
    items, total = await service.list(limit=limit, offset=offset)
    return GenerationHistoryPage(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
    )


@router.post(
    "/export",
    status_code=status.HTTP_200_OK,
    summary="Export a strategy as a file",
)
async def user_export(
    payload: ExportCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    _: ExportStrategy,
    db: DbDep,
) -> Response:
    """Export a strategy (user role). Same service as POST /export."""
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
