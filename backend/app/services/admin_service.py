from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.admin import AdminDashboardStats, AdminUserOut


class AdminService:
    """Business logic for the admin dashboard."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_dashboard_stats(self) -> AdminDashboardStats:
        """Return aggregate stats for the admin dashboard."""
        total_users_r = await self.db.execute(select(func.count(User.id)))
        active_users_r = await self.db.execute(
            select(func.count(User.id)).where(User.is_active.is_(True))
        )
        total_orders_r = await self.db.execute(select(func.count(Order.id)))
        total_products_r = await self.db.execute(
            select(func.count(Product.id)).where(Product.is_active.is_(True))
        )
        total_reviews_r = await self.db.execute(select(func.count(Review.id)))

        total_users = total_users_r.scalar_one()
        active_users = active_users_r.scalar_one()

        return AdminDashboardStats(
            total_users=total_users,
            active_users=active_users,
            inactive_users=total_users - active_users,
            total_orders=total_orders_r.scalar_one(),
            total_products=total_products_r.scalar_one(),
            total_reviews=total_reviews_r.scalar_one(),
        )

    async def get_users(
        self,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AdminUserOut], int]:
        """Return a paginated list of users with order and review counts."""
        # Build base query with aggregates.
        stmt = (
            select(
                User,
                func.count(func.distinct(Order.id)).label("order_count"),
                func.count(func.distinct(Review.id)).label("review_count"),
            )
            .outerjoin(Order, Order.user_id == User.id)
            .outerjoin(Review, Review.user_id == User.id)
            .group_by(User.id)
        )

        count_stmt = select(func.count(User.id))

        if search:
            pattern = f"%{search}%"
            search_filter = User.full_name.ilike(pattern) | User.email.ilike(pattern)
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        # Count.
        total_r = await self.db.execute(count_stmt)
        total = total_r.scalar_one()

        # Paginated results.
        offset = (page - 1) * page_size
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size)

        result = await self.db.execute(stmt)
        rows = result.all()

        users = []
        for row in rows:
            user = row[0]
            user_out = AdminUserOut.model_validate(user)
            user_out.order_count = row[1]
            user_out.review_count = row[2]
            users.append(user_out)

        return users, total

    async def toggle_user_active(self, user_id: UUID) -> AdminUserOut:
        """Toggle a user's is_active flag."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("User not found")

        user.is_active = not user.is_active
        await self.db.flush()
        await self.db.refresh(user)

        return AdminUserOut.model_validate(user)
