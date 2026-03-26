from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodOut


class PaymentMethodService:
    """Business logic for saved payment methods."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, user_id: UUID) -> list[PaymentMethodOut]:
        """Return all payment methods belonging to the user."""
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.user_id == user_id)
        )
        methods = list(result.scalars().all())
        return [PaymentMethodOut.model_validate(m) for m in methods]

    async def create(
        self, user_id: UUID, data: PaymentMethodCreate
    ) -> PaymentMethodOut:
        """Save a new payment method for the user."""
        method = PaymentMethod(
            user_id=user_id,
            **data.model_dump(),
        )
        self.db.add(method)
        await self.db.flush()
        await self.db.refresh(method)

        return PaymentMethodOut.model_validate(method)

    async def delete(self, user_id: UUID, method_id: UUID) -> None:
        """Delete a saved payment method.

        Raises NotFoundException when the method does not exist or does not
        belong to the user.
        """
        result = await self.db.execute(
            select(PaymentMethod).where(
                PaymentMethod.id == method_id,
                PaymentMethod.user_id == user_id,
            )
        )
        method = result.scalar_one_or_none()
        if method is None:
            raise NotFoundException("Payment method not found")

        await self.db.delete(method)
        await self.db.flush()
