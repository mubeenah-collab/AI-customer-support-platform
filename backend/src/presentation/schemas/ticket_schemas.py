from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TicketCreateRequest(BaseModel):
    subject: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    priority: str = Field(default="medium", description="low, medium, high, urgent")
    category: Optional[str] = Field(None, description="billing, technical, account, general")


class TicketUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, description="open, in_progress, resolved, closed")
    priority: Optional[str] = Field(None, description="low, medium, high, urgent")


class TicketResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    description: str
    status: str
    priority: str
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketListResponse(BaseModel):
    items: List[TicketResponse]
    total: int
