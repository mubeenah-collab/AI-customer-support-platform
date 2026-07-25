import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.auth_exceptions import UserNotFoundError
from backend.src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from backend.src.infrastructure.security.password import hash_password

logger = logging.getLogger("user_service")


class UserService:
    """Application service managing user profiles and platform user accounts."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = SQLAlchemyUserRepository(session)

    async def get_profile(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    async def update_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        new_password: Optional[str] = None,
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        if full_name and full_name.strip():
            user.full_name = full_name.strip()

        if new_password and new_password.strip():
            user.hashed_password = hash_password(new_password.strip())

        return await self.user_repo.update(user)

    async def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        return await self.user_repo.list(skip=skip, limit=limit)
