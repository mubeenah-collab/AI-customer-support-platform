import logging
from typing import Any, Dict, List, Optional
from backend.src.ai.rag.retriever import KnowledgeBaseRetriever
from backend.src.presentation.schemas.search_schemas import SearchResponse, SearchResultItem

logger = logging.getLogger("search_service")


class SearchService:
    """Application service for semantic and hybrid knowledge retrieval search operations."""

    def __init__(self, retriever: KnowledgeBaseRetriever):
        self.retriever = retriever

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """Perform semantic similarity search against ChromaDB vector store using Gemini query embeddings."""
        if not query or not query.strip():
            return SearchResponse(query="", results=[], total_results=0)

        retrieved_chunks = self.retriever.retrieve(
            query=query.strip(),
            top_k=top_k,
            score_threshold=score_threshold,
            filter_metadata=filter_metadata,
        )

        items: List[SearchResultItem] = []
        for chunk in retrieved_chunks:
            pct_str = f"{int(round(chunk.relevance_score * 100))}%"
            item = SearchResultItem(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                page_number=chunk.page_number,
                relevance_score=chunk.relevance_score,
                relevance_percentage=pct_str,
                metadata=chunk.metadata or {},
            )
            items.append(item)

        return SearchResponse(query=query.strip(), results=items, total_results=len(items))

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """Perform hybrid search combining vector semantic similarity and keyword presence boosting."""
        base_response = self.semantic_search(
            query=query,
            top_k=top_k * 2,  # Fetch wider candidate pool
            score_threshold=score_threshold,
            filter_metadata=filter_metadata,
        )

        if not base_response.results:
            return base_response

        # Keyword presence score boost
        query_words = set(query.lower().split())
        scored_items: List[SearchResultItem] = []

        for item in base_response.results:
            content_lower = item.content.lower()
            keyword_matches = sum(1 for word in query_words if word in content_lower)
            keyword_boost = 0.05 * min(keyword_matches, 3)

            adjusted_score = min(1.0, item.relevance_score + keyword_boost)
            adjusted_pct = f"{int(round(adjusted_score * 100))}%"

            scored_item = SearchResultItem(
                chunk_id=item.chunk_id,
                content=item.content,
                document_id=item.document_id,
                document_name=item.document_name,
                page_number=item.page_number,
                relevance_score=adjusted_score,
                relevance_percentage=adjusted_pct,
                metadata=item.metadata,
            )
            scored_items.append(scored_item)

        # Sort by adjusted hybrid score descending and trim to top_k
        scored_items.sort(key=lambda x: x.relevance_score, reverse=True)
        final_items = scored_items[:top_k]

        return SearchResponse(query=query.strip(), results=final_items, total_results=len(final_items))
