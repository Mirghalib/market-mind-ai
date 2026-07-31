"""Reusable FastAPI dependencies.

Exposes get_current_user: HTTP Bearer authentication. Any protected
endpoint declares:

    current_user: User = Depends(get_current_user)

The Swagger "Authorize" popup therefore shows a single "Value" field
for pasting a JWT (Bearer <token>), instead of the OAuth2 password
dialog. JWT validation itself is unchanged.
"""
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

# HTTP Bearer security: Swagger shows one "Value" field where the
# caller pastes "Bearer <jwt>" (or just the JWT). It replaces the
# OAuth2 password dialog, which required username/password form
# fields that this API does not use for authentication.
#
# auto_error=False lets us raise the 401 ourselves with a
# WWW-Authenticate header; True would let FastAPI raise a bare 403.
bearer_scheme = HTTPBearer(auto_error=False)

CredentialsError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve the authenticated user from a Bearer token."""
    if credentials is None:
        raise CredentialsError

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise CredentialsError

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError, AttributeError):
        raise CredentialsError

    # Eager-load the role so downstream serialization (role_name, JWT
    # claims) never triggers a lazy load outside an async context.
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise CredentialsError
    return user
