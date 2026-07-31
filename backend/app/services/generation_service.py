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

        strategy = result.get("marketingStrategy") or {}
        add("Executive Summary", strategy.get("overview"))
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
        )

        logger.info(
            "Strategy generated strategy_id=%s sections=%d",
            response.strategy_id,
            len(response.sections),
        )
        return response
