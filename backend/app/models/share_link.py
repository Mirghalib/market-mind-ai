"""ShareLink model — secure, expiring public links to exported reports."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import UUIDPrimaryKeyTimestampMixin


class ShareLink(UUIDPrimaryKeyTimestampMixin, Base):
    __tablename__ = "share_links"

    export_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exports.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    download_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    export: Mapped["Export"] = relationship(back_populates="share_links")

    def __repr__(self) -> str:
        return f"<ShareLink id={self.id} export_id={self.export_id}>"


from app.models.export import Export  # noqa: E402  (typing only)
