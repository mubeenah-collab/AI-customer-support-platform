from typing import Any, Dict, List, Optional, TypedDict


class SupportState(TypedDict, total=False):
    """Typed state dictionary passed across LangGraph nodes during support workflow execution."""

    user_id: str
    conversation_id: str
    query: str
    image_bytes: Optional[bytes]
    image_path: Optional[str]
    intent: str
    retrieved_documents: List[Dict[str, Any]]
    retrieved_context: str
    visual_context: Optional[Dict[str, Any]]
    conversation_context: str
    draft_response: str
    final_response: str
    citations: List[Dict[str, Any]]
    confidence: float
    has_sufficient_context: bool
    errors: List[str]
