from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserOut, UserUpdate


class UserService:
    """Profile retrieval and update logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.db = db

    async def get_profile(self, user_id: UUID) -> UserOut:
        """Fetch a user's public profile by ID.

        Raises NotFoundException when the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")

        return UserOut.model_validate(user)

    async def update_profile(self, user_id: UUID, data: UserUpdate) -> UserOut:
        """Update the authenticated user's profile.

        Only fields that are explicitly provided (not ``None``) are written.
        Raises NotFoundException when the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)

        return UserOut.model_validate(user)
