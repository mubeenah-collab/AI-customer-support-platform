import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
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
    query: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    json_payload: Optional[ChatMessageRequest] = None,
    current_user: User = Depends(get_current_active_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    # Extract query text and conversation ID from Form or JSON payload
    query_text = query if query else (json_payload.query if json_payload else None)
    conv_id = conversation_id if conversation_id else (json_payload.conversation_id if json_payload else None)

    if not query_text or not query_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'query' is required.",
        )

    image_bytes = None
    if image:
        image_bytes = await image.read()

    try:
        assistant_message = await chat_service.process_user_question(
            user_id=current_user.id,
            query=query_text.strip(),
            conversation_id=conv_id,
            image_bytes=image_bytes,
        )

        return ChatMessageResponse(
            id=assistant_message.id,
            conversation_id=assistant_message.conversation_id,
            sender_type=assistant_message.sender_type,
            content=assistant_message.content,
            citations=assistant_message.sources or [],
            confidence_score=1.0,
            has_sufficient_context=True,
            created_at=assistant_message.created_at,
        )
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MessageProcessingError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)


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
        return [
            ChatMessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_type=m.sender_type,
                content=m.content,
                citations=m.sources or [],
                confidence_score=1.0,
                has_sufficient_context=True,
                created_at=m.created_at,
            )
            for m in messages
        ]
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
