"""Branded HTML preview page for shared reports.

Server-rendered so unauthenticated stakeholders can open a share link
in any browser: logo mark, business name, industry, generated date,
marketing score, executive summary, key highlights, and per-format
download buttons that hit ``/s/<token>/download?format=...``.
"""
from __future__ import annotations

from html import escape

from app.services.export.report_data import APP_NAME, ReportData

FORMATS = [
    ("pdf", "PDF"),
    ("docx", "DOCX"),
    ("pptx", "PPTX"),
    ("markdown", "Markdown"),
    ("html", "HTML"),
    ("json", "JSON"),
]


def render_share_preview(share, token: str) -> str:
    """Return the full HTML page for a valid share link."""
    export = share.export
    strategy = export.strategy if export else None
    data = ReportData(strategy) if strategy else None
    name = data.name if data else "Marketing Strategy Report"
    score = data.score if data else 0
    has_score = data is not None and (data.score or data.score_breakdown)

    highlights = ""
    if data and data.highlights:
        lis = "".join(f"<li>{escape(h)}</li>" for h in data.highlights[:5])
        highlights = f'<div class="card"><h2>Key Highlights</h2><ul>{lis}</ul></div>'

    summary = ""
    if data and data.summary_text:
        summary = f'<div class="card"><h2>Executive Summary</h2><p>{escape(data.summary_text)}</p></div>'

    score_html = ""
    if has_score:
        score_html = f"""
        <div class="score-card">
          <span class="score-value">{score}</span>
          <span class="score-label">Marketing Score / 100</span>
        </div>"""

    meta = ""
    if data:
        meta_items = [
            ("Industry", data.industry),
            ("Country", data.country),
            ("Target audience", data.audience or "—"),
        ]
        if data.budget_label and data.budget_label != "Not specified":
            meta_items.append(("Budget", data.budget_label))
        meta_items.append(("Generated", data.generated_date or "—"))
        meta = "".join(
            f'<span class="meta-item"><b>{escape(label)}</b>{escape(value)}</span>'
            for label, value in meta_items
        )

    download_buttons = "".join(
        f'<a class="dl-btn" href="/api/v1/s/{token}/download?format={fmt}">'
        f'<span class="dl-icon">{label[0]}</span>{label}</a>'
        for fmt, label in FORMATS
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(name)} — Shared Report | {APP_NAME}</title>
<style>
  :root {{ --primary:#4f46e5; --primary-dark:#4338ca; --secondary:#7c3aed;
           --ink:#1e293b; --muted:#64748b; --line:#e2e8f0; --panel:#f8fafc; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
          background: #f1f5f9; color: var(--ink); line-height: 1.6; }}
  .topbar {{ background: #fff; border-bottom: 1px solid var(--line);
             padding: 0.9rem 1.5rem; }}
  .topbar-inner {{ max-width: 920px; margin: 0 auto; display: flex;
                   align-items: center; gap: 0.6rem; }}
  .mark {{ display: inline-flex; align-items: center; justify-content: center;
           width: 2.1rem; height: 2.1rem; border-radius: 8px;
           background: linear-gradient(135deg, #4f46e5, #7c3aed);
           color: #fff; font-weight: 800; }}
  .brand-name {{ font-weight: 700; color: var(--primary-dark); }}
  .tagline {{ margin-left: auto; font-size: 0.8rem; color: var(--muted);
              letter-spacing: 0.05em; text-transform: uppercase; }}
  main {{ max-width: 920px; margin: 2rem auto; padding: 0 1.25rem; }}
  .hero {{ background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
           color: #fff; border-radius: 18px; padding: 2.6rem 2.2rem; }}
  .hero h1 {{ font-size: 1.9rem; line-height: 1.2; margin: 0.6rem 0 0.2rem; }}
  .hero .subtitle {{ opacity: 0.85; font-size: 1rem; }}
  .hero .meta {{ display: flex; flex-wrap: wrap; gap: 1.4rem; margin-top: 1.5rem;
                 font-size: 0.82rem; opacity: 0.92; }}
  .meta-item b {{ display: block; font-size: 0.68rem; text-transform: uppercase;
                  opacity: 0.7; letter-spacing: 0.06em; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; margin-top: 1.4rem; }}
  .card {{ background: #fff; border: 1px solid var(--line); border-radius: 14px;
           padding: 1.4rem 1.5rem; }}
  .card h2 {{ color: var(--primary-dark); font-size: 1.05rem; margin-bottom: 0.7rem; }}
  .card ul {{ padding-left: 1.2rem; }}
  .card li {{ margin: 0.25rem 0; font-size: 0.92rem; }}
  .card p {{ font-size: 0.94rem; color: #334155; }}
  .score-card {{ background: #fff; border: 1px solid var(--line); border-radius: 14px;
                 padding: 1.4rem; text-align: center; display: flex;
                 flex-direction: column; justify-content: center; }}
  .score-value {{ font-size: 3.4rem; font-weight: 800; color: var(--primary);
                  line-height: 1; }}
  .score-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em;
                  color: var(--muted); margin-top: 0.5rem; }}
  .downloads {{ background: #fff; border: 1px solid var(--line); border-radius: 14px;
                padding: 1.5rem; margin-top: 1.2rem; }}
  .downloads h2 {{ color: var(--primary-dark); font-size: 1.05rem; margin-bottom: 1rem; }}
  .dl-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
             gap: 0.7rem; }}
  .dl-btn {{ display: flex; align-items: center; gap: 0.6rem; padding: 0.7rem 0.9rem;
            border: 1px solid var(--line); border-radius: 10px; color: var(--ink);
            text-decoration: none; font-size: 0.85rem; font-weight: 600;
            transition: all 0.15s ease; background: var(--panel); }}
  .dl-btn:hover {{ border-color: var(--primary); color: var(--primary);
                   background: #eef2ff; transform: translateY(-1px); }}
  .dl-icon {{ display: inline-flex; align-items: center; justify-content: center;
              width: 1.7rem; height: 1.7rem; border-radius: 6px;
              background: var(--primary); color: #fff; font-size: 0.8rem;
              font-weight: 800; }}
  footer {{ text-align: center; color: var(--muted); font-size: 0.78rem;
            padding: 2rem 1rem 2.5rem; }}
  @media (max-width: 640px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .hero {{ padding: 2rem 1.4rem; }}
    .hero h1 {{ font-size: 1.5rem; }}
    .tagline {{ display: none; }}
  }}
</style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <span class="mark">M</span>
      <span class="brand-name">{APP_NAME}</span>
      <span class="tagline">AI-Powered Marketing Intelligence</span>
    </div>
  </div>

  <main>
    <div class="hero">
      <p class="subtitle">Marketing Strategy Report</p>
      <h1>{escape(name)}</h1>
      <div class="meta">{meta}</div>
    </div>

    <div class="grid">
      {score_html}
      {summary}
    </div>
    {highlights}

    <div class="downloads">
      <h2>Download the report</h2>
      <div class="dl-grid">{download_buttons}</div>
    </div>
  </main>

  <footer>
    {APP_NAME} — Professional consulting-grade reports generated by AI.<br/>
    This link is private and expires automatically.
  </footer>
</body>
</html>"""
