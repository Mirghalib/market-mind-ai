"""MarketingStrategy model — the core AI-generated artifact."""
import uuid
from datetime import datetime

from enum import Enum

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, UUIDPrimaryKeyTimestampMixin


class StrategyStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class MarketingStrategy(UUIDPrimaryKeyTimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "marketing_strategies"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="List of strategy goal strings"
    )
    content: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Structured AI-generated strategy payload",
    )
    status: Mapped[StrategyStatus] = mapped_column(
        SqlEnum(StrategyStatus, name="strategy_status"),
        default=StrategyStatus.DRAFT,
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="marketing_strategies")
    generation_history: Mapped[list["GenerationHistory"]] = relationship(
        back_populates="strategy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    exports: Mapped[list["Export"]] = relationship(
        back_populates="strategy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<MarketingStrategy id={self.id} name={self.name!r}>"


from app.models.export import Export  # noqa: E402
from app.models.generation_history import GenerationHistory  # noqa: E402
from app.models.project import Project  # noqa: E402
