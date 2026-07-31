"""Reusable FastAPI dependencies.

Exposes get_current_user: the standard OAuth2 password-bearer dependency.
Any protected endpoint declares:

    current_user: User = Depends(get_current_user)
"""
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
)

CredentialsError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve the authenticated user from a Bearer token."""
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise CredentialsError

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError, AttributeError):
        raise CredentialsError

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise CredentialsError
    return user
