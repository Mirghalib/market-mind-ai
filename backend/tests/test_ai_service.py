"""Tests for the AIService pipeline.

Uses a fake provider so no API calls or API keys are needed. The fake
returns a minimal-but-valid payload matching the response schema.
"""
import asyncio

import pytest

from app.services.ai.ai_service import AIService
from app.services.ai.exceptions import (
    ParseError,
    ProviderError,
    ValidationError,
)
from app.services.ai.parsers.response_parser import ResponseParser
from app.services.ai.prompt_builder import MarketingBrief, PromptBuilder
from app.services.ai.providers.base import LLMProvider
from app.services.ai.validators.json_validator import JSONValidator


class FakeProvider(LLMProvider):
    """Configurable fake provider: queue responses or raise errors."""

    name = "fake"

    def __init__(self) -> None:
        super().__init__(model="fake-model", api_key="test-key")
        self.calls = 0
        self.recorded_prompts: list[str] = []
        self.responses: list[str | Exception] = []

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        self.calls += 1
        self.recorded_prompts.append(system_prompt)
        item = self.responses.pop(0) if self.responses else _VALID_JSON
        if isinstance(item, Exception):
            raise item
        return item


_VALID_JSON = """{
  "marketingStrategy": {
    "overview": "Test strategy",
    "objectives": ["Increase sales"],
    "positioning": "Premium",
    "keyMessages": ["Quality first"],
    "channels": [{"id": "c1", "name": "Instagram", "priority": "high"}],
    "budgetAllocation": [{"channel": "Instagram", "percentage": 100}],
    "kpis": [{"id": "k1", "metric": "Sales", "target": "+20%"}]
  },
  "customerPersona": {
    "name": "Sam",
    "ageRange": "25-40",
    "location": "US",
    "occupation": "Engineer",
    "incomeLevel": "80k",
    "summary": "Busy professional",
    "interests": ["Coffee"],
    "painPoints": ["No time"],
    "goals": ["Save time"],
    "preferredChannels": ["Instagram"],
    "buyingTriggers": ["Discounts"],
    "objections": ["Price"]
  },
  "swotAnalysis": {
    "strengths": ["Quality"],
    "weaknesses": ["Small team"],
    "opportunities": ["Online growth"],
    "threats": ["Big brands"],
    "overallAssessment": "Positioned to grow."
  },
  "seoKeywords": {
    "primaryKeywords": [{"id": "k1", "keyword": "coffee beans", "intent": "commercial", "priority": "high"}],
    "secondaryKeywords": [{"id": "k2", "keyword": "specialty coffee", "intent": "informational"}],
    "longTailKeywords": [{"id": "k3", "keyword": "best coffee for home", "intent": "commercial"}],
    "contentTopics": [{"id": "t1", "title": "How to brew", "targetKeyword": "coffee beans", "funnelStage": "consideration"}],
    "onPageRecommendations": ["Improve meta titles"]
  },
  "contentCalendar": {
    "timeframe": "30 days",
    "cadence": "3 posts/week",
    "schedule": [{"id": "d1", "date": "2026-08-01", "channel": "Instagram", "contentFormat": "Reel", "topic": "Brewing tips", "cta": "Shop now"}]
  },
  "advertisementIdeas": {
    "summary": "Run Meta ads",
    "campaigns": [{
      "id": "a1", "name": "Launch", "platform": "Meta Ads", "objective": "Sales",
      "audience": "Coffee lovers", "budget": "$2k", "duration": "3 weeks",
      "adCopy": [{"id": "c1", "headline": "Fresh beans", "description": "Taste the difference", "cta": "Buy"}],
      "targetingSuggestions": ["Interests: coffee"], "expectedOutcome": "3k clicks"
    }]
  },
  "emailCampaign": {
    "campaignName": "Welcome series", "goal": "Onboard", "audience": "New subscribers",
    "subjectLines": ["Welcome!"], "preheader": "Hello",
    "sequence": [{
      "id": "e1", "day": 0, "type": "Welcome", "subject": "Welcome to Acme",
      "previewText": "Hi", "bodySections": [{"heading": "Hi", "content": "Welcome"}], "cta": "Shop"
    }]
  },
  "competitorAnalysis": {
    "competitors": [{
      "id": "cp1", "name": "Blue Bottle", "marketPosition": "Leader",
      "strengths": ["Brand"], "weaknesses": ["Price"], "pricing": "Premium",
      "differentiators": ["Stores"], "threatLevel": "high"
    }],
    "competitiveAdvantages": ["Direct trade"],
    "marketGaps": ["Home delivery"],
    "keyTakeaways": ["Win on delivery"]
  },
  "recommendedTools": {
    "summary": "Lean stack",
    "tools": [{
      "id": "tl1", "name": "Notion", "category": "project-management",
      "purpose": "Planning", "pricing": "Free", "difficulty": "easy", "recommendation": "recommended"
    }]
  }
}"""


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


def make_service(provider: FakeProvider, **kwargs) -> AIService:
    """Build an AIService wired to a fake provider."""
    return AIService(
        builder=PromptBuilder(),
        provider=provider,
        parser=ResponseParser(),
        validator=JSONValidator(),
        retry_attempts=kwargs.get("retry_attempts", 3),
        retry_backoff_seconds=kwargs.get("retry_backoff_seconds", 0.0),
    )


@pytest.mark.asyncio
async def test_generates_validated_strategy(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    service = make_service(provider)

    result = await service.generate_marketing_strategy(brief)

    assert result["marketingStrategy"]["overview"] == "Test strategy"
    assert result["customerPersona"]["name"] == "Sam"
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_prompt_is_built_from_brief(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    service = make_service(provider)

    await service.generate_marketing_strategy(brief)

    prompt = provider.recorded_prompts[0]
    assert "Acme Coffee" in prompt
    assert "Allocate the marketing budget." in prompt
    assert "Return ONLY valid JSON." in prompt


@pytest.mark.asyncio
async def test_retries_transient_provider_error_then_succeeds(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    provider.responses = [
        ProviderError("temporary 503", provider="fake", status_code=503, retryable=True),
        _VALID_JSON,
    ]
    service = make_service(provider, retry_attempts=3)

    result = await service.generate_marketing_strategy(brief)

    assert provider.calls == 2
    assert result["marketingStrategy"]["overview"] == "Test strategy"


@pytest.mark.asyncio
async def test_exhausts_retries_on_persistent_error(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    provider.responses = [
        ProviderError("temporary 503", provider="fake", status_code=503, retryable=True),
        ProviderError("temporary 503", provider="fake", status_code=503, retryable=True),
        ProviderError("temporary 503", provider="fake", status_code=503, retryable=True),
    ]
    service = make_service(provider, retry_attempts=3)

    with pytest.raises(ProviderError):
        await service.generate_marketing_strategy(brief)

    assert provider.calls == 3


@pytest.mark.asyncio
async def test_does_not_retry_non_retryable_error(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    provider.responses = [
        ProviderError("invalid api key", provider="fake", status_code=401, retryable=False),
    ]
    service = make_service(provider, retry_attempts=3)

    with pytest.raises(ProviderError):
        await service.generate_marketing_strategy(brief)

    assert provider.calls == 1


@pytest.mark.asyncio
async def test_parse_error_raises_parse_error(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    provider.responses = ["Here is some prose with no JSON at all."]
    service = make_service(provider)

    with pytest.raises(ParseError):
        await service.generate_marketing_strategy(brief)


@pytest.mark.asyncio
async def test_validation_error_for_invalid_output(brief: MarketingBrief) -> None:
    provider = FakeProvider()
    provider.responses = ['{"marketingStrategy": {}}']  # missing required sections
    service = make_service(provider)

    with pytest.raises(ValidationError):
        await service.generate_marketing_strategy(brief)


@pytest.mark.asyncio
async def test_parser_handles_markdown_fence_and_prose() -> None:
    parser = ResponseParser()
    raw = 'Sure! Here is the JSON:\n```json\n{"hello": "world"}\n```\nHope that helps.'

    result = parser.parse(raw)

    assert result == {"hello": "world"}


@pytest.mark.asyncio
async def test_parser_repairs_trailing_commas() -> None:
    parser = ResponseParser()

    result = parser.parse('{"items": [1, 2, 3,]}')

    assert result == {"items": [1, 2, 3]}


@pytest.mark.asyncio
async def test_backoff_delay_uses_retry_config(brief: MarketingBrief) -> None:
    """A non-zero backoff should make the retry path wait (0.01s base)."""
    provider = FakeProvider()
    provider.responses = [
        ProviderError("temporary", provider="fake", retryable=True),
        _VALID_JSON,
    ]
    service = make_service(provider, retry_attempts=2, retry_backoff_seconds=0.01)

    started = asyncio.get_event_loop().time()
    result = await service.generate_marketing_strategy(brief)
    elapsed = asyncio.get_event_loop().time() - started

    assert provider.calls == 2
    assert result["marketingStrategy"]["overview"] == "Test strategy"
    assert elapsed >= 0.01
