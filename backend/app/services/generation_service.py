"""AI strategy generation service.

Kept fully decoupled from HTTP. The real LLM pipeline lives in
app.services.ai (AIService + PromptBuilder + providers). When no
provider API key is configured — or the provider is temporarily
unavailable (rate limits, outages) — the service falls back to a
deterministic mock so the app still demos end-to-end.
"""
import logging
import uuid

from app.core.config import settings
from app.schemas.strategy import (
    StrategyGenerationRequest,
    StrategyGenerationResponse,
    StrategySection,
)
from app.services.ai.ai_service import AIService
from app.services.ai.exceptions import (
    AIServiceError,
    ProviderError,
    ValidationError,
)
from app.services.ai.prompt_builder import MarketingBrief

logger = logging.getLogger("market_mind_ai.strategy_generation")

# Mock model identifier; used only when no provider key is configured.
MOCK_MODEL = "mock-groq-llama-3.3-70b"


class GenerationError(Exception):
    """Raised when strategy generation fails."""


class GenerationQuotaExceededError(GenerationError):
    """Raised when the LLM provider rate limit is exceeded.

    Carries a human-readable retry hint so the API can return a 503
    instead of a generic 500.
    """


def _provider_key() -> str:
    """Return the API key for the configured provider (settings or env)."""
    name = settings.AI_PROVIDER.lower()
    return getattr(settings, f"{name.upper()}_API_KEY", "") or ""


class StrategyGenerationService:
    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai_service = ai_service

    async def generate(
        self, request: StrategyGenerationRequest
    ) -> StrategyGenerationResponse:
        """Produce a structured marketing strategy via the AI pipeline."""
        logger.info(
            "Generating strategy for project=%r industry=%r goals=%d",
            request.project_name,
            request.industry,
            len(request.goals),
        )

        # Fall back to the deterministic mock when no API key is set so
        # the endpoint keeps working in offline demos and CI.
        if self._ai_service is None and not _provider_key():
            logger.info("No AI provider key configured; using mock strategy")
            return await self._generate_mock(request)

        try:
            service = self._ai_service or AIService()
            result = await service.generate_marketing_strategy(
                MarketingBrief(
                    business_name=request.project_name,
                    industry=request.industry,
                    product=request.project_name,
                    audience=request.target_audience,
                    country="Global",
                    goal="; ".join(request.goals),
                    budget="Not specified",
                    brand_tone=request.tone,
                    competitors=[],
                )
            )
        except ProviderError as exc:
            if exc.status_code == 429:
                if settings.AI_FALLBACK_TO_MOCK:
                    logger.warning(
                        "LLM provider rate limit reached for project=%r; "
                        "falling back to mock strategy (AI_FALLBACK_TO_MOCK=true)",
                        request.project_name,
                    )
                    return await self._generate_mock(request)
                logger.error(
                    "LLM provider rate limit exceeded for project=%r: %s",
                    request.project_name,
                    exc,
                )
                raise GenerationQuotaExceededError(
                    "The AI provider's rate limit was reached. Try again later."
                ) from None
            # Temporary provider outage: degrade to the mock so the demo
            # keeps working instead of surfacing a 500.
            logger.warning(
                "LLM provider unavailable (%s), falling back to mock strategy",
                exc,
            )
            return await self._generate_mock(request)
        except (ValidationError, AIServiceError) as exc:
            logger.exception("Strategy generation failed: %s", exc)
            raise GenerationError("Failed to generate strategy") from None
        except Exception:
            logger.exception("Strategy generation failed unexpectedly")
            raise GenerationError("Failed to generate strategy") from None
            logger.exception("Strategy generation failed unexpectedly")
            raise GenerationError("Failed to generate strategy") from None

        return self._to_response(request, result)

    def _to_response(
        self,
        request: StrategyGenerationRequest,
        result: dict,
    ) -> StrategyGenerationResponse:
        """Map the validated AI JSON document to the API response shape."""
        sections: list[StrategySection] = []

        strategy = result.get("marketingStrategy") or {}
        if strategy.get("overview"):
            sections.append(
                StrategySection(title="Marketing Strategy", content=strategy["overview"])
            )

        persona = result.get("customerPersona") or {}
        if persona.get("summary"):
            sections.append(
                StrategySection(title="Customer Persona", content=persona["summary"])
            )

        swot = result.get("swotAnalysis") or {}
        if swot.get("overallAssessment"):
            sections.append(
                StrategySection(title="SWOT Analysis", content=swot["overallAssessment"])
            )

        calendar = result.get("contentCalendar") or {}
        if calendar.get("timeframe") or calendar.get("schedule"):
            items = calendar.get("schedule") or []
            content = f"Timeframe: {calendar.get('timeframe')}. Cadence: {calendar.get('cadence')}."
            if items:
                content += " " + " ".join(
                    f"{item.get('date')}: {item.get('topic')} ({item.get('channel')})."
                    for item in items[:8]
                )
            sections.append(StrategySection(title="Content Calendar", content=content))

        email = result.get("emailCampaign") or {}
        if email.get("campaignName") or email.get("goal"):
            content = f"{email.get('campaignName')} — {email.get('goal')}. "
            content += "Subject lines: " + "; ".join(
                (email.get("subjectLines") or [])[:5]
            )
            sections.append(StrategySection(title="Email Campaign", content=content))

        ads = result.get("advertisementIdeas") or {}
        if ads.get("summary"):
            content = ads["summary"]
            campaigns = ads.get("campaigns") or []
            if campaigns:
                content += " " + " ".join(
                    f"{c.get('name')} on {c.get('platform')}: {c.get('objective')}."
                    for c in campaigns[:5]
                )
            sections.append(StrategySection(title="Advertisement Ideas", content=content))

        if not sections:
            # Nothing to render from the LLM output; fail loudly rather
            # than returning an empty strategy.
            raise GenerationError("AI output contained no usable sections")

        summary = (
            f"A {request.tone} {request.industry} strategy for "
            f"{request.project_name} targeting {request.target_audience}."
        )

        return StrategyGenerationResponse(
            strategy_id=str(uuid.uuid4()),
            summary=summary,
            sections=sections,
            model_used=settings.AI_MODEL,
        )

    async def _generate_mock(
        self, request: StrategyGenerationRequest
    ) -> StrategyGenerationResponse:
        """Deterministic placeholder content used when no key is set."""
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
