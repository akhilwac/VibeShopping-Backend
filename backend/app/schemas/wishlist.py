from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WishlistToggleRequest(BaseModel):
    product_id: UUID


class WishlistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_name: str
    product_price: Decimal
    primary_image_url: str | None = None
    created_at: datetime
