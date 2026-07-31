"""AI strategy generation endpoint."""
import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.strategy import (
    StrategyGenerationRequest,
    StrategyGenerationResponse,
)
from app.services.generation_service import (
    GenerationError,
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

    Returns a structured JSON document. The underlying AI service is
    mocked for now and will be replaced with a real LLM provider call.
    """
    logger.info("POST /generate received for project=%r", request.project_name)

    service = StrategyGenerationService()
    try:
        return await service.generate(request)
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
