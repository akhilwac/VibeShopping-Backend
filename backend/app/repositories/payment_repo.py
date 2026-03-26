from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Data-access layer for Payment records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Payment, db)

    async def get_by_order_id(self, order_id: UUID) -> Payment | None:
        """Fetch the payment associated with a given order."""
        result = await self.db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_gateway_txn_id(self, txn_id: str) -> Payment | None:
        """Look up a payment by the external gateway transaction ID.

        Useful for processing webhook callbacks from payment providers.
        """
        result = await self.db.execute(
            select(Payment).where(Payment.gateway_txn_id == txn_id)
        )
        return result.scalar_one_or_none()
