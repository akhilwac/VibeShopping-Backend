from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.schemas.cart import CartAddRequest, CartUpdateRequest
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/")
async def get_cart(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CartService(db)
    cart = await service.get_cart(user_id)
    return success_response(cart)


@router.post("/items")
async def add_cart_item(
    data: CartAddRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CartService(db)
    cart = await service.add_item(user_id, data)
    return success_response(cart, message="Item added to cart")


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: UUID,
    data: CartUpdateRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CartService(db)
    cart = await service.update_item(user_id, item_id, data)
    return success_response(cart, message="Cart item updated")


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CartService(db)
    cart = await service.remove_item(user_id, item_id)
    return success_response(cart, message="Item removed from cart")
