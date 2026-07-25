from abc import abstractmethod
from typing import List
from backend.src.domain.entities.message import Message
from backend.src.domain.repositories.base_repository import IBaseRepository


class IMessageRepository(IBaseRepository[Message]):
    """Repository interface for Message entity database operations."""

    @abstractmethod
    async def get_by_conversation_id(self, conversation_id: str) -> List[Message]:
        """Fetch all messages for a specific conversation sorted by creation time."""
        pass
