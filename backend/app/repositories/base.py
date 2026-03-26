from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing common CRUD operations.

    All concrete repositories should inherit from this class, specifying
    the SQLAlchemy model type as the generic parameter.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Fetch a single record by its primary key."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Fetch all records with offset/limit pagination (ordered by PK for stability)."""
        result = await self.db.execute(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Add a new record to the session and flush to obtain generated values."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType, data: dict) -> ModelType:
        """Apply a dict of updates to an existing record, flush, and refresh."""
        for field, value in data.items():
            setattr(obj, field, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a record from the session and flush."""
        await self.db.delete(obj)
        await self.db.flush()
