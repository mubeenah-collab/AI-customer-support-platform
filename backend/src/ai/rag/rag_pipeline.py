from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from backend.src.ai.rag.base_vector_store import RetrievedChunk
from backend.src.ai.rag.citation_formatter import format_citations, format_citations_text
from backend.src.ai.rag.context_builder import build_rag_context
from backend.src.ai.rag.retriever import KnowledgeBaseRetriever


@dataclass
class RAGResult:
    query: str
    context: str
    chunks: List[RetrievedChunk]
    citations: List[Dict[str, Any]]
    citations_text: str
    has_sufficient_context: bool


class RAGPipeline:
    """RAG orchestration pipeline executing retrieval, context assembly, and citation extraction."""

    def __init__(self, retriever: KnowledgeBaseRetriever):
        self.retriever = retriever

    def run_retrieval(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> RAGResult:
        """Execute retrieval step and prepare grounded prompt context and citations."""
        chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            filter_metadata=filter_metadata,
        )

        context_str = build_rag_context(chunks)
        citations_list = format_citations(chunks)
        citations_txt = format_citations_text(citations_list)
        has_context = len(chunks) > 0

        return RAGResult(
            query=query,
            context=context_str,
            chunks=chunks,
            citations=citations_list,
            citations_text=citations_txt,
            has_sufficient_context=has_context,
        )
