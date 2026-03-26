from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderCreateRequest(BaseModel):
    address_id: UUID
    payment_method_id: UUID | None = None


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_name: str
    variant_label: str
    unit_price: Decimal
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    items: list[OrderItemOut]
    created_at: datetime


class OrderListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    total: Decimal
    item_count: int
    created_at: datetime
