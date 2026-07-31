"""calendar_prompt.py — content calendar generation.

Input contract (context keys):
    brand, audience, goals, channels, start_date, duration, cadence

Output contract:
    JSON with a scheduled list of content items (date, channel,
    format, topic, CTA). Shape defined in app.services.ai.models.
"""
