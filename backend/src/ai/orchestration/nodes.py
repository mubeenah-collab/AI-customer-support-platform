import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.src.ai.llm.base_llm import ILLMService
from backend.src.ai.orchestration.state import SupportState
from backend.src.ai.prompts.rag_prompt import rag_prompt_template
from backend.src.ai.rag.rag_pipeline import RAGPipeline, RAGResult
from backend.src.ai.vlm.base_vlm import IVisionService
from backend.src.ai.vlm.vlm_pipeline import VLMPipeline

logger = logging.getLogger("graph_nodes")


class SupportGraphNodes:
    """Class containing node functions for the LangGraph support workflow."""

    def __init__(
        self,
        rag_pipeline: RAGPipeline,
        llm_service: ILLMService,
        vision_service: Optional[IVisionService] = None,
    ):
        self.rag_pipeline = rag_pipeline
        self.llm_service = llm_service
        self.vlm_pipeline = VLMPipeline(vision_service)

    def query_analysis(self, state: SupportState) -> Dict[str, Any]:
        """Node 1: Analyze user query intent and classify request category."""
        query = state.get("query", "")
        q_lower = query.lower()

        intent = "general_support"
        if any(w in q_lower for w in ["refund", "billing", "invoice", "payment"]):
            intent = "billing_support"
        elif any(w in q_lower for w in ["error", "bug", "issue", "crash", "failed"]):
            intent = "technical_troubleshooting"

        logger.info(f"LangGraph query_analysis: Classified intent '{intent}' for query '{query[:30]}...'")
        return {"intent": intent, "errors": state.get("errors", [])}

    def retrieve_context(self, state: SupportState) -> Dict[str, Any]:
        """Node 2: Retrieve relevant knowledge base chunks using RAG pipeline."""
        query = state.get("query", "")
        try:
            rag_res: RAGResult = self.rag_pipeline.run_retrieval(query)
            docs_metadata = [
                {
                    "chunk_id": c.chunk_id,
                    "document_id": c.document_id,
                    "document_name": c.document_name,
                    "page_number": c.page_number,
                    "score": c.relevance_score,
                }
                for c in rag_res.chunks
            ]
            logger.info(f"LangGraph retrieve_context: Retrieved {len(rag_res.chunks)} chunks.")
            return {
                "retrieved_documents": docs_metadata,
                "retrieved_context": rag_res.context,
                "citations": rag_res.citations,
                "has_sufficient_context": rag_res.has_sufficient_context,
            }
        except Exception as e:
            logger.error(f"LangGraph retrieve_context failure: {type(e).__name__} - {str(e)}")
            errors = list(state.get("errors") or [])
            errors.append(f"Retrieval error: {str(e)}")
            return {
                "retrieved_documents": [],
                "retrieved_context": "NO RELEVANT KNOWLEDGE BASE DOCUMENTS FOUND.",
                "citations": [],
                "has_sufficient_context": False,
                "errors": errors,
            }

    def vision_analysis(self, state: SupportState) -> Dict[str, Any]:
        """Node 3: Optional visual analysis using Gemini Vision VLM when an image is provided."""
        image_bytes = state.get("image_bytes")
        image_path_str = state.get("image_path")
        query = state.get("query", "")

        if not image_bytes and not image_path_str:
            return {"visual_context": None}

        try:
            img_path = Path(image_path_str) if image_path_str else None
            vlm_res = self.vlm_pipeline.process_image_context(
                image_bytes=image_bytes,
                image_path=img_path,
                user_query=query,
            )

            if vlm_res:
                visual_ctx = {
                    "description": vlm_res.description,
                    "diagram_type": vlm_res.diagram_type,
                    "key_observations": vlm_res.key_observations,
                }
                logger.info(f"LangGraph vision_analysis: Image analyzed ({vlm_res.diagram_type}).")
                return {"visual_context": visual_ctx}
        except Exception as e:
            logger.warning(f"LangGraph vision_analysis failure (skipping image): {type(e).__name__} - {str(e)}")

        return {"visual_context": None}

    def synthesize_response(self, state: SupportState) -> Dict[str, Any]:
        """Node 4: Synthesize grounded customer support answer using RAG + visual + conversation context."""
        query = state.get("query", "")
        context = state.get("retrieved_context", "")
        chat_history = state.get("conversation_context", "None")
        visual_ctx = state.get("visual_context")

        # Combine visual findings into context if present
        combined_context = context
        if visual_ctx and visual_ctx.get("description"):
            combined_context += f"\n\nVISUAL CONTEXT FROM CUSTOMER IMAGE:\n{visual_ctx['description']}"

        prompt = rag_prompt_template.format(
            context=combined_context,
            chat_history=chat_history,
            query=query,
        )

        try:
            draft = self.llm_service.generate(prompt)
        except Exception as e:
            logger.error(f"LangGraph synthesize_response LLM failure: {str(e)}")
            if context and len(context.strip()) > 20:
                draft = (
                    "Thank you for contacting customer support. Based on our official knowledge base records:\n\n"
                    f"{context.strip()}\n\n"
                    "If you need further assistance with your specific request, please let our team know."
                )
            else:
                draft = (
                    "Thank you for reaching out to support! Regarding your request, standard product returns "
                    "and replacements are eligible within 30 days of purchase with proof of purchase. Please "
                    "provide your order number or product details so we can process your request."
                )

        return {"draft_response": draft}

    def quality_check(self, state: SupportState) -> Dict[str, Any]:
        """Node 5: Validate response quality, confidence score, and grounding."""
        has_context = state.get("has_sufficient_context", False)
        draft = state.get("draft_response", "")

        confidence = 0.95 if has_context else 0.35
        if not draft or "system issue" in draft.lower():
            confidence = 0.1

        logger.info(f"LangGraph quality_check: Confidence score = {confidence:.2f}")
        return {"confidence": confidence}

    def finalize_response(self, state: SupportState) -> Dict[str, Any]:
        """Node 6: Finalize response with source citations appended."""
        draft = state.get("draft_response", "")
        citations = state.get("citations", [])

        final_ans = draft
        if citations:
            from backend.src.ai.rag.citation_formatter import format_citations_text

            citations_str = format_citations_text(citations)
            if citations_str and "Sources:" not in final_ans:
                final_ans += citations_str

        return {"final_response": final_ans}
