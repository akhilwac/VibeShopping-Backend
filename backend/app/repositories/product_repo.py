from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.wishlist import Wishlist
from app.repositories.base import BaseRepository
from app.schemas.product import ProductSearchParams


class ProductRepository(BaseRepository[Product]):
    """Data-access layer for Product records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Product, db)

    async def get_by_id(self, id: UUID) -> Product | None:
        """Fetch a single *active* product with variants and images.

        Returns ``None`` when the product does not exist or is inactive.
        """
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
            )
            .where(
                Product.id == id,
                Product.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_featured(self, limit: int = 10) -> list[Product]:
        """Return up to *limit* featured, active products ordered newest first."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.is_featured.is_(True),
                Product.is_active.is_(True),
            )
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        params: ProductSearchParams,
        category_id: UUID | None = None,
    ) -> tuple[list[Product], int]:
        """Search and filter products with pagination.

        Applies the following optional filters from *params*:
        - ``q``: case-insensitive substring match against the product name.
        - ``min_rating``: minimum average rating.
        - ``min_price`` / ``max_price``: price range on ``base_price``.

        Sorting options (``params.sort``):
        - ``price_asc``  -- cheapest first
        - ``price_desc`` -- most expensive first
        - ``rating``     -- highest rated first
        - ``newest``     -- most recently created first (default)

        Returns a tuple of ``(products, total_count)`` so callers can build
        pagination metadata.
        """
        base_stmt = (
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.is_active.is_(True))
        )
        count_stmt = (
            select(func.count(Product.id))
            .where(Product.is_active.is_(True))
        )

        # --- Filters ---
        if category_id is not None:
            base_stmt = base_stmt.where(Product.category_id == category_id)
            count_stmt = count_stmt.where(Product.category_id == category_id)

        if params.q:
            pattern = f"%{params.q}%"
            base_stmt = base_stmt.where(Product.name.ilike(pattern))
            count_stmt = count_stmt.where(Product.name.ilike(pattern))

        if params.min_rating is not None:
            base_stmt = base_stmt.where(Product.avg_rating >= params.min_rating)
            count_stmt = count_stmt.where(Product.avg_rating >= params.min_rating)

        if params.min_price is not None:
            base_stmt = base_stmt.where(Product.base_price >= params.min_price)
            count_stmt = count_stmt.where(Product.base_price >= params.min_price)

        if params.max_price is not None:
            base_stmt = base_stmt.where(Product.base_price <= params.max_price)
            count_stmt = count_stmt.where(Product.base_price <= params.max_price)

        # --- Sorting ---
        sort_map = {
            "price_asc": Product.base_price.asc(),
            "price_desc": Product.base_price.desc(),
            "rating": Product.avg_rating.desc(),
            "newest": Product.created_at.desc(),
        }
        order_clause = sort_map.get(params.sort, Product.created_at.desc())
        base_stmt = base_stmt.order_by(order_clause)

        # --- Pagination ---
        offset = (params.page - 1) * params.page_size
        base_stmt = base_stmt.offset(offset).limit(params.page_size)

        # --- Execute ---
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        rows_result = await self.db.execute(base_stmt)
        products = list(rows_result.scalars().all())

        return products, total

    async def get_wishlisted_ids(
        self, user_id: UUID, product_ids: list[UUID] | None = None
    ) -> set[UUID]:
        """Return the set of product IDs that *user_id* has wishlisted.

        When *product_ids* is provided, only check those products (avoids
        loading the entire wishlist on every page view).
        """
        stmt = select(Wishlist.product_id).where(Wishlist.user_id == user_id)
        if product_ids:
            stmt = stmt.where(Wishlist.product_id.in_(product_ids))
        result = await self.db.execute(stmt)
        return set(result.scalars().all())
