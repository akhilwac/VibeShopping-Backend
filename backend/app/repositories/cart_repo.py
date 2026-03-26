from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_item import CartItem
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[CartItem]):
    """Data-access layer for CartItem records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(CartItem, db)

    async def get_user_cart(self, user_id: UUID) -> list[CartItem]:
        """Return all cart items for a user with the variant (and its
        product) eagerly loaded.
        """
        result = await self.db.execute(
            select(CartItem)
            .options(
                selectinload(CartItem.variant)
            )
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_item(
        self, user_id: UUID, variant_id: UUID
    ) -> CartItem | None:
        """Find a cart item by user and variant (the natural unique pair)."""
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.variant_id == variant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_item_by_id(
        self, item_id: UUID, user_id: UUID
    ) -> CartItem | None:
        """Fetch a cart item by its primary key, ensuring it belongs to
        *user_id* (ownership check).
        """
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.id == item_id,
                CartItem.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def clear_user_cart(self, user_id: UUID) -> None:
        """Delete all cart items belonging to *user_id*."""
        await self.db.execute(
            delete(CartItem).where(CartItem.user_id == user_id)
        )
        await self.db.flush()
