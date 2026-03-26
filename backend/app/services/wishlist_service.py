from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wishlist_repo import WishlistRepository
from app.schemas.wishlist import WishlistItemOut


class WishlistService:
    """Business logic for the user wishlist (toggle & listing)."""

    def __init__(self, db: AsyncSession) -> None:
        self.wishlist_repo = WishlistRepository(db)
        self.db = db

    async def toggle(self, user_id: UUID, product_id: UUID) -> dict:
        """Toggle a product in the user's wishlist.

        Returns ``{"added": True}`` when the item was added and
        ``{"added": False}`` when it was removed.
        """
        added = await self.wishlist_repo.toggle(user_id, product_id)
        return {"added": added}

    async def get_user_wishlist(self, user_id: UUID) -> list[WishlistItemOut]:
        """Return all items in the user's wishlist, newest first."""
        items = await self.wishlist_repo.get_user_wishlist(user_id)
        return [
            WishlistItemOut(
                id=item.id,
                product_id=item.product.id,
                product_name=item.product.name,
                product_price=item.product.base_price,
                primary_image_url=item.product.primary_image_url,
                created_at=item.created_at,
            )
            for item in items
        ]
