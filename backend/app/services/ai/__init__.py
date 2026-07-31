"""AI pipeline — prompt building, LLM interaction, parsing, validation.

Starter package. Public surface (imported by the rest of the app):

    from app.services.ai.ai_service import AIService
    from app.services.ai.prompt_builder import PromptBuilder

Pipeline flow (implement later):

    AIService -> PromptBuilder -> LLM provider -> ResponseParser
    -> JSONValidator -> typed output from app.services.ai.models
"""
