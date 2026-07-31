"""Pydantic schemas for strategy exports."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.export import ExportFormat, ExportStatus


class ExportCreateRequest(BaseModel):
    """Request payload for POST /export."""

    strategy_id: uuid.UUID = Field(description="Strategy to export")
    format: ExportFormat = Field(
        default=ExportFormat.JSON,
        description="Output format; JSON is fully supported, more are planned",
    )


class ExportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    strategy_id: uuid.UUID
    format: ExportFormat
    file_key: str | None
    file_url: str | None
    status: ExportStatus
    created_at: datetime
    updated_at: datetime
