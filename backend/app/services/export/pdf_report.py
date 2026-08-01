"""Professional, consulting-grade PDF report builder for marketing strategies.

Built on ReportLab's ``BaseDocTemplate`` with a cover page, table of
contents (two-pass build), per-section styled tables and charts, page
headers/footers, and page numbers.

Design language:
  - Corporate palette: indigo primary (#4f46e5), slate ink (#1e293b),
    light panel (#f1f5f9), muted gray (#64748b).
  - Helvetica family, generous spacing, consistent heading styles.
  - Every section is data-driven from ``MarketingStrategy.content``.
    When a structured section is missing (e.g. legacy strategies) the
    builder falls back gracefully and the section is skipped.

The module is imported lazily by ``PdfRenderer`` to keep the renderer
registry importable even when reportlab is unavailable.
"""
from html import escape
from io import BytesIO
from typing import Any

from reportlab.graphics import shapes
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Palette & typography
# ---------------------------------------------------------------------------

INDIGO = HexColor("#4f46e5")
INDIGO_DARK = HexColor("#4338ca")
INDIGO_LIGHT = HexColor("#eef2ff")
SLATE = HexColor("#1e293b")
MUTED = HexColor("#64748b")
PANEL = HexColor("#f1f5f9")
LINE = HexColor("#e2e8f0")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
COVER_ACCENT = HexColor("#312e81")
COVER_BAR = HexColor("#eef2ff")

styles = getSampleStyleSheet()

_TITLE = ParagraphStyle(
    "ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=28, leading=34, textColor=SLATE, spaceAfter=6,
)
_H1 = ParagraphStyle(
    "ReportH1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=20, leading=26, textColor=INDIGO_DARK, spaceBefore=0,
    spaceAfter=8, alignment=TA_LEFT,
)
_H2 = ParagraphStyle(
    "ReportH2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=13, leading=17, textColor=SLATE, spaceBefore=12, spaceAfter=4,
)
_BODY = ParagraphStyle(
    "ReportBody", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9.5, leading=14, textColor=SLATE, spaceAfter=6,
)
_META = ParagraphStyle(
    "ReportMeta", parent=_BODY, fontName="Helvetica", fontSize=8.5,
    leading=12, textColor=MUTED,
)
_BULLET = ParagraphStyle(
    "ReportBullet", parent=_BODY, leftIndent=10, bulletIndent=0, spaceAfter=2,
)
_CAPTION = ParagraphStyle(
    "ReportCaption", parent=_META, fontSize=8, textColor=MUTED,
    alignment=TA_CENTER, spaceBefore=2,
)
_CARD_LABEL = ParagraphStyle(
    "CardLabel", parent=_BODY, fontName="Helvetica-Bold", fontSize=8,
    leading=11, textColor=MUTED, alignment=TA_CENTER,
)
_CARD_VALUE = ParagraphStyle(
    "CardValue", parent=_BODY, fontName="Helvetica-Bold", fontSize=20,
    leading=24, textColor=INDIGO_DARK, alignment=TA_CENTER, spaceBefore=2,
)
_TOC_STYLE = ParagraphStyle(
    "TocStyle", parent=_BODY, fontSize=10, leading=18, textColor=SLATE,
)


def _esc(text: Any) -> str:
    """Safe string for ReportLab paragraphs."""
    return escape(str(text)) if text is not None else ""


# ---------------------------------------------------------------------------
# Document scaffold with header/footer
# ---------------------------------------------------------------------------


class _ReportDoc(BaseDocTemplate):
    """A4 document with a cover template and an inner header/footer template."""

    def __init__(self, buffer: BytesIO, report_title: str) -> None:
        super().__init__(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=2.2 * cm, bottomMargin=2.2 * cm,
            title=report_title,
            author="Market Mind AI",
        )
        self.report_title = report_title
        frame = Frame(
            MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 4.4 * cm,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        cover_frame = Frame(
            MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        self.addPageTemplates(
            [
                PageTemplate(id="cover", frames=[cover_frame],
                             onPage=self._draw_cover_frame),
                PageTemplate(id="inner", frames=[frame],
                             onPage=self._draw_header_footer),
            ]
        )

    def _draw_cover_frame(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setFillColor(COVER_ACCENT)
        canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        canvas.setFillColor(COVER_BAR)
        canvas.rect(0, PAGE_H - 4.6 * cm, PAGE_W, 4.6 * cm, stroke=0, fill=1)
        canvas.setStrokeColor(INDIGO_LIGHT)
        canvas.setLineWidth(3)
        canvas.line(0, PAGE_H - 4.6 * cm, PAGE_W, PAGE_H - 4.6 * cm)
        canvas.restoreState()

    def _draw_header_footer(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(MARGIN, PAGE_H - 1.4 * cm, self.report_title[:70])
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, PAGE_H - 1.6 * cm, PAGE_W - MARGIN, PAGE_H - 1.6 * cm)
        page_num = canvas.getPageNumber()
        if page_num > 1:
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(PAGE_W / 2, 1.2 * cm, str(page_num))
        canvas.restoreState()


class _PageMarker(Flowable):
    """Zero-size flowable that records the page where a section starts."""

    def __init__(self, title: str) -> None:
        super().__init__()
        self.title = title
        self.page = 1
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        pass


class _CaptureMarker(_PageMarker):
    """Marker that records the live page number during a TOC pass."""

    def __init__(self, title: str, sink: dict[str, int], doc) -> None:
        super().__init__(title)
        self.sink = sink
        self._doc = doc

    def draw(self):
        self.sink[self.title] = self._doc.page


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------


def _budget_pie_chart(data: list[dict]) -> Drawing:
    """Pie chart of budget allocation; data: [{channel, percentage}]."""
    items = [d for d in data if (d.get("percentage") or 0) > 0]
    drawing = Drawing(9.2 * cm, 7.4 * cm)
    pie = Pie()
    pie.x = 90
    pie.y = 70
    pie.width = 6.0 * cm
    pie.height = 6.0 * cm
    pie.data = [float(d.get("percentage") or 0) for d in items]
    palette = [INDIGO, HexColor("#818cf8"), HexColor("#a5b4fc"),
               HexColor("#c7d2fe"), HexColor("#e0e7ff"), HexColor("#94a3b8")]
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = WHITE
    pie.slices.label_visible = False
    for i, (item, color) in enumerate(zip(items, palette)):
        pie.slices[i].fillColor = color
    drawing.add(pie)

    legend_y = 7.0 * cm
    for i, (item, color) in enumerate(zip(items, palette)):
        y = legend_y - i * 0.55 * cm
        drawing.add(shapes.Rect(9.0 * cm, y, 0.32 * cm, 0.32 * cm,
                                fillColor=color, strokeColor=WHITE, strokeWidth=0.5))
        drawing.add(shapes.String(
            9.5 * cm, y - 0.05 * cm,
            f"{item.get('channel', '')} — {item.get('percentage', 0)}%",
            fontName="Helvetica", fontSize=7.5, fillColor=SLATE,
        ))
    return drawing


def _roi_line_chart(projections: list[dict]) -> Drawing:
    """Hand-drawn line chart of ROI percentage across periods.

    Uses raw ``shapes`` primitives so it is independent of the reportlab
    charting API (which changed across versions).
    """
    values = []
    for p in projections:
        raw = str(p.get("roiPercent") or "0")
        try:
            values.append(float(raw.replace("%", "").replace(",", "")))
        except ValueError:
            values.append(0.0)
    if not values:
        return Drawing(0, 0)

    width, height = 16.5 * cm, 7.0 * cm
    left, bottom = 2.2 * cm, 1.4 * cm
    plot_w, plot_h = width - left - 1.2 * cm, height - bottom - 1.2 * cm

    drawing = Drawing(width, height)
    drawing.add(shapes.Line(left, bottom, left, bottom + plot_h,
                            strokeColor=LINE, strokeWidth=0.8))
    drawing.add(shapes.Line(left, bottom, left + plot_w, bottom,
                            strokeColor=LINE, strokeWidth=0.8))

    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        vmax += 10
    span = vmax - vmin

    def y_for(value: float) -> float:
        return bottom + (value - vmin) / span * plot_h

    steps = 4
    for i in range(steps + 1):
        value = vmin + (vmax - vmin) * i / steps
        y = y_for(value)
        drawing.add(shapes.Line(left, y, left + plot_w, y,
                                strokeColor=LINE, strokeWidth=0.4))
        drawing.add(shapes.String(
            left - 0.25 * cm, y - 0.12 * cm, f"{value:.0f}%",
            fontName="Helvetica", fontSize=7, fillColor=MUTED,
            textAnchor="end",
        ))

    n = len(values)
    step_x = plot_w / max(n - 1, 1)
    points = [(left + i * step_x, y_for(values[i])) for i in range(n)]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        drawing.add(shapes.Line(x0, y0, x1, y1, strokeColor=INDIGO, strokeWidth=2))
    for x, y in points:
        drawing.add(shapes.Circle(x, y, 2.4, fillColor=INDIGO, strokeColor=WHITE,
                                  strokeWidth=1))

    for i, (x, _y) in enumerate(points):
        drawing.add(shapes.String(
            x, bottom - 0.35 * cm, str(projections[i].get("period", ""))[:12],
            fontName="Helvetica", fontSize=6.5, fillColor=MUTED,
            textAnchor="middle",
        ))
    return drawing


def _is_number(text: str) -> bool:
    cleaned = text.replace(",", "").replace("%", "").replace("+", "").strip()
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def _parse_number(text: str) -> float:
    return float(text.replace(",", "").replace("%", "").replace("+", "").strip())


def _kpi_bar_chart(kpis: list[dict]) -> Drawing:
    """Hand-drawn vertical bar chart of KPI target leading numbers."""
    values = []
    for k in kpis:
        target = str(k.get("target", ""))
        nums = [float(_parse_number(s)) for s in target.split() if _is_number(s)]
        values.append(nums[0] if nums else 0)

    width, height = 16.5 * cm, 7.0 * cm
    left, bottom = 2.2 * cm, 1.4 * cm
    plot_w, plot_h = width - left - 1.2 * cm, height - bottom - 1.2 * cm

    drawing = Drawing(width, height)
    drawing.add(shapes.Line(left, bottom, left, bottom + plot_h,
                            strokeColor=LINE, strokeWidth=0.8))
    drawing.add(shapes.Line(left, bottom, left + plot_w, bottom,
                            strokeColor=LINE, strokeWidth=0.8))

    vmax = max(values) if values else 1
    vmax = vmax or 1
    n = len(values)
    slot = plot_w / max(n, 1)
    bar_w = min(0.9 * cm, slot * 0.55)

    for i, value in enumerate(values):
        bar_h = (value / vmax) * plot_h
        x = left + i * slot + (slot - bar_w) / 2
        drawing.add(shapes.Rect(x, bottom, bar_w, bar_h,
                                fillColor=INDIGO, strokeColor=None))
        drawing.add(shapes.String(
            x + bar_w / 2, bottom + bar_h + 0.15 * cm, f"{value:g}",
            fontName="Helvetica-Bold", fontSize=7, fillColor=SLATE,
            textAnchor="middle",
        ))
        drawing.add(shapes.String(
            x + bar_w / 2, bottom - 0.35 * cm,
            str(kpis[i].get("metric", ""))[:12],
            fontName="Helvetica", fontSize=6.5, fillColor=MUTED,
            textAnchor="middle",
        ))
    return drawing


def _progress_bar(value: float, width: float) -> Drawing:
    """A rounded progress bar (value 0-100) with a track."""
    d = Drawing(width, 0.5 * cm)
    d.add(shapes.Rect(0, 0, width, 0.42 * cm, rx=4, ry=4,
                      fillColor=PANEL, strokeColor=LINE, strokeWidth=0.5))
    fill_width = max(0.0, min(100.0, value)) / 100.0 * (width - 0.1 * cm)
    d.add(shapes.Rect(0.05 * cm, 0.03 * cm, fill_width, 0.36 * cm,
                      rx=3.5, ry=3.5, fillColor=INDIGO, strokeColor=None))
    return d


# ---------------------------------------------------------------------------
# Table helper
# ---------------------------------------------------------------------------


def _styled_table(header: list[str], rows: list[list[str]],
                  col_widths: list[float] | None = None) -> Table:
    data = [[Paragraph(f"<b>{_esc(h)}</b>", _BODY) for h in header]]
    for row in rows:
        data.append([Paragraph(_esc(cell), _BODY) for cell in row])

    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PANEL]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _bullet_list(items: list[Any]) -> list[Paragraph]:
    return [Paragraph(f"• {_esc(item)}", _BULLET) for item in items if str(item).strip()]


def _keep(items: list[Any]) -> KeepTogether:
    return KeepTogether(items)


# ---------------------------------------------------------------------------
# Section builders (each returns a list of flowables)
# ---------------------------------------------------------------------------


def _cover_flowables(strategy) -> list[Any]:
    now = strategy.created_at
    date_str = now.strftime("%B %d, %Y") if hasattr(now, "strftime") else ""
    content = strategy.content or {}
    exec_summary = content.get("executiveSummary") or {}
    tagline = exec_summary.get("ask") or "A data-driven marketing growth plan."
    business = strategy.name or "Marketing Strategy"

    # Logo mark: indigo rounded square with a white "M".
    logo_box = Table(
        [[Paragraph(
            "<font color='white' size='16'><b>M</b></font>",
            ParagraphStyle("Logo", parent=_BODY, alignment=TA_CENTER),
        )]],
        colWidths=[1.3 * cm], rowHeights=[1.3 * cm], hAlign="LEFT",
    )
    logo_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INDIGO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    flow: list[Any] = [
        Spacer(1, 3.2 * cm),
        logo_box,
        Spacer(1, 0.8 * cm),
        Paragraph(_esc(business), ParagraphStyle(
            "CoverTitle", parent=_TITLE, fontName="Helvetica-Bold", fontSize=30,
            leading=36, textColor=WHITE, alignment=TA_LEFT,
        )),
        Paragraph(
            "Marketing Strategy Report",
            ParagraphStyle(
                "CoverSub", parent=_TITLE, fontName="Helvetica-Bold",
                fontSize=15, leading=20, textColor=HexColor("#c7d2fe"),
                alignment=TA_LEFT, spaceBefore=4,
            ),
        ),
        Spacer(1, 1.4 * cm),
        Paragraph(_esc(tagline), ParagraphStyle(
            "CoverTag", parent=_BODY, fontSize=11, leading=16,
            textColor=HexColor("#e0e7ff"), alignment=TA_LEFT,
        )),
        Spacer(1, 2.2 * cm),
    ]

    industry = "—"
    market = content.get("marketOverview") or {}
    if market.get("targetMarketSize"):
        industry = market["targetMarketSize"]
    meta_rows = [
        [Paragraph("<font color='#c7d2fe'>INDUSTRY</font>", _META),
         Paragraph(_esc(industry), ParagraphStyle(
             "CoverMetaV", parent=_BODY, fontSize=10, textColor=WHITE))],
        [Paragraph("<font color='#c7d2fe'>TARGET AUDIENCE</font>", _META),
         Paragraph(_esc(strategy.target_audience or "—"), ParagraphStyle(
             "CoverMetaV", parent=_BODY, fontSize=10, textColor=WHITE))],
        [Paragraph("<font color='#c7d2fe'>GENERATION DATE</font>", _META),
         Paragraph(_esc(date_str or "—"), ParagraphStyle(
             "CoverMetaV", parent=_BODY, fontSize=10, textColor=WHITE))],
    ]
    meta_table = Table(meta_rows, colWidths=[4.2 * cm, 11.5 * cm], hAlign="LEFT")
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#1e1b4b")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, HexColor("#4338ca")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    flow.append(meta_table)
    flow.append(Spacer(1, 1.4 * cm))
    flow.append(Paragraph(
        "Prepared by <b>Market Mind AI</b> — Professional Consulting Report",
        ParagraphStyle("CoverFoot", parent=_META, fontSize=9,
                       textColor=HexColor("#a5b4fc"), alignment=TA_LEFT),
    ))
    return flow


def _summary_cards(content: dict) -> list[Any]:
    score = (content.get("marketingScore") or {}).get("overall")
    strategy = content.get("marketingStrategy") or {}
    objectives = len(strategy.get("objectives") or [])
    channels = len(strategy.get("channels") or [])

    cards = [
        ("MARKETING SCORE", _esc(score if score is not None else "—"), "/ 100"),
        ("OBJECTIVES", _esc(objectives), ""),
        ("CHANNELS", _esc(channels), ""),
    ]
    cell_w = (16.5 * cm - 2 * 0.5) / 3
    rows = []
    for label, value, suffix in cards:
        cell = [
            Paragraph(label, _CARD_LABEL),
            Spacer(1, 0.12 * cm),
            Paragraph(f"{value}<font size='9' color='#64748b'> {suffix}</font>", _CARD_VALUE),
        ]
        rows.append(cell)
    table = Table([rows], colWidths=[cell_w] * 3, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [_keep([table])]


def _toc_flowables(entries: list[tuple[str, int]]) -> list[Any]:
    flow = [Paragraph("Table of Contents", _H1), Spacer(1, 0.4 * cm)]
    rows = []
    for title, page in entries:
        rows.append([Paragraph(_esc(title), _TOC_STYLE),
                     Paragraph(_esc(page), _TOC_STYLE)])
    toc = Table(rows, colWidths=[14.2 * cm, 1.5 * cm], hAlign="LEFT")
    toc.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    flow.append(toc)
    return flow


def _executive_summary_flowables(content: dict) -> list[Any]:
    exec_summary = content.get("executiveSummary") or {}
    flow = [Paragraph("Executive Summary", _H1)]
    if exec_summary.get("summary"):
        flow.append(Paragraph(_esc(exec_summary["summary"]), _BODY))
    highlights = exec_summary.get("highlights") or []
    if highlights:
        flow.append(Paragraph("Key Highlights", _H2))
        flow.extend(_bullet_list(highlights))
    if exec_summary.get("ask"):
        flow.append(Spacer(1, 0.2 * cm))
        flow.append(Paragraph(
            f"<b>Recommendation:</b> {_esc(exec_summary['ask'])}", _BODY))
    flow.append(Spacer(1, 0.5 * cm))
    flow.extend(_summary_cards(content))
    return flow


def _marketing_score_flowables(content: dict) -> list[Any]:
    score = content.get("marketingScore") or {}
    flow = [Paragraph("Marketing Score", _H1)]
    if score.get("overall") is not None:
        flow.append(Paragraph(
            f"Overall readiness: <b>{_esc(score['overall'])}/100</b>", _BODY))
    if score.get("summary"):
        flow.append(Paragraph(_esc(score["summary"]), _BODY))
    if score.get("benchmark"):
        flow.append(Paragraph(f"<i>Benchmark: {_esc(score['benchmark'])}</i>", _META))
    for item in score.get("breakdown") or []:
        area = item.get("area", "")
        try:
            num = float(item.get("score"))
        except (TypeError, ValueError):
            num = 0
        flow.append(Spacer(1, 0.3 * cm))
        flow.append(Paragraph(
            f"<b>{_esc(area)}</b> — {_esc(item.get('assessment', ''))}", _BODY))
        flow.append(_progress_bar(num, 16.5 * cm))
        flow.append(Paragraph(
            f"{num:.0f} / 100",
            ParagraphStyle("ScoreNum", parent=_META, alignment=TA_CENTER),
        ))
    return flow


def _kpi_flowables(content: dict) -> list[Any]:
    strategy = content.get("marketingStrategy") or {}
    kpis = strategy.get("kpis") or []
    flow = [Paragraph("KPI Summary", _H1)]
    if not kpis:
        return flow
    rows = [[k.get("metric", ""), k.get("target", ""), k.get("timeframe", "")]
            for k in kpis]
    flow.append(_styled_table(["Metric", "Target", "Timeframe"], rows,
                              col_widths=[7.5 * cm, 4.5 * cm, 4.5 * cm]))
    flow.append(Spacer(1, 0.5 * cm))
    flow.append(_kpi_bar_chart(kpis))
    flow.append(Paragraph("KPI targets (leading number)", _CAPTION))
    return flow


def _budget_flowables(content: dict) -> list[Any]:
    strategy = content.get("marketingStrategy") or {}
    allocation = strategy.get("budgetAllocation") or []
    flow = [Paragraph("Budget Summary", _H1)]
    if not allocation:
        return flow
    flow.append(_keep([_budget_pie_chart(allocation)]))
    flow.append(Spacer(1, 0.5 * cm))
    rows = [[a.get("channel", ""), f"{a.get('percentage', 0)}%"] for a in allocation]
    flow.append(_styled_table(["Channel", "Allocation"], rows,
                              col_widths=[12.5 * cm, 4.0 * cm]))
    return flow


def _market_overview_flowables(content: dict) -> list[Any]:
    market = content.get("marketOverview") or {}
    flow = [Paragraph("Market Overview", _H1)]
    if market.get("summary"):
        flow.append(Paragraph(_esc(market["summary"]), _BODY))
    meta = []
    if market.get("targetMarketSize"):
        meta.append(f"Market size: {market.get('targetMarketSize')}")
    if market.get("growthRate"):
        meta.append(f"Growth rate: {market.get('growthRate')}")
    if meta:
        flow.append(Paragraph(" • ".join(meta), _META))
    for label, key in [("Market Trends", "marketTrends"),
                       ("Key Drivers", "keyDrivers"),
                       ("Market Risks", "marketRisks")]:
        items = market.get(key) or []
        if items:
            flow.append(Paragraph(label, _H2))
            flow.extend(_bullet_list(items))
    return flow


def _persona_flowables(content: dict) -> list[Any]:
    persona = content.get("customerPersona") or {}
    flow = [Paragraph("Customer Persona", _H1)]
    profile = [
        ("Name", persona.get("name")),
        ("Age range", persona.get("ageRange")),
        ("Location", persona.get("location")),
        ("Occupation", persona.get("occupation")),
        ("Income level", persona.get("incomeLevel")),
    ]
    rows = [[label, _esc(value or "—")] for label, value in profile]
    flow.append(_styled_table(["Attribute", "Profile"], rows,
                              col_widths=[4.5 * cm, 12.0 * cm]))
    if persona.get("summary"):
        flow.append(Spacer(1, 0.4 * cm))
        flow.append(Paragraph(_esc(persona["summary"]), _BODY))
    for label, key in [("Interests", "interests"), ("Pain Points", "painPoints"),
                       ("Goals", "goals"), ("Buying Triggers", "buyingTriggers"),
                       ("Common Objections", "objections"),
                       ("Preferred Channels", "preferredChannels")]:
        items = persona.get(key) or []
        if items:
            flow.append(Paragraph(label, _H2))
            flow.extend(_bullet_list(items))
    return flow


def _swot_flowables(content: dict) -> list[Any]:
    swot = content.get("swotAnalysis") or {}
    flow = [Paragraph("SWOT Analysis", _H1)]

    def quadrant(label: str, items: list[Any]) -> list[list[str]]:
        return [[Paragraph(f"<b>{_esc(label)}</b>", _BODY),
                 Paragraph("<br/>".join(f"• {_esc(i)}" for i in items), _BODY)]]

    quad_rows = (
        quadrant("Strengths", swot.get("strengths") or [])
        + quadrant("Weaknesses", swot.get("weaknesses") or [])
        + quadrant("Opportunities", swot.get("opportunities") or [])
        + quadrant("Threats", swot.get("threats") or [])
    )
    matrix = Table(quad_rows, colWidths=[4.0 * cm, 12.5 * cm], hAlign="LEFT")
    matrix.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), INDIGO_DARK),
        ("TEXTCOLOR", (0, 0), (0, -1), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(matrix)
    if swot.get("overallAssessment"):
        flow.append(Spacer(1, 0.4 * cm))
        flow.append(Paragraph(_esc(swot["overallAssessment"]), _BODY))
    return flow


def _channels_flowables(content: dict) -> list[Any]:
    strategy = content.get("marketingStrategy") or {}
    channels = strategy.get("channels") or []
    flow = [Paragraph("Marketing Channels", _H1)]
    if not channels:
        return flow
    rows = [[c.get("name", ""), c.get("priority", "").capitalize(),
             c.get("description", "")] for c in channels]
    flow.append(_styled_table(["Channel", "Priority", "Why / How"], rows,
                              col_widths=[3.5 * cm, 2.2 * cm, 10.8 * cm]))
    return flow


def _seo_flowables(content: dict) -> list[Any]:
    seo = content.get("seoKeywords") or {}
    flow = [Paragraph("SEO Strategy", _H1)]
    primary = seo.get("primaryKeywords") or []
    if primary:
        flow.append(Paragraph("Primary Keywords", _H2))
        rows = [[k.get("keyword", ""), k.get("intent", ""),
                 k.get("volume") or "—", k.get("difficulty") or "—",
                 k.get("priority", "")] for k in primary]
        flow.append(_styled_table(
            ["Keyword", "Intent", "Volume", "Difficulty", "Priority"],
            rows, col_widths=[4.5 * cm, 3.0 * cm, 2.4 * cm, 2.4 * cm, 2.2 * cm],
        ))
    topics = seo.get("contentTopics") or []
    if topics:
        flow.append(Paragraph("Content Topics", _H2))
        rows = [[t.get("title", ""), t.get("contentType") or "—",
                 t.get("targetKeyword", ""), t.get("funnelStage", "")] for t in topics]
        flow.append(_styled_table(["Title", "Format", "Target Keyword", "Stage"],
                                  rows, col_widths=[6.0 * cm, 3.0 * cm, 4.5 * cm, 3.0 * cm]))
    recs = seo.get("onPageRecommendations") or []
    if recs:
        flow.append(Paragraph("On-Page Recommendations", _H2))
        flow.extend(_bullet_list(recs))
    return flow


def _email_flowables(content: dict) -> list[Any]:
    email = content.get("emailCampaign") or {}
    flow = [Paragraph("Email Marketing Strategy", _H1)]
    name, goal, audience = (email.get("campaignName"), email.get("goal"),
                            email.get("audience"))
    if name or goal or audience:
        rows = [[label, _esc(value or "—")]
                for label, value in (("Campaign", name), ("Goal", goal),
                                     ("Audience", audience))]
        flow.append(_styled_table(["Field", "Value"], rows,
                                  col_widths=[4.0 * cm, 12.5 * cm]))
    subjects = email.get("subjectLines") or []
    if subjects:
        flow.append(Paragraph("Subject Lines", _H2))
        flow.extend(_bullet_list(subjects))
    seq = email.get("sequence") or []
    if seq:
        flow.append(Paragraph("Email Sequence", _H2))
        rows = [[f"Day {e.get('day', '')}", e.get("type", ""),
                 e.get("subject", ""), e.get("cta", "")] for e in seq]
        flow.append(_styled_table(["Day", "Type", "Subject", "CTA"],
                                  rows, col_widths=[1.6 * cm, 3.0 * cm, 8.4 * cm, 3.5 * cm]))
    return flow


def _social_flowables(content: dict) -> list[Any]:
    social = content.get("socialMediaStrategy") or {}
    flow = [Paragraph("Social Media Strategy", _H1)]
    if social.get("summary"):
        flow.append(Paragraph(_esc(social["summary"]), _BODY))
    platforms = social.get("platforms") or []
    if platforms:
        flow.append(Paragraph("Platforms", _H2))
        rows = [[p.get("name", ""), p.get("focus", ""),
                 p.get("postingCadence", ""),
                 ", ".join(p.get("goals") or [])] for p in platforms]
        flow.append(_styled_table(["Platform", "Focus", "Cadence", "Goals"],
                                  rows, col_widths=[2.8 * cm, 5.0 * cm, 3.0 * cm, 5.7 * cm]))
        for p in platforms:
            mix = p.get("contentMix") or []
            if mix:
                flow.append(Paragraph(
                    f"<b>{_esc(p.get('name', ''))}</b> content mix", _H2))
                flow.extend(_bullet_list(mix))
    cm_items = social.get("communityManagement") or []
    if cm_items:
        flow.append(Paragraph("Community Management", _H2))
        flow.extend(_bullet_list(cm_items))
    metrics = social.get("performanceMetrics") or []
    if metrics:
        flow.append(Paragraph("Social Performance Metrics", _H2))
        rows = [[m.get("metric", ""), m.get("target", "")] for m in metrics]
        flow.append(_styled_table(["Metric", "Target"], rows,
                                  col_widths=[12.0 * cm, 4.5 * cm]))
    return flow


def _ads_flowables(content: dict) -> list[Any]:
    ads = content.get("advertisementIdeas") or {}
    flow = [Paragraph("Google & Meta Ads Plan", _H1)]
    if ads.get("summary"):
        flow.append(Paragraph(_esc(ads["summary"]), _BODY))
    campaigns = ads.get("campaigns") or []
    if campaigns:
        flow.append(Paragraph("Campaigns", _H2))
        rows = [[c.get("name", ""), c.get("platform", ""), c.get("objective", ""),
                 c.get("budget", ""), c.get("duration", ""),
                 c.get("expectedOutcome", "")] for c in campaigns]
        flow.append(_styled_table(
            ["Campaign", "Platform", "Objective", "Budget", "Duration", "Expected"],
            rows, col_widths=[3.2 * cm, 2.4 * cm, 4.0 * cm, 2.4 * cm, 2.0 * cm, 2.5 * cm],
        ))
        for c in campaigns:
            copies = c.get("adCopy") or []
            if copies:
                flow.append(Paragraph(
                    f"<b>{_esc(c.get('name', ''))}</b> — ad copy", _H2))
                for copy in copies:
                    parts = [copy.get("headline", ""), copy.get("description", ""),
                             copy.get("cta", "")]
                    line = " / ".join(x for x in parts if x)
                    if line:
                        flow.append(Paragraph(f"• {_esc(line)}", _BULLET))
    return flow


def _calendar_flowables(content: dict) -> list[Any]:
    calendar = content.get("contentCalendar") or {}
    flow = [Paragraph("Content Calendar", _H1)]
    timeframe, cadence = calendar.get("timeframe"), calendar.get("cadence")
    if timeframe or cadence:
        flow.append(Paragraph(
            " • ".join(x for x in (timeframe, cadence) if x), _META))
    schedule = calendar.get("schedule") or []
    if schedule:
        rows = [[s.get("date", ""), s.get("channel", ""),
                 s.get("contentFormat", ""), s.get("topic", ""),
                 s.get("cta", "")] for s in schedule]
        flow.append(_styled_table(
            ["Date", "Channel", "Format", "Topic", "CTA"],
            rows, col_widths=[2.0 * cm, 2.6 * cm, 2.6 * cm, 6.2 * cm, 3.1 * cm],
        ))
    return flow


def _roadmap_flowables(content: dict) -> list[Any]:
    roadmap = content.get("implementationRoadmap") or {}
    flow = [Paragraph("90-Day Implementation Roadmap", _H1)]
    if roadmap.get("summary"):
        flow.append(Paragraph(_esc(roadmap["summary"]), _BODY))
    for phase in roadmap.get("phases") or []:
        name = phase.get("name", "")
        duration = phase.get("duration", "")
        flow.append(Spacer(1, 0.4 * cm))
        flow.append(Paragraph(
            f"<b>{_esc(name)}</b> <font color='#64748b'>— {_esc(duration)}</font>", _H2))
        flow.append(Paragraph("Objectives", _META))
        flow.extend(_bullet_list(phase.get("objectives") or []))
        flow.append(Paragraph("Key Activities", _META))
        flow.extend(_bullet_list(phase.get("keyActivities") or []))
        flow.append(Paragraph("Success Metrics", _META))
        flow.extend(_bullet_list(phase.get("successMetrics") or []))
    return flow


def _milestones_flowables(content: dict) -> list[Any]:
    milestones = content.get("weeklyMilestones") or {}
    flow = [Paragraph("Weekly Milestones", _H1)]
    if milestones.get("summary"):
        flow.append(Paragraph(_esc(milestones["summary"]), _BODY))
    weeks = milestones.get("weeks") or []
    if weeks:
        rows = [[w.get("week", ""), w.get("focus", ""),
                 w.get("owner") or "—",
                 w.get("successIndicator", "")] for w in weeks]
        flow.append(_styled_table(
            ["Week", "Focus", "Owner", "Success Indicator"],
            rows, col_widths=[2.2 * cm, 4.6 * cm, 3.0 * cm, 6.7 * cm],
        ))
    return flow


def _roi_flowables(content: dict) -> list[Any]:
    roi = content.get("estimatedROI") or {}
    flow = [Paragraph("Estimated ROI", _H1)]
    if roi.get("summary"):
        flow.append(Paragraph(_esc(roi["summary"]), _BODY))
    if roi.get("paybackPeriod"):
        flow.append(Paragraph(f"<b>Payback period:</b> {_esc(roi['paybackPeriod'])}", _BODY))
    projections = roi.get("projections") or []
    if projections:
        flow.append(Paragraph("Projections", _H2))
        rows = [[p.get("period", ""), p.get("investment", ""),
                 p.get("projectedReturn", ""), p.get("roiPercent", "")] for p in projections]
        flow.append(_styled_table(
            ["Period", "Investment", "Projected Return", "ROI"],
            rows, col_widths=[4.5 * cm, 4.0 * cm, 4.5 * cm, 3.5 * cm],
        ))
        flow.append(Spacer(1, 0.6 * cm))
        chart = _roi_line_chart(projections)
        if chart.width > 0:
            flow.append(chart)
            flow.append(Paragraph("ROI by period", _CAPTION))
    assumptions = roi.get("assumptions") or []
    if assumptions:
        flow.append(Paragraph("Assumptions", _H2))
        flow.extend(_bullet_list(assumptions))
    if roi.get("methodology"):
        flow.append(Paragraph("Methodology", _H2))
        flow.append(Paragraph(_esc(roi["methodology"]), _BODY))
    return flow


def _risks_flowables(content: dict) -> list[Any]:
    risks = content.get("riskMitigation") or {}
    flow = [Paragraph("Risks and Mitigation", _H1)]
    if risks.get("summary"):
        flow.append(Paragraph(_esc(risks["summary"]), _BODY))
    risk_list = risks.get("risks") or []
    if risk_list:
        rows = [[r.get("risk", ""), r.get("category", ""),
                 r.get("likelihood", "").capitalize(),
                 r.get("impact", "").capitalize(),
                 ", ".join(r.get("mitigation") or [])] for r in risk_list]
        flow.append(_styled_table(
            ["Risk", "Category", "Likelihood", "Impact", "Mitigation"],
            rows, col_widths=[4.4 * cm, 2.6 * cm, 2.0 * cm, 1.8 * cm, 5.7 * cm],
        ))
    return flow


def _recommendations_flowables(content: dict) -> list[Any]:
    recs = content.get("finalRecommendations") or {}
    flow = [Paragraph("Final Recommendations", _H1)]
    if recs.get("summary"):
        flow.append(Paragraph(_esc(recs["summary"]), _BODY))
    for label, key in [("Top Priorities", "priorities"),
                       ("Quick Wins", "quickWins"),
                       ("Long-Term Investments", "longTermInvestments"),
                       ("Success Criteria", "successCriteria")]:
        items = recs.get(key) or []
        if items:
            flow.append(Paragraph(label, _H2))
            flow.extend(_bullet_list(items))
    if recs.get("closingStatement"):
        flow.append(Spacer(1, 0.4 * cm))
        flow.append(Paragraph(_esc(recs["closingStatement"]), _BODY))
    return flow


def _competitor_flowables(content: dict) -> list[Any]:
    comp = content.get("competitorAnalysis") or {}
    flow = [Paragraph("Competitor Analysis", _H1)]
    competitors = comp.get("competitors") or []
    if competitors:
        rows = [[c.get("name", ""), c.get("marketPosition", ""),
                 c.get("threatLevel", "").capitalize(),
                 ", ".join(c.get("strengths") or []),
                 ", ".join(c.get("weaknesses") or [])] for c in competitors]
        flow.append(_styled_table(
            ["Competitor", "Position", "Threat", "Strengths", "Weaknesses"],
            rows, col_widths=[3.0 * cm, 3.2 * cm, 1.7 * cm, 4.3 * cm, 4.3 * cm],
        ))
    for label, key in [("Competitive Advantages", "competitiveAdvantages"),
                       ("Market Gaps", "marketGaps"),
                       ("Key Takeaways", "keyTakeaways")]:
        items = comp.get(key) or []
        if items:
            flow.append(Paragraph(label, _H2))
            flow.extend(_bullet_list(items))
    return flow


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

_SECTION_BUILDERS: list[tuple[str, Any]] = [
    ("Executive Summary", _executive_summary_flowables),
    ("Marketing Score", _marketing_score_flowables),
    ("KPI Summary", _kpi_flowables),
    ("Budget Summary", _budget_flowables),
    ("Market Overview", _market_overview_flowables),
    ("Customer Persona", _persona_flowables),
    ("SWOT Analysis", _swot_flowables),
    ("Competitor Analysis", _competitor_flowables),
    ("Marketing Channels", _channels_flowables),
    ("SEO Strategy", _seo_flowables),
    ("Email Marketing Strategy", _email_flowables),
    ("Social Media Strategy", _social_flowables),
    ("Google & Meta Ads Plan", _ads_flowables),
    ("Content Calendar", _calendar_flowables),
    ("90-Day Implementation Roadmap", _roadmap_flowables),
    ("Weekly Milestones", _milestones_flowables),
    ("Estimated ROI", _roi_flowables),
    ("Risks and Mitigation", _risks_flowables),
    ("Final Recommendations", _recommendations_flowables),
]


def _section_entries(content: dict) -> list[tuple[str, Any]]:
    """Return [(title, builder)] for sections present in the content."""
    entries = []
    for title, builder in _SECTION_BUILDERS:
        if builder is _kpi_flowables:
            present = bool(content.get("marketingStrategy", {}).get("kpis"))
        elif builder is _budget_flowables:
            present = bool(content.get("marketingStrategy", {}).get("budgetAllocation"))
        elif builder is _channels_flowables:
            present = bool(content.get("marketingStrategy", {}).get("channels"))
        else:
            # All other builders map to a top-level content key.
            key_map = {
                _executive_summary_flowables: "executiveSummary",
                _marketing_score_flowables: "marketingScore",
                _market_overview_flowables: "marketOverview",
                _persona_flowables: "customerPersona",
                _swot_flowables: "swotAnalysis",
                _competitor_flowables: "competitorAnalysis",
                _seo_flowables: "seoKeywords",
                _email_flowables: "emailCampaign",
                _social_flowables: "socialMediaStrategy",
                _ads_flowables: "advertisementIdeas",
                _calendar_flowables: "contentCalendar",
                _roadmap_flowables: "implementationRoadmap",
                _milestones_flowables: "weeklyMilestones",
                _roi_flowables: "estimatedROI",
                _risks_flowables: "riskMitigation",
                _recommendations_flowables: "finalRecommendations",
            }
            present = bool(content.get(key_map[builder]))
        if present:
            entries.append((title, builder))
    return entries


def _assemble_story(strategy, content: dict, entries: list[tuple[str, Any]],
                    toc_page_numbers: dict[str, int] | None) -> list[Any]:
    story: list[Any] = []
    story.append(NextPageTemplate("inner"))
    story.append(PageBreak())
    story.extend(_cover_flowables(strategy))
    story.append(PageBreak())
    story.extend(_executive_summary_flowables(content))
    story.append(PageBreak())
    if entries:
        toc_entries = [(title, (toc_page_numbers or {}).get(title, 0))
                       for title, _builder in entries]
        story.extend(_toc_flowables(toc_entries))
    for title, builder in entries:
        story.append(PageBreak())
        story.append(_PageMarker(title))
        story.extend(builder(content))
    return story


def _capture_page_numbers(story: list[Any], doc: _ReportDoc) -> dict[str, int]:
    """First build pass: record the page where each section marker lands."""
    captured: dict[str, int] = {}
    buffer = BytesIO()
    temp_doc = _ReportDoc(buffer, doc.report_title)
    replaced: list[Any] = []
    for flowable in story:
        if isinstance(flowable, _PageMarker):
            replaced.append(_CaptureMarker(flowable.title, captured, temp_doc))
        else:
            replaced.append(flowable)
    temp_doc.build(replaced)
    return captured


def build_strategy_report(strategy) -> bytes:
    """Render the full professional report as PDF bytes."""
    buffer = BytesIO()
    report_title = f"Marketing Strategy Report — {strategy.name}"
    doc = _ReportDoc(buffer, report_title)
    content = strategy.content or {}
    entries = _section_entries(content)

    # Pass 1: record TOC page numbers.
    pass1_story = _assemble_story(strategy, content, entries, toc_page_numbers=None)
    page_numbers = _capture_page_numbers(pass1_story, doc)

    # Pass 2: final build with the TOC populated.
    final_story = _assemble_story(strategy, content, entries,
                                  toc_page_numbers=page_numbers)
    doc.build(final_story)
    return buffer.getvalue()
