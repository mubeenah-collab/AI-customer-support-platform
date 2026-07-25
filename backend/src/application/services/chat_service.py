import logging
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.ai.llm.conversation_context import ChatMessageItem, format_conversation_history
from backend.src.ai.orchestration.state import SupportState
from backend.src.ai.orchestration.support_graph import build_support_graph
from backend.src.ai.rag.rag_pipeline import RAGPipeline
from backend.src.ai.vlm.base_vlm import IVisionService
from backend.src.ai.llm.base_llm import ILLMService
from backend.src.domain.entities.conversation import Conversation
from backend.src.domain.entities.message import Message
from backend.src.domain.exceptions.chat_exceptions import ConversationNotFoundError, MessageProcessingError
from backend.src.infrastructure.repositories.conversation_repository import SQLAlchemyConversationRepository
from backend.src.infrastructure.repositories.message_repository import SQLAlchemyMessageRepository

logger = logging.getLogger("chat_service")


class ChatService:
    """Application service managing chat conversations, Q&A message persistence, and LangGraph workflow invocation."""

    def __init__(
        self,
        session: AsyncSession,
        rag_pipeline: RAGPipeline,
        llm_service: ILLMService,
        vision_service: Optional[IVisionService] = None,
    ):
        self.session = session
        self.conv_repo = SQLAlchemyConversationRepository(session)
        self.msg_repo = SQLAlchemyMessageRepository(session)
        self.rag_pipeline = rag_pipeline
        self.llm_service = llm_service
        self.vision_service = vision_service
        self.graph = build_support_graph(
            rag_pipeline=rag_pipeline,
            llm_service=llm_service,
            vision_service=vision_service,
        )

    async def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        title_hint: Optional[str] = None,
    ) -> Conversation:
        if conversation_id:
            conv = await self.conv_repo.get_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                raise ConversationNotFoundError(conversation_id)
            return conv

        new_title = title_hint[:50] if title_hint else "New Customer Support Chat"
        conv = Conversation(user_id=user_id, title=new_title)
        return await self.conv_repo.create(conv)

    async def process_user_question(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> Message:
        """Process user question through LangGraph AI workflow, persist user and assistant messages to DB."""
        if not query or not query.strip():
            raise MessageProcessingError("Customer query cannot be empty.")

        # 1. Resolve Conversation
        conv = await self.get_or_create_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            title_hint=query,
        )

        # 2. Persist User Message
        user_msg = Message(
            conversation_id=conv.id,
            sender_type="user",
            content=query.strip(),
        )
        await self.msg_repo.create(user_msg)

        # 3. Retrieve prior messages for context
        prior_messages = await self.msg_repo.get_by_conversation_id(conv.id)
        chat_items = [
            ChatMessageItem(sender_type=m.sender_type, content=m.content)
            for m in prior_messages[:-1]  # Exclude current user message
        ]
        history_str = format_conversation_history(chat_items)

        # 4. Invoke LangGraph State Machine
        initial_state: SupportState = {
            "user_id": user_id,
            "conversation_id": conv.id,
            "query": query.strip(),
            "image_bytes": image_bytes,
            "conversation_context": history_str,
        }

        try:
            final_state = self.graph.invoke(initial_state)
            answer_text = final_state.get("final_response", "I apologize, but no answer could be generated.")
            citations = final_state.get("citations", [])
            confidence = final_state.get("confidence", 1.0)
            has_context = final_state.get("has_sufficient_context", True)
        except Exception as e:
            logger.error(f"ChatService graph execution failure: {str(e)}")
            raise MessageProcessingError(f"AI workflow execution error: {str(e)}") from e

        # 5. Persist Assistant Response Message
        assistant_msg = Message(
            conversation_id=conv.id,
            sender_type="assistant",
            content=answer_text,
            sources=citations,
        )
        saved_assistant_msg = await self.msg_repo.create(assistant_msg)
        return saved_assistant_msg

    async def list_user_conversations(self, user_id: str) -> List[Conversation]:
        return await self.conv_repo.get_by_user_id(user_id)

    async def list_conversation_messages(self, user_id: str, conversation_id: str) -> List[Message]:
        conv = await self.conv_repo.get_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise ConversationNotFoundError(conversation_id)
        return await self.msg_repo.get_by_conversation_id(conversation_id)

    async def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        conv = await self.conv_repo.get_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise ConversationNotFoundError(conversation_id)
        return await self.conv_repo.delete(conversation_id)
