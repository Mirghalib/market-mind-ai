"""Business logic layer.

Services orchestrate models and schemas. Domain rules live here, not
in the API endpoints. Start with a concrete model + schema:

    class UserService(BaseService[User, UserCreate, UserUpdate]):
        pass
"""
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD scaffold for async SQLAlchemy sessions."""

    model: type[ModelType]  # set on the concrete subclass

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
