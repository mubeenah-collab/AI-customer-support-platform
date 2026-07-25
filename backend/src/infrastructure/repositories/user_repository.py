from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.domain.entities.user import User
from backend.src.domain.repositories.user_repository import IUserRepository
from backend.src.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User], IUserRepository):
    """SQLAlchemy implementation of User Repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()
