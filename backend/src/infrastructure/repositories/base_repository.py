from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.domain.repositories.base_repository import IBaseRepository
from backend.src.infrastructure.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyBaseRepository(IBaseRepository[ModelType], Generic[ModelType]):
    """Generic SQLAlchemy Repository implementation handling async DB operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: str) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity_id: str) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False
