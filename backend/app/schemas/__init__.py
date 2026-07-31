"""Pydantic schemas.

Request/response DTOs. Keep these decoupled from the ORM models — the
API contract should not leak the database shape.
"""
from app.schemas.strategy import (
    StrategyGenerationRequest,
    StrategyGenerationResponse,
    StrategySection,
)

__all__ = [
    "StrategyGenerationRequest",
    "StrategyGenerationResponse",
    "StrategySection",
]
