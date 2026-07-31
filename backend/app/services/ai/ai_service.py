"""AIService — orchestrator for the AI Marketing Strategist pipeline.

Flow:
    1. Build the system prompt from the business brief (PromptBuilder).
    2. Ask the configured LLM provider for a completion (with retries).
    3. Parse the raw completion into JSON (ResponseParser).
    4. Validate the JSON against the shared response schema (JSONValidator).
    5. Return the validated, structured JSON.

Responsibilities are split across modules: providers isolate vendor
SDKs, the parser/validator own text handling and schema enforcement,
and this service owns orchestration, retry policy, and logging.

Usage:

    from app.services.ai.ai_service import AIService
    from app.services.ai.prompt_builder import MarketingBrief

    service = AIService()
    result = await service.generate_marketing_strategy(brief)

Raises subclasses of `AIServiceError` (see app.services.ai.exceptions)
on failure, with a `retryable` flag on provider errors.
"""
import asyncio
import logging
from typing import Any

from app.core.config import settings
from app.services.ai.exceptions import (
    AIServiceError,
    InvalidPromptError,
    ParseError,
    ProviderError,
    ValidationError,
)
from app.services.ai.parsers.response_parser import ResponseParser
from app.services.ai.prompt_builder import MarketingBrief, PromptBuilder
from app.services.ai.providers.base import LLMProvider
from app.services.ai.providers.factory import get_llm_provider
from app.services.ai.validators.json_validator import JSONValidator

logger = logging.getLogger("market_mind_ai.ai.service")


class AIService:
    """Coordinate prompt building, provider calls, parsing, and validation."""

    def __init__(
        self,
        *,
        builder: PromptBuilder | None = None,
        provider: LLMProvider | None = None,
        parser: ResponseParser | None = None,
        validator: JSONValidator | None = None,
        retry_attempts: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> None:
        self._builder = builder or PromptBuilder()
        self._provider = provider or get_llm_provider(settings)
        self._parser = parser or ResponseParser()
        self._validator = validator or JSONValidator()
        self._retry_attempts = retry_attempts or settings.AI_RETRY_ATTEMPTS
        self._retry_backoff = retry_backoff_seconds or settings.AI_RETRY_BACKOFF_SECONDS

    async def generate_marketing_strategy(self, brief: MarketingBrief) -> dict[str, Any]:
        """Generate and return a validated marketing strategy as JSON."""
        # --- 1. Build the prompt ------------------------------------------------
        try:
            prompt = self._builder.build(brief)
        except (TypeError, ValueError, KeyError) as exc:
            logger.exception("Prompt building failed for business '%s'", brief.business_name)
            raise InvalidPromptError(
                f"Could not build the marketing prompt: {exc}"
            ) from exc

        logger.info(
            "Generating marketing strategy for '%s' (provider=%s, model=%s)",
            brief.business_name,
            self._provider.name,
            self._provider.model,
        )

        # --- 2. Call the provider with retries ---------------------------------
        raw_response = await self._generate_with_retry(prompt, brief.business_name)

        # --- 3. Parse ----------------------------------------------------------
        try:
            parsed = self._parser.parse(raw_response)
        except ParseError:
            logger.exception("Could not parse LLM response for '%s'", brief.business_name)
            raise
        if not isinstance(parsed, dict):
            raise ParseError(
                f"LLM response parsed to {type(parsed).__name__}, expected an object.",
                raw_response=raw_response,
            )

        # --- 4. Validate -------------------------------------------------------
        try:
            validated = self._validator.validate(parsed)
        except ValidationError:
            logger.exception("LLM output failed validation for '%s'", brief.business_name)
            raise

        logger.info("Validated marketing strategy for '%s'", brief.business_name)
        return validated

    async def _generate_with_retry(self, prompt: str, business_name: str) -> str:
        """Call the provider, retrying temporary failures with backoff."""
        attempts = max(1, self._retry_attempts)
        for attempt in range(1, attempts + 1):
            try:
                return await self._provider.generate(prompt, prompt)
            except ProviderError as exc:
                if not exc.retryable or attempt == attempts:
                    logger.error(
                        "Provider error for '%s' after %d attempt(s): %s",
                        business_name,
                        attempt,
                        exc,
                    )
                    raise
                logger.warning(
                    "Temporary provider failure for '%s' (attempt %d/%d): %s",
                    business_name,
                    attempt,
                    attempts,
                    exc,
                )
                await self._backoff(attempt)

        raise AIServiceError("Unreachable: retry loop exhausted.")

    async def _backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff between retry attempts."""
        delay = self._retry_backoff * (2 ** (attempt - 1))
        await asyncio.sleep(delay)
