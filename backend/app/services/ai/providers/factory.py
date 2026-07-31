"""Provider factory — build the configured LLM provider.

Keeps provider selection in one place. `settings.AI_PROVIDER` chooses
the vendor and the matching API key environment variable:

    openai    -> OPENAI_API_KEY
    anthropic -> ANTHROPIC_API_KEY
"""
import os

from app.core.config import settings
from app.services.ai.exceptions import ProviderError
from app.services.ai.providers.anthropic_provider import AnthropicProvider
from app.services.ai.providers.base import LLMProvider
from app.services.ai.providers.openai_provider import OpenAIProvider


def get_llm_provider(cfg: object = settings) -> LLMProvider:
    """Build the provider instance selected by the application settings."""
    provider_name = cfg.AI_PROVIDER.lower()
    max_tokens = getattr(cfg, "AI_MAX_TOKENS", 4096)
    timeout = getattr(cfg, "AI_REQUEST_TIMEOUT_SECONDS", 60.0)

    if provider_name == "openai":
        return OpenAIProvider(
            model=cfg.AI_MODEL,
            api_key=os.getenv("OPENAI_API_KEY", ""),
            max_tokens=max_tokens,
            timeout=timeout,
        )

    if provider_name == "anthropic":
        return AnthropicProvider(
            model=cfg.AI_MODEL,
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            max_tokens=max_tokens,
            timeout=timeout,
        )

    raise ProviderError(
        f"Unsupported AI provider '{cfg.AI_PROVIDER}'. "
        "Use 'openai' or 'anthropic'.",
        retryable=False,
    )
