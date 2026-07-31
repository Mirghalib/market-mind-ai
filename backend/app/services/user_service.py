"""User domain logic: registration, authentication and lookup.

Dependencies: database session + security primitives only. Raises
plain exceptions; the API layer translates them into HTTP errors.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class EmailAlreadyRegisteredError(Exception):
    """Raised when registering an email that already exists."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials do not match a user."""


class UserNotFoundError(Exception):
    """Raised when a user id does not exist."""


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def register(self, data: UserCreate) -> User:
        email = data.email.lower()
        if await self.get_by_email(email):
            raise EmailAlreadyRegisteredError(email)

        user = User(
            email=email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.get_by_email(email.lower())
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return user
