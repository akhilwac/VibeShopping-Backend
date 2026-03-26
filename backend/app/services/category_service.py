from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryDetail, CategoryOut


class CategoryService:
    """Business logic for product categories."""

    def __init__(self, db: AsyncSession) -> None:
        self.category_repo = CategoryRepository(db)
        self.db = db

    async def get_all(self) -> list[CategoryOut]:
        """Return all active categories with their product counts."""
        rows = await self.category_repo.get_with_product_counts()
        return [
            CategoryOut(
                id=category.id,
                name=category.name,
                icon_url=category.icon_url,
                sort_order=category.sort_order,
                product_count=count,
            )
            for category, count in rows
        ]

    async def get_by_id(self, category_id: UUID) -> CategoryDetail:
        """Fetch a single category by its ID.

        Raises NotFoundException when the category does not exist.
        """
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise NotFoundException("Category not found")

        return CategoryDetail.model_validate(category)
