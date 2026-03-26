from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.address import Address
from app.repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    """Data-access layer for Address records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Address, db)

    async def get_user_addresses(self, user_id: UUID) -> list[Address]:
        """Return all addresses belonging to *user_id*."""
        result = await self.db.execute(
            select(Address).where(Address.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_address_by_id(
        self, address_id: UUID, user_id: UUID
    ) -> Address | None:
        """Fetch a single address by its ID, ensuring it belongs to
        *user_id* (ownership check).
        """
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def clear_user_defaults(self, user_id: UUID) -> None:
        """Set ``is_default=False`` on every address belonging to *user_id*.

        Typically called right before marking a new address as default.
        """
        await self.db.execute(
            update(Address)
            .where(Address.user_id == user_id, Address.is_default.is_(True))
            .values(is_default=False)
        )
        await self.db.flush()
