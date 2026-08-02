"""Normalizer for raw LLM output before schema validation.

LLMs routinely drift from a strict JSON contract in two predictable
ways, and rather than failing the whole generation with a 500 we repair
those here:

1. Extra fields — the model adds keys the schema forbids
   (``additionalProperties: false``). Dropped recursively.
2. Enum casing — the model writes "SEO" instead of "seo",
   "High" instead of "high". Matched case-insensitively to the first
   allowed value.

Required fields are never touched; the strict JSONValidator still
enforces them afterwards, so this module cannot mask a genuinely
incomplete response.
"""
import json
from pathlib import Path

_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "marketing_strategist_output.schema.json"

with _SCHEMA_PATH.open(encoding="utf-8") as _f:
    _SCHEMA = json.load(_f)


def _normalize_enum(value: str, allowed: list[object]) -> str:
    for candidate in allowed:
        if isinstance(candidate, str) and value.lower() == candidate.lower():
            return candidate
    return value


def _prune_value(value: object, subschema: dict | None) -> object:
    """Return a repaired copy of ``value`` guided by ``subschema``."""
    if not isinstance(subschema, dict):
        return value

    if isinstance(value, dict):
        props = subschema.get("properties", {})
        return {
            key: _prune_value(item, props.get(key))
            for key, item in value.items()
            if key in props
        }

    if isinstance(value, list) and isinstance(subschema.get("items"), dict):
        return [_prune_value(item, subschema["items"]) for item in value]

    if isinstance(value, str) and isinstance(subschema.get("enum"), list):
        return _normalize_enum(value, subschema["enum"])

    return value


def normalize_llm_output(data: object) -> object:
    """Repair a parsed LLM response so it satisfies the schema contract.

    Non-destructive: unknown keys are removed and enum casing is fixed,
    but every value the model did provide is preserved. Arrays keep
    their order and length.
    """
    if not isinstance(data, dict):
        return data

    return {
        key: _prune_value(value, _SCHEMA.get("properties", {}).get(key))
        for key, value in data.items()
        if key in _SCHEMA.get("properties", {})
    }
