"""Authentication endpoints: register, login, token, me."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.token import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserService,
)

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: DbDep,
) -> User:
    """Create a user account and return its public profile."""
    service = UserService(db)
    try:
        return await service.register(payload)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login with email and password",
)
async def login(
    payload: LoginRequest,
    db: DbDep,
) -> Token:
    """Authenticate with JSON credentials and receive a Bearer token."""
    service = UserService(db)
    try:
        user = await service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(subject=user.id))


@router.post(
    "/token",
    response_model=Token,
    include_in_schema=False,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDep,
) -> Token:
    """OAuth2 password form endpoint backing the Swagger Authorize flow."""
    service = UserService(db)
    try:
        user = await service.authenticate(form_data.username, form_data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(subject=user.id))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
)
async def read_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the profile of the authenticated user."""
    return current_user
