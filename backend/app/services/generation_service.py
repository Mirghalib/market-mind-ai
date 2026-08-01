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
from app.services.ai.exceptions import (
    AIServiceError,
    ProviderError,
    ValidationError,
)
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
    return request.budget or "Not specified"


def _budget_amount(request: StrategyGenerationRequest) -> float:
    """Extract a numeric budget from the request for ROI math.

    Accepts values like "$10,000", "10k USD", "10000", "£8,000 / quarter".
    Falls back to a representative demo figure when nothing numeric is
    present so the mock ROI stays deterministic and useful.
    """
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
            result = await service.generate_marketing_strategy(
                MarketingBrief(
                    business_name=request.project_name,
                    industry=request.industry,
                    product=request.project_name,
                    audience=request.target_audience,
                    country=request.country or "Global",
                    goal="; ".join(request.goals),
                    budget=_budget_label(request),
                    brand_tone=request.tone,
                    competitors=request.competitors or [],
                )
            )
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

        return sections

    async def _generate_mock(
        self,
        request: StrategyGenerationRequest,
        *,
        db: AsyncSession | None = None,
        user: User | None = None,
    ) -> StrategyGenerationResponse:
        """Deterministic fallback content used when the LLM is unavailable.

        Mirrors the section set the real pipeline produces so the UI and
        exports behave identically in offline demos.
        """
        mock_doc = {
            "executiveSummary": {
                "summary": (
                    f"{request.project_name} enters the {request.industry} market with a "
                    "differentiated offer and a disciplined 90-day growth plan. This strategy "
                    "prioritizes high-intent channels, a measurable scorecard, and fast "
                    "execution loops so results compound quickly."
                ),
                "highlights": [
                    "A prioritized channel mix aligned with the target audience",
                    "A measurable KPI scorecard with 90-day targets",
                    "A phased roadmap with weekly milestones and clear owners",
                ],
                "ask": (
                    f"Approve the plan and begin Phase 1 — Foundation — within the first "
                    "week to start capturing demand."
                ),
            },
            "marketingScore": {
                "overall": 74,
                "breakdown": [
                    {"id": "ms1", "area": "Strategy", "score": 78, "assessment": "Clear positioning and objectives with room to sharpen messaging."},
                    {"id": "ms2", "area": "SEO", "score": 62, "assessment": "Foundational keyword set defined; needs content investment."},
                    {"id": "ms3", "area": "Content", "score": 68, "assessment": "Calendar is structured; cadence should increase over time."},
                    {"id": "ms4", "area": "Social", "score": 71, "assessment": "Platform plan is solid; community management needs staffing."},
                    {"id": "ms5", "area": "Email", "score": 82, "assessment": "Nurture sequence is strong and ready to launch."},
                    {"id": "ms6", "area": "Ads", "score": 69, "assessment": "Campaign structure is sound; budgets need active optimization."},
                ],
                "benchmark": "Industry average for similar SMBs is 60/100",
                "summary": (
                    f"{request.project_name} is above the typical benchmark for its "
                    "segment. The biggest near-term gains come from SEO and content "
                    "execution."
                ),
            },
            "marketingStrategy": {
                "overview": (
                    f"{request.project_name} is entering the {request.industry} "
                    "market with a differentiated offer. This strategy lays out a "
                    "prioritized growth plan covering positioning, channels, budget "
                    "and measurement."
                ),
                "objectives": list(request.goals),
                "positioning": (
                    f"Position {request.project_name} as the accessible, "
                    "outcome-driven choice for the target audience, emphasizing "
                    "value and measurable results over generic alternatives."
                ),
                "keyMessages": [
                    "Built around your goals, not templates",
                    "Clear results from week one",
                    "A dedicated plan for every channel",
                ],
                "channels": [
                    {"id": "c1", "name": "Email", "priority": "high", "description": "Nurture high-intent leads"},
                    {"id": "c2", "name": "Paid Social", "priority": "high", "description": "Retarget engaged visitors"},
                    {"id": "c3", "name": "SEO", "priority": "medium", "description": "Capture search demand"},
                ],
                "budgetAllocation": [
                    {"channel": "Paid Social", "percentage": 40},
                    {"channel": "Email", "percentage": 20},
                    {"channel": "SEO & Content", "percentage": 25},
                    {"channel": "Influencers", "percentage": 15},
                ],
                "kpis": [
                    {"id": "k1", "metric": "Qualified leads", "target": "+30%", "timeframe": "Quarter 1"},
                    {"id": "k2", "metric": "Online conversion rate", "target": "3.5%", "timeframe": "Quarter 1"},
                    {"id": "k3", "metric": "Email list growth", "target": "+1,500", "timeframe": "Quarter 1"},
                ],
            },
            "customerPersona": {
                "name": "The Decision-Maker",
                "ageRange": "28-45",
                "location": request.country or "Global",
                "occupation": "Owner / team lead",
                "incomeLevel": "Mid-to-senior",
                "summary": (
                    f"A results-focused professional in {request.country or 'the target market'} "
                    "who values clarity, speed and measurable outcomes and is actively "
                    "looking for a better way to reach customers."
                ),
                "interests": ["Growth", "Automation", "Industry news"],
                "painPoints": ["Limited time", "Fragmented channels", "Hard to measure ROI"],
                "goals": list(request.goals),
                "preferredChannels": ["Email", "LinkedIn", "Search"],
                "buyingTriggers": ["Time savings", "Clear pricing", "Proven case studies"],
                "objections": ["Budget", "Switching cost", "Time to results"],
            },
            "swotAnalysis": {
                "strengths": ["Focused offer", "Fast time-to-value", "Agile team"],
                "weaknesses": ["Brand awareness", "Limited budget"],
                "opportunities": [
                    f"Growing {request.industry} demand",
                    "Under-served niche segments",
                    "Automation-driven efficiency",
                ],
                "threats": ["Established incumbents", "Price competition", "AI fatigue"],
                "overallAssessment": (
                    f"{request.project_name} can win by pairing a sharp value "
                    "proposition with disciplined channel execution and fast "
                    "measurement loops."
                ),
            },
            "marketOverview": {
                "summary": (
                    f"The {request.industry} market is growing steadily, driven by "
                    "digital adoption and shifting customer expectations. Competition "
                    "is fragmented, which leaves room for a focused, outcome-driven "
                    "player like {request.project_name}."
                ),
                "marketTrends": [
                    f"Continued growth in {request.industry} demand",
                    "Rise of personalized, automated customer journeys",
                    "Increased weight on measurable ROI in buying decisions",
                ],
                "targetMarketSize": "Estimated addressable market of $500M+",
                "growthRate": "8% year-over-year",
                "keyDrivers": [
                    "Digital transformation among buyers",
                    "Demand for faster time-to-value",
                    "Shift toward subscription and outcome-based models",
                ],
                "marketRisks": [
                    "Economic sensitivity in discretionary spending",
                    "Aggressive pricing from incumbents",
                ],
            },
            "seoKeywords": {
                "primaryKeywords": [
                    {"id": "s1", "keyword": f"{request.industry.lower()} strategy", "intent": "commercial", "priority": "high"},
                    {"id": "s2", "keyword": f"best {request.industry.lower()} tools", "intent": "commercial", "priority": "high"},
                ],
                "contentTopics": [
                    {"id": "t1", "title": f"5 ways to grow in {request.industry}", "funnelStage": "awareness"},
                    {"id": "t2", "title": "A 90-day growth plan", "funnelStage": "consideration"},
                ],
                "onPageRecommendations": [
                    "Optimize meta titles with target keywords",
                    "Add internal links from high-traffic pages",
                ],
            },
            "contentCalendar": {
                "timeframe": "Next 30 days",
                "cadence": "3 posts / week",
                "schedule": [
                    {"id": "d1", "date": "Week 1", "channel": "Blog", "topic": "Industry deep-dive", "cta": "Learn more"},
                    {"id": "d2", "date": "Week 1", "channel": "Email", "topic": "Welcome sequence", "cta": "Get started"},
                    {"id": "d3", "date": "Week 2", "channel": "LinkedIn", "topic": "Thought leadership", "cta": "Engage"},
                    {"id": "d4", "date": "Week 2", "channel": "Paid Social", "topic": "Offer teaser", "cta": "Claim offer"},
                    {"id": "d5", "date": "Week 3", "channel": "Blog", "topic": "Case study", "cta": "Read story"},
                    {"id": "d6", "date": "Week 4", "channel": "Email", "topic": "Monthly recap", "cta": "Next steps"},
                ],
            },
            "emailCampaign": {
                "campaignName": "Launch Nurture",
                "goal": "Convert cold subscribers into qualified leads",
                "audience": "New subscribers",
                "subjectLines": [
                    "The plan that fits your goals",
                    "Your growth roadmap, in one place",
                    "Start with a clear advantage",
                ],
                "sequence": [
                    {"id": "e1", "day": 0, "type": "Welcome", "subject": "Welcome to the plan"},
                    {"id": "e2", "day": 3, "type": "Value", "subject": "One tactic, three ways"},
                    {"id": "e3", "day": 7, "type": "Offer", "subject": "Your next step"},
                ],
            },
            "advertisementIdeas": {
                "summary": "Focused paid campaigns across Google and Meta that capture high-intent demand and retarget engaged audiences.",
                "campaigns": [
                    {
                        "id": "a1",
                        "name": "Search Capture",
                        "platform": "Google Ads",
                        "objective": "Capture high-intent search demand",
                        "audience": request.target_audience,
                        "budget": _budget_label(request),
                        "duration": "Ongoing",
                        "expectedOutcome": "Qualified clicks at a controlled cost",
                    },
                    {
                        "id": "a2",
                        "name": "Retargeting",
                        "platform": "Meta Ads",
                        "objective": "Convert engaged visitors",
                        "audience": "Website visitors, email openers",
                        "budget": _budget_label(request),
                        "duration": "30 days",
                        "expectedOutcome": "Improved conversion rate",
                    },
                ],
            },
            "socialMediaStrategy": {
                "summary": (
                    "A focused social presence on LinkedIn and Instagram that builds "
                    "authority, distributes content, and funnels engaged audiences "
                    "into the nurture sequence."
                ),
                "platforms": [
                    {
                        "id": "soc1",
                        "name": "LinkedIn",
                        "focus": "Thought leadership and B2B trust",
                        "postingCadence": "3x / week",
                        "contentMix": ["Industry insights", "Case studies", "Founder commentary"],
                        "goals": ["Build authority", "Drive profile visits to the funnel"],
                    },
                    {
                        "id": "soc2",
                        "name": "Instagram",
                        "focus": "Brand awareness and community",
                        "postingCadence": "4x / week",
                        "contentMix": ["Reels", "Carousels", "Behind the scenes"],
                        "goals": ["Grow following", "Surface offers to engaged users"],
                    },
                ],
                "communityManagement": [
                    "Respond to comments within 4 hours on business days",
                    "Weekly social listening for brand mentions and industry chatter",
                    "Highlight customer wins monthly to build social proof",
                ],
                "performanceMetrics": [
                    {"id": "socm1", "metric": "Engagement rate", "target": "4%"},
                    {"id": "socm2", "metric": "Profile clicks", "target": "+500 / month"},
                    {"id": "socm3", "metric": "Follower growth", "target": "+1,200 in 90 days"},
                ],
            },
            "competitorAnalysis": {
                "competitors": [
                    {
                        "id": "cp1",
                        "name": "Direct competitors",
                        "marketPosition": "Established",
                        "strengths": ["Brand", "Scale"],
                        "weaknesses": ["Slower to personalize", "Higher prices"],
                        "threatLevel": "medium",
                    }
                ],
                "competitiveAdvantages": ["Speed", "Personalization", "Transparent pricing"],
                "marketGaps": ["Under-served niche segments", "Simpler onboarding"],
                "keyTakeaways": [
                    "Differentiate on outcomes and speed",
                    "Target segments incumbents ignore",
                ],
            },
            "implementationRoadmap": {
                "summary": (
                    "A 90-day roadmap in three phases: Foundation, Momentum, and "
                    "Scale. Each phase has clear objectives, activities, and "
                    "success metrics."
                ),
                "phases": [
                    {
                        "id": "ph1",
                        "name": "Foundation",
                        "duration": "Days 1-30",
                        "objectives": [
                            "Stand up tracking and attribution",
                            "Launch the nurture email sequence",
                            "Publish the first SEO-optimized content",
                        ],
                        "keyActivities": [
                            "Set up analytics and conversion tracking",
                            "Configure the email platform and sequence",
                            "Ship two pillar blog posts and update meta tags",
                        ],
                        "successMetrics": [
                            "Analytics reporting all core events",
                            "Welcome sequence live",
                            "2 pillar posts published",
                        ],
                    },
                    {
                        "id": "ph2",
                        "name": "Momentum",
                        "duration": "Days 31-60",
                        "objectives": [
                            "Scale paid acquisition within targets",
                            "Grow the email list by 1,500 subscribers",
                            "Establish a 3x/week social cadence",
                        ],
                        "keyActivities": [
                            "Launch Google + Meta campaigns with structured testing",
                            "Run weekly A/B tests on ads and email sends",
                            "Post 3x/week on LinkedIn and Instagram",
                        ],
                        "successMetrics": [
                            "CPA within 20% of target",
                            "List growth at or above plan",
                            "Social engagement rate at 4%",
                        ],
                    },
                    {
                        "id": "ph3",
                        "name": "Scale",
                        "duration": "Days 61-90",
                        "objectives": [
                            "Double down on winning channels",
                            "Reach 3.5% conversion on optimized funnels",
                            "Deliver the first quarterly report",
                        ],
                        "keyActivities": [
                            "Shift budget to top-performing campaigns",
                            "Expand content to 4 pieces/week",
                            "Compile results, learnings, and next-quarter plan",
                        ],
                        "successMetrics": [
                            "Conversion rate at target",
                            "ROI at or above projection",
                            "Quarterly report delivered",
                        ],
                    },
                ],
            },
            "weeklyMilestones": {
                "summary": (
                    "Twelve weekly milestones keep execution accountable and "
                    "surface problems early."
                ),
                "weeks": [
                    {"id": "w1", "week": "Week 1", "focus": "Foundation setup", "tasks": ["Analytics + tracking live", "Email platform configured"], "owner": "Marketing lead", "successIndicator": "All core events reporting"},
                    {"id": "w2", "week": "Week 2", "focus": "Welcome sequence", "tasks": ["Write sequence copy", "Launch welcome email"], "owner": "Marketing lead", "successIndicator": "Welcome email sent to new subscribers"},
                    {"id": "w3", "week": "Week 3", "focus": "SEO content", "tasks": ["Publish pillar post 1", "Update meta titles"], "owner": "Content lead", "successIndicator": "First pillar post live"},
                    {"id": "w4", "week": "Week 4", "focus": "Ads launch", "tasks": ["Set up Google campaign", "Launch first Meta ad set"], "owner": "Ads manager", "successIndicator": "Campaigns delivering impressions"},
                    {"id": "w5", "week": "Week 5", "focus": "Social cadence", "tasks": ["Kick off 3x/week posting", "First monthly recap"], "owner": "Social manager", "successIndicator": "9 posts published"},
                    {"id": "w6", "week": "Week 6", "focus": "Optimization", "tasks": ["Review ad results", "A/B test subject lines"], "owner": "Ads manager", "successIndicator": "CPA within 20% of target"},
                    {"id": "w7", "week": "Week 7", "focus": "List growth", "tasks": ["Launch lead magnet", "Promote on social"], "owner": "Content lead", "successIndicator": "List growth at plan pace"},
                    {"id": "w8", "week": "Week 8", "focus": "Scale content", "tasks": ["Publish pillar post 2", "Add 2 supporting posts"], "owner": "Content lead", "successIndicator": "Content library growing on plan"},
                    {"id": "w9", "week": "Week 9", "focus": "Retargeting", "tasks": ["Launch retargeting campaigns", "Segment email list"], "owner": "Ads manager", "successIndicator": "Retargeting live"},
                    {"id": "w10", "week": "Week 10", "focus": "Conversion lift", "tasks": ["Optimize landing pages", "Run CRO experiments"], "owner": "Marketing lead", "successIndicator": "Conversion rate improving"},
                    {"id": "w11", "week": "Week 11", "focus": "Community", "tasks": ["Engagement sprints", "Customer spotlight"], "owner": "Social manager", "successIndicator": "Engagement rate at 4%"},
                    {"id": "w12", "week": "Week 12", "focus": "Reporting", "tasks": ["Compile 90-day results", "Draft next-quarter plan"], "owner": "Marketing lead", "successIndicator": "Quarterly report delivered"},
                ],
            },
            "estimatedROI": {
                "summary": (
                    "Based on the stated budget and channel mix, the plan is "
                    "projected to deliver positive ROI within the first 90 days."
                ),
                "assumptions": [
                    "Budget allocated per the recommended split",
                    "Average customer value holds steady",
                    "Conversion rates improve with ongoing optimization",
                ],
                "projections": [
                    {"id": "roi1", "period": "Month 1", "investment": "$3,000", "projectedReturn": "$2,400", "roiPercent": "-20%"},
                    {"id": "roi2", "period": "Month 2", "investment": "$3,500", "projectedReturn": "$4,900", "roiPercent": "40%"},
                    {"id": "roi3", "period": "Month 3", "investment": "$4,000", "projectedReturn": "$7,200", "roiPercent": "80%"},
                    {"id": "roi4", "period": "Quarter 2", "investment": "$4,500", "projectedReturn": "$10,800", "roiPercent": "140%"},
                ],
                "paybackPeriod": "Month 3",
                "methodology": (
                    "Projections assume the recommended budget allocation, "
                    "blended customer acquisition cost, and improving conversion "
                    "rates month over month."
                ),
            },
            "riskMitigation": {
                "summary": (
                    "The plan carries moderate execution risk, concentrated in "
                    "budget and channel performance. Each risk has a concrete "
                    "mitigation."
                ),
                "risks": [
                    {
                        "id": "rk1",
                        "risk": "Underperforming ad campaigns",
                        "category": "Execution",
                        "likelihood": "medium",
                        "impact": "high",
                        "mitigation": [
                            "Structured A/B testing from day one",
                            "Weekly budget reallocation to winning ad sets",
                        ],
                    },
                    {
                        "id": "rk2",
                        "risk": "Content production delays",
                        "category": "Capacity",
                        "likelihood": "medium",
                        "impact": "medium",
                        "mitigation": [
                            "Batch-create content one week ahead",
                            "Template-first approach for recurring formats",
                        ],
                    },
                    {
                        "id": "rk3",
                        "risk": "Budget overruns",
                        "category": "Budget",
                        "likelihood": "low",
                        "impact": "medium",
                        "mitigation": [
                            "Hard cap per campaign with daily pacing",
                            "Monthly budget review against ROI",
                        ],
                    },
                    {
                        "id": "rk4",
                        "risk": "Market shifts or new entrants",
                        "category": "Market",
                        "likelihood": "low",
                        "impact": "medium",
                        "mitigation": [
                            "Quarterly competitive review",
                            "Positioning refresh based on feedback",
                        ],
                    },
                ],
            },
            "finalRecommendations": {
                "summary": (
                    f"Execute the 90-day plan in order, keep measurement "
                    "continuous, and review the scorecard monthly. The priority is "
                    "to build the foundation, then scale what performs."
                ),
                "priorities": [
                    "Stand up analytics and attribution first",
                    "Launch the email nurture sequence within two weeks",
                    "Open Google + Meta campaigns by week four",
                ],
                "quickWins": [
                    "Publish the two pillar posts within the first month",
                    "Activate the welcome sequence to capture early list growth",
                    "Fix on-page SEO fundamentals on the highest-traffic pages",
                ],
                "longTermInvestments": [
                    "Deepen SEO content into a 4x/week cadence",
                    "Build out a referral or partnership channel",
                    "Invest in conversion-rate optimization after month two",
                ],
                "successCriteria": [
                    "Qualified leads up 30% by end of Quarter 1",
                    "Conversion rate at 3.5% by day 90",
                    "ROI positive by month three",
                ],
                "closingStatement": (
                    f"{request.project_name} has a clear, executable path to growth. "
                    "With disciplined execution of this plan, the first 90 days will "
                    "establish the measurement, channels, and momentum needed to scale."
                ),
            },
            "recommendedTools": {
                "summary": "A lean, affordable stack that covers analytics, email, social scheduling and SEO.",
                "tools": [
                    {"id": "r1", "name": "Google Analytics", "category": "analytics", "purpose": "Measure performance", "pricing": "Free", "difficulty": "easy", "recommendation": "recommended"},
                    {"id": "r2", "name": "Email platform", "category": "email-marketing", "purpose": "Send campaigns", "pricing": "From free", "difficulty": "easy", "recommendation": "recommended"},
                    {"id": "r3", "name": "SEO suite", "category": "seo", "purpose": "Track keywords", "pricing": "From $99/mo", "difficulty": "medium", "recommendation": "optional"},
                ],
            },
        }

        sections = self._build_sections(mock_doc)

        strategy_id = str(uuid.uuid4())
        if db is not None and user is not None:
            strategy_id = await self._persist(request, user, mock_doc, db)

        response = StrategyGenerationResponse(
            strategy_id=strategy_id,
            summary=(
                f"A {request.tone} {request.industry} strategy for "
                f"{request.project_name} targeting {request.target_audience}."
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
