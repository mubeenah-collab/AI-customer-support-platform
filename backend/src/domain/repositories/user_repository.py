from typing import Optional
from backend.src.domain.entities.user import User
from backend.src.domain.repositories.base_repository import IBaseRepository


class IUserRepository(IBaseRepository[User]):
    """Repository contract for User entity."""

    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError
