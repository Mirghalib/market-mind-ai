"""Permission model — a granular capability (create_strategy, etc.)."""
import uuid
from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import UUIDPrimaryKeyTimestampMixin


class Permission(UUIDPrimaryKeyTimestampMixin, Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Roles that carry this permission, through the join table.
    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission id={self.id} name={self.name!r}>"


from app.models.role import Role  # noqa: E402  (typing only)
