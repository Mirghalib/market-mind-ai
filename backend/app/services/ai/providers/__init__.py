"""Provider layer — isolates LLM vendor specifics from business logic.

The rest of the pipeline (AIService, PromptBuilder, parser, validator)
only depends on `LLMProvider.generate()`, so swapping vendors is a
configuration change, not a code change.

Usage:
    provider = get_llm_provider(settings)
    response = await provider.generate(system_prompt, user_prompt, temperature=0.2)
"""
from app.services.ai.providers.base import LLMProvider
from app.services.ai.providers.factory import get_llm_provider

__all__ = ["LLMProvider", "get_llm_provider"]
