from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentInitiateRequest, PaymentOut, PaymentVerifyRequest


class PaymentService:
    """Business logic for payment initiation and verification."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def initiate(
        self, user_id: UUID, data: PaymentInitiateRequest
    ) -> PaymentOut:
        """Create a new pending Payment record for an order.

        Raises NotFoundException when the order does not exist or does not
        belong to the user.
        Raises BadRequestException when a payment already exists for the
        order.
        """
        order = await self._get_user_order(user_id, data.order_id)

        # Ensure no duplicate payment.
        existing_result = await self.db.execute(
            select(Payment).where(Payment.order_id == order.id)
        )
        if existing_result.scalar_one_or_none() is not None:
            raise BadRequestException("Payment already exists for this order")

        payment = Payment(
            order_id=order.id,
            payment_method_id=data.payment_method_id,
            amount=order.total,
            status=PaymentStatus.PENDING,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)

        return PaymentOut.model_validate(payment)

    async def verify(self, user_id: UUID, data: PaymentVerifyRequest) -> PaymentOut:
        """Mark a payment as completed and update the associated order.

        Raises NotFoundException when the order does not belong to the user
        or no pending payment exists for the given order.
        """
        order = await self._get_user_order(user_id, data.order_id)

        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order.id)
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            raise NotFoundException("Payment not found for this order")

        payment.gateway_txn_id = data.gateway_txn_id
        payment.status = PaymentStatus.COMPLETED
        payment.paid_at = datetime.now(timezone.utc)

        order.status = OrderStatus.CONFIRMED

        await self.db.flush()
        await self.db.refresh(payment)

        return PaymentOut.model_validate(payment)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_user_order(self, user_id: UUID, order_id: UUID) -> Order:
        """Fetch an order that belongs to the given user.

        Raises NotFoundException when not found.
        """
        result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise NotFoundException("Order not found")
        return order
