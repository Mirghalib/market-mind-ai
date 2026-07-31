"""LLMProvider — abstract contract for AI vendors.

Provider implementations translate the pipeline's prompt/parameters
into vendor-specific API calls and normalize the raw completion text
back out. They know about their SDK and error codes only; all business
logic lives outside this package.
"""
from abc import ABC, abstractmethod

from app.services.ai.exceptions import ProviderError


class LLMProvider(ABC):
    """Minimal, vendor-agnostic interface for LLM completion calls."""

    def __init__(self, *, model: str, api_key: str, max_tokens: int = 4096) -> None:
        if not api_key:
            raise ProviderError(
                f"No API key configured for provider '{self.name}'. "
                "Set the corresponding environment variable.",
                provider=self.name,
                retryable=False,
            )
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable provider identifier (e.g. 'openai', 'anthropic')."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        """Return the raw completion text for the given prompts."""
        raise NotImplementedError
