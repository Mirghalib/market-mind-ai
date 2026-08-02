"""Input-driven deterministic mock strategy.

Used when no LLM provider is configured (offline demos, CI, rate-limit
fallback). Unlike the old single generic mock, this one is driven by the
business inputs: the industry playbook picks channels/ads/content/KPIs,
the country profile picks local platforms, the currency formats every
budget/ROI figure, and the persona/SEO/calendar are built from the
business name + industry + audience. Different inputs produce different
strategies, so Restaurant (PK) != SaaS (US) != Gym (AE).
"""
from __future__ import annotations

from app.services.ai.country_profiles import profile_for_country
from app.services.ai.currencies import currency_for_country, format_budget
from app.services.ai.industry_playbooks import match_playbook

def _city(country: str) -> str:
    """A plausible major city per country for local SEO strings."""
    cities = {
        "pakistan": "Karachi",
        "india": "Mumbai",
        "united states": "Austin",
        "usa": "Austin",
        "united kingdom": "London",
        "uk": "London",
        "uae": "Dubai",
        "united arab emirates": "Dubai",
        "saudi arabia": "Riyadh",
        "canada": "Toronto",
        "australia": "Sydney",
        "germany": "Berlin",
        "france": "Paris",
        "brazil": "São Paulo",
        "mexico": "Mexico City",
        "nigeria": "Lagos",
        "japan": "Tokyo",
        "singapore": "Singapore",
    }
    return cities.get((country or "").strip().lower(), "your city")


def build_mock_strategy(request) -> dict:
    """Build a deterministic but input-unique strategy document."""
    playbook = match_playbook(request.industry)
    country_profile = profile_for_country(request.country)
    country = request.country or "Global"
    city = _city(country)
    industry = request.industry
    business = request.project_name
    product = request.product or business
    audience = request.target_audience

    symbol = request.currency_symbol or currency_for_country(request.country)[1]
    code = request.currency_code or currency_for_country(request.country)[0]
    period = request.budget_period or "month"
    budget_amount = _resolve_amount(request)
    budget_label = format_budget(budget_amount, symbol, code, period)

    # Currency-formatted ROI figures.
    monthly = budget_amount / 3  # per-month slice of a 90-day plan
    roi_invest = [
        format_budget(monthly * m, symbol, code, None) for m in (1, 1.15, 1.3, 1.45)
    ]
    roi_return = [
        format_budget(monthly * r, symbol, code, None)
        for r in (0.8, 1.6, 2.3, 3.4)
    ]
    roi_pct = ["-20%", "40%", "75%", "130%"]

    channels = playbook["channels"]
    # Merge country platforms as additional recommended channels.
    country_platforms = country_profile.get("platforms", [])
    all_channels = list(dict.fromkeys(channels + country_platforms))[:6]

    budget_split = _budget_split(all_channels)

    platform_names = playbook["social_platforms"]
    content_mix = playbook["content_types"]
    influencer_tiers = playbook["influencers"]
    kpis = playbook["kpis"]

    seo_terms = _seo_terms(playbook, business, industry, city, product)

    goals = list(request.goals) or ["Grow the business"]
    competitors = list(request.competitors) or ["Local incumbents"]

    return {
        "metadata": {
            "country": country,
            "industry": industry,
            "product": product,
            "currency_code": code,
            "currency_symbol": symbol,
            "budget_amount": budget_amount,
            "budget_period": period,
            "budget_label": budget_label,
        },
        "executiveSummary": {
            "summary": (
                f"{business} is entering the {industry} market in {country} with a focused "
                f"90-day plan built around {', '.join(all_channels[:3])}. This strategy "
                "prioritizes the channels that actually convert for this industry, a "
                "measurable scorecard, and fast execution."
            ),
            "highlights": [
                f"Industry-specific channel mix: {', '.join(all_channels[:3])}",
                f"Country-aware approach for {country} using {', '.join(country_platforms[:2])}",
                f"A {budget_label} budget with a clear allocation and ROI plan",
            ],
            "ask": "Approve the plan and begin Phase 1 this week to start capturing demand.",
        },
        "businessAnalysis": {
            "overview": (
                f"{business} offers {product} to {audience} in {country}. The core growth "
                f"opportunity is to dominate the {industry} niche locally while building "
                "repeatable acquisition through the channels in this plan."
            ),
            "strengths": [
                f"Focused offer in {industry}",
                f"Local presence in {country}",
                f"Clear audience: {audience}",
            ],
            "growthLevers": playbook["tactics"][:4],
            "immediateWins": [
                f"Claim and optimize local listings in {city}",
                f"Launch {', '.join(all_channels[:2])} campaigns this week",
                "Publish the first two content pieces within 14 days",
            ],
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
            "benchmark": f"Industry average for {industry} SMBs is 60/100",
            "summary": (
                f"{business} is above the typical benchmark for its segment. The biggest "
                "near-term gains come from executing the industry playbook channels."
            ),
        },
        "marketingStrategy": {
            "overview": (
                f"{business} is entering the {industry} market in {country}. This plan "
                f"prioritizes {', '.join(all_channels[:4])} — the channels that work for "
                f"{industry} businesses — with a {budget_label} budget."
            ),
            "objectives": goals,
            "positioning": playbook["positioning"],
            "keyMessages": [
                f"Built for {audience}",
                f"The trusted {industry} choice in {country}",
                "Clear results from week one",
            ],
            "channels": [
                {"id": f"c{i}", "name": ch, "priority": "high" if i < 3 else "medium",
                 "description": f"{playbook['tactics'][i % len(playbook['tactics'])]}"}
                for i, ch in enumerate(all_channels[:5])
            ],
            "budgetAllocation": [
                {"channel": ch, "percentage": pct} for ch, pct in budget_split
            ],
            "kpis": [
                {"id": f"k{i}", "metric": kpi, "target": "+30%", "timeframe": "Quarter 1"}
                for i, kpi in enumerate(kpis[:3])
            ],
        },
        "customerPersona": {
            "name": f"The {industry} Buyer",
            "ageRange": "25-45",
            "location": city,
            "occupation": "Owner / decision-maker",
            "incomeLevel": "Mid-to-senior",
            "summary": (
                f"A {industry} customer in {city} who values quality, trust and "
                f"convenience, and is actively looking for the best {product} option."
            ),
            "interests": [f"{industry} trends", "Local events", "Quality products"],
            "painPoints": ["Hard to find a trusted option", "Limited time", "Price sensitivity"],
            "goals": goals,
            "preferredChannels": all_channels[:4],
            "buyingTriggers": ["Strong reviews", "Recommendations", "Special offers"],
            "objections": ["Budget", "Trust in a new provider", "Time to results"],
        },
        "swotAnalysis": {
            "strengths": [f"Focused {industry} offer", f"Local presence in {city}", "Agile execution"],
            "weaknesses": ["Brand awareness", "Limited budget"],
            "opportunities": [
                f"Growing {industry} demand in {country}",
                "Under-served niche segments",
                f"{', '.join(country_platforms[:2])} reach",
            ],
            "threats": ["Established incumbents", "Price competition", "Market noise"],
            "overallAssessment": (
                f"{business} can win by pairing a sharp value proposition with "
                f"disciplined execution of the {industry} playbook channels."
            ),
        },
        "marketOverview": {
            "summary": (
                f"The {industry} market in {country} is growing, driven by digital "
                "adoption and shifting customer expectations. Competition is fragmented, "
                f"leaving room for a focused player like {business}."
            ),
            "marketTrends": [
                f"Growth in {industry} demand across {country}",
                "Rise of mobile and social discovery",
                "Increasing weight on reviews and social proof",
            ],
            "targetMarketSize": f"Estimated addressable market in {country}: {symbol} {max(budget_amount * 40, 500000):,.0f}+",
            "growthRate": "8% year-over-year",
            "keyDrivers": ["Digital adoption", "Demand for convenience", "Social proof"],
            "marketRisks": ["Economic sensitivity", "Aggressive pricing", "Market noise"],
        },
        "seoKeywords": {
            "primaryKeywords": [
                {"id": "s1", "keyword": seo_terms[0], "intent": "commercial", "priority": "high", "volume": "4.5K", "difficulty": "Medium"},
                {"id": "s2", "keyword": seo_terms[1], "intent": "commercial", "priority": "high", "volume": "3.1K", "difficulty": "Medium"},
                {"id": "s3", "keyword": seo_terms[2], "intent": "transactional", "priority": "medium", "volume": "2.2K", "difficulty": "Low"},
            ],
            "secondaryKeywords": [
                {"id": "s4", "keyword": seo_terms[3], "intent": "informational"},
            ],
            "longTailKeywords": [
                {"id": "s5", "keyword": f"best {product} {city}", "intent": "commercial"},
            ],
            "contentTopics": [
                {"id": "t1", "title": f"How to choose the right {product} in {city}", "targetKeyword": seo_terms[0], "funnelStage": "awareness"},
                {"id": "t2", "title": f"5 ways {industry} businesses grow in {country}", "targetKeyword": seo_terms[1], "funnelStage": "consideration"},
                {"id": "t3", "title": f"{business}: a {city} {industry} success story", "targetKeyword": seo_terms[2], "funnelStage": "conversion"},
            ],
            "onPageRecommendations": [
                "Optimize meta titles with target keywords",
                "Add internal links from high-traffic pages",
                "Add local schema markup for " + city,
            ],
        },
        "contentCalendar": {
            "timeframe": "Next 30 days",
            "cadence": "3 posts / week",
            "schedule": [
                {"id": "d1", "date": "Week 1", "channel": platform_names[0], "contentFormat": "Reel", "topic": f"Meet {business}", "cta": "Follow"},
                {"id": "d2", "date": "Week 1", "channel": "Blog", "contentFormat": "Article", "topic": f"How to choose {product}", "cta": "Read"},
                {"id": "d3", "date": "Week 2", "channel": platform_names[0], "contentFormat": "Carousel", "topic": "Customer wins", "cta": "Share"},
                {"id": "d4", "date": "Week 2", "channel": "Email", "contentFormat": "Email", "topic": "Welcome + offer", "cta": "Claim"},
                {"id": "d5", "date": "Week 3", "channel": platform_names[1], "contentFormat": "Video", "topic": "Behind the scenes", "cta": "Engage"},
                {"id": "d6", "date": "Week 4", "channel": "Email", "contentFormat": "Email", "topic": "Monthly recap", "cta": "Next steps"},
            ],
        },
        "emailCampaign": {
            "campaignName": f"{business} Welcome & Nurture",
            "goal": "Convert new subscribers into customers",
            "audience": "New subscribers and inquirers",
            "subjectLines": [
                f"Welcome to {business}",
                "Your next step, in one place",
                "Start with a clear advantage",
            ],
            "preheader": f"The {industry} plan for {audience}",
            "sequence": [
                {"id": "e1", "day": 0, "type": "Welcome", "subject": f"Welcome to {business}", "previewText": "Here's what to expect", "bodySections": [{"heading": "Welcome", "content": "Thanks for choosing us"}], "cta": "Get started"},
                {"id": "e2", "day": 3, "type": "Value", "subject": "One tactic, three ways", "previewText": "Quick wins", "bodySections": [{"heading": "Tip", "content": "A fast win"}], "cta": "Learn more"},
                {"id": "e3", "day": 7, "type": "Offer", "subject": "Your next step", "previewText": "A special offer", "bodySections": [{"heading": "Offer", "content": "Limited-time offer"}], "cta": "Claim offer"},
            ],
        },
        "advertisementIdeas": {
            "summary": (
                f"Focused paid campaigns on {', '.join(playbook['ad_platforms'][:2])} "
                f"that capture high-intent demand in {country}."
            ),
            "campaigns": [
                {
                    "id": "a1",
                    "name": f"{industry} Intent Capture",
                    "platform": playbook["ad_platforms"][0],
                    "objective": "Capture high-intent search demand",
                    "audience": audience,
                    "budget": format_budget(budget_amount * 0.4, symbol, code, None),
                    "duration": "Ongoing",
                    "adCopy": [
                        {"id": "c1", "headline": f"The best {product} in {city}", "description": "Trusted by local customers", "cta": "Learn more"},
                        {"id": "c2", "headline": f"Top-rated {industry} choice", "description": "See why customers choose us", "cta": "Book now"},
                    ],
                    "targetingSuggestions": [f"People near {city}", f"{industry}-related interests"],
                    "expectedOutcome": "Qualified clicks at a controlled cost",
                },
                {
                    "id": "a2",
                    "name": "Local Retargeting",
                    "platform": playbook["ad_platforms"][1],
                    "objective": "Convert engaged visitors",
                    "audience": "Website visitors, social engagers",
                    "budget": format_budget(budget_amount * 0.3, symbol, code, None),
                    "duration": "30 days",
                    "adCopy": [
                        {"id": "c3", "headline": "Still thinking about it?", "description": "Here's a reason to act", "cta": "Claim offer"},
                    ],
                    "targetingSuggestions": ["Website visitors", "Instagram engagers"],
                    "expectedOutcome": "Improved conversion rate",
                },
            ],
        },
        "socialMediaStrategy": {
            "summary": (
                f"A {industry}-focused social presence on {', '.join(platform_names[:2])} "
                f"that builds trust and funnels engaged audiences into the nurture sequence."
            ),
            "platforms": [
                {"id": "soc1", "name": platform_names[0], "focus": "Brand and community", "postingCadence": "4x / week", "contentMix": content_mix[:3], "goals": ["Grow following", "Surface offers"]},
                {"id": "soc2", "name": platform_names[1], "focus": "Authority and trust", "postingCadence": "3x / week", "contentMix": content_mix[2:], "goals": ["Build authority", "Drive engagement"]},
            ],
            "communityManagement": [
                "Respond to comments within 4 hours on business days",
                "Weekly social listening for brand mentions",
                "Highlight customer wins monthly",
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
                    "name": competitors[0],
                    "marketPosition": "Established",
                    "strengths": ["Brand", "Scale"],
                    "weaknesses": ["Slower to personalize", "Higher prices"],
                    "pricing": "Market rate",
                    "differentiators": ["Legacy reputation"],
                    "threatLevel": "medium",
                }
            ],
            "competitiveAdvantages": ["Speed", "Personalization", "Local focus"],
            "marketGaps": ["Under-served niche segments", "Better customer experience"],
            "keyTakeaways": [
                "Differentiate on outcomes and speed",
                "Target segments incumbents ignore",
            ],
        },
        "implementationRoadmap": {
            "summary": (
                "A 90-day roadmap in three phases: Foundation, Momentum, and Scale. "
                "Each phase has clear objectives, activities, and success metrics."
            ),
            "phases": [
                {
                    "id": "ph1",
                    "name": "Foundation",
                    "duration": "Days 1-30",
                    "objectives": ["Stand up tracking and attribution", f"Launch {all_channels[0]} campaigns", "Publish first content"],
                    "keyActivities": ["Set up analytics", f"Configure {all_channels[0]} campaigns", "Ship two content pieces"],
                    "successMetrics": ["Analytics reporting core events", "Campaigns live", "2 pieces published"],
                },
                {
                    "id": "ph2",
                    "name": "Momentum",
                    "duration": "Days 31-60",
                    "objectives": ["Scale acquisition within targets", "Grow the audience", "Establish social cadence"],
                    "keyActivities": ["Scale winning campaigns", "Run weekly A/B tests", "Post consistently"],
                    "successMetrics": ["CPA within 20% of target", "Audience growing", "Engagement at 4%"],
                },
                {
                    "id": "ph3",
                    "name": "Scale",
                    "duration": "Days 61-90",
                    "objectives": ["Double down on winners", "Optimize conversion", "Deliver quarterly report"],
                    "keyActivities": ["Shift budget to top campaigns", "Expand content cadence", "Compile results"],
                    "successMetrics": ["Conversion at target", "ROI at or above projection", "Quarterly report delivered"],
                },
            ],
        },
        "weeklyMilestones": {
            "summary": "Twelve weekly milestones keep execution accountable.",
            "weeks": [
                {"id": f"w{i}", "week": f"Week {i}", "focus": _week_focus(i, all_channels), "tasks": [f"Execute {all_channels[i % len(all_channels)]} plan"], "owner": "Marketing lead", "successIndicator": f"{all_channels[i % len(all_channels)]} on track"}
                for i in range(1, 13)
            ],
        },
        "estimatedROI": {
            "summary": (
                f"Based on a {budget_label} budget and the {industry} channel mix, the "
                "plan is projected to deliver positive ROI within the first 90 days."
            ),
            "assumptions": [
                f"Budget allocated per the {industry} split",
                "Average customer value holds steady",
                "Conversion rates improve with optimization",
            ],
            "projections": [
                {"id": "roi1", "period": "Month 1", "investment": roi_invest[0], "projectedReturn": roi_return[0], "roiPercent": roi_pct[0]},
                {"id": "roi2", "period": "Month 2", "investment": roi_invest[1], "projectedReturn": roi_return[1], "roiPercent": roi_pct[1]},
                {"id": "roi3", "period": "Month 3", "investment": roi_invest[2], "projectedReturn": roi_return[2], "roiPercent": roi_pct[2]},
                {"id": "roi4", "period": "Quarter 2", "investment": roi_invest[3], "projectedReturn": roi_return[3], "roiPercent": roi_pct[3]},
            ],
            "paybackPeriod": "Month 3",
            "methodology": (
                "Projections assume the recommended budget allocation, blended "
                "customer acquisition cost, and improving conversion rates."
            ),
        },
        "riskMitigation": {
            "summary": "The plan carries moderate execution risk, concentrated in budget and channel performance.",
            "risks": [
                {"id": "rk1", "risk": "Underperforming ad campaigns", "category": "Execution", "likelihood": "medium", "impact": "high", "mitigation": ["Structured A/B testing", "Weekly budget reallocation"]},
                {"id": "rk2", "risk": "Content production delays", "category": "Capacity", "likelihood": "medium", "impact": "medium", "mitigation": ["Batch-create content", "Template-first approach"]},
                {"id": "rk3", "risk": "Budget overruns", "category": "Budget", "likelihood": "low", "impact": "medium", "mitigation": ["Hard cap per campaign", "Monthly budget review"]},
                {"id": "rk4", "risk": "Market shifts or new entrants", "category": "Market", "likelihood": "low", "impact": "medium", "mitigation": ["Quarterly competitive review", "Positioning refresh"]},
            ],
        },
        "finalRecommendations": {
            "summary": (
                f"Execute the 90-day plan in order. The priority is to build the "
                f"foundation across {', '.join(all_channels[:3])}, then scale what performs."
            ),
            "priorities": [
                "Stand up analytics and attribution first",
                f"Launch {all_channels[0]} within two weeks",
                "Open paid campaigns by week four",
            ],
            "quickWins": playbook["tactics"][:3],
            "longTermInvestments": [
                "Deepen content into a consistent cadence",
                "Build a referral or partnership channel",
                "Invest in conversion optimization after month two",
            ],
            "successCriteria": [
                "Qualified leads up 30% by end of Quarter 1",
                "Conversion at target by day 90",
                "ROI positive by month three",
            ],
            "closingStatement": (
                f"{business} has a clear, executable path to growth in {country}. "
                "With disciplined execution of this plan, the first 90 days will "
                "establish the measurement, channels, and momentum needed to scale."
            ),
        },
        "recommendedTools": {
            "summary": "A lean, affordable stack that covers analytics, email, social scheduling and SEO.",
            "tools": [
                {"id": "r1", "name": "Google Analytics", "category": "analytics", "purpose": "Measure performance", "pricing": "Free", "difficulty": "easy", "recommendation": "recommended"},
                {"id": "r2", "name": "Email platform", "category": "email-marketing", "purpose": "Send campaigns", "pricing": "From free", "difficulty": "easy", "recommendation": "recommended"},
                {"id": "r3", "name": "SEO suite", "category": "seo", "purpose": "Track keywords", "pricing": "From market rate", "difficulty": "medium", "recommendation": "optional"},
            ],
        },
        "businessAnalysis": {
            "overview": (
                f"{business} offers {product} to {audience} in {country}. The core growth "
                f"opportunity is to dominate the {industry} niche locally while building "
                "repeatable acquisition through the channels in this plan."
            ),
            "strengths": [
                f"Focused offer in {industry}",
                f"Local presence in {country}",
                f"Clear audience: {audience}",
            ],
            "growthLevers": playbook["tactics"][:4],
            "immediateWins": [
                f"Claim and optimize local listings in {city}",
                f"Launch {', '.join(all_channels[:2])} campaigns this week",
                "Publish the first two content pieces within 14 days",
            ],
        },
        "marketingFunnel": {
            "summary": (
                f"A {industry} funnel that moves {audience} from awareness to repeat "
                f"customers using {', '.join(all_channels[:3])}."
            ),
            "stages": [
                {"id": "f1", "stage": "Awareness", "tactics": [f"{', '.join(platform_names[:2])} content", f"{', '.join(country_platforms[:2])} reach", "Local SEO"]},
                {"id": "f2", "stage": "Interest", "tactics": ["Educational content", "Social proof posts", "Behind-the-scenes"]},
                {"id": "f3", "stage": "Consideration", "tactics": ["Reviews and testimonials", "Comparison content", "Email value drops"]},
                {"id": "f4", "stage": "Conversion", "tactics": [f"Paid campaigns on {', '.join(playbook['ad_platforms'][:2])}", "Limited-time offers", "Easy booking/ordering"]},
                {"id": "f5", "stage": "Retention", "tactics": ["Loyalty program", "Re-engagement emails", "Referral rewards"]},
            ],
        },
        "influencerStrategy": {
            "summary": (
                f"Partner with {', '.join(influencer_tiers[:2])} to build trust and "
                f"reach the right audience in {city}."
            ),
            "tiers": [
                {"tier": "Micro", "strategy": f"Local {industry} creators with engaged audiences"},
                {"tier": "Mid", "strategy": "Regional voices for broader reach and credibility"},
            ],
            "campaignIdeas": [
                f"{' '.join(influencer_tiers[:1])} unboxing/review of {product}",
                f"A day-in-the-life feature with {business} in {city}",
                "A referral discount code shared by creators",
            ],
        },
        "growthOpportunities": {
            "summary": (
                f"Untapped angles for {business} in the {industry} market of {country}."
            ),
            "opportunities": [
                {"id": "g1", "name": f"{', '.join(country_platforms[:2])} first-mover advantage", "why": "These platforms dominate locally and are under-used by competitors", "effort": "low", "impact": "high"},
                {"id": "g2", "name": "Niche specialization", "why": f"Focus on a specific {industry} segment competitors ignore", "effort": "medium", "impact": "high"},
                {"id": "g3", "name": "Referral engine", "why": "Word-of-mouth converts strongly in local markets", "effort": "low", "impact": "medium"},
            ],
        },
        "futureScaling": {
            "summary": (
                f"After the first 90 days, {business} can scale by doubling winning "
                "channels, expanding geography, and adding capacity."
            ),
            "phases": [
                {"phase": "3-6 months", "focus": "Double down on top channels and add a second location/vertical"},
                {"phase": "6-12 months", "focus": "Expand to nearby cities and deepen content authority"},
                {"phase": "12+ months", "focus": "Add team capacity, automation, and new product lines"},
            ],
            "scaleLevers": ["Team and hiring", "Automation tools", "New channels", "New geographies", "Partnerships"],
        },
    }


def _resolve_amount(request) -> float:
    if request.budget_amount is not None:
        return max(float(request.budget_amount), 500.0)
    # Fall back to parsing the human label, then a default.
    text = (request.budget or "").lower()
    digits = [d for d in __import__("re").findall(r"[\d,.]+", text)]
    if not digits:
        return 10_000.0
    value = float(digits[0].replace(",", ""))
    if "k" in text:
        value *= 1000
    if "m" in text and "k" not in text:
        value *= 1_000_000
    return max(value, 500.0)


def _seo_terms(playbook: dict, business: str, industry: str, city: str, product: str) -> list[str]:
    template = playbook.get("seo_terms") or ["best {industry} {city}"]
    terms = []
    for t in template[:4]:
        terms.append(
            t.replace("{product}", product.lower())
            .replace("{industry}", industry.lower())
            .replace("{city}", city)
            .replace("{business}", business)
            .replace("{country}", "")
            .strip()
        )
    return terms or [f"{industry.lower()} near me"]


def _budget_split(channels: list[str]) -> list[tuple[str, int]]:
    """A deterministic percentage split that sums to 100."""
    n = len(channels) or 1
    weights = [max(40 - i * 6, 10) for i in range(n)]
    total = sum(weights)
    splits = [round(w * 100 / total) for w in weights]
    # Fix rounding drift so it sums to exactly 100.
    diff = 100 - sum(splits)
    splits[0] += diff
    return list(zip(channels, splits))


def _week_focus(week: int, channels: list[str]) -> str:
    focuses = [
        "Foundation setup", "First campaign live", "Content kickoff", "Optimization",
        "Social cadence", "Email nurture", "List growth", "Retargeting", "Conversion lift",
        "Community", "Reporting prep", "Quarterly report",
    ]
    return focuses[(week - 1) % len(focuses)]
