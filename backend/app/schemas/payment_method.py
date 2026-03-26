from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentMethodCreate(BaseModel):
    type: str
    provider: str
    last_four: str | None = None
    token: str
    is_default: bool = False


class PaymentMethodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    provider: str
    last_four: str | None = None
    is_default: bool
