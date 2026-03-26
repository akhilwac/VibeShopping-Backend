from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data-access layer for User records."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Look up a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Look up a user by their phone number."""
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_email_or_phone(self, identifier: str) -> User | None:
        """Look up a user by either email or phone.

        Useful for login flows where the user can authenticate with either.
        """
        result = await self.db.execute(
            select(User).where(
                or_(User.email == identifier, User.phone == identifier)
            )
        )
        return result.scalar_one_or_none()
