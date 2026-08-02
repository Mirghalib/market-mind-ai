"""Render a sample PDF with rich content to visually verify the new design."""
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.marketing_strategy import MarketingStrategy, StrategyStatus
from app.services.export.renderers import PdfRenderer

CONTENT = {
    "executiveSummary": {
        "summary": "Resham & Co. is a fashion boutique ready to scale digital presence.",
        "highlights": ["Strong brand loyalty", "Untapped Instagram audience"],
        "ask": "Invest 60% of budget into Meta ads and 40% into content.",
    },
    "marketingScore": {
        "overall": 74,
        "summary": "Solid foundation with clear growth headroom.",
        "benchmark": "Industry avg 62",
        "breakdown": [
            {"area": "Branding", "score": 82, "assessment": "Strong"},
            {"area": "SEO", "score": 55, "assessment": "Needs work"},
            {"area": "Social", "score": 68, "assessment": "Growing"},
        ],
    },
    "marketOverview": {
        "summary": "The boutique fashion market is expanding 12% YoY.",
        "targetMarketSize": "$3.2B",
        "growthRate": "12%",
        "marketTrends": ["Sustainable fashion", "AI styling tools"],
        "keyDrivers": ["Millennial spend", "Social commerce"],
        "marketRisks": ["Fast fashion competition"],
    },
    "customerPersona": {
        "name": "Aisha", "ageRange": "25-34", "location": "Karachi",
        "occupation": "Marketing manager", "incomeLevel": "$40-60k",
        "summary": "Style-conscious professional who shops on Instagram.",
        "interests": ["Fashion", "Travel"], "painPoints": ["Limited time"],
        "goals": ["Curated wardrobe"], "preferredChannels": ["Instagram", "Email"],
    },
    "swotAnalysis": {
        "strengths": ["Loyal customers"], "weaknesses": ["No SEO"],
        "opportunities": ["Social commerce"], "threats": ["Fast fashion"],
        "overallAssessment": "Differentiate on curation.",
    },
    "competitorAnalysis": {
        "competitors": [{
            "name": "Zara", "marketPosition": "Leader",
            "threatLevel": "high", "strengths": ["Scale"], "weaknesses": ["Price"],
        }],
        "competitiveAdvantages": ["Curation"], "marketGaps": ["Plus size"],
    },
    "marketingStrategy": {
        "objectives": ["Reach 100k followers", "30% online sales growth"],
        "positioning": "Curation-first boutique",
        "channels": [
            {"name": "Instagram", "priority": "high", "description": "Visual discovery"},
            {"name": "Email", "priority": "medium", "description": "Retention"},
        ],
        "budgetAllocation": [
            {"channel": "Meta Ads", "percentage": 60},
            {"channel": "Content", "percentage": 25},
            {"channel": "Influencers", "percentage": 15},
        ],
        "kpis": [
            {"metric": "Followers", "target": "100k", "timeframe": "6 months"},
            {"metric": "ROAS", "target": "3x", "timeframe": "Quarterly"},
        ],
    },
    "seoKeywords": {
        "primaryKeywords": [
            {"keyword": "boutique fashion", "intent": "commercial",
             "volume": "8k", "difficulty": "medium", "priority": "high"},
        ],
        "contentTopics": [
            {"title": "Fall capsule", "contentType": "Blog",
             "targetKeyword": "capsule wardrobe", "funnelStage": "TOFU"},
        ],
        "onPageRecommendations": ["Fix meta titles"],
    },
    "emailCampaign": {
        "campaignName": "New arrivals", "goal": "Drive sales",
        "audience": "Subscribers",
        "subjectLines": ["New in!", "Your wishlist is live"],
        "sequence": [
            {"day": 1, "type": "Welcome", "subject": "Welcome", "cta": "Shop"},
        ],
    },
    "socialMediaStrategy": {
        "summary": "Instagram-first with daily stories.",
        "platforms": [
            {"name": "Instagram", "focus": "Reels", "postingCadence": "Daily",
             "goals": ["Awareness"], "contentMix": ["Reels", "Stories"]},
        ],
        "communityManagement": ["Reply within 2h"],
        "performanceMetrics": [{"metric": "Engagement", "target": "4%"}],
    },
    "advertisementIdeas": {
        "summary": "Meta ads with strong creative testing.",
        "campaigns": [
            {"name": "Collection launch", "platform": "Meta",
             "objective": "Conversions", "budget": "$2k", "duration": "30 days",
             "expectedOutcome": "120 orders",
             "adCopy": [{"headline": "New drop", "description": "Shop now", "cta": "Buy"}]},
        ],
    },
    "contentCalendar": {
        "timeframe": "Q3", "cadence": "3 posts/week",
        "schedule": [
            {"date": "Jul 1", "channel": "Instagram", "contentFormat": "Reel",
             "topic": "Lookbook", "cta": "Shop"},
        ],
    },
    "implementationRoadmap": {
        "summary": "Foundations first, then scale.",
        "phases": [
            {"name": "Foundation", "duration": "Days 1-30",
             "objectives": ["Set up tracking"], "keyActivities": ["GA4", "Pixels"],
             "successMetrics": ["Tracking live"]},
            {"name": "Launch", "duration": "Days 31-60",
             "objectives": ["Campaigns live"], "keyActivities": ["Meta ads"],
             "successMetrics": ["ROAS 2x"]},
        ],
    },
    "weeklyMilestones": {
        "summary": "Weekly wins.",
        "weeks": [
            {"week": "Week 1", "focus": "Setup", "owner": "Lead",
             "successIndicator": "Pixels installed"},
        ],
    },
    "estimatedROI": {
        "summary": "Payback by month 3.",
        "paybackPeriod": "Month 3",
        "projections": [
            {"period": "M1", "investment": "$3k", "projectedReturn": "$2.4k", "roiPercent": "-20%"},
            {"period": "M2", "investment": "$3k", "projectedReturn": "$4.2k", "roiPercent": "40%"},
            {"period": "M3", "investment": "$4k", "projectedReturn": "$8k", "roiPercent": "100%"},
        ],
        "assumptions": ["CPC holds"], "methodology": "Blended attribution.",
    },
    "riskMitigation": {
        "summary": "Key risks managed.",
        "risks": [
            {"risk": "Ad fatigue", "category": "Execution",
             "likelihood": "medium", "impact": "high",
             "mitigation": ["Rotate creatives"]},
        ],
    },
    "finalRecommendations": {
        "summary": "Execute the plan.",
        "priorities": ["Meta ads"], "quickWins": ["Fix SEO"],
        "longTermInvestments": ["Influencer program"],
        "successCriteria": ["ROAS 3x"], "closingStatement": "Go time.",
    },
}


def main() -> None:
    from app.services.export.renderers import DocxRenderer, PdfRenderer, PptxRenderer

    strategy = MarketingStrategy(
        id=uuid4(),
        project_id=uuid4(),
        name="Resham & Co.",
        target_audience="Fashion-forward women 25-34",
        goals=["Reach 100k followers", "30% online sales growth"],
        content=CONTENT,
        status=StrategyStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    out_dir = Path(__file__).resolve().parent
    renders = [
        ("sample_report.pdf", PdfRenderer().render(strategy).content),
        ("sample_report.docx", DocxRenderer().render(strategy).content),
        ("sample_report.pptx", PptxRenderer().render(strategy).content),
    ]
    for filename, content in renders:
        out = out_dir / filename
        out.write_bytes(content)
        print(f"wrote {out} ({len(content)} bytes)")


main()
