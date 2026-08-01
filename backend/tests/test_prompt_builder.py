"""Tests for the PromptBuilder (no API calls involved)."""
import pytest

from app.services.ai.prompt_builder import MARKETING_PROMPT_TEMPLATE, MarketingBrief, PromptBuilder


@pytest.fixture
def brief() -> MarketingBrief:
    return MarketingBrief(
        business_name="Acme Coffee",
        industry="Food & Beverage",
        product="Single-origin coffee beans",
        audience="Urban professionals aged 25-40",
        country="United States",
        goal="Increase online sales",
        budget="10,000 USD / quarter",
        brand_tone="Friendly, premium, sustainable",
        competitors=["Blue Bottle", "Stumptown"],
    )


def test_build_returns_prompt_with_all_sections(brief: MarketingBrief) -> None:
    prompt = PromptBuilder().build(brief)

    assert "Acme Coffee" in prompt
    assert "Food & Beverage" in prompt
    assert "Single-origin coffee beans" in prompt
    assert "Urban professionals aged 25-40" in prompt
    assert "United States" in prompt
    assert "Increase online sales" in prompt
    assert "10,000 USD / quarter" in prompt
    assert "Friendly, premium, sustainable" in prompt
    assert "- Blue Bottle" in prompt
    assert "- Stumptown" in prompt


def test_build_is_reusable_across_briefs() -> None:
    builder = PromptBuilder()
    first = builder.build(
        MarketingBrief(
            business_name="Acme",
            industry="Tech",
            product="SaaS",
            audience="Startups",
            country="US",
            goal="Signups",
            budget="5k",
            brand_tone="Bold",
        )
    )
    second = builder.build(
        MarketingBrief(
            business_name="Beta",
            industry="Fitness",
            product="App",
            audience="Runners",
            country="UK",
            goal="Retention",
            budget="2k",
            brand_tone="Energetic",
        )
    )

    assert "Acme" in first and "Beta" not in first
    assert "Beta" in second and "Acme" not in second


def test_competitors_placeholder_when_none(brief: MarketingBrief) -> None:
    brief.competitors = []
    prompt = PromptBuilder().build(brief)

    assert "None provided" in prompt


def test_output_format_and_extra_rules_are_included(brief: MarketingBrief) -> None:
    prompt = PromptBuilder(
        output_format="JSON with keys: strategy, channels, kpis",
        extra_rules=["Keep it under 300 words", "Use markdown headings"],
    ).build(brief)

    assert "JSON with keys: strategy, channels, kpis" in prompt
    assert "Keep it under 300 words" in prompt
    assert "Use markdown headings" in prompt


def test_custom_template_via_subclass(brief: MarketingBrief) -> None:
    class MinimalBuilder(PromptBuilder):
        def build_marketing_prompt(self, brief: MarketingBrief) -> str:
            return f"Marketing brief for {brief.business_name}: {brief.goal}"

    prompt = MinimalBuilder().build(brief)

    assert prompt == "Marketing brief for Acme Coffee: Increase online sales"


def test_default_template_is_complete(brief: MarketingBrief) -> None:
    prompt = PromptBuilder().build(brief)

    assert all(section in MARKETING_PROMPT_TEMPLATE for section in ("# Business", "# Audience", "# Goal", "# Budget", "# Brand tone", "# Competitors", "# Responsibilities"))


def test_default_prompt_contains_strict_json_rules(brief: MarketingBrief) -> None:
    prompt = PromptBuilder().build(brief)

    assert "Return ONLY valid JSON." in prompt
    assert "Do not return markdown." in prompt
    assert "Do not include explanations outside the JSON." in prompt
    assert "Follow the provided response schema exactly." in prompt


def test_default_prompt_embeds_response_schema(brief: MarketingBrief) -> None:
    prompt = PromptBuilder().build(brief)

    assert '"title":"AI Marketing Strategist Output"' in prompt
    assert '"marketingStrategy"' in prompt
    assert '"competitorAnalysis"' in prompt
    assert '"recommendedTools"' in prompt
    # New report sections are part of the output contract.
    assert '"marketingScore"' in prompt
    assert '"implementationRoadmap"' in prompt
    assert '"estimatedROI"' in prompt
    assert '"riskMitigation"' in prompt
    assert '"executiveSummary"' in prompt


def test_all_responsibilities_present(brief: MarketingBrief) -> None:
    prompt = PromptBuilder().build(brief)

    responsibilities = [
        "Analyze the business and its market.",
        "Identify the target audience.",
        "Create a customer persona.",
        "Generate a SWOT analysis.",
        "Provide a market overview with trends, size, and drivers.",
        "Recommend marketing channels.",
        "Suggest SEO keywords and content topics.",
        "Create a 30-day content calendar.",
        "Generate a social media strategy with per-platform plans.",
        "Write a marketing email campaign.",
        "Recommend advertisement ideas (Google & Meta).",
        "Suggest competitor positioning.",
        "Allocate the marketing budget.",
        "Score the overall marketing plan (0-100) with a per-area breakdown.",
        "Build a 90-day implementation roadmap with 3 phases.",
        "Define weekly milestones for the 90-day plan.",
        "Estimate ROI with assumptions and period-by-period projections.",
        "Identify risks and mitigation plans.",
        "Write an executive summary for the report cover.",
        "Provide final recommendations with quick wins and success criteria.",
    ]
    for responsibility in responsibilities:
        assert responsibility in prompt
