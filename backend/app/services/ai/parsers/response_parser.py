"""ResponseParser — turn a raw LLM completion into structured data.

LLM responses are messy: models wrap JSON in markdown code fences, add
prose before/after, or emit trailing tokens. This parser extracts the
first JSON object/array and decodes it, raising `ParseError` with the
raw response attached when nothing parseable is found.
"""
import json
import logging
import re

from app.services.ai.exceptions import ParseError

logger = logging.getLogger("market_mind_ai.ai.parser")

# Matches a top-level JSON value, tolerating markdown fences and prose.
_JSON_PATTERN = re.compile(
    r"(\{.*\}|\[.*\])",
    re.DOTALL,
)


class ResponseParser:
    """Normalize raw model output into structured, JSON-serializable data."""

    def parse(self, raw_response: str) -> dict:
        """Return the parsed JSON object from the raw model output."""
        if not raw_response or not raw_response.strip():
            raise ParseError(
                "LLM returned an empty response.",
                raw_response=raw_response,
            )

        # 1. Strip markdown code fences if the model wrapped the JSON.
        text = raw_response.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)

        # 2. Extract the first JSON value (object or array).
        match = _JSON_PATTERN.search(text)
        if not match:
            raise ParseError(
                "No JSON found in the LLM response.",
                raw_response=raw_response,
            )

        # 3. Decode, with a fallback for trailing commas models sometimes emit.
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            # Fallback: strip trailing commas before array/object closers.
            try:
                repaired = re.sub(r",\s*([\]}])", r"\1", match.group(1))
                return json.loads(repaired)
            except json.JSONDecodeError:
                raise ParseError(
                    f"Invalid JSON in LLM response: {exc.msg}",
                    raw_response=raw_response,
                ) from exc
