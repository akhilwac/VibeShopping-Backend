from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.schemas.payment_method import PaymentMethodCreate
from app.services.payment_method_service import PaymentMethodService

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])


@router.get("/")
async def get_payment_methods(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = PaymentMethodService(db)
    methods = await service.get_all(user_id)
    return success_response(methods)


@router.post("/", status_code=201)
async def create_payment_method(
    data: PaymentMethodCreate,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = PaymentMethodService(db)
    method = await service.create(user_id, data)
    return success_response(method, message="Payment method added")


@router.delete("/{method_id}")
async def delete_payment_method(
    method_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = PaymentMethodService(db)
    await service.delete(user_id, method_id)
    return success_response(message="Payment method removed")
