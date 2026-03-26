from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.responses import success_response
from app.services.banner_service import BannerService

router = APIRouter(prefix="/banners", tags=["Banners"])


@router.get("/")
async def get_active_banners(
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = BannerService(db)
    banners = await service.get_active()
    return success_response(banners)
