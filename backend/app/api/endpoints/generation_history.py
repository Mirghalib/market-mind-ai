"""Generation history endpoints: list, retrieve and delete audit records."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.generation_history import GenerationHistory
from app.models.user import User
from app.schemas.generation_history import (
    GenerationHistoryPage,
    GenerationHistoryRead,
)
from app.services.generation_history_service import (
    GenerationHistoryNotFoundError,
    GenerationHistoryService,
)

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "",
    response_model=GenerationHistoryPage,
    summary="List generation history",
)
async def list_generation_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
    strategy_id: Annotated[uuid.UUID | None, Query(description="Filter by strategy")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> GenerationHistoryPage:
    """Return paginated generation records, newest first.

    Records are the append-only audit log of AI generation runs. The
    ``strategy_id`` query parameter narrows the list to one strategy.
    """
    service = GenerationHistoryService(db)
    items, total = await service.list(
        strategy_id=strategy_id,
        limit=limit,
        offset=offset,
    )
    return GenerationHistoryPage(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
    )


@router.get(
    "/{history_id}",
    response_model=GenerationHistoryRead,
    summary="Get one generation history record",
)
async def get_generation_history(
    history_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> GenerationHistory:
    """Return a single generation record by id."""
    service = GenerationHistoryService(db)
    try:
        return await service.get(history_id)
    except GenerationHistoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation history record not found",
        )


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a generation history record",
)
async def delete_generation_history(
    history_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DbDep,
) -> None:
    """Permanently delete a generation record by id."""
    service = GenerationHistoryService(db)
    try:
        await service.delete(history_id)
    except GenerationHistoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation history record not found",
        )
