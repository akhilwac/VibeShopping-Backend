from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_optional, get_db
from app.core.responses import paginated_response, success_response
from app.schemas.product import ProductSearchParams
from app.services.category_service import CategoryService
from app.services.product_service import ProductService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CategoryService(db)
    categories = await service.get_all()
    return success_response(categories)


@router.get("/{category_id}")
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    return success_response(category)


@router.get("/{category_id}/products")
async def get_category_products(
    category_id: UUID,
    sort: str = Query(default="newest"),
    min_rating: float | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: UUID | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> dict:
    params = ProductSearchParams(
        sort=sort,
        min_rating=min_rating,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )
    service = ProductService(db)
    items, total = await service.search(params, category_id=category_id, user_id=user_id)
    return paginated_response(items=items, page=page, page_size=page_size, total=total)
