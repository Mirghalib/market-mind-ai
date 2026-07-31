"""Role model — a named role (admin, user) with a set of permissions."""
import uuid
from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import UUIDPrimaryKeyTimestampMixin


class Role(UUIDPrimaryKeyTimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Users holding this role.
    users: Mapped[list["User"]] = relationship(back_populates="role")

    # Permissions granted to this role, through the join table.
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r}>"


from app.models.user import User  # noqa: E402  (typing only)
from app.models.permission import Permission  # noqa: E402  (typing only)
