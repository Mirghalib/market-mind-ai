"""Strategy export renderers.

Each format is a ``Renderer`` that turns a MarketingStrategy into
file bytes plus the metadata needed for an HTTP file response
(media type, file extension). New formats — PDF, DOCX, Markdown,
HTML — are added by implementing the protocol and registering the
class in ``RENDERERS``; the endpoint and service stay untouched.
"""
from dataclasses import dataclass

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


class JsonRenderer(BaseRenderer):
    """Serialise the strategy document as a JSON file."""

    format = ExportFormat.JSON

    def render(self, strategy: MarketingStrategy) -> RenderedExport:
        import json

        document = {
            "strategy_id": str(strategy.id),
            "name": strategy.name,
            "target_audience": strategy.target_audience,
            "goals": strategy.goals,
            "status": strategy.status.value,
            "content": strategy.content,
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat(),
        }
        payload = json.dumps(document, indent=2, ensure_ascii=False).encode("utf-8")
        return RenderedExport(
            content=payload,
            media_type="application/json",
            file_extension="json",
        )


# Maps ExportFormat values to their renderer. Extend here to add
# PDF/DOCX/etc. renderers without touching the service or endpoint.
RENDERERS: dict[ExportFormat, BaseRenderer] = {
    JsonRenderer.format: JsonRenderer(),
}


def get_renderer(format_: ExportFormat) -> BaseRenderer:
    """Return the renderer for a format, raising if none is registered."""
    try:
        return RENDERERS[format_]
    except KeyError:
        raise ValueError(f"Unsupported export format: {format_.value}") from None
