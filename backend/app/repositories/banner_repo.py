from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banner import Banner
from app.repositories.base import BaseRepository


class BannerRepository(BaseRepository[Banner]):
    """Data-access layer for Banner records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Banner, db)

    async def get_active_banners(self) -> list[Banner]:
        """Return banners that are currently active.

        A banner is considered active when:
        - ``is_active`` is True, AND
        - ``starts_at`` is null or in the past/present, AND
        - ``ends_at`` is null or in the future/present.

        Results are ordered by ``sort_order`` ascending.
        """
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(Banner)
            .where(
                Banner.is_active.is_(True),
                or_(Banner.starts_at.is_(None), Banner.starts_at <= now),
                or_(Banner.ends_at.is_(None), Banner.ends_at >= now),
            )
            .order_by(Banner.sort_order.asc())
        )
        return list(result.scalars().all())
