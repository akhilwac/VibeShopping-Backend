from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banner import Banner
from app.schemas.banner import BannerOut


class BannerService:
    """Business logic for promotional banners."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_active(self) -> list[BannerOut]:
        """Return all currently active banners.

        A banner is active when:
        - ``is_active`` is True
        - ``starts_at`` is null **or** in the past
        - ``ends_at`` is null **or** in the future
        """
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(Banner)
            .where(
                Banner.is_active.is_(True),
                (Banner.starts_at.is_(None)) | (Banner.starts_at <= now),
                (Banner.ends_at.is_(None)) | (Banner.ends_at >= now),
            )
            .order_by(Banner.sort_order.asc())
        )
        banners = list(result.scalars().all())
        return [BannerOut.model_validate(b) for b in banners]
