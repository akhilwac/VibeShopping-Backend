from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SocialLoginRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AuthService(db)
    tokens = await service.register(data)
    return success_response(tokens, message="Registration successful")


@router.post("/login")
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AuthService(db)
    tokens = await service.login(data)
    return success_response(tokens, message="Login successful")


@router.post("/social")
async def social_login(
    data: SocialLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AuthService(db)
    tokens = await service.social_login(data)
    return success_response(tokens, message="Social login successful")


@router.post("/refresh")
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AuthService(db)
    tokens = await service.refresh_token(data)
    return success_response(tokens, message="Token refreshed")


@router.post("/forgot-password", status_code=501)
async def forgot_password(
    data: ForgotPasswordRequest,
) -> dict:
    return {"success": False, "data": None, "message": "Password reset is not yet implemented"}


@router.post("/reset-password", status_code=501)
async def reset_password(
    data: ResetPasswordRequest,
) -> dict:
    return {"success": False, "data": None, "message": "Password reset is not yet implemented"}


@router.get("/me")
async def get_me(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AuthService(db)
    user = await service.get_current_user(user_id)
    return success_response(user)


@router.post("/logout", status_code=501)
async def logout(
    user_id: UUID = Depends(get_current_user),
) -> dict:
    # TODO: Implement token blocklist (Redis) to invalidate tokens on logout.
    return {"success": False, "data": None, "message": "Logout with token revocation is not yet implemented"}
