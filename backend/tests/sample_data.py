"""Shared sample payloads for AI pipeline tests."""
import json

VALID_MARKETING_STRATEGY = {
    "executiveSummary": {
        "summary": "A focused growth plan for the coming quarter.",
        "highlights": ["Clear positioning", "Measurable KPIs"],
        "ask": "Approve and begin Phase 1.",
    },
    "marketingScore": {
        "overall": 74,
        "breakdown": [
            {"id": "ms1", "area": "Strategy", "score": 80, "assessment": "Solid plan."},
            {"id": "ms2", "area": "SEO", "score": 60, "assessment": "Needs content."},
            {"id": "ms3", "area": "Content", "score": 70, "assessment": "On track."},
            {"id": "ms4", "area": "Social", "score": 72, "assessment": "Good cadence."},
            {"id": "ms5", "area": "Email", "score": 84, "assessment": "Strong sequence."},
            {"id": "ms6", "area": "Ads", "score": 66, "assessment": "Optimize budgets."},
        ],
        "benchmark": "Industry average 60/100",
        "summary": "Above benchmark overall.",
    },
    "marketingStrategy": {
        "overview": "Test strategy",
        "objectives": ["Increase sales"],
        "positioning": "Premium",
        "keyMessages": ["Quality first"],
        "channels": [{"id": "c1", "name": "Instagram", "priority": "high"}],
        "budgetAllocation": [{"channel": "Instagram", "percentage": 100}],
        "kpis": [{"id": "k1", "metric": "Sales", "target": "+20%"}],
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
        "objections": ["Price"],
    },
    "swotAnalysis": {
        "strengths": ["Quality"],
        "weaknesses": ["Small team"],
        "opportunities": ["Online growth"],
        "threats": ["Big brands"],
        "overallAssessment": "Positioned to grow.",
    },
    "marketOverview": {
        "summary": "A growing, fragmented market.",
        "marketTrends": ["Digital adoption"],
        "targetMarketSize": "$500M",
        "growthRate": "8% YoY",
        "keyDrivers": ["Convenience"],
        "marketRisks": ["Price competition"],
    },
    "seoKeywords": {
        "primaryKeywords": [
            {"id": "k1", "keyword": "coffee beans", "intent": "commercial", "priority": "high"}
        ],
        "secondaryKeywords": [
            {"id": "k2", "keyword": "specialty coffee", "intent": "informational"}
        ],
        "longTailKeywords": [
            {"id": "k3", "keyword": "best coffee for home", "intent": "commercial"}
        ],
        "contentTopics": [
            {
                "id": "t1",
                "title": "How to brew",
                "targetKeyword": "coffee beans",
                "funnelStage": "consideration",
            }
        ],
        "onPageRecommendations": ["Improve meta titles"],
    },
    "contentCalendar": {
        "timeframe": "30 days",
        "cadence": "3 posts/week",
        "schedule": [
            {
                "id": "d1",
                "date": "2026-08-01",
                "channel": "Instagram",
                "contentFormat": "Reel",
                "topic": "Brewing tips",
                "cta": "Shop now",
            }
        ],
    },
    "advertisementIdeas": {
        "summary": "Run Meta ads",
        "campaigns": [
            {
                "id": "a1",
                "name": "Launch",
                "platform": "Meta Ads",
                "objective": "Sales",
                "audience": "Coffee lovers",
                "budget": "$2k",
                "duration": "3 weeks",
                "adCopy": [
                    {
                        "id": "c1",
                        "headline": "Fresh beans",
                        "description": "Taste the difference",
                        "cta": "Buy",
                    }
                ],
                "targetingSuggestions": ["Interests: coffee"],
                "expectedOutcome": "3k clicks",
            }
        ],
    },
    "emailCampaign": {
        "campaignName": "Welcome series",
        "goal": "Onboard",
        "audience": "New subscribers",
        "subjectLines": ["Welcome!"],
        "preheader": "Hello",
        "sequence": [
            {
                "id": "e1",
                "day": 0,
                "type": "Welcome",
                "subject": "Welcome to Acme",
                "previewText": "Hi",
                "bodySections": [{"heading": "Hi", "content": "Welcome"}],
                "cta": "Shop",
            }
        ],
    },
    "socialMediaStrategy": {
        "summary": "Focused social presence.",
        "platforms": [
            {
                "id": "soc1",
                "name": "Instagram",
                "focus": "Awareness",
                "postingCadence": "4x/week",
                "contentMix": ["Reels"],
                "goals": ["Grow followers"],
            }
        ],
        "communityManagement": ["Reply within 4h"],
        "performanceMetrics": [{"id": "m1", "metric": "Engagement", "target": "4%"}],
    },
    "competitorAnalysis": {
        "competitors": [
            {
                "id": "cp1",
                "name": "Blue Bottle",
                "marketPosition": "Leader",
                "strengths": ["Brand"],
                "weaknesses": ["Price"],
                "pricing": "Premium",
                "differentiators": ["Stores"],
                "threatLevel": "high",
            }
        ],
        "competitiveAdvantages": ["Direct trade"],
        "marketGaps": ["Home delivery"],
        "keyTakeaways": ["Win on delivery"],
    },
    "implementationRoadmap": {
        "summary": "Three phases over 90 days.",
        "phases": [
            {
                "id": "ph1",
                "name": "Foundation",
                "duration": "Days 1-30",
                "objectives": ["Stand up tracking"],
                "keyActivities": ["Set up analytics"],
                "successMetrics": ["Tracking live"],
            }
        ],
    },
    "weeklyMilestones": {
        "summary": "Twelve weekly milestones.",
        "weeks": [
            {
                "id": "w1",
                "week": "Week 1",
                "focus": "Setup",
                "tasks": ["Configure analytics"],
                "owner": "Marketing lead",
                "successIndicator": "Tracking live",
            }
        ],
    },
    "estimatedROI": {
        "summary": "Positive ROI by month three.",
        "assumptions": ["Budget per plan"],
        "projections": [
            {"id": "r1", "period": "Month 1", "investment": "$3k", "projectedReturn": "$2.4k", "roiPercent": "-20%"},
            {"id": "r2", "period": "Month 2", "investment": "$3.5k", "projectedReturn": "$4.9k", "roiPercent": "40%"},
        ],
        "paybackPeriod": "Month 3",
        "methodology": "Based on blended CAC.",
    },
    "riskMitigation": {
        "summary": "Moderate execution risk.",
        "risks": [
            {
                "id": "rk1",
                "risk": "Ad underperformance",
                "category": "Execution",
                "likelihood": "medium",
                "impact": "high",
                "mitigation": ["A/B testing"],
            }
        ],
    },
    "finalRecommendations": {
        "summary": "Execute in order.",
        "priorities": ["Stand up tracking"],
        "quickWins": ["Fix on-page SEO"],
        "longTermInvestments": ["Build content engine"],
        "successCriteria": ["Leads +30%"],
        "closingStatement": "Disciplined execution wins.",
    },
    "recommendedTools": {
        "summary": "Lean stack",
        "tools": [
            {
                "id": "tl1",
                "name": "Notion",
                "category": "project-management",
                "purpose": "Planning",
                "pricing": "Free",
                "difficulty": "easy",
                "recommendation": "recommended",
            }
        ],
    },
    "businessAnalysis": {
        "overview": "A focused offer in the coffee market with room to dominate the local niche.",
        "strengths": ["Focused offer", "Local presence", "Clear audience"],
        "growthLevers": ["Local SEO", "Delivery apps", "Referral program"],
        "immediateWins": ["Claim listings", "Launch social", "Publish content"],
    },
    "marketingFunnel": {
        "summary": "A funnel that moves customers from awareness to repeat purchase.",
        "stages": [
            {"id": "f1", "stage": "Awareness", "tactics": ["Instagram Reels", "Local SEO", "Food influencers"]},
            {"id": "f2", "stage": "Consideration", "tactics": ["Reviews", "Comparison content", "Email drops"]},
            {"id": "f3", "stage": "Conversion", "tactics": ["Limited-time offers", "Easy ordering"]},
            {"id": "f4", "stage": "Retention", "tactics": ["Loyalty program", "Re-engagement emails"]},
        ],
    },
    "influencerStrategy": {
        "summary": "Partner with local food creators to build trust.",
        "tiers": [
            {"tier": "Micro", "strategy": "Local foodies with engaged audiences"},
            {"tier": "Mid", "strategy": "Regional voices for broader reach"},
        ],
        "campaignIdeas": ["Unboxing of the signature blend", "A day-in-the-life feature", "Referral discount codes"],
    },
    "growthOpportunities": {
        "summary": "Untapped angles for growth.",
        "opportunities": [
            {"id": "g1", "name": "Delivery-app dominance", "why": "Under-used by competitors", "effort": "low", "impact": "high"},
            {"id": "g2", "name": "Niche specialization", "why": "Segment competitors ignore", "effort": "medium", "impact": "high"},
        ],
    },
    "futureScaling": {
        "summary": "Scale beyond the first 90 days.",
        "phases": [
            {"phase": "3-6 months", "focus": "Double down on top channels"},
            {"phase": "6-12 months", "focus": "Expand to nearby cities"},
        ],
        "scaleLevers": ["Team", "Automation", "New channels", "Partnerships"],
    },
}

# Raw LLM-style payload for providers/fake providers to return.
VALID_MARKETING_STRATEGY_JSON = json.dumps(VALID_MARKETING_STRATEGY)
