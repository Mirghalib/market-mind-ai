"""AI strategy generation endpoint."""
import logging

from fastapi import APIRouter, HTTPException, status

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


@router.post(
    "/generate",
    response_model=StrategyGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate an AI marketing strategy",
)
async def generate_strategy(
    request: StrategyGenerationRequest,
) -> StrategyGenerationResponse:
    """Generate a structured marketing strategy from the request payload.

    Runs the request through the AI pipeline (Groq/OpenAI/Anthropic)
    and returns a structured JSON document. Falls back to a mock when
    no provider API key is configured.
    """
    logger.info("POST /generate received for project=%r", request.project_name)

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
        logger.exception("Unexpected error in /generate")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
