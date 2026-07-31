"""Groq provider.

Uses the `openai` Python SDK against Groq's OpenAI-compatible endpoint
(https://api.groq.com/openai/v1). Errors are mapped to `ProviderError`
with a `retryable` flag so the caller can decide whether to retry.
"""
from openai import AsyncOpenAI
from openai import APIStatusError, APITimeoutError, APIConnectionError

from app.services.ai.exceptions import ProviderError
from app.services.ai.providers.base import LLMProvider

# Provider status codes that indicate a temporary failure worth retrying.
_RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(LLMProvider):
    """Groq (Llama) chat completions provider."""

    name = "groq"

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        max_tokens: int = 4096,
        timeout: float = 60.0,
    ) -> None:
        super().__init__(model=model, api_key=api_key, max_tokens=max_tokens)
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=GROQ_BASE_URL,
            timeout=timeout,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
        except APIStatusError as exc:
            raise ProviderError(
                f"Groq request failed with status {exc.status_code}: {exc.message}",
                provider=self.name,
                status_code=exc.status_code,
                retryable=exc.status_code in _RETRYABLE_STATUS_CODES,
            ) from exc
        except (APITimeoutError, APIConnectionError) as exc:
            raise ProviderError(
                f"Groq request failed (timeout/connection): {exc}",
                provider=self.name,
                retryable=True,
            ) from exc

        if not response.choices:
            raise ProviderError(
                "Groq returned no completion choices.",
                provider=self.name,
                retryable=True,
            )
        return response.choices[0].message.content or ""
