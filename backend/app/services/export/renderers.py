"""Strategy export renderers.

Each format is a ``Renderer`` that turns a MarketingStrategy into
file bytes plus the metadata needed for an HTTP file response
(media type, file extension). Renderers are registered in ``RENDERERS``;
the endpoint and service stay untouched.

Formats:
  - json: full document
  - markdown: readable, version-control friendly
  - html: styled single-file report
  - pdf: reportlab-based (requires ``reportlab``)
  - docx: python-docx-based (requires ``python-docx``)
"""
import json
from dataclasses import dataclass
from html import escape

from app.models.export import ExportFormat
from app.models.marketing_strategy import MarketingStrategy


@dataclass(frozen=True)
class RenderedExport:
    """Result of a renderer: payload bytes + response metadata."""

    content: bytes
    media_type: str
    file_extension: str


class BaseRenderer:
    """Interface implemented by every export format renderer."""

    format: ExportFormat

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        raise NotImplementedError


def _document(strategy: MarketingStrategy) -> dict:
    """Normalized document shared by the text-based renderers."""
    goals = getattr(strategy, "goals", None) or []
    status = getattr(strategy, "status", None)
    created_at = getattr(strategy, "created_at", None)
    updated_at = getattr(strategy, "updated_at", None)
    return {
        "strategy_id": str(strategy.id),
        "name": strategy.name,
        "target_audience": strategy.target_audience,
        "goals": goals,
        "status": status.value if status else "",
        "content": strategy.content or {},
        "created_at": created_at.isoformat() if created_at else "",
        "updated_at": updated_at.isoformat() if updated_at else "",
    }


def clean_md(value) -> str:
    """Safe single-line string for Markdown (escapes pipes)."""
    text = str(value) if value is not None else ""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _sections(strategy: MarketingStrategy) -> list[tuple[str, str]]:
    """Return [(title, content)] pairs from the stored payload.

    Handles three shapes:
      1. Flat list shape:  content.sections = [{title, content}, ...]
      2. Raw LLM document: content = {marketingStrategy: {...}, customerPersona: {...}, ...}
      3. Legacy flat:      content = {summary: "...", sections: [...]}
    """
    content = strategy.content or {}

    # Shape 1: flat list.
    sections = content.get("sections")
    if isinstance(sections, list) and sections:
        return [
            (str(s.get("title", "Section")), str(s.get("content", "")))
            for s in sections
        ]

    # Shape 2: raw LLM document — flatten top-level objects into sections.
    flat: list[tuple[str, str]] = []
    for key, value in content.items():
        title = key.replace("_", " ").title()
        if isinstance(value, dict):
            rendered = _flatten_block(value)
            if rendered:
                flat.append((title, rendered))
        elif isinstance(value, str) and value.strip():
            flat.append((title, value))
    if flat:
        return flat

    # Shape 3: legacy flat shape.
    legacy = []
    if content.get("summary"):
        legacy.append(("Summary", str(content["summary"])))
    for key, value in content.items():
        if key in ("summary", "sections"):
            continue
        if isinstance(value, str):
            legacy.append((key.replace("_", " ").title(), value))
    return legacy


def _flatten_block(block: dict) -> str:
    """Render a nested LLM block (e.g. marketingStrategy) as readable text.

    Dicts inside lists are rendered from their human-readable fields
    (name / title / keyword / risk / period ...) rather than raw ``str``
    so exported text never shows Python dict reprs.
    """
    def _list_item(item) -> str:
        if isinstance(item, dict):
            for key in ("name", "title", "keyword", "risk", "period",
                        "metric", "channel", "campaign", "week", "phase",
                        "headline", "subject", "platform", "topic"):
                if item.get(key):
                    return str(item[key])
            return " ".join(str(v) for v in item.values() if str(v).strip())
        return str(item)

    lines: list[str] = []
    for key, value in block.items():
        label = key.replace("_", " ").replace("-", " ").title()
        if isinstance(value, str) and value.strip():
            lines.append(f"{label}: {value.strip()}")
        elif isinstance(value, list):
            items = [_list_item(i) for i in value if str(i).strip()]
            if items:
                lines.append(f"{label}:")
                lines.extend(f"- {item}" for item in items)
        elif isinstance(value, dict):
            inner = _flatten_block(value)
            if inner:
                lines.append(f"{label}:")
                lines.extend(f"  {line}" for line in inner.split("\n"))
    return "\n".join(lines)


class JsonRenderer(BaseRenderer):
    """Serialise the strategy document as a JSON file."""

    format = ExportFormat.JSON

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        document = _document(strategy)
        payload = json.dumps(document, indent=2, ensure_ascii=False).encode("utf-8")
        return RenderedExport(
            content=payload,
            media_type="application/json",
            file_extension="json",
        )


class MarkdownRenderer(BaseRenderer):
    """Render the strategy as a professional, GitHub-friendly Markdown doc.

    Produces front matter, a table of contents, structured sections with
    tables (KPIs, budget, competitors, milestones, ROI), bullet lists and
    action checklists — so it renders beautifully on GitHub and in any
    Markdown viewer.
    """

    format = ExportFormat.MARKDOWN

    def _table(self, header: list[str], rows: list[list[str]]) -> list[str]:
        if not rows:
            return []
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
        ]
        for row in rows:
            lines.append("| " + " | ".join(str(c) for c in row) + " |")
        return lines

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        from app.services.export.report_data import ReportData

        data = ReportData(strategy)
        md: list[str] = []

        # --- Front matter --------------------------------------------------
        md.append(f"# {data.name}")
        md.append("")
        md.append("> **Marketing Strategy Report** — prepared by **Market Mind AI**")
        md.append("")
        md.append("| | |")
        md.append("|---|---|")
        md.append(f"| **Industry** | {data.industry} |")
        md.append(f"| **Country** | {data.country} |")
        md.append(f"| **Target audience** | {data.audience or '—'} |")
        if data.budget_label and data.budget_label != "Not specified":
            md.append(f"| **Budget** | {data.budget_label} |")
        md.append(f"| **Status** | {data.status} |")
        md.append(f"| **Generated** | {data.generated_date or '—'} |")
        md.append("")
        md.append("---")
        md.append("")

        # --- TOC -------------------------------------------------------------
        toc_names = {
            "executiveSummary": "Executive Summary",
            "marketingScore": "Marketing Score",
            "marketOverview": "Market Overview",
            "customerPersona": "Customer Persona",
            "swotAnalysis": "SWOT Analysis",
            "competitorAnalysis": "Competitor Analysis",
            "marketingStrategy": "Marketing Strategy",
            "seoKeywords": "SEO Strategy",
            "emailCampaign": "Email Marketing",
            "socialMediaStrategy": "Social Media Strategy",
            "advertisementIdeas": "Paid Advertising",
            "contentCalendar": "Content Calendar",
            "implementationRoadmap": "90-Day Roadmap",
            "weeklyMilestones": "Next 90-Day Action Plan",
            "estimatedROI": "Estimated ROI",
            "riskMitigation": "Risks & Mitigation",
            "finalRecommendations": "Final Recommendations",
        }
        present = [toc_names.get(k, k.replace("_", " ").title()) for k in data.present_sections]
        if present:
            md.append("## Table of Contents")
            md.append("")
            for name in present:
                slug = name.lower().replace("&", "").replace("(", "").replace(")", "")
                slug = "-".join(slug.split())
                md.append(f"- [{name}](#{slug})")
            md.append("")
            md.append("---")
            md.append("")

        # --- Executive summary -----------------------------------------------
        if data.summary_text:
            md.append("## Executive Summary")
            md.append("")
            md.append(data.summary_text)
            md.append("")
            if data.highlights:
                md.append("### Key Highlights")
                md.append("")
                for h in data.highlights:
                    md.append(f"- **{h}**")
                md.append("")
            if data.recommendation:
                md.append(f"> **Recommendation:** {data.recommendation}")
                md.append("")
            md.append("---")
            md.append("")

        # --- Marketing score ---------------------------------------------------
        if data.score_breakdown or data.score:
            md.append("## Marketing Score")
            md.append("")
            if data.score:
                md.append(f"**Overall readiness: {data.score}/100**")
                md.append("")
            if data.score_summary:
                md.append(data.score_summary)
                md.append("")
            if data.score_benchmark:
                md.append(f"*Benchmark: {data.score_benchmark}*")
                md.append("")
            if data.score_breakdown:
                rows = [[b["area"], f"{b['score']}/100", b["assessment"]]
                        for b in data.score_breakdown]
                md.extend(self._table(["Area", "Score", "Assessment"], rows))
                md.append("")
            md.append("---")
            md.append("")

        # --- Market overview ----------------------------------------------------
        if data.market or data.market_trends:
            md.append("## Market Overview")
            md.append("")
            if data.market.get("summary"):
                md.append(str(data.market["summary"]))
                md.append("")
            if data.market.get("targetMarketSize") or data.market.get("growthRate"):
                meta = []
                if data.market.get("targetMarketSize"):
                    meta.append(f"Market size: {data.market['targetMarketSize']}")
                if data.market.get("growthRate"):
                    meta.append(f"Growth rate: {data.market['growthRate']}")
                md.append(" - ".join(meta))
                md.append("")
            for label, items in [("Market Trends", data.market_trends),
                                 ("Key Drivers", data.market_drivers),
                                 ("Market Risks", data.market_risks)]:
                if items:
                    md.append(f"### {label}")
                    md.append("")
                    md.extend(f"- {i}" for i in items)
                    md.append("")
            md.append("---")
            md.append("")

        # --- Persona --------------------------------------------------------------
        if data.persona:
            md.append("## Customer Persona")
            md.append("")
            persona = data.persona
            rows = []
            for label, key in [("Name", "name"), ("Age range", "ageRange"),
                               ("Location", "location"), ("Occupation", "occupation"),
                               ("Income level", "incomeLevel")]:
                if persona.get(key):
                    rows.append([label, str(persona[key])])
            if rows:
                md.extend(self._table(["Attribute", "Profile"], rows))
                md.append("")
            for label, key in [("Interests", "interests"), ("Pain Points", "painPoints"),
                               ("Goals", "goals"), ("Preferred Channels", "preferredChannels")]:
                items = [clean_md(i) for i in (persona.get(key) or []) if clean_md(i)]
                if items:
                    md.append(f"### {label}")
                    md.append("")
                    md.extend(f"- {i}" for i in items)
                    md.append("")
            md.append("---")
            md.append("")

        # --- SWOT ------------------------------------------------------------------
        if any(data.swot_quadrants.values()):
            md.append("## SWOT Analysis")
            md.append("")
            for label, items in data.swot_quadrants.items():
                if items:
                    md.append(f"### {label}")
                    md.append("")
                    md.extend(f"- {i}" for i in items)
                    md.append("")
            if data.swot.get("overallAssessment"):
                md.append(f"*{data.swot['overallAssessment']}*")
                md.append("")
            md.append("---")
            md.append("")

        # --- Marketing strategy -------------------------------------------------------
        if data.objectives or data.channels or data.budget:
            md.append("## Marketing Strategy")
            md.append("")
            if data.objectives:
                md.append("### Objectives")
                md.append("")
                for i, obj in enumerate(data.objectives, start=1):
                    md.append(f"{i}. {obj}")
                md.append("")
            if data.positioning:
                md.append(f"**Positioning:** {data.positioning}")
                md.append("")
            if data.channels:
                rows = [[c["name"], c["priority"].capitalize(), c["description"]]
                        for c in data.channels]
                md.extend(self._table(["Channel", "Priority", "Why / How"], rows))
                md.append("")
            if data.budget:
                md.append("### Budget Allocation")
                md.append("")
                md.extend(self._table(["Channel", "Allocation"], data.budget_rows))
                md.append("")
            md.append("---")
            md.append("")

        # --- KPIs ---------------------------------------------------------------------
        if data.kpis:
            md.append("## Key Performance Indicators")
            md.append("")
            md.extend(self._table(["Metric", "Target", "Timeframe"], data.kpi_rows))
            md.append("")
            md.append("---")
            md.append("")

        # --- Competitors ----------------------------------------------------------------
        if data.competitors:
            md.append("## Competitor Analysis")
            md.append("")
            rows = [[c["name"], c["position"], c["threat"].capitalize(),
                     ", ".join(str(s) for s in c["strengths"]),
                     ", ".join(str(w) for w in c["weaknesses"])] for c in data.competitors]
            md.extend(self._table(["Competitor", "Position", "Threat", "Strengths", "Weaknesses"], rows))
            md.append("")
            md.append("---")
            md.append("")

        # --- SEO / email / social / ads ---------------------------------------------------
        for heading, section_key in [
            ("SEO Strategy", "seoKeywords"),
            ("Email Marketing", "emailCampaign"),
            ("Social Media Strategy", "socialMediaStrategy"),
            ("Paid Advertising", "advertisementIdeas"),
            ("Content Calendar", "contentCalendar"),
        ]:
            section = data.content.get(section_key)
            if not section:
                continue
            md.append(f"## {heading}")
            md.append("")
            if isinstance(section, dict) and section.get("summary"):
                md.append(str(section["summary"]))
                md.append("")
            lines = _flatten_block(section)
            for line in lines.split("\n"):
                if line.strip():
                    md.append(f"- {line.lstrip('- ')}" if not line.startswith(("  ", "•")) else line)
            md.append("")
            md.append("---")
            md.append("")

        # --- Roadmap + 90-day plan ----------------------------------------------------------
        if data.roadmap_phases:
            md.append("## 90-Day Implementation Roadmap")
            md.append("")
            if data.roadmap.get("summary"):
                md.append(str(data.roadmap["summary"]))
                md.append("")
            for phase in data.roadmap_phases:
                name = clean_md(phase.get("name"))
                duration = clean_md(phase.get("duration"))
                md.append(f"### {name}" + (f" — {duration}" if duration else ""))
                md.append("")
                for label, key in [("Objectives", "objectives"),
                                   ("Key Activities", "keyActivities"),
                                   ("Success Metrics", "successMetrics")]:
                    items = [clean_md(i) for i in (phase.get(key) or []) if clean_md(i)]
                    if items:
                        md.append(f"**{label}**")
                        md.append("")
                        if key == "keyActivities":
                            # Action checklist.
                            md.extend(f"- [ ] {i}" for i in items)
                        else:
                            md.extend(f"- {i}" for i in items)
                        md.append("")
            md.append("---")
            md.append("")

        # --- Next 90-day action plan ------------------------------------------------------------
        if data.milestone_weeks:
            md.append("## Next 90-Day Action Plan")
            md.append("")
            if data.milestones.get("summary"):
                md.append(str(data.milestones["summary"]))
                md.append("")
            md.extend(self._table(["Week", "Focus", "Owner", "Success Indicator"], data.milestone_rows))
            md.append("")
            md.append("---")
            md.append("")

        # --- ROI -------------------------------------------------------------------------------
        if data.roi_projections:
            md.append("## Estimated ROI")
            md.append("")
            if data.roi.get("summary"):
                md.append(str(data.roi["summary"]))
                md.append("")
            if data.roi.get("paybackPeriod"):
                md.append(f"**Payback period:** {data.roi['paybackPeriod']}")
                md.append("")
            md.extend(self._table(["Period", "Investment", "Projected Return", "ROI"], data.roi_rows))
            md.append("")
            md.append("---")
            md.append("")

        # --- Risks -------------------------------------------------------------------------------
        if data.risk_items:
            md.append("## Risks & Mitigation")
            md.append("")
            rows = [[r["risk"], r["category"], r["likelihood"].capitalize(),
                     r["impact"].capitalize(), ", ".join(str(m) for m in r["mitigation"])]
                    for r in data.risk_items]
            md.extend(self._table(["Risk", "Category", "Likelihood", "Impact", "Mitigation"], rows))
            md.append("")
            md.append("---")
            md.append("")

        # --- Final recommendations ------------------------------------------------------------------
        if data.recommendations:
            md.append("## Final Recommendations")
            md.append("")
            rec = data.recommendations
            if rec.get("summary"):
                md.append(str(rec["summary"]))
                md.append("")
            for label, key in [("Top Priorities", "priorities"),
                               ("Quick Wins", "quickWins"),
                               ("Long-Term Investments", "longTermInvestments"),
                               ("Success Criteria", "successCriteria")]:
                items = [clean_md(i) for i in (rec.get(key) or []) if clean_md(i)]
                if items:
                    md.append(f"### {label}")
                    md.append("")
                    md.extend(f"- {i}" for i in items)
                    md.append("")
            if rec.get("closingStatement"):
                md.append(f"*{rec['closingStatement']}*")
                md.append("")

        md.append("---")
        md.append("")
        md.append(f"*Report generated by **Market Mind AI** on {data.generated_date or '—'}.*")
        md.append("")

        payload = "\n".join(md).encode("utf-8")
        return RenderedExport(
            content=payload,
            media_type="text/markdown",
            file_extension="md",
        )


class HtmlRenderer(BaseRenderer):
    """Render the strategy as a polished, self-contained HTML report."""

    format = ExportFormat.HTML

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        from app.services.export.report_data import ReportData

        data = ReportData(strategy)
        blocks: list[str] = []

        # Cover header.
        blocks.append(
            f"""<header class="cover">
      <div class="brand"><span class="mark">M</span><span>Market Mind AI</span></div>
      <h1>{escape(data.name)}</h1>
      <p class="subtitle">Marketing Strategy Report</p>
      <div class="meta">
        <span><b>Industry</b> {escape(data.industry)}</span>
        <span><b>Country</b> {escape(data.country)}</span>
        <span><b>Audience</b> {escape(data.audience or '—')}</span>
        <span><b>Budget</b> {escape(data.budget_label if data.budget_label != 'Not specified' else '—')}</span>
        <span><b>Generated</b> {escape(data.generated_date or '—')}</span>
      </div>
    </header>"""
        )

        # Executive summary.
        if data.summary_text:
            blocks.append("<section><h2>Executive Summary</h2>")
            blocks.append(f"<p>{escape(data.summary_text)}</p>")
            if data.highlights:
                blocks.append("<ul>")
                blocks.extend(f"<li>{escape(h)}</li>" for h in data.highlights)
                blocks.append("</ul>")
            blocks.append("</section>")

        # Marketing score.
        if data.score or data.score_breakdown:
            blocks.append("<section><h2>Marketing Score</h2>")
            if data.score:
                blocks.append(
                    f'<div class="score"><strong>{data.score}</strong><span>/ 100</span></div>'
                )
            if data.score_summary:
                blocks.append(f"<p>{escape(data.score_summary)}</p>")
            if data.score_breakdown:
                rows = "".join(
                    f"<tr><td>{escape(b['area'])}</td><td>{b['score']}/100</td>"
                    f"<td>{escape(b['assessment'])}</td></tr>"
                    for b in data.score_breakdown
                )
                blocks.append(
                    f'<table><thead><tr><th>Area</th><th>Score</th><th>Assessment</th></tr></thead>'
                    f"<tbody>{rows}</tbody></table>"
                )
            blocks.append("</section>")

        # Structured tables for KPI / budget / competitors / ROI.
        if data.kpis:
            rows = "".join(
                f"<tr><td>{escape(k['metric'])}</td><td>{escape(k['target'])}</td>"
                f"<td>{escape(k['timeframe'])}</td></tr>"
                for k in data.kpis
            )
            blocks.append(
                "<section><h2>Key Performance Indicators</h2>"
                "<table><thead><tr><th>Metric</th><th>Target</th><th>Timeframe</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></section>"
            )
        if data.budget:
            rows = "".join(
                f"<tr><td>{escape(b['channel'])}</td><td>{b['percentage']:.0f}%</td></tr>"
                for b in data.budget
            )
            blocks.append(
                "<section><h2>Budget Allocation</h2>"
                "<table><thead><tr><th>Channel</th><th>Allocation</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></section>"
            )
        if data.competitors:
            rows = "".join(
                f"<tr><td>{escape(c['name'])}</td><td>{escape(c['position'])}</td>"
                f"<td>{escape(c['threat'])}</td></tr>"
                for c in data.competitors
            )
            blocks.append(
                "<section><h2>Competitor Analysis</h2>"
                "<table><thead><tr><th>Competitor</th><th>Position</th><th>Threat</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></section>"
            )
        if data.roi_projections:
            rows = "".join(
                f"<tr><td>{escape(p['period'])}</td><td>{escape(p['investment'])}</td>"
                f"<td>{escape(p['projected_return'])}</td><td>{p['roi_percent']:.0f}%</td></tr>"
                for p in data.roi_projections
            )
            blocks.append(
                "<section><h2>Estimated ROI</h2>"
                "<table><thead><tr><th>Period</th><th>Investment</th>"
                "<th>Projected Return</th><th>ROI</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></section>"
            )

        # Remaining flattened sections.
        for title, content in _sections(strategy):
            if title in ("Executive Summary", "Marketing Score", "Key Performance Indicators",
                         "Budget Allocation", "Competitor Analysis", "Estimated Roi"):
                continue
            blocks.append(
                f"<section><h2>{escape(title)}</h2>"
                f"<p>{escape(content).replace(chr(10), '<br/>')}</p></section>"
            )

        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(data.name)} — Market Mind AI</title>
<style>
  :root {{ --primary:#4f46e5; --primary-dark:#4338ca; --secondary:#7c3aed;
           --ink:#1e293b; --muted:#64748b; --line:#e2e8f0; --panel:#f8fafc; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: var(--ink);
          max-width: 860px; margin: 0 auto; padding: 0 1.5rem 3rem; line-height: 1.65;
          background: #fafafa; }}
  .cover {{ background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: #fff; border-radius: 18px; padding: 3rem 2.5rem; margin: 2rem 0; }}
  .brand {{ display: flex; align-items: center; gap: 0.6rem; font-size: 0.85rem;
            letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.9; }}
  .mark {{ display: inline-flex; align-items: center; justify-content: center;
           width: 2rem; height: 2rem; border-radius: 8px; background: #fff;
           color: var(--primary); font-weight: 800; }}
  .cover h1 {{ margin: 1.2rem 0 0.2rem; font-size: 2.2rem; line-height: 1.15; }}
  .cover .subtitle {{ font-size: 1.05rem; opacity: 0.85; margin: 0; }}
  .cover .meta {{ display: flex; flex-wrap: wrap; gap: 1.2rem; margin-top: 1.6rem;
                  font-size: 0.85rem; opacity: 0.92; }}
  section {{ background: #fff; border: 1px solid var(--line); border-radius: 14px;
             padding: 1.6rem 1.8rem; margin: 1.2rem 0; }}
  h2 {{ color: var(--primary-dark); font-size: 1.25rem; margin: 0 0 0.8rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 0.6rem 0; font-size: 0.9rem; }}
  th {{ background: var(--primary); color: #fff; text-align: left; padding: 0.5rem 0.7rem; }}
  td {{ border-bottom: 1px solid var(--line); padding: 0.5rem 0.7rem; }}
  tr:nth-child(even) td {{ background: var(--panel); }}
  ul {{ padding-left: 1.2rem; }}
  .score {{ display: flex; align-items: baseline; gap: 0.4rem; margin: 0.4rem 0; }}
  .score strong {{ font-size: 2.4rem; color: var(--primary); }}
  .score span {{ color: var(--muted); }}
  footer {{ text-align: center; color: var(--muted); font-size: 0.8rem; margin-top: 2rem; }}
</style>
</head>
<body>
  {''.join(blocks)}
  <footer>Generated by Market Mind AI — AI-Powered Marketing Intelligence</footer>
</body>
</html>"""
        return RenderedExport(
            content=html.encode("utf-8"),
            media_type="text/html",
            file_extension="html",
        )


class PdfRenderer(BaseRenderer):
    """Render the strategy as a professional consulting-grade PDF.

    Delegates to ``pdf_report.build_strategy_report`` (a reportlab-based
    builder with cover page, table of contents, charts, tables, summary
    cards, headers/footers and page numbers). The import is lazy so the
    registry stays importable without reportlab.
    """

    format = ExportFormat.PDF

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        try:
            from app.services.export.pdf_report import build_strategy_report
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "PDF export requires the 'reportlab' package. "
                "Install it with: pip install reportlab"
            ) from exc

        payload = build_strategy_report(strategy)
        return RenderedExport(
            content=payload,
            media_type="application/pdf",
            file_extension="pdf",
        )


class DocxRenderer(BaseRenderer):
    """Render the strategy as a professionally formatted .docx file.

    Delegates to ``docx_report.build_strategy_report_docx`` (a
    python-docx based builder with cover page, table of contents,
    colored headings, styled tables, lists, footer with page numbers).
    The import is lazy so the registry stays importable without
    python-docx.
    """

    format = ExportFormat.DOCX

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        try:
            from app.services.export.docx_report import build_strategy_report_docx
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "DOCX export requires the 'python-docx' package. "
                "Install it with: pip install python-docx"
            ) from exc

        return RenderedExport(
            content=build_strategy_report_docx(strategy),
            media_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            file_extension="docx",
        )


class PptxRenderer(BaseRenderer):
    """Render the strategy as a professional .pptx deck.

    Delegates to ``pptx_deck.build_deck`` (a python-pptx based builder
    with cover, agenda, charts, timeline, ROI and recommendations —
    minimum 15 slides). The import is lazy so the registry stays
    importable without python-pptx.
    """

    format = ExportFormat.PPTX

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        try:
            from app.services.export.pptx_deck import build_deck
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "PPTX export requires the 'python-pptx' package. "
                "Install it with: pip install python-pptx"
            ) from exc

        payload = build_deck(strategy)
        return RenderedExport(
            content=payload,
            media_type=(
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            ),
            file_extension="pptx",
        )


# Maps ExportFormat values to their renderer. Extend here to add formats.
RENDERERS: dict[ExportFormat, BaseRenderer] = {
    JsonRenderer.format: JsonRenderer(),
    MarkdownRenderer.format: MarkdownRenderer(),
    HtmlRenderer.format: HtmlRenderer(),
    PdfRenderer.format: PdfRenderer(),
    DocxRenderer.format: DocxRenderer(),
    PptxRenderer.format: PptxRenderer(),
}


def get_renderer(format_: ExportFormat) -> BaseRenderer:
    """Return the renderer for a format, raising if none is registered."""
    try:
        return RENDERERS[format_]
    except KeyError:
        raise ValueError(f"Unsupported export format: {format_.value}") from None
