import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.application.services.user_service import UserService
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.auth_exceptions import UserNotFoundError
from backend.src.infrastructure.database.session import get_async_db
from backend.src.presentation.api.v1.dependencies import get_current_active_user, require_admin
from backend.src.presentation.schemas.user_schemas import UserListResponse, UserProfileResponse, UserUpdateRequest

logger = logging.getLogger("user_router")

router = APIRouter(prefix="/users", tags=["User Management"])


def get_user_service(session: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(session=session)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    return UserProfileResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
async def update_current_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        updated_user = await user_service.update_profile(
            user_id=current_user.id,
            full_name=request.full_name,
            new_password=request.password,
        )
        return UserProfileResponse.model_validate(updated_user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all platform users (Admin only)",
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    users = await user_service.list_users(skip=skip, limit=limit)
    items = [UserProfileResponse.model_validate(u) for u in users]
    return UserListResponse(items=items, total=len(items))
