from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentInitiateRequest(BaseModel):
    order_id: UUID
    payment_method_id: UUID | None = None


class PaymentVerifyRequest(BaseModel):
    order_id: UUID
    gateway_txn_id: str


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    amount: Decimal
    status: str
    paid_at: datetime | None = None
