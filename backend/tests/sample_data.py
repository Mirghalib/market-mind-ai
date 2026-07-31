"""Shared sample payloads for AI pipeline tests."""
import json

VALID_MARKETING_STRATEGY = {
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
}

# Raw LLM-style payload for providers/fake providers to return.
VALID_MARKETING_STRATEGY_JSON = json.dumps(VALID_MARKETING_STRATEGY)
