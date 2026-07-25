from abc import ABC, abstractmethod
from typing import List


class EmbeddingServiceError(Exception):
    """Exception raised when embedding generation fails."""

    def __init__(self, message: str = "Embedding service failure"):
        self.message = message
        super().__init__(self.message)


class IEmbeddingService(ABC):
    """Abstract interface defining contract for vector embedding generation."""

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding vector for a single search query."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of document chunk texts."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimension size (e.g. 768 for Gemini text-embedding-004)."""
        pass
