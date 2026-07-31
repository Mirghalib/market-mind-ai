"""Pydantic schemas for AI strategy generation."""
from typing import Literal

from pydantic import BaseModel, Field


class StrategyGenerationRequest(BaseModel):
    """Request payload for POST /generate."""

    project_name: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the project the strategy belongs to",
    )
    industry: str = Field(
        min_length=1,
        max_length=100,
        description="Industry or vertical, e.g. 'SaaS', 'E-commerce'",
    )
    target_audience: str = Field(
        min_length=1,
        max_length=1000,
        description="Description of the target audience",
    )
    goals: list[str] = Field(
        min_length=1,
        max_length=10,
        description="Business goals the strategy should address",
    )
    tone: Literal["professional", "friendly", "persuasive"] = Field(
        default="professional",
        description="Desired tone of the generated strategy",
    )


class StrategySection(BaseModel):
    title: str
    content: str


class StrategyGenerationResponse(BaseModel):
    """Structured mock output of the generation service."""

    strategy_id: str
    summary: str
    sections: list[StrategySection]
    model_used: str
    status: Literal["completed", "failed"] = "completed"
