"""Provider factory — build the configured LLM provider.

The OpenAI SDK is the single LLM interface. Any OpenAI-compatible
endpoint is configured purely via settings:

    AI_BASE_URL  -> base_url passed to AsyncOpenAI (default api.openai.com)
    AI_API_KEY   -> the API key
    AI_MODEL     -> the model id

So switching between OpenAI, Groq, OpenRouter, local vLLM/Ollama, etc.
is a `.env` change, never a code change.
"""
from app.core.config import settings
from app.services.ai.exceptions import ProviderError
from app.services.ai.providers.base import LLMProvider
from app.services.ai.providers.openai_provider import OpenAIProvider


def get_llm_provider(cfg: object = settings) -> LLMProvider:
    """Build the OpenAI-compatible provider from the application settings."""
    max_tokens = getattr(cfg, "AI_MAX_TOKENS", 4096)
    timeout = getattr(cfg, "AI_REQUEST_TIMEOUT_SECONDS", 60.0)
    api_key = getattr(cfg, "AI_API_KEY", "") or ""

    if not api_key:
        raise ProviderError(
            "No AI_API_KEY configured. Set it in the environment or .env.",
            provider="openai",
            retryable=False,
        )

    return OpenAIProvider(
        model=getattr(cfg, "AI_MODEL", "") or "gpt-4o-mini",
        api_key=api_key,
        max_tokens=max_tokens,
        timeout=timeout,
        base_url=getattr(cfg, "AI_BASE_URL", "") or None,
    )
