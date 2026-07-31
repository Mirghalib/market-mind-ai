"""AI strategy generation endpoint."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.strategy import (
    StrategyGenerationRequest,
    StrategyGenerationResponse,
)
from app.services.generation_service import (
    GenerationError,
    GenerationQuotaExceededError,
    StrategyGenerationService,
)

router = APIRouter()

logger = logging.getLogger("market_mind_ai.generate")

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/generate",
    response_model=StrategyGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate an AI marketing strategy",
)
async def generate_strategy(
    request: StrategyGenerationRequest,
    db: DbDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> StrategyGenerationResponse:
    """Generate a structured marketing strategy from the request payload.

    Runs the request through the AI pipeline (Groq/OpenAI/Anthropic),
    persists the result (project + strategy + history), and returns a
    structured JSON document. Falls back to a mock when no provider API
    key is configured or the provider is temporarily unavailable.
    """
    logger.info("POST /generate received for project=%r", request.project_name)

    service = StrategyGenerationService()
    try:
        return await service.generate(request, db=db, user=current_user)
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
        logger.exception("Unexpected error in /generate")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
