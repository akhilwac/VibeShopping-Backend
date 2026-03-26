from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Data-access layer for Order records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Order, db)

    async def get_user_orders(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Order], int]:
        """Return a paginated list of orders for *user_id* (newest first)
        together with the total count.
        """
        count_stmt = (
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        rows_stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        rows_result = await self.db.execute(rows_stmt)
        orders = list(rows_result.scalars().all())

        return orders, total

    async def get_user_order_by_id(
        self, order_id: UUID, user_id: UUID
    ) -> Order | None:
        """Fetch a single order by its ID, ensuring it belongs to *user_id*
        (ownership check).
        """
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
