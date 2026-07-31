"""JSONValidator — validate parsed LLM output against the response schema.

The response schema (app/services/ai/schemas/marketing_strategist_output
.schema.json) is the single source of truth shared by the prompt and the
validator. Validation failures raise `ValidationError` with the detailed
errors attached for logging/debugging.
"""
import json
import logging
from pathlib import Path

from jsonschema import Draft7Validator

from app.services.ai.exceptions import ValidationError

logger = logging.getLogger("market_mind_ai.ai.validator")

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "marketing_strategist_output.schema.json"
)


def _load_response_schema() -> dict:
    """Load the shared response schema once at import time."""
    with _SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class JSONValidator:
    """Ensure parsed AI output is well-formed and matches its contract."""

    def __init__(self) -> None:
        self._schema = _load_response_schema()
        self._validator = Draft7Validator(self._schema)

    def validate(self, data: dict, contract: type | None = None) -> dict:
        """Return validated data, raising ValidationError if it is invalid.

        `contract` is accepted for forward compatibility with the typed
        output models in app.services.ai.models; schema validation is the
        current enforcement mechanism.
        """
        errors = sorted(self._validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            summary = "; ".join(f"{'/'.join(str(p) for p in e.path)}: {e.message}" for e in errors[:5])
            raise ValidationError(
                f"AI output failed schema validation: {summary}",
                errors=errors,
            )
        return data
