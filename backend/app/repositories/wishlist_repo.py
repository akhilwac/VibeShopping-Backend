from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.product import Product
from app.models.wishlist import Wishlist
from app.repositories.base import BaseRepository


class WishlistRepository(BaseRepository[Wishlist]):
    """Data-access layer for Wishlist records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Wishlist, db)

    async def get_by_user_and_product(
        self, user_id: UUID, product_id: UUID
    ) -> Wishlist | None:
        """Find an existing wishlist entry for a specific user + product pair."""
        result = await self.db.execute(
            select(Wishlist).where(
                Wishlist.user_id == user_id,
                Wishlist.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_wishlist(self, user_id: UUID) -> list[Wishlist]:
        """Return all wishlist items for a user with the product relationship
        eagerly loaded, ordered by creation date descending.
        """
        result = await self.db.execute(
            select(Wishlist)
            .options(
                joinedload(Wishlist.product).selectinload(Product.images),
            )
            .where(Wishlist.user_id == user_id)
            .order_by(Wishlist.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def toggle(self, user_id: UUID, product_id: UUID) -> bool:
        """Toggle a product in the user's wishlist.

        If the entry exists it is removed and ``False`` is returned.
        If the entry does not exist it is created and ``True`` is returned.
        """
        existing = await self.get_by_user_and_product(user_id, product_id)
        if existing is not None:
            await self.delete(existing)
            return False

        new_entry = Wishlist(user_id=user_id, product_id=product_id)
        await self.create(new_entry)
        return True
