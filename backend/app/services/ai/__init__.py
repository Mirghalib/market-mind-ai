"""AI pipeline — prompt building, LLM interaction, parsing, validation.

Public surface (imported by the rest of the app):

    from app.services.ai.ai_service import AIService
    from app.services.ai.prompt_builder import MarketingBrief, PromptBuilder
    from app.services.ai.exceptions import (
        AIServiceError, ProviderError, InvalidPromptError, ParseError,
        ValidationError,
    )

Pipeline flow:

    AIService -> PromptBuilder -> LLM provider -> ResponseParser
    -> JSONValidator -> structured JSON (dict)
"""
from app.services.ai.ai_service import AIService
from app.services.ai.exceptions import (
    AIServiceError,
    InvalidPromptError,
    ParseError,
    ProviderError,
    ValidationError,
)
from app.services.ai.prompt_builder import MarketingBrief, PromptBuilder

__all__ = [
    "AIService",
    "AIServiceError",
    "InvalidPromptError",
    "MarketingBrief",
    "ParseError",
    "PromptBuilder",
    "ProviderError",
    "ValidationError",
]
