from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Data-access layer for Review records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Review, db)

    async def get_product_reviews(
        self, product_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        """Return a paginated list of reviews for *product_id* (newest first)
        with the user relationship eagerly loaded, together with the total
        count.
        """
        count_stmt = (
            select(func.count(Review.id)).where(
                Review.product_id == product_id
            )
        )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        rows_stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        rows_result = await self.db.execute(rows_stmt)
        reviews = list(rows_result.scalars().unique().all())

        return reviews, total

    async def get_by_user_and_product(
        self, user_id: UUID, product_id: UUID
    ) -> Review | None:
        """Find an existing review by a specific user for a specific product.

        Useful for enforcing the one-review-per-user-per-product constraint
        at the application level.
        """
        result = await self.db.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()
