import logging
from typing import Any, Dict, List, Optional
from backend.src.ai.embeddings.base_embedding import EmbeddingServiceError, IEmbeddingService
from backend.src.ai.rag.base_vector_store import IVectorStore, RetrievedChunk, VectorStoreError
from backend.src.config.settings import settings

logger = logging.getLogger("rag_retriever")


class KnowledgeBaseRetriever:
    """Retriever engine coordinating query embedding and vector store similarity search."""

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStore,
        top_k: int = settings.RETRIEVAL_TOP_K,
        score_threshold: float = settings.RETRIEVAL_SCORE_THRESHOLD,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        """Embed user query and retrieve matching knowledge chunks from vector store."""
        if not query or not query.strip():
            return []

        effective_k = top_k if top_k is not None else self.top_k
        effective_threshold = score_threshold if score_threshold is not None else self.score_threshold

        try:
            query_vector = self.embedding_service.embed_query(query.strip())
        except EmbeddingServiceError as e:
            logger.error(f"Retriever error during query embedding: {e.message}")
            return []

        try:
            retrieved_chunks = self.vector_store.similarity_search(
                query_embedding=query_vector,
                top_k=effective_k,
                score_threshold=effective_threshold,
                filter_metadata=filter_metadata,
            )
            logger.info(f"Retriever fetched {len(retrieved_chunks)} relevant chunks for query.")
            return retrieved_chunks
        except VectorStoreError as e:
            logger.error(f"Retriever error during vector search: {e.message}")
            return []
