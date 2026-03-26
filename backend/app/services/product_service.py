from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.product import Product
from app.repositories.product_repo import ProductRepository
from app.schemas.product import (
    ProductDetail,
    ProductImageOut,
    ProductListItem,
    ProductSearchParams,
    ProductVariantOut,
)


class ProductService:
    """Business logic for product listing, search, and detail views."""

    def __init__(self, db: AsyncSession) -> None:
        self.product_repo = ProductRepository(db)
        self.db = db

    async def get_featured(self, user_id: UUID | None = None) -> list[ProductListItem]:
        """Return featured products, annotating the wishlisted state when
        a ``user_id`` is provided.
        """
        products = await self.product_repo.get_featured()
        product_ids = [p.id for p in products]
        wishlisted_ids = await self._get_wishlisted_ids(user_id, product_ids)
        return [self._to_list_item(p, wishlisted_ids) for p in products]

    async def search(
        self,
        params: ProductSearchParams,
        category_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> tuple[list[ProductListItem], int]:
        """Search / filter products with pagination.

        Returns ``(items, total_count)`` so callers can build pagination
        metadata.
        """
        products, total = await self.product_repo.search(params, category_id)
        product_ids = [p.id for p in products]
        wishlisted_ids = await self._get_wishlisted_ids(user_id, product_ids)
        items = [self._to_list_item(p, wishlisted_ids) for p in products]
        return items, total

    async def get_detail(
        self, product_id: UUID, user_id: UUID | None = None
    ) -> ProductDetail:
        """Fetch a full product detail view.

        Raises NotFoundException when the product does not exist or is
        inactive.
        """
        product = await self.product_repo.get_by_id(product_id)
        if product is None:
            raise NotFoundException("Product not found")

        wishlisted_ids = await self._get_wishlisted_ids(user_id)

        return ProductDetail(
            id=product.id,
            name=product.name,
            description=product.description,
            base_price=product.base_price,
            avg_rating=product.avg_rating,
            review_count=product.review_count,
            category_id=product.category_id,
            variants=[ProductVariantOut.model_validate(v) for v in product.variants],
            images=[ProductImageOut.model_validate(i) for i in product.images],
            is_wishlisted=product.id in wishlisted_ids,
            created_at=product.created_at,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_wishlisted_ids(
        self, user_id: UUID | None, product_ids: list[UUID] | None = None
    ) -> set[UUID]:
        """Return the set of wishlisted product IDs for the user, or an
        empty set if no user is authenticated.
        """
        if user_id is None:
            return set()
        return await self.product_repo.get_wishlisted_ids(user_id, product_ids)

    @staticmethod
    def _to_list_item(product: Product, wishlisted_ids: set[UUID]) -> ProductListItem:
        """Map a Product ORM instance to a lightweight list-item schema."""
        return ProductListItem(
            id=product.id,
            name=product.name,
            base_price=product.base_price,
            avg_rating=product.avg_rating,
            review_count=product.review_count,
            primary_image_url=product.primary_image_url,
            is_wishlisted=product.id in wishlisted_ids,
        )
