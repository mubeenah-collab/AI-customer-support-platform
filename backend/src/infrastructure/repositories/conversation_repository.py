from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.domain.entities.conversation import Conversation
from backend.src.domain.entities.message import Message
from backend.src.domain.repositories.conversation_repository import IConversationRepository
from backend.src.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyConversationRepository(SQLAlchemyBaseRepository[Conversation], IConversationRepository):
    """SQLAlchemy implementation of Conversation Repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_message(self, conversation_id: str, sender_type: str, content: str, citations: Optional[dict] = None, image_url: Optional[str] = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            citations=citations,
            image_url=image_url,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
