from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class IBaseRepository(Generic[T]):
    """Generic Repository Interface defining CRUD contracts."""

    async def get_by_id(self, entity_id: str) -> Optional[T]:
        raise NotImplementedError

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        raise NotImplementedError

    async def create(self, entity: T) -> T:
        raise NotImplementedError

    async def update(self, entity: T) -> T:
        raise NotImplementedError

    async def delete(self, entity_id: str) -> bool:
        raise NotImplementedError
