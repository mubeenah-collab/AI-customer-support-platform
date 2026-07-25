from abc import abstractmethod
from typing import List
from backend.src.domain.entities.report import Report
from backend.src.domain.repositories.base_repository import IBaseRepository


class IReportRepository(IBaseRepository[Report]):
    """Repository interface for Report entity database operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Report]:
        """Fetch all reports belonging to a specific user ordered by creation time descending."""
        pass
