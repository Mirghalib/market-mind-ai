"""GenerationHistory model — append-only audit log of AI generation runs."""
import uuid
from datetime import datetime

from enum import Enum

from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import UUIDPrimaryKeyTimestampMixin


class GenerationStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class GenerationHistory(UUIDPrimaryKeyTimestampMixin, Base):
    __tablename__ = "generation_history"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("marketing_strategies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    model_used: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    input_params: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Request payload sent to the model",
    )
    output: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Raw model response",
    )
    tokens_used: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Token usage breakdown, e.g. {prompt, completion, total}",
    )
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[GenerationStatus] = mapped_column(
        SqlEnum(GenerationStatus, name="generation_status"),
        default=GenerationStatus.SUCCESS,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    strategy: Mapped["MarketingStrategy"] = relationship(
        back_populates="generation_history"
    )

    def __repr__(self) -> str:
        return (
            f"<GenerationHistory id={self.id} "
            f"strategy_id={self.strategy_id} status={self.status.value}>"
        )


from app.models.marketing_strategy import MarketingStrategy  # noqa: E402
