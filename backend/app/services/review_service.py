from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ConflictException, NotFoundException
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut


class ReviewService:
    """Business logic for product reviews."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user_id: UUID, data: ReviewCreate) -> ReviewOut:
        """Create a review for a product.

        Raises ConflictException if the user already reviewed this product.
        Raises NotFoundException if the product does not exist.
        """
        # Verify product exists.
        product_result = await self.db.execute(
            select(Product).where(Product.id == data.product_id)
        )
        product = product_result.scalar_one_or_none()
        if product is None:
            raise NotFoundException("Product not found")

        # Check for duplicate review.
        dup_result = await self.db.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == data.product_id,
            )
        )
        if dup_result.scalar_one_or_none() is not None:
            raise ConflictException("You have already reviewed this product")

        # Create the review.
        review = Review(
            user_id=user_id,
            product_id=data.product_id,
            rating=data.rating,
            comment=data.comment,
        )
        self.db.add(review)
        await self.db.flush()

        # Recompute avg_rating and review_count on the product.
        stats_result = await self.db.execute(
            select(
                func.count(Review.id).label("cnt"),
                func.avg(Review.rating).label("avg"),
            ).where(Review.product_id == data.product_id)
        )
        row = stats_result.one()
        product.review_count = row.cnt
        product.avg_rating = (
            Decimal(str(round(float(row.avg), 1))) if row.avg is not None else Decimal("0.0")
        )

        await self.db.flush()
        await self.db.refresh(review)

        # Fetch the user name for the response.
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one()

        return ReviewOut(
            id=review.id,
            user_id=review.user_id,
            user_name=user.full_name,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )

    async def get_product_reviews(
        self, product_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[ReviewOut], int]:
        """Return paginated reviews for a product.

        Returns ``(items, total_count)``.
        """
        count_result = await self.db.execute(
            select(func.count(Review.id)).where(Review.product_id == product_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        reviews = list(result.scalars().unique().all())

        items = [
            ReviewOut(
                id=r.id,
                user_id=r.user_id,
                user_name=r.user.full_name,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
            )
            for r in reviews
        ]
        return items, total
