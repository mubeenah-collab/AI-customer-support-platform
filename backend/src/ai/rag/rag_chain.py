import logging
from typing import Any, Dict, List, Optional
from backend.src.ai.llm.base_llm import ILLMService, LLMServiceError
from backend.src.ai.prompts.rag_prompt import rag_prompt_template
from backend.src.ai.rag.rag_pipeline import RAGPipeline, RAGResult
from backend.src.presentation.schemas.ai_schemas import ChatResponseSchema, CitationSchema

logger = logging.getLogger("rag_chain")


class RAGChain:
    """LangChain RAG chain combining retrieval context, prompt formatting, and LLM text generation."""

    def __init__(
        self,
        rag_pipeline: RAGPipeline,
        llm_service: ILLMService,
    ):
        self.rag_pipeline = rag_pipeline
        self.llm_service = llm_service

    def invoke(
        self,
        query: str,
        chat_history: str = "",
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> ChatResponseSchema:
        """Execute full RAG chain: retrieval -> prompt construction -> LLM generation -> citation appending."""
        # 1. Retrieve knowledge
        rag_res: RAGResult = self.rag_pipeline.run_retrieval(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        # 2. Format Prompt
        formatted_prompt = rag_prompt_template.format(
            context=rag_res.context,
            chat_history=chat_history or "None",
            query=query,
        )

        # 3. Generate Answer via LLM
        try:
            raw_answer = self.llm_service.generate(formatted_prompt)
        except LLMServiceError as e:
            logger.error(f"RAGChain LLM generation error: {e.message}")
            raw_answer = "I apologize, but I encountered a system issue while processing your request."

        # 4. Map Citations
        citations_schemas: List[CitationSchema] = [
            CitationSchema(
                citation_index=c["citation_index"],
                document_id=c["document_id"],
                document_name=c["document_name"],
                page_number=c.get("page_number"),
                relevance_percentage=c["relevance_percentage"],
                snippet=c["snippet"],
            )
            for c in rag_res.citations
        ]

        return ChatResponseSchema(
            answer=raw_answer,
            citations=citations_schemas,
            confidence_score=1.0 if rag_res.has_sufficient_context else 0.3,
            has_sufficient_context=rag_res.has_sufficient_context,
        )
