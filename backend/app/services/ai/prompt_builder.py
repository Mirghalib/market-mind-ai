"""PromptBuilder — compose a complete LLM prompt from a template + inputs.

Starter scaffold. Responsibilities to implement later:
    - load the template for a given deliverable (marketing, persona, seo, ...)
    - inject business inputs (brand, audience, budget, ...)
    - apply formatting rules (JSON output contract, tone, length)
    - return the final prompt string sent to the LLM provider
"""


class PromptBuilder:
    """Assemble prompts from templates and structured inputs."""

    def build(self, deliverable: str, context: dict) -> str:
        """Return the compiled prompt. Implementation later."""
        raise NotImplementedError
