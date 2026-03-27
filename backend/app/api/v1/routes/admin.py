from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import paginated_response, success_response
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def dashboard_stats(db: AsyncSession = Depends(get_db)) -> dict:
    service = AdminService(db)
    stats = await service.get_dashboard_stats()
    return success_response(stats.model_dump())


@router.get("/users")
async def list_users(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AdminService(db)
    users, total = await service.get_users(search=search, page=page, page_size=page_size)
    items = [u.model_dump() for u in users]
    return paginated_response(items=items, page=page, page_size=page_size, total=total)


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AdminService(db)
    user = await service.toggle_user_active(user_id)
    return success_response(user.model_dump(), message="User status toggled")


@router.get("/orders")
async def list_all_orders(
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AdminService(db)
    orders, total = await service.get_all_orders(status=status, page=page, page_size=page_size)
    items = [o.model_dump() for o in orders]
    return paginated_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/products")
async def list_all_products(
    search: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AdminService(db)
    products, total = await service.get_all_products(
        search=search, category_id=category_id, page=page, page_size=page_size
    )
    items = [p.model_dump() for p in products]
    return paginated_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/revenue")
async def revenue_stats(db: AsyncSession = Depends(get_db)) -> dict:
    service = AdminService(db)
    data = await service.get_revenue_stats()
    return success_response(data)
