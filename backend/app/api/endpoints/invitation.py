"""Public invitation endpoints: validate a token and accept an invite."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.user import UserRead
from app.services.invitation_service import (
    DuplicateInviteError,
    InvitationService,
    InviteAlreadyAcceptedError,
    InviteExpiredError,
    InviteNotFoundError,
    InviteRevokedError,
)

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]


class AcceptInviteRequest(BaseModel):
    """Payload for accepting an invitation."""

    token: str = Field(min_length=10)
    full_name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=128)


@router.get(
    "/validate",
    summary="Validate an invitation token (public)",
)
async def validate_invitation(
    db: DbDep,
    token: str = "",
) -> dict:
    """Return invitation details when the token is valid and unused."""
    service = InvitationService(db)
    try:
        invitation = await service.validate_token(token)
    except InviteNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This invitation link is invalid.",
        )
    except InviteAlreadyAcceptedError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has already been used.",
        )
    except InviteRevokedError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has been revoked.",
        )
    except InviteExpiredError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has expired. Ask the admin to send a new one.",
        )
    return {
        "email": invitation.email,
        "full_name": invitation.full_name,
        "role_name": invitation.role_name,
        "expires_at": invitation.expires_at.isoformat(),
    }


@router.post(
    "/accept",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    summary="Accept an invitation and activate the account (public)",
)
async def accept_invitation(
    payload: AcceptInviteRequest,
    db: DbDep,
) -> UserRead:
    """Create the invited user's account and activate it."""
    service = InvitationService(db)
    try:
        user = await service.accept_invitation(
            payload.token,
            password=payload.password,
            full_name=payload.full_name,
        )
    except InviteNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This invitation link is invalid.",
        )
    except InviteAlreadyAcceptedError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has already been used.",
        )
    except InviteRevokedError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has been revoked.",
        )
    except InviteExpiredError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has expired. Ask the admin to send a new one.",
        )
    except DuplicateInviteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return UserRead.model_validate(user)
