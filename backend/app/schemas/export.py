"""Pydantic schemas for strategy exports."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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
    strategy_name: str | None = Field(
        default=None,
        description="Name of the strategy this export belongs to (for lists).",
    )


class ExportPage(BaseModel):
    """Paginated response envelope for export lists."""

    items: list[ExportRead]
    total: int = Field(description="Total number of exports matching the filter")
    limit: int = Field(description="Maximum items returned in this page")
    offset: int = Field(description="Number of items skipped before this page")
    has_more: bool = Field(description="Whether more records exist after this page")


class ExportEmailRequest(BaseModel):
    """Request payload for POST /export/{export_id}/email."""

    to_email: EmailStr = Field(description="Recipient email address")
