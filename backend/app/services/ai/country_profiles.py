"""Country marketing profiles — localized platforms, tactics and notes.

Injected into the AI prompt and used by the fallback mock so that a
restaurant in Pakistan and a restaurant in the USA receive different,
country-appropriate recommendations.
"""
from __future__ import annotations

from app.services.ai.currencies import COUNTRY_PLATFORMS

COUNTRY_PROFILES: dict[str, dict] = {
    "pakistan": {
        "platforms": COUNTRY_PLATFORMS["pakistan"],
        "tactics": [
            "Leverage WhatsApp Business for order updates and customer care",
            "Run Facebook Ads with Urdu/English mixed creative",
            "List on Daraz and local marketplaces if selling products",
            "Claim and optimize the Google Business Profile for local search",
            "Use TikTok and Instagram Reels for short, local-format video",
        ],
        "notes": "Price sensitivity is high; lead with value and trust signals. Payment links and Cash on Delivery matter.",
    },
    "india": {
        "platforms": COUNTRY_PLATFORMS["india"],
        "tactics": [
            "Use WhatsApp Business for conversational sales and reminders",
            "Run Meta Ads with Hindi/English mix for broad reach",
            "List on Flipkart/Amazon for product businesses",
            "Optimize Google Business Profile and local SEO",
            "Lean on Instagram Reels and YouTube Shorts for reach",
        ],
        "notes": "Massive mobile-first audience; keep creatives light and fast. Festival seasons (Diwali, etc.) drive spikes.",
    },
    "united states": {
        "platforms": COUNTRY_PLATFORMS["united states"],
        "tactics": [
            "Lead with LinkedIn and Google Ads for B2B intent",
            "Use HubSpot-style email automation for nurture",
            "Invest in YouTube and podcast presence for authority",
            "Retarget across Meta and Google with polished creative",
            "Emphasize measurable ROI and case studies",
        ],
        "notes": "High competition and high ad costs; focus on conversion optimization and qualified intent.",
    },
    "usa": {
        "platforms": COUNTRY_PLATFORMS["usa"],
        "tactics": [
            "Lead with LinkedIn and Google Ads for B2B intent",
            "Use HubSpot-style email automation for nurture",
            "Invest in YouTube and podcast presence for authority",
            "Retarget across Meta and Google with polished creative",
            "Emphasize measurable ROI and case studies",
        ],
        "notes": "High competition and high ad costs; focus on conversion optimization and qualified intent.",
    },
    "united kingdom": {
        "platforms": COUNTRY_PLATFORMS["united kingdom"],
        "tactics": [
            "Use Google Ads with strong local intent targeting",
            "Leverage LinkedIn for B2B and professional services",
            "Build email automation with GDPR-compliant consent flows",
            "Use TikTok for brand reach among younger segments",
            "Optimize for 'near me' and local pack listings",
        ],
        "notes": "GDPR compliance is critical; UK consumers respond to transparency and trust.",
    },
    "uk": {
        "platforms": COUNTRY_PLATFORMS["uk"],
        "tactics": [
            "Use Google Ads with strong local intent targeting",
            "Leverage LinkedIn for B2B and professional services",
            "Build email automation with GDPR-compliant consent flows",
            "Use TikTok for brand reach among younger segments",
            "Optimize for 'near me' and local pack listings",
        ],
        "notes": "GDPR compliance is critical; UK consumers respond to transparency and trust.",
    },
    "uae": {
        "platforms": COUNTRY_PLATFORMS["uae"],
        "tactics": [
            "Lead with Instagram and luxury-branded visual content",
            "Run Arabic + English bilingual campaigns",
            "Partner with regional influencers for credibility",
            "Use Google Ads for high-intent local and expat segments",
            "Emphasize premium experience and exclusivity",
        ],
        "notes": "High disposable income among expats; visual polish and exclusivity convert well.",
    },
    "united arab emirates": {
        "platforms": COUNTRY_PLATFORMS["united arab emirates"],
        "tactics": [
            "Lead with Instagram and luxury-branded visual content",
            "Run Arabic + English bilingual campaigns",
            "Partner with regional influencers for credibility",
            "Use Google Ads for high-intent local and expat segments",
            "Emphasize premium experience and exclusivity",
        ],
        "notes": "High disposable income among expats; visual polish and exclusivity convert well.",
    },
    "saudi arabia": {
        "platforms": COUNTRY_PLATFORMS["saudi arabia"],
        "tactics": [
            "Lead with Instagram and Snapchat for younger audiences",
            "Run Arabic-first creative with English support",
            "Partner with local influencers and content creators",
            "Use Google Ads for high-intent searches",
            "Respect cultural norms in imagery and messaging",
        ],
        "notes": "Mobile-first, social-heavy market; Arabic localization is non-negotiable.",
    },
    "canada": {
        "platforms": COUNTRY_PLATFORMS["canada"],
        "tactics": [
            "Use Google Ads with regional targeting (EN/FR)",
            "Leverage LinkedIn for B2B and professional services",
            "Build email automation with clear consent flows",
            "Use YouTube and Meta for brand reach",
            "Localize creative for French-speaking markets",
        ],
        "notes": "Bilingual market; trust and transparency are valued.",
    },
    "australia": {
        "platforms": COUNTRY_PLATFORMS["australia"],
        "tactics": [
            "Use Google Ads for high-intent local search",
            "Leverage Meta and TikTok for broad reach",
            "Build email automation for retention",
            "Use LinkedIn for B2B services",
            "Optimize for local and 'near me' search",
        ],
        "notes": "Small but mature market; word-of-mouth and reviews carry weight.",
    },
    "germany": {
        "platforms": COUNTRY_PLATFORMS["germany"],
        "tactics": [
            "Use Google Ads with strong intent targeting",
            "Leverage LinkedIn and XING for B2B",
            "Build GDPR-compliant email flows",
            "Emphasize quality, precision and data protection",
            "Use Meta for broad consumer reach",
        ],
        "notes": "German consumers value quality, transparency and privacy.",
    },
    "france": {
        "platforms": COUNTRY_PLATFORMS["france"],
        "tactics": [
            "Use Google Ads and Meta for consumer reach",
            "Leverage Instagram for visual brands",
            "Build email flows with consent-first practices",
            "Emphasize brand storytelling and French-language creative",
            "Use LinkedIn for B2B",
        ],
        "notes": "Brand aesthetics and French-language copy matter greatly.",
    },
    "brazil": {
        "platforms": COUNTRY_PLATFORMS["brazil"],
        "tactics": [
            "Lead with Instagram and WhatsApp Business",
            "Use Facebook Ads for broad reach",
            "List on Mercado Livre for product businesses",
            "Use YouTube for long-form content",
            "Lean into seasonal events and festivals",
        ],
        "notes": "Social-first, mobile-heavy market; vibrant creative performs best.",
    },
    "mexico": {
        "platforms": COUNTRY_PLATFORMS["mexico"],
        "tactics": [
            "Use Facebook and Instagram for broad reach",
            "Leverage WhatsApp Business for sales",
            "List on Mercado Libre for products",
            "Use Google Ads for intent",
            "Lean into local cultural moments",
        ],
        "notes": "Price-sensitive, social-first market; strong creative with local references wins.",
    },
    "nigeria": {
        "platforms": COUNTRY_PLATFORMS["nigeria"],
        "tactics": [
            "Use Facebook and Instagram for broad reach",
            "Leverage WhatsApp Business for sales and support",
            "List on Jumia for product businesses",
            "Use Google Search for intent",
            "Lean into local influencers and community",
        ],
        "notes": "Mobile-first; WhatsApp is the dominant messaging channel for commerce.",
    },
    "japan": {
        "platforms": COUNTRY_PLATFORMS["japan"],
        "tactics": [
            "Use LINE for messaging and customer care",
            "Leverage Google Ads for intent",
            "Use Twitter/X and Instagram for brand",
            "Build YouTube presence for trust",
            "Emphasize politeness, detail and quality",
        ],
        "notes": "Japanese consumers expect precision, politeness and high-quality presentation.",
    },
    "singapore": {
        "platforms": COUNTRY_PLATFORMS["singapore"],
        "tactics": [
            "Use Google Ads and Meta for intent + reach",
            "Leverage LinkedIn for B2B and professional services",
            "List on Shopee/Lazada for products",
            "Build email automation for retention",
            "Emphasize trust and convenience",
        ],
        "notes": "High digital penetration; consumers value convenience and trusted brands.",
    },
    "indonesia": {
        "platforms": COUNTRY_PLATFORMS["indonesia"],
        "tactics": [
            "Lead with Instagram and TikTok",
            "Use Facebook Ads for reach",
            "Leverage WhatsApp Business for commerce",
            "List on Shopee/Tokopedia for products",
            "Lean into local creators and community",
        ],
        "notes": "Mobile-first, social-commerce-heavy market.",
    },
}

DEFAULT_COUNTRY_PROFILE = {
    "platforms": ["Google Ads", "Meta Ads", "Email Marketing", "Instagram", "LinkedIn"],
    "tactics": [
        "Run search and social campaigns on the dominant local platforms",
        "Build an email automation flow to nurture leads",
        "Optimize local search (Google Business Profile / equivalent)",
        "Use influencer and creator partnerships where relevant",
        "Retarget engaged audiences to lift conversion",
    ],
    "notes": "Tailor language and creative to the local market.",
}


def profile_for_country(country: str | None) -> dict:
    """Return the country marketing profile (or a sensible default)."""
    if not country:
        return DEFAULT_COUNTRY_PROFILE
    return COUNTRY_PROFILES.get(country.strip().lower(), DEFAULT_COUNTRY_PROFILE)
