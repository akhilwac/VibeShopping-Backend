from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session with commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_user_id_from_token(authorization: str) -> UUID:
    """Parse the Authorization header, verify the JWT, and return the user UUID."""
    exc = _credentials_exception()

    if not authorization.startswith("Bearer "):
        raise exc

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise exc

    try:
        payload = verify_token(token)
    except JWTError:
        raise exc

    if payload.get("type") != "access":
        raise exc

    subject: str | None = payload.get("sub")
    if subject is None:
        raise exc

    try:
        return UUID(subject)
    except ValueError:
        raise exc


async def get_current_user(
    authorization: Annotated[str, Header()],
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """
    Extract and validate the JWT from the Authorization header,
    then verify the user exists and is active in the database.

    Returns the user_id as a UUID.
    Raises HTTP 401 if the token is invalid or the user is inactive/deleted.
    """
    user_id = _extract_user_id_from_token(authorization)

    result = await db.execute(
        select(User.id, User.is_active).where(User.id == user_id)
    )
    row = result.one_or_none()
    if row is None or not row.is_active:
        raise _credentials_exception()

    return user_id


async def get_current_user_optional(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> UUID | None:
    """
    Optionally extract and validate the JWT from the Authorization header.

    Returns the user_id as a UUID if a valid token is present and the user
    is active, or None otherwise.
    """
    if authorization is None:
        return None

    try:
        user_id = _extract_user_id_from_token(authorization)
    except HTTPException:
        return None

    result = await db.execute(
        select(User.id, User.is_active).where(User.id == user_id)
    )
    row = result.one_or_none()
    if row is None or not row.is_active:
        return None

    return user_id
