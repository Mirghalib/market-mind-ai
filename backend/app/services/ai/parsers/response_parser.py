"""ResponseParser — turn a raw LLM completion into structured data.

Starter scaffold. Responsibilities to implement later:
    - strip markdown code fences / surrounding prose
    - decode JSON text into Python objects
    - fall back gracefully on malformed output (retry / repair)
    - return data ready for JSONValidator
"""


class ResponseParser:
    """Normalize raw model output into structured, JSON-serializable data."""

    def parse(self, raw_response: str) -> dict:
        """Return parsed content. Implementation later."""
        raise NotImplementedError
