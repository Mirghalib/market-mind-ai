"""JSONValidator — validate parsed LLM output against expected schemas.

Starter scaffold. Responsibilities to implement later:
    - validate structure/type of parsed output (required keys, types)
    - coerce or reject invalid data with meaningful errors
    - optionally retry the pipeline on validation failure
"""


class JSONValidator:
    """Ensure parsed AI output is well-formed and matches its contract."""

    def validate(self, data: dict, contract: type) -> dict:
        """Return validated data. Implementation later."""
        raise NotImplementedError
