from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.schemas.address import AddressCreate, AddressUpdate
from app.services.address_service import AddressService

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("/")
async def get_addresses(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AddressService(db)
    addresses = await service.get_all(user_id)
    return success_response(addresses)


@router.post("/", status_code=201)
async def create_address(
    data: AddressCreate,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AddressService(db)
    address = await service.create(user_id, data)
    return success_response(address, message="Address created")


@router.put("/{address_id}")
async def update_address(
    address_id: UUID,
    data: AddressUpdate,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AddressService(db)
    address = await service.update(user_id, address_id, data)
    return success_response(address, message="Address updated")


@router.delete("/{address_id}")
async def delete_address(
    address_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AddressService(db)
    await service.delete(user_id, address_id)
    return success_response(message="Address deleted")
