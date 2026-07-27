from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from backend.src.presentation.schemas.ai_schemas import CitationSchema


class ChatMessageRequest(BaseModel):
    query: Optional[str] = Field(None, description="Customer question or support query text")
    message: Optional[str] = Field(None, description="Alternative field name for customer question text")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for multi-turn thread")

    @model_validator(mode="before")
    @classmethod
    def check_query_or_message(cls, data: Any) -> Any:
        if isinstance(data, dict):
            q = data.get("query") or data.get("message")
            if q:
                data["query"] = q
                data["message"] = q
        return data



class ChatMessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    content: str
    citations: List[CitationSchema] = Field(default_factory=list)
    confidence_score: float = 1.0
    has_sufficient_context: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
