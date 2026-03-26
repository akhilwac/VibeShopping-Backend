from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.schemas.payment import PaymentInitiateRequest, PaymentVerifyRequest
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initiate")
async def initiate_payment(
    data: PaymentInitiateRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = PaymentService(db)
    payment = await service.initiate(user_id, data)
    return success_response(payment, message="Payment initiated")


@router.post("/verify")
async def verify_payment(
    data: PaymentVerifyRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = PaymentService(db)
    payment = await service.verify(user_id, data)
    return success_response(payment, message="Payment verified")
