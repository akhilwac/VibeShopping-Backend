from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.models.review import Review
from app.models.user import User
from app.schemas.admin import (
    AdminDashboardStats,
    AdminOrderOut,
    AdminProductOut,
    AdminUserOut,
)


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

        # Revenue & order status counts
        revenue_r = await self.db.execute(
            select(func.coalesce(func.sum(Order.total), 0))
        )
        pending_r = await self.db.execute(
            select(func.count(Order.id)).where(Order.status == "pending")
        )
        delivered_r = await self.db.execute(
            select(func.count(Order.id)).where(Order.status == "delivered")
        )
        cancelled_r = await self.db.execute(
            select(func.count(Order.id)).where(Order.status == "cancelled")
        )

        total_users = total_users_r.scalar_one()
        active_users = active_users_r.scalar_one()

        return AdminDashboardStats(
            total_users=total_users,
            active_users=active_users,
            inactive_users=total_users - active_users,
            total_orders=total_orders_r.scalar_one(),
            total_products=total_products_r.scalar_one(),
            total_reviews=total_reviews_r.scalar_one(),
            total_revenue=revenue_r.scalar_one(),
            pending_orders=pending_r.scalar_one(),
            delivered_orders=delivered_r.scalar_one(),
            cancelled_orders=cancelled_r.scalar_one(),
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

    async def get_all_orders(
        self,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AdminOrderOut], int]:
        """Return a paginated list of all orders with user info."""
        stmt = (
            select(
                Order,
                User.full_name.label("user_name"),
                User.email.label("user_email"),
                func.count(OrderItem.id).label("item_count"),
            )
            .join(User, User.id == Order.user_id)
            .outerjoin(OrderItem, OrderItem.order_id == Order.id)
            .group_by(Order.id, User.full_name, User.email)
        )
        count_stmt = select(func.count(Order.id))

        if status:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)

        total_r = await self.db.execute(count_stmt)
        total = total_r.scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Order.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(stmt)
        rows = result.all()

        orders = []
        for row in rows:
            order = row[0]
            orders.append(AdminOrderOut(
                id=order.id,
                user_name=row[1],
                user_email=row[2],
                status=order.status,
                subtotal=order.subtotal,
                delivery_fee=order.delivery_fee,
                total=order.total,
                item_count=row[3],
                created_at=order.created_at,
            ))

        return orders, total

    async def get_all_products(
        self,
        search: str | None = None,
        category_id: UUID | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AdminProductOut], int]:
        """Return a paginated list of products with stock and category info."""
        # Subquery for primary image
        img_sub = (
            select(ProductImage.image_url)
            .where(
                ProductImage.product_id == Product.id,
                ProductImage.is_primary.is_(True),
            )
            .correlate(Product)
            .limit(1)
            .scalar_subquery()
        )

        stmt = (
            select(
                Product,
                Category.name.label("category_name"),
                func.coalesce(func.sum(ProductVariant.stock_quantity), 0).label("total_stock"),
                func.count(func.distinct(ProductVariant.id)).label("variant_count"),
                img_sub.label("primary_image_url"),
            )
            .join(Category, Category.id == Product.category_id)
            .outerjoin(ProductVariant, ProductVariant.product_id == Product.id)
            .group_by(Product.id, Category.name)
        )
        count_stmt = select(func.count(Product.id))

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(Product.name.ilike(pattern))
            count_stmt = count_stmt.where(Product.name.ilike(pattern))

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
            count_stmt = count_stmt.where(Product.category_id == category_id)

        total_r = await self.db.execute(count_stmt)
        total = total_r.scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Product.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(stmt)
        rows = result.all()

        products = []
        for row in rows:
            product = row[0]
            products.append(AdminProductOut(
                id=product.id,
                name=product.name,
                category_name=row[1],
                base_price=product.base_price,
                avg_rating=product.avg_rating,
                review_count=product.review_count,
                is_featured=product.is_featured,
                is_active=product.is_active,
                total_stock=row[2],
                variant_count=row[3],
                primary_image_url=row[4],
            ))

        return products, total

    async def get_revenue_stats(self) -> dict:
        """Return revenue breakdown by order status and category."""
        # Revenue by status
        status_r = await self.db.execute(
            select(Order.status, func.sum(Order.total))
            .group_by(Order.status)
        )
        by_status = {row[0]: float(row[1] or 0) for row in status_r.all()}

        # Revenue by category
        cat_r = await self.db.execute(
            select(
                Category.name,
                func.sum(OrderItem.unit_price * OrderItem.quantity),
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(ProductVariant, ProductVariant.id == OrderItem.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .join(Category, Category.id == Product.category_id)
            .group_by(Category.name)
        )
        by_category = {row[0]: float(row[1] or 0) for row in cat_r.all()}

        # Order count by status for chart
        count_r = await self.db.execute(
            select(Order.status, func.count(Order.id)).group_by(Order.status)
        )
        orders_by_status = {row[0]: row[1] for row in count_r.all()}

        return {
            "revenue_by_status": by_status,
            "revenue_by_category": by_category,
            "orders_by_status": orders_by_status,
        }
