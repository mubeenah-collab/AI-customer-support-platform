import logging
from typing import Any, Dict, List, Optional

try:
    from crewai import Agent
except ImportError:
    class Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

from backend.src.ai.llm.base_llm import ILLMService
from backend.src.ai.prompts.rag_prompt import rag_prompt_template
from backend.src.ai.rag.rag_pipeline import RAGResult
from backend.src.presentation.schemas.ai_schemas import ChatResponseSchema, CitationSchema

logger = logging.getLogger("synthesis_agent")


class SynthesisAgent:
    """CrewAI Synthesis Agent responsible for combining RAG evidence, visual context, and conversation history into a grounded answer."""

    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service
        self.crew_agent = Agent(
            role="Customer Support Response Synthesis Agent",
            goal="Combine retrieved knowledge, visual understanding, and conversation history into a grounded, professional customer response with source citations",
            backstory="Master technical communicator dedicated to composing accurate, grounded customer support answers.",
            verbose=False,
            allow_delegation=False,
        )

    def execute_synthesis(
        self,
        query: str,
        rag_result: RAGResult,
        visual_context: Optional[Dict[str, Any]] = None,
        chat_history: str = "None",
    ) -> ChatResponseSchema:
        """Execute synthesis task: generate grounded final response with citations."""
        logger.info("SynthesisAgent generating final customer support response...")
        context_str = rag_result.context

        if visual_context and visual_context.get("description"):
            context_str += f"\n\nVISUAL EVIDENCE FROM CUSTOMER IMAGE:\n{visual_context['description']}"

        prompt = rag_prompt_template.format(
            context=context_str,
            chat_history=chat_history or "None",
            query=query,
        )

        try:
            raw_answer = self.llm_service.generate(prompt)
        except Exception as e:
            logger.error(f"SynthesisAgent LLM failure: {str(e)}")
            raw_answer = "I apologize, but an error occurred while composing the response."

        citation_schemas: List[CitationSchema] = [
            CitationSchema(
                citation_index=c["citation_index"],
                document_id=c["document_id"],
                document_name=c["document_name"],
                page_number=c.get("page_number"),
                relevance_percentage=c["relevance_percentage"],
                snippet=c["snippet"],
            )
            for c in rag_result.citations
        ]

        return ChatResponseSchema(
            answer=raw_answer,
            citations=citation_schemas,
            confidence_score=0.95 if rag_result.has_sufficient_context else 0.35,
            has_sufficient_context=rag_result.has_sufficient_context,
        )
