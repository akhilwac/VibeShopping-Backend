from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Data-access layer for Category records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Category, db)

    async def get_all_active(self) -> list[Category]:
        """Return all active categories ordered by sort_order ascending."""
        result = await self.db.execute(
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.sort_order.asc())
        )
        return list(result.scalars().all())

    async def get_with_product_counts(self) -> list[tuple[Category, int]]:
        """Return all active categories together with the count of active
        products in each category.

        Returns a list of ``(Category, product_count)`` tuples.
        """
        product_count_subq = (
            select(
                Product.category_id,
                func.count(Product.id).label("product_count"),
            )
            .where(Product.is_active.is_(True))
            .group_by(Product.category_id)
            .subquery()
        )

        stmt = (
            select(
                Category,
                func.coalesce(product_count_subq.c.product_count, 0).label(
                    "product_count"
                ),
            )
            .outerjoin(
                product_count_subq,
                Category.id == product_count_subq.c.category_id,
            )
            .where(Category.is_active.is_(True))
            .order_by(Category.sort_order.asc())
        )

        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
