"""AIService — orchestrator for the AI pipeline.

Starter scaffold. Responsibilities to implement later:
    - accept a deliverable type + business input
    - build the prompt via PromptBuilder
    - call the LLM provider (TBD, async)
    - parse and validate the response
    - return a typed result from app.services.ai.models
"""


class AIService:
    """Coordinate prompt building, LLM calls, parsing, and validation."""

    def __init__(self) -> None:
        # Wire in PromptBuilder, parser, validator, and provider later.
        self._builder = None  # PromptBuilder
        self._parser = None  # ResponseParser
        self._validator = None  # JSONValidator
