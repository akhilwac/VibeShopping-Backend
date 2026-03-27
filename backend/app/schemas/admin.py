from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str
    phone: str | None = None
    avatar_url: str | None = None
    auth_provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    order_count: int = 0
    review_count: int = 0


class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    total_orders: int
    total_products: int
    total_reviews: int
    total_revenue: Decimal = Decimal("0.00")
    pending_orders: int = 0
    delivered_orders: int = 0
    cancelled_orders: int = 0


class AdminOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_name: str = ""
    user_email: str = ""
    status: str
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    item_count: int = 0
    created_at: datetime


class AdminProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category_name: str = ""
    base_price: Decimal
    avg_rating: Decimal
    review_count: int
    is_featured: bool
    is_active: bool
    total_stock: int = 0
    variant_count: int = 0
    primary_image_url: str | None = None
