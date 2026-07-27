from typing import List, Optional
from backend.src.domain.entities.ticket import SupportTicket
from backend.src.domain.entities.user import User
from backend.src.infrastructure.repositories.ticket_repository import SQLAlchemyTicketRepository


class TicketService:
    def __init__(self, ticket_repo: SQLAlchemyTicketRepository):
        self.ticket_repo = ticket_repo

    async def create_ticket(
        self,
        user: User,
        subject: str,
        description: str,
        priority: str = "medium",
        category: Optional[str] = None,
    ) -> SupportTicket:
        ticket = SupportTicket(
            user_id=user.id,
            subject=subject,
            description=description,
            priority=priority.lower(),
            category=category,
            status="open",
        )
        return await self.ticket_repo.create(ticket)

    async def list_tickets(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
    ) -> List[SupportTicket]:
        if user.role == "admin" or user.is_superuser:
            return await self.ticket_repo.get_all_tickets(skip=skip, limit=limit, status_filter=status_filter)
        return await self.ticket_repo.get_by_user_id(user.id, skip=skip, limit=limit)

    async def get_ticket_by_id(self, user: User, ticket_id: str) -> Optional[SupportTicket]:
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None
        if ticket.user_id != user.id and user.role != "admin" and not user.is_superuser:
            return None
        return ticket

    async def update_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Optional[SupportTicket]:
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None
        if status:
            ticket.status = status.lower()
        if priority:
            ticket.priority = priority.lower()
        return await self.ticket_repo.update(ticket)
