from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.schemas.wishlist import WishlistToggleRequest
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("/")
async def get_wishlist(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = WishlistService(db)
    items = await service.get_user_wishlist(user_id)
    return success_response(items)


@router.post("/toggle")
async def toggle_wishlist(
    data: WishlistToggleRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = WishlistService(db)
    result = await service.toggle(user_id, data.product_id)
    return success_response(result)
