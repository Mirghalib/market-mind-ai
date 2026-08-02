"""Reusable SQLAlchemy mixins.

Every model composes three concerns:
  - UUIDPrimaryKeyMixin: uuid4 primary key
  - TimestampMixin:    created_at / updated_at (server-side now())
  - SoftDeleteMixin:   nullable deleted_at for soft deletes
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class UUIDPrimaryKeyTimestampMixin(UUIDPrimaryKeyMixin, TimestampMixin):
    """Convenience base for the common (uuid pk + timestamps) case."""
