import logging
from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.src.ai.gemini_retry import call_with_retry
from backend.src.ai.embeddings.base_embedding import EmbeddingServiceError, IEmbeddingService
from backend.src.config.settings import settings

logger = logging.getLogger("gemini_embedding")

GEMINI_EMBEDDING_DIMENSION = 3072  # gemini-embedding-001 output dimension


class GeminiEmbeddingService(IEmbeddingService):
    """Concrete implementation of IEmbeddingService using Google Gemini Embeddings."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        # Use provided api_key; only fall back to settings when argument is None (not when explicitly empty).
        self.api_key = settings.GOOGLE_API_KEY if api_key is None else api_key
        self.model_name = model_name or settings.GEMINI_EMBEDDING_MODEL
        self._embeddings_client: Optional[GoogleGenerativeAIEmbeddings] = None

        if self.api_key:
            try:
                self._embeddings_client = GoogleGenerativeAIEmbeddings(
                    model=self.model_name,
                    google_api_key=self.api_key,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Embeddings client: {str(e)}")

    @property
    def dimension(self) -> int:
        return GEMINI_EMBEDDING_DIMENSION

    def _get_client(self) -> GoogleGenerativeAIEmbeddings:
        if not self._embeddings_client:
            if not self.api_key:
                raise EmbeddingServiceError("Google API Key is missing. Set GOOGLE_API_KEY environment variable.")
            try:
                self._embeddings_client = GoogleGenerativeAIEmbeddings(
                    model=self.model_name,
                    google_api_key=self.api_key,
                )
            except Exception as e:
                raise EmbeddingServiceError(f"Initialization error: {str(e)}") from e
        return self._embeddings_client

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding vector for a single query text using Gemini."""
        if not text or not text.strip():
            raise EmbeddingServiceError("Cannot embed empty text query.")

        client = self._get_client()
        try:
            vector = call_with_retry(client.embed_query, text)
            if not vector or len(vector) == 0:
                raise EmbeddingServiceError("Gemini API returned empty embedding vector.")
            return vector
        except EmbeddingServiceError:
            raise
        except Exception as e:
            logger.error("Gemini embed_query failure: %s", type(e).__name__)
            raise EmbeddingServiceError(f"Gemini API error during embed_query: {type(e).__name__}") from e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of document chunk texts using Gemini."""
        if not texts:
            return []

        client = self._get_client()
        try:
            vectors = call_with_retry(client.embed_documents, texts)
            if not vectors or len(vectors) != len(texts):
                raise EmbeddingServiceError("Gemini API returned mismatched number of embedding vectors.")
            return vectors
        except EmbeddingServiceError:
            raise
        except Exception as e:
            logger.error("Gemini embed_documents failure: %s", type(e).__name__)
            raise EmbeddingServiceError(f"Gemini API error during embed_documents: {type(e).__name__}") from e
