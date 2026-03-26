from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate


class AddressService:
    """Business logic for user addresses."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, user_id: UUID) -> list[AddressOut]:
        """Return all addresses belonging to the user."""
        result = await self.db.execute(
            select(Address).where(Address.user_id == user_id)
        )
        addresses = list(result.scalars().all())
        return [AddressOut.model_validate(a) for a in addresses]

    async def create(self, user_id: UUID, data: AddressCreate) -> AddressOut:
        """Create a new address for the user.

        If ``is_default`` is set, all other addresses for the user have
        their default flag cleared first.
        """
        if data.is_default:
            await self._clear_defaults(user_id)

        address = Address(
            user_id=user_id,
            **data.model_dump(),
        )
        self.db.add(address)
        await self.db.flush()
        await self.db.refresh(address)

        return AddressOut.model_validate(address)

    async def update(
        self, user_id: UUID, address_id: UUID, data: AddressUpdate
    ) -> AddressOut:
        """Update an existing address.

        If ``is_default`` is being set to ``True``, other defaults are
        cleared first.
        Raises NotFoundException when the address does not exist or does not
        belong to the user.
        """
        address = await self._get_user_address(user_id, address_id)

        update_data = data.model_dump(exclude_unset=True)

        if update_data.get("is_default") is True:
            await self._clear_defaults(user_id)

        for field, value in update_data.items():
            setattr(address, field, value)

        await self.db.flush()
        await self.db.refresh(address)

        return AddressOut.model_validate(address)

    async def delete(self, user_id: UUID, address_id: UUID) -> None:
        """Delete an address.

        Raises NotFoundException when the address does not exist or does not
        belong to the user.
        """
        address = await self._get_user_address(user_id, address_id)
        await self.db.delete(address)
        await self.db.flush()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_user_address(
        self, user_id: UUID, address_id: UUID
    ) -> Address:
        """Fetch an address ensuring it belongs to the given user."""
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id, Address.user_id == user_id
            )
        )
        address = result.scalar_one_or_none()
        if address is None:
            raise NotFoundException("Address not found")
        return address

    async def _clear_defaults(self, user_id: UUID) -> None:
        """Set ``is_default = False`` for all of the user's addresses."""
        await self.db.execute(
            update(Address)
            .where(Address.user_id == user_id, Address.is_default.is_(True))
            .values(is_default=False)
        )
