from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.domain.entities.message import Message
from backend.src.domain.repositories.message_repository import IMessageRepository
from backend.src.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyMessageRepository(SQLAlchemyBaseRepository[Message], IMessageRepository):
    """SQLAlchemy implementation of IMessageRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def get_by_conversation_id(self, conversation_id: str) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
