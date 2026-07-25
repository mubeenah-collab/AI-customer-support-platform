from typing import List, Optional
from backend.src.domain.entities.conversation import Conversation
from backend.src.domain.entities.message import Message
from backend.src.domain.repositories.base_repository import IBaseRepository


class IConversationRepository(IBaseRepository[Conversation]):
    """Repository contract for Conversation entity."""

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
        raise NotImplementedError

    async def add_message(self, conversation_id: str, sender_type: str, content: str, citations: Optional[dict] = None, image_url: Optional[str] = None) -> Message:
        raise NotImplementedError
