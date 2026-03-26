from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_method import PaymentMethod
from app.repositories.base import BaseRepository


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    """Data-access layer for PaymentMethod records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(PaymentMethod, db)

    async def get_user_methods(self, user_id: UUID) -> list[PaymentMethod]:
        """Return all payment methods belonging to *user_id*."""
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_method_by_id(
        self, method_id: UUID, user_id: UUID
    ) -> PaymentMethod | None:
        """Fetch a single payment method by its ID, ensuring it belongs to
        *user_id* (ownership check).
        """
        result = await self.db.execute(
            select(PaymentMethod).where(
                PaymentMethod.id == method_id,
                PaymentMethod.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def clear_user_defaults(self, user_id: UUID) -> None:
        """Set ``is_default=False`` on every payment method belonging to
        *user_id*.

        Typically called right before marking a new method as default.
        """
        await self.db.execute(
            update(PaymentMethod)
            .where(
                PaymentMethod.user_id == user_id,
                PaymentMethod.is_default.is_(True),
            )
            .values(is_default=False)
        )
        await self.db.flush()
