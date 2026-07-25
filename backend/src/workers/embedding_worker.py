import logging
from typing import List, Tuple
from backend.src.ai.embeddings.base_embedding import EmbeddingServiceError, IEmbeddingService
from backend.src.ai.embeddings.gemini_embedding import GeminiEmbeddingService

logger = logging.getLogger("embedding_worker")


def generate_chunk_embeddings(
    chunks: List[Tuple[str, str]],  # List of (chunk_id, chunk_text)
    embedding_service: IEmbeddingService = GeminiEmbeddingService(),
) -> List[Tuple[str, List[float]]]:
    """Generate vector embeddings for a list of (chunk_id, text) tuples."""
    if not chunks:
        return []

    texts = [c[1] for c in chunks]
    try:
        vectors = embedding_service.embed_documents(texts)
        result = [(chunks[i][0], vectors[i]) for i in range(len(chunks))]
        logger.info(f"Generated {len(result)} embeddings successfully.")
        return result
    except EmbeddingServiceError as e:
        logger.error(f"Embedding worker error: {e.message}")
        raise
