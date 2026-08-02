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


def _extract_first_json(text: str) -> str:
    """Return the first balanced JSON value (object or array) in ``text``.

    Walks character-by-character, tracking string/escape state, so a
    ``}`` or ``]`` inside a string value does not terminate the match
    and trailing prose after the JSON is not captured.
    """
    start = -1
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start == -1:
        raise ValueError("No JSON value found")

    open_char = text[start]
    close_char = "}" if open_char == "{" else "]"
    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    raise ValueError("Unbalanced JSON value")


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

        # 2. Extract the first balanced JSON value (object or array).
        try:
            span = _extract_first_json(text)
        except ValueError:
            raise ParseError(
                "No JSON found in the LLM response.",
                raw_response=raw_response,
            ) from None

        # 3. Decode, with a fallback for trailing commas models sometimes emit.
        try:
            return json.loads(span)
        except json.JSONDecodeError as exc:
            # Fallback: strip trailing commas before array/object closers.
            try:
                repaired = re.sub(r",\s*([\]}])", r"\1", span)
                return json.loads(repaired)
            except json.JSONDecodeError:
                raise ParseError(
                    f"Invalid JSON in LLM response: {exc.msg}",
                    raw_response=raw_response,
                ) from exc
