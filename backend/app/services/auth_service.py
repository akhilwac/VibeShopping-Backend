from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password, verify_token
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, SocialLoginRequest, TokenResponse
from app.schemas.user import UserOut


class AuthService:
    """Handles registration, login, social-auth, and token generation."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.db = db

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Register a new user with email + password.

        Raises ConflictException when the email is already taken.
        """
        existing = await self.user_repo.get_by_email(data.email)
        if existing is not None:
            raise ConflictException("A user with this email already exists")

        user = User(
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            auth_provider="email",
        )
        user = await self.user_repo.create(user)

        return self._generate_tokens(str(user.id))

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate a user by email and password.

        Raises UnauthorizedException when the email is not found or the
        password does not match.
        """
        user = await self.user_repo.get_by_email(data.email)
        if user is None:
            raise UnauthorizedException("Invalid email or password")

        if user.password_hash is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        return self._generate_tokens(str(user.id))

    async def social_login(self, data: SocialLoginRequest) -> TokenResponse:
        """Authenticate or register a user via a social provider.

        .. warning::
            This endpoint is disabled until proper provider-specific token
            verification is implemented (Google OAuth2 / Apple JWKS).

        Raises BadRequestException unconditionally.
        """
        raise BadRequestException(
            "Social login is not yet available. "
            "Provider token verification must be implemented before this "
            "endpoint can be enabled."
        )

    async def refresh_token(self, data: RefreshRequest) -> TokenResponse:
        """Verify a refresh token and issue a new token pair.

        Raises UnauthorizedException if the refresh token is invalid or expired.
        """
        from jose import JWTError

        try:
            payload = verify_token(data.refresh_token)
        except JWTError:
            raise UnauthorizedException("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        subject = payload.get("sub")
        if subject is None:
            raise UnauthorizedException("Invalid refresh token")

        # Verify user still exists and is active.
        user = await self.user_repo.get_by_id(UUID(subject))
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        return self._generate_tokens(str(user.id))

    async def get_current_user(self, user_id: UUID) -> UserOut:
        """Return the public profile of the authenticated user.

        Raises NotFoundException when the user ID does not match any record.
        """
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")

        return UserOut.model_validate(user)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_tokens(self, user_id: str) -> TokenResponse:
        """Create an access + refresh token pair for the given user ID."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
