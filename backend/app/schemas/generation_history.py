"""Pydantic schemas for Generation History."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.generation_history import GenerationStatus


class GenerationHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    strategy_id: uuid.UUID
    model_used: str
    prompt_version: str | None
    input_params: dict | None
    output: dict | None
    tokens_used: dict | None
    latency_ms: float | None
    status: GenerationStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class GenerationHistoryPage(BaseModel):
    """Paginated response envelope for generation history lists."""

    items: list[GenerationHistoryRead]
    total: int = Field(description="Total number of records matching the filter")
    limit: int = Field(description="Maximum items returned in this page")
    offset: int = Field(description="Number of items skipped before this page")
    has_more: bool = Field(description="Whether more records exist after this page")
