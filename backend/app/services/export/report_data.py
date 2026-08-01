"""Shared report data extraction for every export renderer.

Normalizes ``MarketingStrategy.content`` (the structured LLM document)
into one typed, consistent view so the PDF, DOCX, PPTX, Markdown, HTML
and share-preview builders all consume identical data with identical
fallbacks. Every getter fails soft: missing sections produce empty
collections, never a crash.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Brand system — single source of truth for the consulting look
# ---------------------------------------------------------------------------

BRAND = {
    "primary": "#4F46E5",      # indigo-600
    "primary_dark": "#4338CA",  # indigo-700
    "secondary": "#7C3AED",     # violet-600
    "accent": "#06B6D4",        # cyan-500
    "dark": "#1E293B",          # slate-800 ink
    "slate": "#0F172A",         # slate-900
    "muted": "#64748B",         # slate-500
    "light": "#EEF2FF",         # indigo-50
    "panel": "#F8FAFC",         # slate-50
    "line": "#E2E8F0",          # slate-200
    "white": "#FFFFFF",
    "emerald": "#10B981",
    "amber": "#F59E0B",
    "rose": "#F43F5E",
    "chart": ["#4F46E5", "#818CF8", "#A5B4FC", "#C7D2FE", "#E0E7FF", "#7C3AED"],
}

APP_NAME = "Market Mind AI"
APP_TAGLINE = "AI-Powered Marketing Intelligence"


# ---------------------------------------------------------------------------
# Small parsing helpers
# ---------------------------------------------------------------------------


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def to_number(value: Any, default: float = 0.0) -> float:
    """Parse a number out of free text like '40%' or '$2.4k' or '+3%'."""
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return default
    cleaned = str(value).replace(",", "").replace("%", "").replace("+", "").strip()
    if not cleaned:
        return default
    try:
        return float(cleaned)
    except ValueError:
        return default


def to_int(value: Any, default: int = 0) -> int:
    return int(to_number(value, float(default)))


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def format_date(value: Any, fmt: str = "%B %d, %Y") -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str) and value.strip():
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    else:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(fmt)


# ---------------------------------------------------------------------------
# ReportData — normalized view over one strategy
# ---------------------------------------------------------------------------


class ReportData:
    """One strategy, normalized for every export format."""

    def __init__(self, strategy) -> None:
        self.strategy = strategy
        self.content: dict = _as_dict(getattr(strategy, "content", None))
        self.name = clean_text(getattr(strategy, "name", None)) or "Marketing Strategy"
        self.audience = clean_text(getattr(strategy, "target_audience", None))
        self.goals = _as_list(getattr(strategy, "goals", None))
        status = getattr(strategy, "status", None)
        self.status = getattr(status, "value", status) or "completed"
        self.created_at = getattr(strategy, "created_at", None)
        self.generated_date = format_date(self.created_at)
        self.strategy_id = str(getattr(strategy, "id", ""))

    # --- metadata (currency / country) --------------------------------------

    @property
    def metadata(self) -> dict:
        meta = _as_dict(self.content.get("metadata"))
        if meta:
            return meta
        # Fall back to request-derived values stored at generation time.
        return {
            "country": self.country_fallback,
            "industry": self.industry,
            "product": self.name,
        }

    @property
    def country_fallback(self) -> str:
        persona = self.persona
        location = clean_text(persona.get("location"))
        if location and location != "Global":
            return location
        return "Global"

    @property
    def country(self) -> str:
        return clean_text(self.metadata.get("country")) or self.country_fallback

    @property
    def currency_code(self) -> str:
        return clean_text(self.metadata.get("currency_code")) or "USD"

    @property
    def currency_symbol(self) -> str:
        return clean_text(self.metadata.get("currency_symbol")) or "$"

    @property
    def budget_period(self) -> str:
        return clean_text(self.metadata.get("budget_period")) or "month"

    @property
    def budget_amount(self) -> float | None:
        value = self.metadata.get("budget_amount")
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def budget_label(self) -> str:
        label = clean_text(self.metadata.get("budget_label"))
        if label and label != "Not specified":
            return label
        return self.format_budget()

    def format_budget(self, amount: float | None = None) -> str:
        """Format the budget with the correct symbol, e.g. 'Rs. 100,000 / month'."""
        from app.services.ai.currencies import format_budget as fmt

        value = amount if amount is not None else self.budget_amount
        return fmt(value, self.currency_symbol, self.currency_code, self.budget_period)

    @property
    def currency_label(self) -> str:
        return f"{self.currency_code} ({self.currency_symbol.strip()})"

    # --- top-level sections ------------------------------------------------

    @property
    def executive_summary(self) -> dict:
        return _as_dict(self.content.get("executiveSummary"))

    @property
    def summary_text(self) -> str:
        es = self.executive_summary
        text = clean_text(es.get("summary"))
        if text:
            return text
        return clean_text(es.get("ask"))

    @property
    def highlights(self) -> list[str]:
        return [clean_text(h) for h in _as_list(self.executive_summary.get("highlights")) if clean_text(h)]

    @property
    def recommendation(self) -> str:
        return clean_text(self.executive_summary.get("ask"))

    # --- marketing score ----------------------------------------------------

    @property
    def marketing_score(self) -> dict:
        return _as_dict(self.content.get("marketingScore"))

    @property
    def score(self) -> int:
        return to_int(self.marketing_score.get("overall"))

    @property
    def score_breakdown(self) -> list[dict]:
        return [
            {
                "area": clean_text(b.get("area")),
                "score": to_int(b.get("score")),
                "assessment": clean_text(b.get("assessment")),
            }
            for b in _as_list(self.marketing_score.get("breakdown"))
            if clean_text(b.get("area"))
        ]

    @property
    def score_benchmark(self) -> str:
        return clean_text(self.marketing_score.get("benchmark"))

    @property
    def score_summary(self) -> str:
        return clean_text(self.marketing_score.get("summary"))

    # --- market -------------------------------------------------------------

    @property
    def market(self) -> dict:
        return _as_dict(self.content.get("marketOverview"))

    @property
    def industry(self) -> str:
        mkt = self.market
        size = clean_text(mkt.get("targetMarketSize"))
        if size and size != "—":
            return size
        return clean_text(mkt.get("summary"))[:60] or "—"

    @property
    def market_trends(self) -> list[str]:
        return [clean_text(t) for t in _as_list(self.market.get("marketTrends")) if clean_text(t)]

    @property
    def market_drivers(self) -> list[str]:
        return [clean_text(t) for t in _as_list(self.market.get("keyDrivers")) if clean_text(t)]

    @property
    def market_risks(self) -> list[str]:
        return [clean_text(t) for t in _as_list(self.market.get("marketRisks")) if clean_text(t)]

    # --- persona ------------------------------------------------------------

    @property
    def persona(self) -> dict:
        return _as_dict(self.content.get("customerPersona"))

    # --- swot ---------------------------------------------------------------

    @property
    def swot(self) -> dict:
        return _as_dict(self.content.get("swotAnalysis"))

    @property
    def swot_quadrants(self) -> dict[str, list[str]]:
        s = self.swot
        return {
            "Strengths": [clean_text(i) for i in _as_list(s.get("strengths")) if clean_text(i)],
            "Weaknesses": [clean_text(i) for i in _as_list(s.get("weaknesses")) if clean_text(i)],
            "Opportunities": [clean_text(i) for i in _as_list(s.get("opportunities")) if clean_text(i)],
            "Threats": [clean_text(i) for i in _as_list(s.get("threats")) if clean_text(i)],
        }

    # --- marketing strategy (channels/kpis/budget) ---------------------------

    @property
    def strategy_block(self) -> dict:
        return _as_dict(self.content.get("marketingStrategy"))

    @property
    def objectives(self) -> list[str]:
        return [clean_text(o) for o in _as_list(self.strategy_block.get("objectives")) if clean_text(o)]

    @property
    def positioning(self) -> str:
        return clean_text(self.strategy_block.get("positioning"))

    @property
    def key_messages(self) -> list[str]:
        return [clean_text(m) for m in _as_list(self.strategy_block.get("keyMessages")) if clean_text(m)]

    @property
    def channels(self) -> list[dict]:
        return [
            {
                "name": clean_text(c.get("name")),
                "priority": clean_text(c.get("priority")),
                "description": clean_text(c.get("description")),
            }
            for c in _as_list(self.strategy_block.get("channels"))
            if clean_text(c.get("name"))
        ]

    @property
    def kpis(self) -> list[dict]:
        return [
            {
                "metric": clean_text(k.get("metric")),
                "target": clean_text(k.get("target")),
                "timeframe": clean_text(k.get("timeframe")),
            }
            for k in _as_list(self.strategy_block.get("kpis"))
            if clean_text(k.get("metric"))
        ]

    @property
    def budget(self) -> list[dict]:
        items = []
        for a in _as_list(self.strategy_block.get("budgetAllocation")):
            channel = clean_text(a.get("channel"))
            pct = to_number(a.get("percentage"))
            if channel and pct > 0:
                items.append({"channel": channel, "percentage": pct})
        return items

    # --- competitors ---------------------------------------------------------

    @property
    def competitors(self) -> list[dict]:
        comp = _as_dict(self.content.get("competitorAnalysis"))
        return [
            {
                "name": clean_text(c.get("name")),
                "position": clean_text(c.get("marketPosition")),
                "threat": clean_text(c.get("threatLevel")),
                "strengths": _as_list(c.get("strengths")),
                "weaknesses": _as_list(c.get("weaknesses")),
            }
            for c in _as_list(comp.get("competitors"))
            if clean_text(c.get("name"))
        ]

    # --- SEO / email / social / ads -----------------------------------------

    @property
    def seo(self) -> dict:
        return _as_dict(self.content.get("seoKeywords"))

    @property
    def email_campaign(self) -> dict:
        return _as_dict(self.content.get("emailCampaign"))

    @property
    def social(self) -> dict:
        return _as_dict(self.content.get("socialMediaStrategy"))

    @property
    def ads(self) -> dict:
        return _as_dict(self.content.get("advertisementIdeas"))

    @property
    def calendar(self) -> dict:
        return _as_dict(self.content.get("contentCalendar"))

    # --- roadmap / milestones ------------------------------------------------

    @property
    def roadmap(self) -> dict:
        return _as_dict(self.content.get("implementationRoadmap"))

    @property
    def roadmap_phases(self) -> list[dict]:
        return _as_list(self.roadmap.get("phases"))

    @property
    def milestones(self) -> dict:
        return _as_dict(self.content.get("weeklyMilestones"))

    @property
    def milestone_weeks(self) -> list[dict]:
        return _as_list(self.milestones.get("weeks"))

    # --- ROI -----------------------------------------------------------------

    @property
    def roi(self) -> dict:
        return _as_dict(self.content.get("estimatedROI"))

    @property
    def roi_projections(self) -> list[dict]:
        return [
            {
                "period": clean_text(p.get("period")),
                "investment": clean_text(p.get("investment")),
                "projected_return": clean_text(p.get("projectedReturn")),
                "roi_percent": to_number(p.get("roiPercent")),
            }
            for p in _as_list(self.roi.get("projections"))
            if clean_text(p.get("period"))
        ]

    # --- risks / recommendations ----------------------------------------------

    @property
    def risks(self) -> dict:
        return _as_dict(self.content.get("riskMitigation"))

    @property
    def risk_items(self) -> list[dict]:
        return [
            {
                "risk": clean_text(r.get("risk")),
                "category": clean_text(r.get("category")),
                "likelihood": clean_text(r.get("likelihood")),
                "impact": clean_text(r.get("impact")),
                "mitigation": _as_list(r.get("mitigation")),
            }
            for r in _as_list(self.risks.get("risks"))
            if clean_text(r.get("risk"))
        ]

    @property
    def recommendations(self) -> dict:
        return _as_dict(self.content.get("finalRecommendations"))

    # --- presence helpers (for renderers that skip empty sections) -------------

    def has(self, section: str) -> bool:
        value = self.content.get(section)
        if isinstance(value, dict):
            return bool(value)
        if isinstance(value, list):
            return bool(value)
        return bool(value)

    @property
    def present_sections(self) -> list[str]:
        """Ordered list of section keys present in the content (for TOCs)."""
        order = [
            "executiveSummary", "marketingScore", "marketOverview", "customerPersona",
            "swotAnalysis", "competitorAnalysis", "marketingStrategy", "seoKeywords",
            "emailCampaign", "socialMediaStrategy", "advertisementIdeas", "contentCalendar",
            "implementationRoadmap", "weeklyMilestones", "estimatedROI", "riskMitigation",
            "finalRecommendations",
        ]
        return [key for key in order if self.has(key)]

    # --- convenience ----------------------------------------------------------

    @property
    def kpi_rows(self) -> list[list[str]]:
        return [[k["metric"], k["target"], k["timeframe"]] for k in self.kpis]

    @property
    def budget_rows(self) -> list[list[str]]:
        return [[b["channel"], f"{b['percentage']:.0f}%"] for b in self.budget]

    @property
    def milestone_rows(self) -> list[list[str]]:
        return [
            [w.get("week", ""), w.get("focus", ""), w.get("owner", "—"),
             w.get("successIndicator", "")]
            for w in self.milestone_weeks
        ]

    @property
    def roi_rows(self) -> list[list[str]]:
        return [
            [p["period"], p["investment"], p["projected_return"], f"{p['roi_percent']:.0f}%"]
            for p in self.roi_projections
        ]
