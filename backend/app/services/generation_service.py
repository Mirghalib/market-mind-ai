"""AI strategy generation service.

Kept fully decoupled from HTTP. The mock implementation can be swapped
for a real LLM call (e.g. Groq/OpenAI) without touching the endpoint:

    1. Add a prompt builder under app/prompts/
    2. Replace the body of generate() with the provider call
    3. Keep the schema contract identical
"""
import logging
import uuid

from app.schemas.strategy import (
    StrategyGenerationRequest,
    StrategyGenerationResponse,
    StrategySection,
)

logger = logging.getLogger("market_mind_ai.strategy_generation")

# Mock model identifier; replaced once a real provider is wired in.
MOCK_MODEL = "mock-groq-llama-3.3-70b"


class GenerationError(Exception):
    """Raised when strategy generation fails."""


class StrategyGenerationService:
    async def generate(
        self, request: StrategyGenerationRequest
    ) -> StrategyGenerationResponse:
        """Produce a structured marketing strategy.

        Mock implementation: returns deterministic placeholder content.
        """
        logger.info(
            "Generating strategy for project=%r industry=%r goals=%d",
            request.project_name,
            request.industry,
            len(request.goals),
        )

        try:
            sections = [
                StrategySection(
                    title="Market Overview",
                    content=(
                        f"High-level analysis of the {request.industry} "
                        "market and current trends."
                    ),
                ),
                StrategySection(
                    title="Target Audience",
                    content=(
                        f"Profile and segmentation of: "
                        f"{request.target_audience}."
                    ),
                ),
                StrategySection(
                    title="Recommended Tactics",
                    content=(
                        "Prioritized actions mapped to your goals: "
                        + ", ".join(request.goals)
                        + "."
                    ),
                ),
                StrategySection(
                    title="Measurement Plan",
                    content=(
                        "KPIs and review cadence to track "
                        "strategy performance."
                    ),
                ),
            ]
        except Exception:
            logger.exception("Strategy generation failed unexpectedly")
            raise GenerationError("Failed to generate strategy") from None

        response = StrategyGenerationResponse(
            strategy_id=str(uuid.uuid4()),
            summary=(
                f"A {request.tone} {request.industry} strategy for "
                f"{request.project_name} targeting {request.target_audience}."
            ),
            sections=sections,
            model_used=MOCK_MODEL,
        )

        logger.info(
            "Strategy generated strategy_id=%s sections=%d",
            response.strategy_id,
            len(response.sections),
        )
        return response
