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

from app.services.ai.prompts.marketing_prompt import (
    MARKETING_SYSTEM_PROMPT_TEMPLATE,
    RESPONSE_SCHEMA_JSON,
)

# --- Input contract -----------------------------------------------------------


class MarketingBrief(BaseModel):
    """Structured business inputs for marketing prompt generation."""

    business_name: str = Field(description="Name of the business")
    industry: str = Field(description="Industry the business operates in")
    product: str = Field(description="Product or service being marketed")
    audience: str = Field(description="Target audience description")
    country: str = Field(description="Country / market of operation")
    goal: str = Field(description="Primary marketing objective")
    budget: str = Field(description="Budget label, e.g. 'Rs. 100,000 / month'")
    budget_amount: float | None = Field(
        default=None, description="Numeric budget amount"
    )
    currency_code: str | None = Field(
        default=None, description="ISO currency code, e.g. 'PKR', 'USD'"
    )
    currency_symbol: str | None = Field(
        default=None, description="Currency symbol, e.g. 'Rs.', '$'"
    )
    budget_period: str | None = Field(
        default=None, description="Budget period, e.g. 'month', 'quarter'"
    )
    brand_tone: str = Field(description="Desired brand voice and tone")
    competitors: Sequence[str] = Field(
        default_factory=list,
        description="Known competitor names (optional)",
    )
    industry_playbook: str = Field(
        default="", description="Rendered industry playbook lines"
    )
    country_profile: str = Field(
        default="", description="Rendered country marketing profile"
    )


# --- Default marketing template ----------------------------------------------


MARKETING_PROMPT_TEMPLATE = MARKETING_SYSTEM_PROMPT_TEMPLATE


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
        currency_rule = self._build_currency_rule(brief)

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
            industry_playbook=brief.industry_playbook or "Not provided",
            country_profile=brief.country_profile or "Not provided",
            currency_rule=currency_rule,
        ).strip()

    def _format_competitors(self, competitors: Sequence[str]) -> str:
        """Render the competitor list as bullet lines (or a placeholder)."""
        if not competitors:
            return "None provided"
        return "\n".join(f"- {name}" for name in competitors)

    @staticmethod
    def _build_currency_rule(brief: MarketingBrief) -> str:
        """Currency-aware instruction so the AI never assumes USD."""
        symbol = brief.currency_symbol or "$"
        code = brief.currency_code or "USD"
        if brief.budget_amount is not None:
            try:
                amount = f"{float(brief.budget_amount):,.0f}"
            except (TypeError, ValueError):
                amount = str(brief.budget_amount)
            return (
                f"The user's budget is {symbol} {amount} per "
                f"{brief.budget_period or 'month'} ({code}). Use {symbol} for ALL "
                "monetary figures (budgets, ad spend, ROI, projections). Never use USD "
                "or '$' unless the currency is actually USD."
            )
        return (
            f"The user's currency is {code} ({symbol}). Use {symbol} for ALL monetary "
            "figures (budgets, ad spend, ROI, projections). Never assume USD."
        )

    def _build_output_section(self) -> str:
        """Compose the output contract section of the prompt."""
        parts: list[str] = [
            "Return ONLY valid JSON.",
            "Do not return markdown.",
            "Do not include explanations outside the JSON.",
            "Follow the provided response schema exactly.",
            "Response schema:",
            RESPONSE_SCHEMA_JSON,
        ]
        if self._output_format:
            parts.append(f"Return your answer in the following format:\n{self._output_format}")
        if self._extra_rules:
            rules = "\n".join(f"- {rule}" for rule in self._extra_rules)
            parts.append(f"Additional rules:\n{rules}")
        return "\n".join(parts)
