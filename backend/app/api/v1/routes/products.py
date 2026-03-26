from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_optional, get_db
from app.core.responses import paginated_response, success_response
from app.schemas.product import ProductSearchParams
from app.services.product_service import ProductService
from app.services.review_service import ReviewService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
async def list_products(
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
    items, total = await service.search(params, user_id=user_id)
    return paginated_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/featured")
async def get_featured_products(
    user_id: UUID | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ProductService(db)
    products = await service.get_featured(user_id)
    return success_response(products)


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1),
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
        q=q,
        sort=sort,
        min_rating=min_rating,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )
    service = ProductService(db)
    items, total = await service.search(params, user_id=user_id)
    return paginated_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/{product_id}")
async def get_product_detail(
    product_id: UUID,
    user_id: UUID | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ProductService(db)
    product = await service.get_detail(product_id, user_id)
    return success_response(product)


@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ReviewService(db)
    items, total = await service.get_product_reviews(product_id, page, page_size)
    return paginated_response(items=items, page=page, page_size=page_size, total=total)
