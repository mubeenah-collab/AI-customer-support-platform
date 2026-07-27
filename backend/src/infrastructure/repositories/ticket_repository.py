from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.domain.entities.ticket import SupportTicket
from backend.src.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyTicketRepository(SQLAlchemyBaseRepository[SupportTicket]):
    def __init__(self, session: AsyncSession):
        super().__init__(SupportTicket, session)

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[SupportTicket]:
        stmt = (
            select(SupportTicket)
            .where(SupportTicket.user_id == user_id)
            .order_by(SupportTicket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_all_tickets(self, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[SupportTicket]:
        stmt = select(SupportTicket).order_by(SupportTicket.created_at.desc())
        if status_filter:
            stmt = stmt.where(SupportTicket.status == status_filter)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
