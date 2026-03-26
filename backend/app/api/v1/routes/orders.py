from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.schemas.order import OrderCreateRequest
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", status_code=201)
async def create_order(
    data: OrderCreateRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrderService(db)
    order = await service.create_order(user_id, data)
    return success_response(order, message="Order created")


@router.get("/")
async def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrderService(db)
    items, total = await service.get_orders(user_id, page, page_size)
    return paginated_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/{order_id}")
async def get_order_detail(
    order_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrderService(db)
    order = await service.get_order_detail(user_id, order_id)
    return success_response(order)
