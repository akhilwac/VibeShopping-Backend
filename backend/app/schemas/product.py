from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    image_url: str
    sort_order: int
    is_primary: bool


class ProductVariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variant_label: str
    price_override: Decimal | None = None
    stock_quantity: int
    sku: str


class ProductListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    base_price: Decimal
    avg_rating: Decimal
    review_count: int
    primary_image_url: str | None = None
    is_wishlisted: bool = False


class ProductDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    base_price: Decimal
    avg_rating: Decimal
    review_count: int
    category_id: UUID
    variants: list[ProductVariantOut]
    images: list[ProductImageOut]
    is_wishlisted: bool = False
    created_at: datetime


class ProductSearchParams(BaseModel):
    q: str | None = None
    sort: str = "newest"
    min_rating: float | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    is_new: bool | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
