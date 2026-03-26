from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CartAddRequest(BaseModel):
    variant_id: UUID
    quantity: int = Field(ge=1)


class CartUpdateRequest(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variant_id: UUID
    product_name: str
    variant_label: str
    unit_price: Decimal
    quantity: int
    image_url: str | None = None


class CartSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[CartItemOut]
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    item_count: int
