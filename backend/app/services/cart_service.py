from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.constants import DELIVERY_FEE
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.schemas.cart import CartAddRequest, CartItemOut, CartSummary, CartUpdateRequest


class CartService:
    """Business logic for the shopping cart."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_cart(self, user_id: UUID) -> CartSummary:
        """Return the full cart summary for a user."""
        items = await self._fetch_cart_items(user_id)
        cart_items_out = [self._build_cart_item_out(ci) for ci in items]

        subtotal = sum(
            (item.unit_price * item.quantity for item in cart_items_out),
            Decimal("0.00"),
        )
        delivery_fee = DELIVERY_FEE if cart_items_out else Decimal("0.00")
        total = subtotal + delivery_fee

        return CartSummary(
            items=cart_items_out,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
            item_count=len(cart_items_out),
        )

    async def add_item(self, user_id: UUID, data: CartAddRequest) -> CartItemOut:
        """Add a variant to the cart or increment its quantity if it already
        exists.

        Raises NotFoundException when the variant does not exist.
        """
        # Verify the variant exists.
        variant = await self._get_variant(data.variant_id)
        if variant is None:
            raise NotFoundException("Product variant not found")

        # Check for an existing cart entry for this user + variant.
        result = await self.db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
                .selectinload(Product.images),
            )
            .where(
                CartItem.user_id == user_id,
                CartItem.variant_id == data.variant_id,
            )
        )
        existing: CartItem | None = result.scalar_one_or_none()

        if existing is not None:
            existing.quantity += data.quantity
            await self.db.flush()
            await self.db.refresh(existing)
            return self._build_cart_item_out(existing)

        cart_item = CartItem(
            user_id=user_id,
            variant_id=data.variant_id,
            quantity=data.quantity,
        )
        self.db.add(cart_item)
        await self.db.flush()
        # Reload with relationships.
        result = await self.db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
                .selectinload(Product.images),
            )
            .where(CartItem.id == cart_item.id)
        )
        cart_item = result.scalar_one()
        return self._build_cart_item_out(cart_item)

    async def update_item(
        self, user_id: UUID, item_id: UUID, data: CartUpdateRequest
    ) -> CartItemOut:
        """Update the quantity of a cart item.

        Raises NotFoundException when the item does not exist or does not
        belong to the user.
        """
        cart_item = await self._get_user_cart_item(user_id, item_id)
        if cart_item is None:
            raise NotFoundException("Cart item not found")

        cart_item.quantity = data.quantity
        await self.db.flush()
        await self.db.refresh(cart_item)

        return self._build_cart_item_out(cart_item)

    async def remove_item(self, user_id: UUID, item_id: UUID) -> None:
        """Remove an item from the cart.

        Raises NotFoundException when the item does not exist or does not
        belong to the user.
        """
        cart_item = await self._get_user_cart_item(user_id, item_id)
        if cart_item is None:
            raise NotFoundException("Cart item not found")

        await self.db.delete(cart_item)
        await self.db.flush()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _fetch_cart_items(self, user_id: UUID) -> list[CartItem]:
        """Fetch all cart items for a user with variant and product eagerly
        loaded."""
        result = await self.db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
                .selectinload(Product.images),
            )
            .where(CartItem.user_id == user_id)
        )
        return list(result.scalars().unique().all())

    async def _get_user_cart_item(
        self, user_id: UUID, item_id: UUID
    ) -> CartItem | None:
        """Fetch a single cart item ensuring it belongs to the given user."""
        result = await self.db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
                .selectinload(Product.images),
            )
            .where(CartItem.id == item_id, CartItem.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_variant(self, variant_id: UUID) -> ProductVariant | None:
        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.id == variant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _build_cart_item_out(cart_item: CartItem) -> CartItemOut:
        """Map a CartItem ORM instance (with loaded relationships) to the
        response schema."""
        variant = cart_item.variant
        product = variant.product

        unit_price = (
            variant.price_override
            if variant.price_override is not None
            else product.base_price
        )

        return CartItemOut(
            id=cart_item.id,
            variant_id=variant.id,
            product_name=product.name,
            variant_label=variant.variant_label,
            unit_price=unit_price,
            quantity=cart_item.quantity,
            image_url=product.primary_image_url,
        )
