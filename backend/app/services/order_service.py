from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.constants import DELIVERY_FEE
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.cart_item import CartItem
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product_variant import ProductVariant
from app.schemas.order import OrderCreateRequest, OrderItemOut, OrderListItem, OrderOut


class OrderService:
    """Business logic for order creation and retrieval."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_order(
        self, user_id: UUID, data: OrderCreateRequest
    ) -> OrderOut:
        """Convert the user's cart into an order.

        Steps:
        1. Fetch the user's cart items.
        2. Verify the cart is not empty.
        3. Create the Order with computed totals.
        4. Create OrderItems, snapshotting product_name, variant_label,
           and unit_price from the variant/product relationships.
        5. Clear the cart.
        6. Return the fully-formed OrderOut.

        Raises BadRequestException when the cart is empty.
        """
        # 1. Fetch cart items with relationships.
        result = await self.db.execute(
            select(CartItem)
            .options(
                joinedload(CartItem.variant).joinedload(ProductVariant.product),
            )
            .where(CartItem.user_id == user_id)
        )
        cart_items = list(result.scalars().unique().all())

        # 2. Cart must not be empty.
        if not cart_items:
            raise BadRequestException("Cart is empty")

        # 3. Compute totals and create order.
        subtotal = Decimal("0.00")
        order_items: list[OrderItem] = []

        for ci in cart_items:
            variant = ci.variant
            product = variant.product

            # Validate stock availability.
            if variant.stock_quantity < ci.quantity:
                raise BadRequestException(
                    f"Insufficient stock for '{product.name} - {variant.variant_label}' "
                    f"(available: {variant.stock_quantity}, requested: {ci.quantity})"
                )

            unit_price = (
                variant.price_override
                if variant.price_override is not None
                else product.base_price
            )
            line_total = unit_price * ci.quantity
            subtotal += line_total

            # Decrement stock.
            variant.stock_quantity -= ci.quantity

            order_items.append(
                OrderItem(
                    variant_id=variant.id,
                    product_name=product.name,
                    variant_label=variant.variant_label,
                    unit_price=unit_price,
                    quantity=ci.quantity,
                )
            )

        delivery_fee = DELIVERY_FEE
        total = subtotal + delivery_fee

        order = Order(
            user_id=user_id,
            address_id=data.address_id,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
            items=order_items,
        )
        self.db.add(order)
        await self.db.flush()

        # 5. Clear the cart (bulk delete).
        await self.db.execute(
            delete(CartItem).where(CartItem.user_id == user_id)
        )
        await self.db.flush()

        await self.db.refresh(order)

        # 6. Return OrderOut.
        return self._to_order_out(order)

    async def get_orders(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[OrderListItem], int]:
        """Return a paginated list of orders for the user.

        Returns ``(items, total_count)``.
        """
        count_result = await self.db.execute(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Order)
            .options(joinedload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        orders = list(result.scalars().unique().all())

        items = [
            OrderListItem(
                id=o.id,
                status=o.status,
                total=o.total,
                item_count=len(o.items),
                created_at=o.created_at,
            )
            for o in orders
        ]
        return items, total

    async def get_order_detail(self, user_id: UUID, order_id: UUID) -> OrderOut:
        """Fetch full order detail.

        Raises NotFoundException when the order does not exist or does not
        belong to the user.
        """
        result = await self.db.execute(
            select(Order)
            .options(joinedload(Order.items))
            .where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise NotFoundException("Order not found")

        return self._to_order_out(order)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_order_out(order: Order) -> OrderOut:
        return OrderOut(
            id=order.id,
            status=order.status,
            subtotal=order.subtotal,
            delivery_fee=order.delivery_fee,
            total=order.total,
            items=[
                OrderItemOut(
                    id=oi.id,
                    product_name=oi.product_name,
                    variant_label=oi.variant_label,
                    unit_price=oi.unit_price,
                    quantity=oi.quantity,
                )
                for oi in order.items
            ],
            created_at=order.created_at,
        )
