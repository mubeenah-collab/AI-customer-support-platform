from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.application.services.ticket_service import TicketService
from backend.src.domain.entities.user import User
from backend.src.infrastructure.database.session import get_async_db
from backend.src.infrastructure.repositories.ticket_repository import SQLAlchemyTicketRepository
from backend.src.presentation.api.v1.dependencies import get_current_active_user, require_admin
from backend.src.presentation.schemas.ticket_schemas import (
    TicketCreateRequest,
    TicketListResponse,
    TicketResponse,
    TicketUpdateRequest,
)

ticket_router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


def get_ticket_service(session: AsyncSession = Depends(get_async_db)) -> TicketService:
    ticket_repo = SQLAlchemyTicketRepository(session)
    return TicketService(ticket_repo)


@ticket_router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: TicketCreateRequest,
    current_user: User = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """Create a new support ticket."""
    ticket = await ticket_service.create_ticket(
        user=current_user,
        subject=request.subject,
        description=request.description,
        priority=request.priority,
        category=request.category,
    )
    return TicketResponse.model_validate(ticket)


@ticket_router.get("", response_model=TicketListResponse)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """List tickets (Customer sees own, Admin sees all)."""
    tickets = await ticket_service.list_tickets(
        user=current_user,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )
    items = [TicketResponse.model_validate(t) for t in tickets]
    return TicketListResponse(items=items, total=len(items))


@ticket_router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """Get ticket by ID."""
    ticket = await ticket_service.get_ticket_by_id(current_user, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)


@ticket_router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    request: TicketUpdateRequest,
    current_user: User = Depends(require_admin),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    """Update ticket status or priority (Admin only)."""
    ticket = await ticket_service.update_ticket(
        ticket_id=ticket_id,
        status=request.status,
        priority=request.priority,
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)
