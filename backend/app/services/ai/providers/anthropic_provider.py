"""Anthropic provider.

Uses the `anthropic` Python SDK. Errors are mapped to `ProviderError`
with a `retryable` flag so the caller can decide whether to retry.
"""
from anthropic import AsyncAnthropic
from anthropic import (
    APIStatusError,
    APITimeoutError,
    APIConnectionError,
)

from app.services.ai.exceptions import ProviderError
from app.services.ai.providers.base import LLMProvider

# Provider status codes that indicate a temporary failure worth retrying.
_RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) messages provider."""

    name = "anthropic"

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        max_tokens: int = 4096,
        timeout: float = 60.0,
    ) -> None:
        super().__init__(model=model, api_key=api_key, max_tokens=max_tokens)
        self._client = AsyncAnthropic(api_key=api_key, timeout=timeout)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        try:
            message = await self._client.messages.create(
                model=self.model,
                system=system_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except APIStatusError as exc:
            raise ProviderError(
                f"Anthropic request failed with status {exc.status_code}: {exc.message}",
                provider=self.name,
                status_code=exc.status_code,
                retryable=exc.status_code in _RETRYABLE_STATUS_CODES,
            ) from exc
        except (APITimeoutError, APIConnectionError) as exc:
            raise ProviderError(
                f"Anthropic request failed (timeout/connection): {exc}",
                provider=self.name,
                retryable=True,
            ) from exc

        parts = [block.text for block in message.content if getattr(block, "type", None) == "text"]
        return "\n".join(parts).strip()
