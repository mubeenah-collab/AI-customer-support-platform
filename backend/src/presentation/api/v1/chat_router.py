import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.ai.embeddings.gemini_embedding import GeminiEmbeddingService
from backend.src.ai.llm.gemini_llm import GeminiLLMService
from backend.src.ai.rag.chroma_vector_store import ChromaVectorStore
from backend.src.ai.rag.rag_pipeline import RAGPipeline
from backend.src.ai.rag.retriever import KnowledgeBaseRetriever
from backend.src.ai.vlm.gemini_vision import GeminiVisionService
from backend.src.application.services.chat_service import ChatService
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.chat_exceptions import ConversationNotFoundError, MessageProcessingError
from backend.src.infrastructure.database.session import get_async_db
from backend.src.presentation.api.v1.dependencies import get_current_active_user
from backend.src.presentation.schemas.chat_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationListResponse,
    ConversationResponse,
)

logger = logging.getLogger("chat_router")

router = APIRouter(prefix="/chat", tags=["Chat & Q&A"])


def get_chat_service(session: AsyncSession = Depends(get_async_db)) -> ChatService:
    """Dependency provider building ChatService with RAG & Gemini AI services."""
    embed_service = GeminiEmbeddingService()
    chroma_store = ChromaVectorStore()
    retriever = KnowledgeBaseRetriever(embedding_service=embed_service, vector_store=chroma_store)
    rag_pipeline = RAGPipeline(retriever=retriever)
    llm_service = GeminiLLMService()
    vision_service = GeminiVisionService()

    return ChatService(
        session=session,
        rag_pipeline=rag_pipeline,
        llm_service=llm_service,
        vision_service=vision_service,
    )


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a customer question (supports optional screenshot upload)",
)
async def send_chat_message(
    request: Request,
    query: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    query_text = query or message
    conv_id = conversation_id

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body_json = await request.json()
            if isinstance(body_json, dict):
                query_text = query_text or body_json.get("query") or body_json.get("message")
                conv_id = conv_id or body_json.get("conversation_id")
        except Exception:
            pass

    if not query_text or not str(query_text).strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'query' or 'message' is required.",
        )

    image_bytes = None
    if image:
        image_bytes = await image.read()

    try:
        assistant_message = await chat_service.process_user_question(
            user_id=current_user.id,
            query=str(query_text).strip(),
            conversation_id=conv_id,
            image_bytes=image_bytes,
        )

        raw_citations = getattr(assistant_message, "citations", None)
        if not raw_citations or not isinstance(raw_citations, list):
            raw_citations = getattr(assistant_message, "sources", None)
        if not isinstance(raw_citations, list):
            raw_citations = []

        return ChatMessageResponse(
            id=assistant_message.id,
            conversation_id=assistant_message.conversation_id,
            sender_type=assistant_message.sender_type,
            content=assistant_message.content,
            citations=raw_citations,
            confidence_score=1.0,
            has_sufficient_context=True,
            created_at=assistant_message.created_at,
        )
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MessageProcessingError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)


@router.get(
    "/history",
    summary="Get aggregated customer chat history for CustomerHistoryPage",
)
async def get_user_chat_history(
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    conversations = await chat_service.list_user_conversations(user_id=current_user.id)
    history_items = []
    for conv in conversations:
        msgs = await chat_service.list_conversation_messages(user_id=current_user.id, conversation_id=conv.id)
        user_msgs = [m for m in msgs if m.sender_type == "user"]
        assistant_msgs = [m for m in msgs if m.sender_type == "assistant"]
        for idx in range(len(assistant_msgs)):
            u_text = user_msgs[idx].content if idx < len(user_msgs) else (conv.title or "Customer Question")
            a_msg = assistant_msgs[idx]
            created_str = a_msg.created_at.isoformat() if hasattr(a_msg.created_at, "isoformat") else str(a_msg.created_at)
            history_items.append({
                "id": a_msg.id,
                "query": u_text,
                "response": a_msg.content,
                "category": "support_inquiry",
                "created_at": created_str,
            })
    return {"messages": history_items, "total": len(history_items)}


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List all user conversations",
)
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    conversations = await chat_service.list_user_conversations(user_id=current_user.id)
    items = [ConversationResponse.model_validate(c) for c in conversations]
    return ConversationListResponse(items=items, total=len(items))


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[ChatMessageResponse],
    summary="Get conversation history messages",
)
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        messages = await chat_service.list_conversation_messages(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
        res = []
        for m in messages:
            c = getattr(m, "citations", None)
            if not c or not isinstance(c, list):
                c = getattr(m, "sources", None)
            if not isinstance(c, list):
                c = []
            res.append(
                ChatMessageResponse(
                    id=m.id,
                    conversation_id=m.conversation_id,
                    sender_type=m.sender_type,
                    content=m.content,
                    citations=c,
                    confidence_score=1.0,
                    has_sufficient_context=True,
                    created_at=m.created_at,
                )
            )
        return res
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation thread",
)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        await chat_service.delete_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/stream",
    summary="Stream AI customer support response via Server-Sent Events (SSE)",
)
async def stream_chat_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Stream response tokens using Server-Sent Events (media_type='text/event-stream')."""
    if not payload.query or not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'query' is required.",
        )

    async def sse_event_generator():
        try:
            yield f"data: {json.dumps({'type': 'start', 'status': 'connected'})}\n\n"
            for chunk in chat_service.llm_service.stream(payload.query.strip()):
                if chunk:
                    data = json.dumps({"type": "chunk", "content": chunk})
                    yield f"data: {data}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'status': 'completed'})}\n\n"
        except Exception as e:
            logger.error(f"SSE streaming exception: {type(e).__name__} - {str(e)}")
            err_data = json.dumps({"type": "error", "message": "Streaming error occurred"})
            yield f"data: {err_data}\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")
