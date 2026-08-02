"""AI pipeline exceptions.

A small, explicit hierarchy so callers can catch exactly what they need:

- `AIServiceError` — base for everything raised by the AI pipeline.
- `ProviderError` — the LLM provider failed (auth, rate limit, network).
- `InvalidPromptError` — the prompt could not be built.
- `ParseError` — the raw LLM response could not be parsed.
- `ValidationError` — the parsed output failed schema validation.
"""
from typing import Any


class AIServiceError(Exception):
    """Base class for all AI pipeline errors."""


class ProviderError(AIServiceError):
    """The LLM provider call failed or returned an error status."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
        retryable: bool = True,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        # Whether a retry could plausibly succeed (rate limits, 5xx,
        # network hiccups are retryable; auth and bad requests are not).
        self.retryable = retryable


class InvalidPromptError(AIServiceError):
    """The prompt could not be built from the provided inputs."""


class ParseError(AIServiceError):
    """The raw LLM response could not be converted to structured JSON."""

    def __init__(self, message: str, *, raw_response: str | None = None) -> None:
        super().__init__(message)
        self.raw_response = raw_response


class ValidationError(AIServiceError):
    """Parsed output does not conform to the expected response schema."""

    def __init__(self, message: str, *, errors: list[Any] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []
