"""AI strategy generation service.

Kept fully decoupled from HTTP. The real LLM pipeline lives in
app.services.ai (AIService + PromptBuilder + providers). When no
provider API key is configured — or the provider is temporarily
unavailable (rate limits, outages) — the service falls back to a
deterministic mock so the app still demos end-to-end.

Every successful generation persists the owning project, the marketing
strategy and a generation-history audit row, which powers the History
page and the export endpoints.
"""
import logging
import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.generation_history import GenerationHistory, GenerationStatus
from app.models.marketing_strategy import MarketingStrategy, StrategyStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.strategy import (
    StrategyGenerationRequest,
    StrategyGenerationResponse,
    StrategySection,
)
from app.services.ai.ai_service import AIService
from app.services.ai.country_profiles import profile_for_country
from app.services.ai.currencies import budget_label, currency_for_country
from app.services.ai.exceptions import (
    AIServiceError,
    ProviderError,
    ValidationError,
)
from app.services.ai.industry_playbooks import format_playbook, match_playbook
from app.services.ai.prompt_builder import MarketingBrief

logger = logging.getLogger("market_mind_ai.strategy_generation")

# Mock model identifier; used only when no provider key is configured.
MOCK_MODEL = "mock-groq-llama-3.3-70b"


class GenerationError(Exception):
    """Raised when strategy generation fails."""


class GenerationQuotaExceededError(GenerationError):
    """Raised when the LLM provider rate limit is exceeded.

    Carries a human-readable retry hint so the API can return a 503
    instead of a generic 500.
    """


def _provider_key() -> str:
    """Return the API key for the configured provider (settings or env)."""
    name = settings.AI_PROVIDER.lower()
    return getattr(settings, f"{name.upper()}_API_KEY", "") or ""


def _budget_label(request: StrategyGenerationRequest) -> str:
    if request.budget:
        return request.budget
    return budget_label(
        request.budget_amount,
        request.currency_symbol,
        request.currency_code,
        request.budget_period,
    )


def _budget_amount(request: StrategyGenerationRequest) -> float:
    """Resolve a numeric budget from the request for ROI math.

    Prefers the structured ``budget_amount``; falls back to parsing the
    human ``budget`` string; finally a representative demo figure.
    """
    if request.budget_amount is not None:
        return max(float(request.budget_amount), 500.0)

    text = (request.budget or "").strip().lower()
    if not text:
        return 10_000.0
    digits = re.findall(r"[\d,.]+", text)
    if not digits:
        return 10_000.0
    value = digits[0].replace(",", "")
    try:
        number = float(value)
    except ValueError:
        return 10_000.0
    if "k" in text:
        number *= 1000
    if "m" in text and "k" not in text:
        number *= 1_000_000
    return max(number, 500.0)


def _currency_meta(request: StrategyGenerationRequest) -> dict:
    """Currency/country metadata stored on the strategy content."""
    symbol = request.currency_symbol or currency_for_country(request.country)[1]
    code = request.currency_code or currency_for_country(request.country)[0]
    return {
        "country": request.country or "Global",
        "industry": request.industry,
        "product": request.product or request.project_name,
        "currency_code": code,
        "currency_symbol": symbol,
        "budget_amount": request.budget_amount,
        "budget_period": request.budget_period or "month",
        "budget_label": _budget_label(request),
    }


class StrategyGenerationService:
    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai_service = ai_service

    async def generate(
        self,
        request: StrategyGenerationRequest,
        db: AsyncSession | None = None,
        user: User | None = None,
    ) -> StrategyGenerationResponse:
        """Produce a structured marketing strategy via the AI pipeline.

        ``db``/``user`` are optional: when provided, the generated
        strategy, its owning project, and a history record are
        persisted so the result is exportable and shows up in history.
        """
        logger.info(
            "Generating strategy for project=%r industry=%r goals=%d",
            request.project_name,
            request.industry,
            len(request.goals),
        )

        # Fall back to the deterministic mock when no API key is set so
        # the endpoint keeps working in offline demos and CI.
        if self._ai_service is None and not _provider_key():
            logger.info("No AI provider key configured; using mock strategy")
            return await self._generate_mock(request, db=db, user=user)

        try:
            service = self._ai_service or AIService()
            playbook = match_playbook(request.industry)
            country_profile = profile_for_country(request.country)
            result = await service.generate_marketing_strategy(
                MarketingBrief(
                    business_name=request.project_name,
                    industry=request.industry,
                    product=request.product or request.project_name,
                    audience=request.target_audience,
                    country=request.country or "Global",
                    goal="; ".join(request.goals),
                    budget=_budget_label(request),
                    budget_amount=request.budget_amount,
                    currency_code=request.currency_code
                    or currency_for_country(request.country)[0],
                    currency_symbol=request.currency_symbol
                    or currency_for_country(request.country)[1],
                    budget_period=request.budget_period or "month",
                    brand_tone=request.tone,
                    competitors=request.competitors or [],
                    industry_playbook=format_playbook(playbook),
                    country_profile="\n".join(
                        ["Platforms: " + ", ".join(country_profile.get("platforms", []))]
                        + country_profile.get("tactics", [])
                    ),
                )
            )
            # Attach currency/country metadata so exports can render it.
            result.setdefault("metadata", _currency_meta(request))
        except ProviderError as exc:
            if exc.status_code == 429:
                if settings.AI_FALLBACK_TO_MOCK:
                    logger.warning(
                        "LLM provider rate limit reached for project=%r; "
                        "falling back to mock strategy (AI_FALLBACK_TO_MOCK=true)",
                        request.project_name,
                    )
                    return await self._generate_mock(request, db=db, user=user)
                logger.error(
                    "LLM provider rate limit exceeded for project=%r: %s",
                    request.project_name,
                    exc,
                )
                raise GenerationQuotaExceededError(
                    "The AI provider's rate limit was reached. Try again later."
                ) from None
            # Temporary provider outage: degrade to the mock so the demo
            # keeps working instead of surfacing a 500.
            logger.warning(
                "LLM provider unavailable (%s), falling back to mock strategy",
                exc,
            )
            return await self._generate_mock(request, db=db, user=user)
        except (ValidationError, AIServiceError) as exc:
            logger.exception("Strategy generation failed: %s", exc)
            raise GenerationError("Failed to generate strategy") from None
        except Exception:
            logger.exception("Strategy generation failed unexpectedly")
            raise GenerationError("Failed to generate strategy") from None

        return await self._to_response(request, result, db=db, user=user)

    async def _to_response(
        self,
        request: StrategyGenerationRequest,
        result: dict,
        *,
        db: AsyncSession | None,
        user: User | None,
    ) -> StrategyGenerationResponse:
        """Map the validated AI JSON document to the API response shape."""
        sections: list[StrategySection] = self._build_sections(result)

        if not sections:
            # Nothing to render from the LLM output; fail loudly rather
            # than returning an empty strategy.
            raise GenerationError("AI output contained no usable sections")

        summary = (
            f"A {request.tone} {request.industry} strategy for "
            f"{request.project_name} targeting {request.target_audience}."
        )

        strategy_id = str(uuid.uuid4())
        if db is not None and user is not None:
            strategy_id = await self._persist(request, user, result, db)

        return StrategyGenerationResponse(
            strategy_id=strategy_id,
            summary=summary,
            sections=sections,
            model_used=settings.AI_MODEL,
            content=result,
        )

    async def _persist(
        self,
        request: StrategyGenerationRequest,
        user: User,
        result: dict,
        db: AsyncSession,
    ) -> str:
        """Create project + strategy + history rows; return the strategy id."""
        # Reuse an existing project with the same name for this user so
        # repeated generations on the same business stay grouped.
        project = await db.scalar(
            select(Project).where(
                Project.user_id == user.id,
                Project.name == request.project_name,
                Project.deleted_at.is_(None),
            )
        )
        if project is None:
            project = Project(user_id=user.id, name=request.project_name)
            db.add(project)
            await db.flush()

        strategy = MarketingStrategy(
            project_id=project.id,
            name=request.project_name,
            target_audience=request.target_audience,
            goals=list(request.goals),
            content=result,
            status=StrategyStatus.COMPLETED,
        )
        db.add(strategy)
        await db.flush()

        history = GenerationHistory(
            strategy_id=strategy.id,
            model_used=settings.AI_MODEL,
            prompt_version="marketing-strategist-v1",
            input_params=request.model_dump(),
            output=result,
            tokens_used=None,
            latency_ms=None,
            status=GenerationStatus.SUCCESS,
        )
        db.add(history)
        await db.commit()

        logger.info(
            "Persisted strategy=%s project=%s history for user=%s",
            strategy.id,
            project.id,
            user.id,
        )
        return str(strategy.id)

    @staticmethod
    def _build_sections(result: dict) -> list[StrategySection]:
        """Flatten the structured LLM document into ordered sections."""
        sections: list[StrategySection] = []

        def add(title: str, content: str | None) -> None:
            if content and content.strip():
                sections.append(StrategySection(title=title, content=content.strip()))

        def join(items: list | None, separator: str = "; ") -> str:
            if not items:
                return ""
            return separator.join(str(i) for i in items if str(i).strip())

        exec_summary = result.get("executiveSummary") or {}
        add(
            "Executive Summary",
            "".join(
                (
                    f"{exec_summary.get('summary', '')}\n\n"
                    f"Key highlights:\n{join(exec_summary.get('highlights'), chr(10) + '- ')}\n"
                    f"Recommendation: {exec_summary.get('ask', '')}"
                )
            ).strip()
            or None,
        )

        score = result.get("marketingScore") or {}
        breakdown = score.get("breakdown") or []
        if score.get("overall") is not None:
            score_text = "\n".join(
                f"- {b.get('area')}: {b.get('score')}/100 — {b.get('assessment', '')}"
                for b in breakdown
            )
            add(
                "Marketing Score",
                f"Overall score: {score.get('overall')}/100\n{score_text}"
                + (f"\nBenchmark: {score.get('benchmark')}" if score.get("benchmark") else "")
                + (f"\n\n{score.get('summary', '')}" if score.get("summary") else ""),
            )

        strategy = result.get("marketingStrategy") or {}
        add("Marketing Objectives", join(strategy.get("objectives"), "\n- "))
        add("Market Positioning", strategy.get("positioning"))
        add("Key Messages", join(strategy.get("keyMessages"), "\n- "))
        channels = strategy.get("channels") or []
        if channels:
            channel_text = "\n".join(
                f"- {c.get('name')} ({c.get('priority')}): {c.get('description', '')}"
                for c in channels
            )
            add("Marketing Channels", channel_text)
        allocation = strategy.get("budgetAllocation") or []
        if allocation:
            budget_text = "\n".join(
                f"- {a.get('channel')}: {a.get('percentage')}%"
                for a in allocation
            )
            add("Estimated Budget", budget_text)
        kpis = strategy.get("kpis") or []
        if kpis:
            kpi_text = "\n".join(
                f"- {k.get('metric')}: {k.get('target')} ({k.get('timeframe', '')})"
                for k in kpis
            )
            add("KPIs", kpi_text)

        persona = result.get("customerPersona") or {}
        add("Customer Persona", persona.get("summary"))
        add(
            "Target Audience",
            "".join(
                f"{label}: {value}\n"
                for label, value in (
                    ("Age range", persona.get("ageRange")),
                    ("Location", persona.get("location")),
                    ("Occupation", persona.get("occupation")),
                    ("Income level", persona.get("incomeLevel")),
                )
                if value
            ).strip() or None,
        )
        add("Audience Interests", join(persona.get("interests"), ", "))
        add("Audience Pain Points", join(persona.get("painPoints"), "; "))
        add("Audience Goals", join(persona.get("goals"), "; "))
        add("Buying Triggers", join(persona.get("buyingTriggers"), "; "))
        add("Common Objections", join(persona.get("objections"), "; "))
        add(
            "Preferred Channels",
            join(persona.get("preferredChannels"), ", "),
        )

        swot = result.get("swotAnalysis") or {}
        add(
            "SWOT Analysis",
            "".join(
                f"{label}:\n{join(items, chr(10) + '- ')}\n"
                for label, items in (
                    ("Strengths", swot.get("strengths")),
                    ("Weaknesses", swot.get("weaknesses")),
                    ("Opportunities", swot.get("opportunities")),
                    ("Threats", swot.get("threats")),
                )
                if items
            ).strip()
            or swot.get("overallAssessment"),
        )
        add("SWOT Assessment", swot.get("overallAssessment"))

        market = result.get("marketOverview") or {}
        add(
            "Market Overview",
            "".join(
                (
                    f"{market.get('summary', '')}\n"
                    f"Market size: {market.get('targetMarketSize', '')} · "
                    f"Growth: {market.get('growthRate', '')}\n\n"
                    f"Key trends:\n{join(market.get('marketTrends'), chr(10) + '- ')}\n"
                    f"Key drivers:\n{join(market.get('keyDrivers'), chr(10) + '- ')}\n"
                    f"Market risks:\n{join(market.get('marketRisks'), chr(10) + '- ')}"
                )
            ).strip()
            or None,
        )

        seo = result.get("seoKeywords") or {}
        primary = seo.get("primaryKeywords") or []
        if primary:
            seo_text = "\n".join(
                f"- {k.get('keyword')} ({k.get('intent')}) — priority {k.get('priority')}"
                for k in primary[:12]
            )
            add("SEO Strategy", seo_text)
        add(
            "SEO Content Topics",
            "\n".join(
                f"- {t.get('title')} [{t.get('funnelStage')}]"
                for t in (seo.get("contentTopics") or [])
            )
            or None,
        )
        add(
            "On-Page SEO Recommendations",
            join(seo.get("onPageRecommendations"), "\n- "),
        )

        calendar = result.get("contentCalendar") or {}
        schedule = calendar.get("schedule") or []
        if schedule:
            calendar_text = "\n".join(
                f"- {c.get('date')} | {c.get('channel')} | {c.get('topic')} | CTA: {c.get('cta', '')}"
                for c in schedule
            )
            add("Content Calendar", calendar_text)

        email = result.get("emailCampaign") or {}
        add("Email Marketing", email.get("goal"))
        add("Email Subject Lines", join(email.get("subjectLines"), "\n- "))
        sequence = email.get("sequence") or []
        if sequence:
            seq_text = "\n".join(
                f"- Day {e.get('day')} ({e.get('type')}): {e.get('subject')}"
                for e in sequence
            )
            add("Email Sequence", seq_text)

        ads = result.get("advertisementIdeas") or {}
        campaigns = ads.get("campaigns") or []
        if campaigns:
            ads_text = "\n\n".join(
                f"{c.get('name')} — {c.get('platform')}\n"
                f"Objective: {c.get('objective')}\n"
                f"Audience: {c.get('audience')}\n"
                f"Budget: {c.get('budget')} | Duration: {c.get('duration')}\n"
                f"Expected: {c.get('expectedOutcome')}"
                for c in campaigns[:6]
            )
            add("Google & Meta Ads Strategy", ads_text)

        social = result.get("socialMediaStrategy") or {}
        platforms = social.get("platforms") or []
        if platforms:
            social_text = "\n\n".join(
                f"{p.get('name')} — {p.get('postingCadence')}\n"
                f"Focus: {p.get('focus', '')}\n"
                f"Content mix: {join(p.get('contentMix'), ', ')}\n"
                f"Goals: {join(p.get('goals'), ', ')}"
                for p in platforms
            )
            add("Social Media Strategy", social_text)
        add(
            "Social Community Management",
            join(social.get("communityManagement"), "\n- ") or None,
        )

        competitors = result.get("competitorAnalysis") or {}
        comps = competitors.get("competitors") or []
        if comps:
            comp_text = "\n\n".join(
                f"{c.get('name')} ({c.get('marketPosition')}) — threat level {c.get('threatLevel')}\n"
                f"Strengths: {join(c.get('strengths'), ', ')}\n"
                f"Weaknesses: {join(c.get('weaknesses'), ', ')}"
                for c in comps[:5]
            )
            add("Competitor Analysis", comp_text)
        add("Competitive Advantages", join(competitors.get("competitiveAdvantages"), "\n- "))
        add("Market Gaps", join(competitors.get("marketGaps"), "\n- "))
        add("Competitor Takeaways", join(competitors.get("keyTakeaways"), "\n- "))

        roadmap = result.get("implementationRoadmap") or {}
        phases = roadmap.get("phases") or []
        if phases:
            roadmap_text = "\n\n".join(
                f"{p.get('name')} ({p.get('duration')})\n"
                f"Objectives: {join(p.get('objectives'), ', ')}\n"
                f"Key activities:\n{join(p.get('keyActivities'), chr(10) + '- ')}\n"
                f"Success metrics: {join(p.get('successMetrics'), ', ')}"
                for p in phases
            )
            add("Implementation Roadmap (90 Days)", roadmap_text)

        milestones = result.get("weeklyMilestones") or {}
        weeks = milestones.get("weeks") or []
        if weeks:
            week_text = "\n".join(
                f"- {w.get('week')}: {w.get('focus')} — {w.get('successIndicator', '')}"
                for w in weeks
            )
            add("Weekly Milestones", week_text)

        roi = result.get("estimatedROI") or {}
        projections = roi.get("projections") or []
        if projections:
            roi_text = "\n".join(
                f"- {p.get('period')}: invest {p.get('investment')} → "
                f"{p.get('projectedReturn')} ({p.get('roiPercent')} ROI)"
                for p in projections
            )
            add(
                "Estimated ROI",
                f"{roi.get('summary', '')}\nPayback period: {roi.get('paybackPeriod', '')}\n\n{roi_text}"
                + (f"\n\nAssumptions:\n{join(roi.get('assumptions'), chr(10) + '- ')}" if roi.get("assumptions") else ""),
            )

        risks = result.get("riskMitigation") or {}
        risk_list = risks.get("risks") or []
        if risk_list:
            risk_text = "\n\n".join(
                f"{r.get('risk')} — {r.get('category')} "
                f"(likelihood {r.get('likelihood')}, impact {r.get('impact')})\n"
                f"Mitigation: {join(r.get('mitigation'), ', ')}"
                for r in risk_list
            )
            add("Risks and Mitigation", f"{risks.get('summary', '')}\n\n{risk_text}".strip())

        recommendations = result.get("finalRecommendations") or {}
        add(
            "Final Recommendations",
            "".join(
                (
                    f"{recommendations.get('summary', '')}\n\n"
                    f"Top priorities:\n{join(recommendations.get('priorities'), chr(10) + '- ')}\n"
                    f"Quick wins:\n{join(recommendations.get('quickWins'), chr(10) + '- ')}\n"
                    f"Long-term investments:\n{join(recommendations.get('longTermInvestments'), chr(10) + '- ')}\n"
                    f"Success criteria:\n{join(recommendations.get('successCriteria'), chr(10) + '- ')}\n\n"
                    f"{recommendations.get('closingStatement', '')}"
                )
            ).strip()
            or None,
        )

        tools = result.get("recommendedTools") or {}
        tool_list = tools.get("tools") or []
        if tool_list:
            tool_text = "\n".join(
                f"- {t.get('name')} ({t.get('category')}): {t.get('purpose')} — {t.get('pricing')}"
                for t in tool_list[:10]
            )
            add("Recommended Tools", tool_text)

        analysis = result.get("businessAnalysis") or {}
        add("Business Analysis", analysis.get("overview"))
        add(
            "Business Strengths",
            join(analysis.get("strengths"), "\n- "),
        )
        add(
            "Growth Levers",
            join(analysis.get("growthLevers"), "\n- "),
        )
        add(
            "Immediate Wins",
            join(analysis.get("immediateWins"), "\n- "),
        )

        funnel = result.get("marketingFunnel") or {}
        stages = funnel.get("stages") or []
        if stages:
            funnel_text = "\n\n".join(
                f"{s.get('stage')}:\n{join(s.get('tactics'), chr(10) + '- ')}"
                for s in stages
            )
            add("Marketing Funnel", f"{funnel.get('summary', '')}\n\n{funnel_text}".strip())

        influencers = result.get("influencerStrategy") or {}
        add("Influencer Strategy", influencers.get("summary"))
        tiers = influencers.get("tiers") or []
        if tiers:
            tier_text = "\n".join(
                f"- {t.get('tier')}: {t.get('strategy')}" for t in tiers
            )
            add("Influencer Tiers", tier_text)
        add(
            "Influencer Campaign Ideas",
            join(influencers.get("campaignIdeas"), "\n- "),
        )

        opportunities = result.get("growthOpportunities") or {}
        add("Growth Opportunities", opportunities.get("summary"))
        opps = opportunities.get("opportunities") or []
        if opps:
            opp_text = "\n".join(
                f"- {o.get('name')} ({o.get('effort')} effort, {o.get('impact')} impact): {o.get('why')}"
                for o in opps
            )
            add("Growth Opportunity Details", opp_text)

        scaling = result.get("futureScaling") or {}
        add("Future Scaling Strategy", scaling.get("summary"))
        phases = scaling.get("phases") or []
        if phases:
            phase_text = "\n".join(
                f"- {p.get('phase')}: {p.get('focus')}" for p in phases
            )
            add("Scaling Phases", phase_text)
        add(
            "Scale Levers",
            join(scaling.get("scaleLevers"), "\n- "),
        )

        return sections

    async def _generate_mock(
        self,
        request: StrategyGenerationRequest,
        *,
        db: AsyncSession | None = None,
        user: User | None = None,
    ) -> StrategyGenerationResponse:
        """Deterministic but input-unique fallback used when the LLM is
        unavailable.

        Driven by the industry playbook, country profile and currency so
        Restaurant (PK) != SaaS (US) != Gym (AE), matching the section set
        the real pipeline produces.
        """
        from app.services.ai.mock_strategy import build_mock_strategy

        mock_doc = build_mock_strategy(request)

        sections = self._build_sections(mock_doc)

        strategy_id = str(uuid.uuid4())
        if db is not None and user is not None:
            strategy_id = await self._persist(request, user, mock_doc, db)

        response = StrategyGenerationResponse(
            strategy_id=strategy_id,
            summary=(
                f"A {request.tone} {request.industry} strategy for "
                f"{request.project_name} in {request.country or 'their market'} "
                f"targeting {request.target_audience}."
            ),
            sections=sections,
            model_used=MOCK_MODEL,
            content=mock_doc,
        )

        logger.info(
            "Strategy generated strategy_id=%s sections=%d",
            response.strategy_id,
            len(response.sections),
        )
        return response
