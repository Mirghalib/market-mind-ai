"""PromptBuilder — compose a clean marketing prompt from business inputs.

This module is self-contained and performs NO API calls. It only turns
structured inputs into a well-formed prompt string.

Typical usage:

    brief = MarketingBrief(
        business_name="Acme Coffee",
        industry="Food & Beverage",
        product="Single-origin coffee beans",
        audience="Urban professionals 25-40",
        country="United States",
        goal="Increase online sales",
        budget="10,000 USD / quarter",
        brand_tone="Friendly, premium, sustainable",
        competitors=["Blue Bottle", "Stumptown"],
    )
    prompt = PromptBuilder().build(brief)

Extension points:
    - subclass and override `build_marketing_prompt` to change the
      marketing template without touching the orchestration.
    - pass `output_format` / `extra_rules` to shape the output contract.
"""
from typing import Sequence

from pydantic import BaseModel, Field

# --- Input contract -----------------------------------------------------------


class MarketingBrief(BaseModel):
    """Structured business inputs for marketing prompt generation."""

    business_name: str = Field(description="Name of the business")
    industry: str = Field(description="Industry the business operates in")
    product: str = Field(description="Product or service being marketed")
    audience: str = Field(description="Target audience description")
    country: str = Field(description="Country / market of operation")
    goal: str = Field(description="Primary marketing objective")
    budget: str = Field(description="Budget for the campaign or period")
    brand_tone: str = Field(description="Desired brand voice and tone")
    competitors: Sequence[str] = Field(
        default_factory=list,
        description="Known competitor names (optional)",
    )


# --- Default marketing template ----------------------------------------------


MARKETING_PROMPT_TEMPLATE = """You are a senior marketing strategist for the business described below.

# Business
- Business name: {business_name}
- Industry: {industry}
- Product / service: {product}
- Country / market: {country}

# Audience
{audience}

# Goal
{goal}

# Budget
{budget}

# Brand tone
{brand_tone}

# Competitors
{competitors}

# Task
Act as the marketing strategist for this business and produce a complete
marketing strategy: target audience, positioning, marketing channels,
campaign ideas, and KPIs to track success.

{output_section}"""


# --- Builder ------------------------------------------------------------------


class PromptBuilder:
    """Assemble a marketing prompt from a structured brief.

    No API calls are made here; the builder only produces the prompt
    string. Subclass or swap `marketing_template` to customize the
    prompt style.
    """

    def __init__(
        self,
        marketing_template: str = MARKETING_PROMPT_TEMPLATE,
        output_format: str | None = None,
        extra_rules: Sequence[str] = (),
    ) -> None:
        self._marketing_template = marketing_template
        self._output_format = output_format
        self._extra_rules = list(extra_rules)

    def build(self, brief: MarketingBrief) -> str:
        """Return the compiled marketing prompt string for the brief."""
        return self.build_marketing_prompt(brief)

    def build_marketing_prompt(self, brief: MarketingBrief) -> str:
        """Compose the marketing prompt from the brief sections."""
        competitors = self._format_competitors(brief.competitors)
        output_section = self._build_output_section()

        return self._marketing_template.format(
            business_name=brief.business_name,
            industry=brief.industry,
            product=brief.product,
            audience=brief.audience,
            country=brief.country,
            goal=brief.goal,
            budget=brief.budget,
            brand_tone=brief.brand_tone,
            competitors=competitors,
            output_section=output_section,
        ).strip()

    def _format_competitors(self, competitors: Sequence[str]) -> str:
        """Render the competitor list as bullet lines (or a placeholder)."""
        if not competitors:
            return "None provided"
        return "\n".join(f"- {name}" for name in competitors)

    def _build_output_section(self) -> str:
        """Compose the output contract section of the prompt."""
        parts: list[str] = []
        if self._output_format:
            parts.append(f"Return your answer in the following format:\n{self._output_format}")
        if self._extra_rules:
            rules = "\n".join(f"- {rule}" for rule in self._extra_rules)
            parts.append(f"Additional rules:\n{rules}")
        if not parts:
            return "Provide clear, actionable, well-structured recommendations."
        return "\n\n".join(parts)
