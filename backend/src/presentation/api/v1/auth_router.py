from fastapi import APIRouter, Depends, HTTPException, status
from backend.src.application.services.auth_service import AuthService
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.auth_exceptions import (
    AuthException,
    InvalidCredentialsError,
    UnauthorizedError,
    UserAlreadyExistsError,
)
from backend.src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from backend.src.presentation.api.v1.dependencies import (
    get_current_active_user,
    get_user_repository,
)
from backend.src.presentation.schemas.auth_schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user account."""
    try:
        return await auth_service.register_user(request)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate user credentials and return JWT tokens."""
    try:
        return await auth_service.authenticate_user(request.email, request.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Obtain a new access token using a valid refresh token."""
    try:
        return await auth_service.refresh_tokens(request.refresh_token)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@auth_router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve profile details of currently authenticated user."""
    return UserResponse.model_validate(current_user)
