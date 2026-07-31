"""JSONValidator — validate AI output against the shared response schema.

This module is the enforcement point of the AI pipeline: it guarantees
that whatever the LLM produced conforms to the schema that was embedded
in the prompt (app/services/ai/schemas/marketing_strategist_output
.schema.json).

Reusable API:
    validator = JSONValidator()
    validator.validate(data)      # returns data, or raises ValidationError
    validator.find_errors(data)   # returns a list of ValidationErrorItem
                                  # without raising

Errors are structured (`ValidationErrorItem`) so callers can render or
log them precisely: each item carries a `field` (dotted JSON path), a
stable `error_type` ("missing_field", "wrong_type", "unexpected_field",
...), a human-readable `message`, the offending `value`, and the
`expected` constraint. Missing fields are never ignored: every required
key that is absent is reported individually.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft7Validator

from app.services.ai.exceptions import ValidationError

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "marketing_strategist_output.schema.json"
)

# Maps jsonschema keywords to stable, machine-readable error types.
_ERROR_TYPE_BY_KEYWORD = {
    "required": "missing_field",
    "additionalProperties": "unexpected_field",
    "type": "wrong_type",
    "enum": "invalid_value",
    "const": "invalid_value",
    "format": "invalid_format",
    "pattern": "pattern_mismatch",
    "minimum": "below_minimum",
    "maximum": "above_maximum",
    "minLength": "too_short",
    "maxLength": "too_long",
    "minItems": "too_few_items",
    "maxItems": "too_many_items",
    "uniqueItems": "duplicate_items",
    "oneOf": "no_matching_schema",
    "anyOf": "no_matching_schema",
    "allOf": "no_matching_schema",
}


@dataclass(frozen=True)
class ValidationErrorItem:
    """A single validation problem with a precise location and cause."""

    field: str  # dotted JSON path, e.g. "customerPersona.painPoints"
    error_type: str  # stable category, e.g. "missing_field"
    message: str  # human-readable description
    value: object | None = None  # the offending value, when relevant
    expected: object | None = None  # the schema constraint that was violated


def _field_path(error) -> str:
    """Convert a jsonschema error path to a dotted string."""
    return ".".join(str(part) for part in error.absolute_path)


def _join(path: str, name: str) -> str:
    """Join a path and a segment, e.g. ("a.b", "c") -> "a.b.c"."""
    return f"{path}.{name}" if path else name


class JSONValidator:
    """Ensure AI output is well-formed and matches the response schema."""

    def __init__(self) -> None:
        with _SCHEMA_PATH.open(encoding="utf-8") as f:
            self._schema = json.load(f)
        self._validator = Draft7Validator(self._schema)

    def validate(self, data: object, contract: type | None = None) -> dict:
        """Return the validated data, or raise ValidationError.

        `contract` is accepted for forward compatibility with the typed
        output models in app.services.ai.models; schema validation is
        the current enforcement mechanism.
        """
        errors = self.find_errors(data)
        if errors:
            details = "; ".join(f"{e.field}: {e.message}" for e in errors[:8])
            raise ValidationError(
                f"AI output failed schema validation with {len(errors)} error(s): {details}",
                errors=errors,
            )
        return data  # type: ignore[return-value]

    def find_errors(self, data: object) -> list[ValidationErrorItem]:
        """Return every schema violation as structured items (no raising)."""
        if not isinstance(data, dict):
            return [
                ValidationErrorItem(
                    field="<root>",
                    error_type="wrong_type",
                    message=f"Expected a JSON object, got {type(data).__name__}.",
                    value=data,
                    expected="object",
                )
            ]

        items: list[ValidationErrorItem] = []
        for error in sorted(
            self._validator.iter_errors(data),
            key=lambda e: [str(p) for p in e.absolute_path],
        ):
            items.extend(self._to_items(error))
        return items

    def _to_items(self, error) -> list[ValidationErrorItem]:
        """Convert one jsonschema error into one or more structured items."""
        keyword = error.validator
        path = _field_path(error)

        # A 'required' failure can name several missing fields; report
        # each one individually so nothing is silently dropped.
        if keyword == "required":
            return [
                ValidationErrorItem(
                    field=_join(path, name),
                    error_type="missing_field",
                    message="Required field is missing.",
                    expected=name,
                )
                for name in error.validator_value
            ]

        if keyword == "additionalProperties":
            # jsonschema reports the offending property name for nested
            # objects, but the WHOLE instance at the root; detect the
            # root case and extract the extra keys ourselves.
            names = (
                [error.instance]
                if isinstance(error.instance, str)
                else self._extra_root_keys(error)
            )
            return [
                ValidationErrorItem(
                    field=_join(path, name),
                    error_type="unexpected_field",
                    message=f"Field '{name}' is not allowed by the schema.",
                    value=name,
                )
                for name in names
            ]

        if keyword == "type":
            return [
                ValidationErrorItem(
                    field=path or "<root>",
                    error_type="wrong_type",
                    message=(
                        f"Expected type {error.validator_value!r}, "
                        f"got {type(error.instance).__name__}."
                    ),
                    value=error.instance,
                    expected=error.validator_value,
                )
            ]

        if keyword == "enum":
            return [
                ValidationErrorItem(
                    field=path or "<root>",
                    error_type="invalid_value",
                    message=f"Value {error.instance!r} is not one of the allowed values.",
                    value=error.instance,
                    expected=error.validator_value,
                )
            ]

        # Fall back to the schema's own message for anything else.
        return [
            ValidationErrorItem(
                field=path or "<root>",
                error_type=_ERROR_TYPE_BY_KEYWORD.get(keyword, "constraint_violation"),
                message=error.message,
                value=error.instance,
                expected=error.validator_value,
            )
        ]

    @staticmethod
    def _extra_root_keys(error) -> list[str]:
        """Return the extra keys for a root-level additionalProperties error."""
        allowed = set(error.schema.get("properties", {}))
        instance = error.instance if isinstance(error.instance, dict) else {}
        return [key for key in instance if key not in allowed]
