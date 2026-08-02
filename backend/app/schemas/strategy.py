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
        description="Industry or vertical, e.g. 'SaaS', 'E-commerce', 'Restaurant'",
    )
    product: str | None = Field(
        default=None,
        max_length=500,
        description="Product or service being marketed (optional)",
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
    country: str | None = Field(
        default=None,
        max_length=100,
        description="Country / market of operation (optional)",
    )
    budget: str | None = Field(
        default=None,
        max_length=255,
        description="Budget for the campaign or period (optional, human label)",
    )
    budget_amount: float | None = Field(
        default=None,
        ge=0,
        description="Numeric monthly budget amount (optional)",
    )
    currency_code: str | None = Field(
        default=None,
        max_length=10,
        description="ISO currency code, e.g. 'PKR', 'USD', 'GBP'",
    )
    currency_symbol: str | None = Field(
        default=None,
        max_length=10,
        description="Currency symbol, e.g. 'Rs.', '$', '£', '€'",
    )
    budget_period: str | None = Field(
        default=None,
        max_length=50,
        description="Budget period, e.g. 'month', 'quarter', 'year'",
    )
    competitors: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Known competitor names (optional)",
    )


class StrategySection(BaseModel):
    title: str
    content: str


class StrategyGenerationResponse(BaseModel):
    """Structured output of the generation service."""

    strategy_id: str
    summary: str
    sections: list[StrategySection]
    model_used: str
    status: Literal["completed", "failed"] = "completed"
    content: dict | None = Field(
        default=None,
        description="Full structured AI payload (marketingScore, roadmap, ROI, ...). "
        "Optional for backwards compatibility.",
    )
