"""User model — account records."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin, UUIDPrimaryKeyTimestampMixin


class User(UUIDPrimaryKeyTimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id"),
        index=True,
        nullable=True,
        comment="RBAC role; None until a seeder/admin assigns one",
    )
    profile_image: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Relative path of the profile image, e.g. uploads/profile_images/<uuid>.jpg",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Last successful login timestamp",
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    role: Mapped["Role | None"] = relationship(back_populates="users")

    projects: Mapped[list["Project"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    invitations: Mapped[list["Invitation"]] = relationship(
        back_populates="inviter",
        foreign_keys="Invitation.invited_by",
        passive_deletes=True,
    )

    @property
    def role_name(self) -> str | None:
        """Shortcut for JWT claims and dashboard responses."""
        return self.role.name if self.role else None

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


from app.models.invitation import Invitation  # noqa: E402  (typing only)
from app.models.project import Project  # noqa: E402  (typing only)
from app.models.role import Role  # noqa: E402  (typing only)
