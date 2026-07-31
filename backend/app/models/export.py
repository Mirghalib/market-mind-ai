"""Export model — rendered artifacts of a marketing strategy."""
import uuid
from datetime import datetime

from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import UUIDPrimaryKeyTimestampMixin


class ExportFormat(str, Enum):
    JSON = "json"
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    HTML = "html"


class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Export(UUIDPrimaryKeyTimestampMixin, Base):
    __tablename__ = "exports"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("marketing_strategies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    format: Mapped[ExportFormat] = mapped_column(
        SqlEnum(ExportFormat, name="export_format"),
        default=ExportFormat.PDF,
        nullable=False,
    )
    file_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Object-storage key of the rendered file",
    )
    file_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    status: Mapped[ExportStatus] = mapped_column(
        SqlEnum(ExportStatus, name="export_status"),
        default=ExportStatus.PENDING,
        nullable=False,
    )

    strategy: Mapped["MarketingStrategy"] = relationship(
        back_populates="exports"
    )

    def __repr__(self) -> str:
        return (
            f"<Export id={self.id} format={self.format.value} "
            f"status={self.status.value}>"
        )


from app.models.marketing_strategy import MarketingStrategy  # noqa: E402
