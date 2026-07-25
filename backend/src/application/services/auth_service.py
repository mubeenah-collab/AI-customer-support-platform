from datetime import datetime, timedelta, timezone
from typing import Tuple
from backend.src.config.settings import settings
from backend.src.domain.entities.user import User
from backend.src.domain.entities.session import UserSession
from backend.src.domain.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    UnauthorizedError,
    UserAlreadyExistsError,
)
from backend.src.domain.repositories.user_repository import IUserRepository
from backend.src.infrastructure.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.src.infrastructure.security.password import hash_password, verify_password
from backend.src.presentation.schemas.auth_schemas import (
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Application Service handling user authentication workflows."""

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def register_user(self, request: UserRegisterRequest) -> UserResponse:
        existing_user = await self.user_repo.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExistsError(request.email)

        hashed_pwd = hash_password(request.password)
        new_user = User(
            email=request.email,
            hashed_password=hashed_pwd,
            full_name=request.full_name,
            role=request.role or "customer",
            is_active=True,
        )
        created_user = await self.user_repo.create(new_user)
        return UserResponse.model_validate(created_user)

    async def authenticate_user(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UnauthorizedError("User account is inactive.")

        access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except ValueError as e:
            raise UnauthorizedError(str(e))

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type. Refresh token required.")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token payload.")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive.")

        new_access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
        new_refresh_token = create_refresh_token(data={"sub": user.id})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
