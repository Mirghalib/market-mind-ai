"""Country → currency mapping and budget formatting.

Removes the hardcoded-USD assumption. Every generated strategy should
express budgets, ad spend and ROI in the user's real currency.
"""
from __future__ import annotations

# country name (lowercased, as the form sends it) → (ISO code, symbol)
CURRENCIES: dict[str, tuple[str, str]] = {
    "united states": ("USD", "$"),
    "usa": ("USD", "$"),
    "us": ("USD", "$"),
    "united kingdom": ("GBP", "£"),
    "uk": ("GBP", "£"),
    "pakistan": ("PKR", "Rs."),
    "india": ("INR", "₹"),
    "uae": ("AED", "AED "),
    "united arab emirates": ("AED", "AED "),
    "saudi arabia": ("SAR", "SAR "),
    "canada": ("CAD", "C$"),
    "australia": ("AUD", "A$"),
    "germany": ("EUR", "€"),
    "france": ("EUR", "€"),
    "italy": ("EUR", "€"),
    "spain": ("EUR", "€"),
    "netherlands": ("EUR", "€"),
    "brazil": ("BRL", "R$"),
    "mexico": ("MXN", "MX$"),
    "turkey": ("TRY", "₺"),
    "nigeria": ("NGN", "₦"),
    "south africa": ("ZAR", "R"),
    "egypt": ("EGP", "E£"),
    "japan": ("JPY", "¥"),
    "china": ("CNY", "¥"),
    "singapore": ("SGD", "S$"),
    "malaysia": ("MYR", "RM"),
    "indonesia": ("IDR", "Rp"),
    "thailand": ("THB", "฿"),
    "philippines": ("PHP", "₱"),
    "new zealand": ("NZD", "NZ$"),
    "ireland": ("EUR", "€"),
    "switzerland": ("CHF", "CHF "),
    "sweden": ("SEK", "kr"),
    "norway": ("NOK", "kr"),
    "denmark": ("DKK", "kr"),
    "poland": ("PLN", "zł"),
    "portugal": ("EUR", "€"),
    "belgium": ("EUR", "€"),
    "austria": ("EUR", "€"),
    "greece": ("EUR", "€"),
    "qatar": ("QAR", "QR "),
    "kuwait": ("KWD", "KD "),
    "oman": ("OMR", "OMR "),
    "bahrain": ("BHD", "BD "),
    "jordan": ("JOD", "JD "),
    "lebanon": ("LBP", "L£"),
    "morocco": ("MAD", "MAD "),
    "algeria": ("DZD", "DA"),
    "tunisia": ("TND", "DT"),
    "bangladesh": ("BDT", "৳"),
    "sri lanka": ("LKR", "Rs."),
    "nepal": ("NPR", "Rs."),
    "afghanistan": ("AFN", "AFN "),
    "vietnam": ("VND", "₫"),
    "south korea": ("KRW", "₩"),
    "hong kong": ("HKD", "HK$"),
    "taiwan": ("TWD", "NT$"),
    "argentina": ("ARS", "AR$"),
    "chile": ("CLP", "CLP$"),
    "colombia": ("COP", "COL$"),
    "peru": ("PEN", "S/"),
    "ukraine": ("UAH", "₴"),
    "romania": ("RON", "lei"),
    "czech republic": ("CZK", "Kč"),
    "hungary": ("HUF", "Ft"),
    "croatia": ("EUR", "€"),
    "serbia": ("RSD", "дин."),
    "bulgaria": ("BGN", "лв"),
    "finland": ("EUR", "€"),
    "iceland": ("ISK", "kr"),
}

DEFAULT_CURRENCY = ("USD", "$")
DEFAULT_PERIOD = "month"

# Popular local platforms/tactics per country — used by the mock and
# injected into the prompt so recommendations are country-aware.
COUNTRY_PLATFORMS: dict[str, list[str]] = {
    "pakistan": ["Facebook Ads", "TikTok", "WhatsApp Business", "Daraz", "Google Business Profile"],
    "india": ["Facebook Ads", "Instagram", "WhatsApp Business", "Flipkart", "Google Search"],
    "united states": ["LinkedIn", "Google Ads", "Meta Ads", "Email Automation", "YouTube"],
    "usa": ["LinkedIn", "Google Ads", "Meta Ads", "Email Automation", "YouTube"],
    "united kingdom": ["Google Ads", "Meta Ads", "LinkedIn", "Email Automation", "TikTok"],
    "uk": ["Google Ads", "Meta Ads", "LinkedIn", "Email Automation", "TikTok"],
    "uae": ["Instagram", "Arabic Campaigns", "Luxury Branding", "Influencer Marketing", "Google Ads"],
    "united arab emirates": ["Instagram", "Arabic Campaigns", "Luxury Branding", "Influencer Marketing", "Google Ads"],
    "saudi arabia": ["Instagram", "Snapchat", "Arabic Campaigns", "Influencer Marketing", "Google Ads"],
    "canada": ["Google Ads", "Meta Ads", "LinkedIn", "Email Automation", "YouTube"],
    "australia": ["Google Ads", "Meta Ads", "LinkedIn", "Email Automation", "TikTok"],
    "germany": ["Google Ads", "Meta Ads", "LinkedIn", "Email Automation", "XING"],
    "france": ["Google Ads", "Meta Ads", "LinkedIn", "Email Automation", "Instagram"],
    "brazil": ["Instagram", "Facebook Ads", "WhatsApp Business", "Mercado Livre", "YouTube"],
    "mexico": ["Facebook Ads", "Instagram", "WhatsApp Business", "Mercado Libre", "Google Ads"],
    "nigeria": ["Facebook Ads", "Instagram", "WhatsApp Business", "Jumia", "Google Search"],
    "south africa": ["Facebook Ads", "Instagram", "WhatsApp Business", "Takealot", "Google Ads"],
    "egypt": ["Facebook Ads", "Instagram", "WhatsApp Business", "Google Ads", "Arabic Campaigns"],
    "japan": ["LINE", "Google Ads", "Twitter/X", "Instagram", "YouTube"],
    "china": ["WeChat", "Douyin", "Xiaohongshu", "Baidu", "Weibo"],
    "singapore": ["Google Ads", "Meta Ads", "LinkedIn", "Shopee", "Email Automation"],
    "malaysia": ["Facebook Ads", "Instagram", "WhatsApp Business", "Shopee", "Google Ads"],
    "indonesia": ["Instagram", "TikTok", "Facebook Ads", "Shopee", "WhatsApp Business"],
    "thailand": ["Facebook Ads", "LINE", "Instagram", "TikTok", "Google Ads"],
    "philippines": ["Facebook Ads", "Instagram", "TikTok", "Shopee", "Google Ads"],
}


def currency_for_country(country: str | None) -> tuple[str, str]:
    """Return (code, symbol) for a country, defaulting to USD."""
    if not country:
        return DEFAULT_CURRENCY
    return CURRENCIES.get(country.strip().lower(), DEFAULT_CURRENCY)


def format_budget(
    amount: float | int | None,
    symbol: str | None = None,
    currency_code: str | None = None,
    period: str | None = None,
) -> str:
    """Format a budget amount with the right symbol, e.g. 'Rs. 100,000 / month'."""
    if amount is None:
        return "Not specified"
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return "Not specified"

    if value >= 1_000_000:
        display = f"{value / 1_000_000:,.1f}M"
    elif value >= 1_000:
        display = f"{value:,.0f}"
    else:
        display = f"{value:,.0f}"

    sym = symbol or DEFAULT_CURRENCY[1]
    # Symbols like "Rs." / "AED " already carry spacing; plain symbols attach.
    if sym.endswith(" ") or sym in ("$", "£", "€", "₹", "¥", "₩", "₫", "R", "kr"):
        label = f"{sym}{display}".strip()
    else:
        label = f"{sym} {display}".strip()

    if period and period != DEFAULT_PERIOD:
        return f"{label} / {period}"
    return f"{label} / month"


def budget_label(
    amount: float | int | None,
    symbol: str | None,
    currency_code: str | None,
    period: str | None,
) -> str:
    """Human label used in prompts and exports (e.g. 'Rs. 100,000 / month')."""
    return format_budget(amount, symbol, currency_code, period)
