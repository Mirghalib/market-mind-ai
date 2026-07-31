"""Parsers — normalize raw LLM completions into structured data.

LLM responses can be messy (markdown fences, prose, trailing tokens).
Parsers clean that up into JSON-serializable Python objects before
validation. No business logic here.
"""
