from datetime import datetime
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
