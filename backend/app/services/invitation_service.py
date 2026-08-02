"""Invitation domain logic: create, validate, and redeem admin invites."""
import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invitation import Invitation
from app.models.role import Role
from app.models.user import User

logger = logging.getLogger("market_mind_ai.invitations")

INVITE_TTL_DAYS = 7


class InviteNotFoundError(Exception):
    """Raised when an invitation token does not exist."""


class InviteExpiredError(Exception):
    """Raised when an invitation has expired."""


class InviteRevokedError(Exception):
    """Raised when an invitation has been revoked."""


class InviteAlreadyAcceptedError(Exception):
    """Raised when an invitation has already been used."""


class DuplicateInviteError(Exception):
    """Raised when the invitee already has an account or pending invite."""


class InvalidInviteError(Exception):
    """Raised when the invitation is not redeemable."""


def hash_token(token: str) -> str:
    """Store only a hash of the invite token (never the raw token)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class InvitationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_invitation(
        self,
        *,
        email: str,
        full_name: str | None,
        role_name: str,
        invited_by: uuid.UUID | None,
    ) -> tuple[Invitation, str]:
        """Create an invitation and return (record, raw_token).

        The raw token is only returned once; only its hash is stored.
        """
        email = email.lower()
        existing_user = await self.db.scalar(
            select(User).where(func.lower(User.email) == email)
        )
        if existing_user is not None:
            raise DuplicateInviteError("A user with this email already exists")

        existing_invite = await self.db.scalar(
            select(Invitation).where(
                func.lower(Invitation.email) == email,
                Invitation.accepted_at.is_(None),
                Invitation.revoked_at.is_(None),
            )
        )
        if existing_invite is not None:
            raise DuplicateInviteError("An invitation to this email is still pending")

        role = await self.db.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            role_name = "user"

        token = secrets.token_urlsafe(32)
        invitation = Invitation(
            email=email,
            full_name=full_name,
            role_name=role_name,
            token_hash=hash_token(token),
            invited_by=invited_by,
            expires_at=datetime.now(timezone.utc) + timedelta(days=INVITE_TTL_DAYS),
        )
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation, token

    async def get_by_token(self, token: str) -> Invitation:
        invitation = await self.db.scalar(
            select(Invitation).where(Invitation.token_hash == hash_token(token))
        )
        if invitation is None:
            raise InviteNotFoundError()
        return invitation

    async def validate_token(self, token: str) -> Invitation:
        """Validate an invitation token for the accept page."""
        invitation = await self.get_by_token(token)
        if invitation.is_accepted:
            raise InviteAlreadyAcceptedError()
        if invitation.is_revoked:
            raise InviteRevokedError()
        if invitation.is_expired:
            raise InviteExpiredError()
        return invitation

    async def accept_invitation(
        self, token: str, *, password: str, full_name: str | None = None
    ) -> User:
        """Redeem an invitation: create the account and mark it accepted."""
        invitation = await self.validate_token(token)

        existing = await self.db.scalar(
            select(User).where(func.lower(User.email) == invitation.email)
        )
        if existing is not None:
            raise DuplicateInviteError("A user with this email already exists")

        from app.core.security import hash_password

        role = await self.db.scalar(
            select(Role).where(Role.name == invitation.role_name)
        )
        user = User(
            email=invitation.email,
            full_name=full_name or invitation.full_name,
            hashed_password=hash_password(password),
            is_active=True,
            is_email_verified=True,
            email_verified_at=datetime.now(timezone.utc),
            role_id=role.id if role else None,
        )
        self.db.add(user)
        await self.db.flush()

        invitation.accepted_at = datetime.now(timezone.utc)
        await self.db.commit()

        from sqlalchemy.orm import selectinload

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user.id)
        )
        return result.scalar_one()

    async def revoke_invitation(self, invitation_id: uuid.UUID) -> bool:
        invitation = await self.db.get(Invitation, invitation_id)
        if invitation is None:
            return False
        invitation.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def list_invitations(self) -> list[Invitation]:
        result = await self.db.execute(
            select(Invitation).order_by(Invitation.created_at.desc())
        )
        return list(result.scalars().all())
