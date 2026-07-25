from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class VectorStoreError(Exception):
    """Exception raised when vector database operations fail."""

    def __init__(self, message: str = "Vector store error"):
        self.message = message
        super().__init__(self.message)


@dataclass
class VectorChunk:
    chunk_id: str
    content: str
    embedding: List[float]
    document_id: str
    document_name: str
    chunk_index: int
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    document_id: str
    document_name: str
    page_number: Optional[int]
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class IVectorStore(ABC):
    """Abstract contract for vector database interactions."""

    @abstractmethod
    def add_chunks(self, chunks: List[VectorChunk]) -> List[str]:
        """Store chunk vectors and metadata in vector database."""
        pass

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        """Perform semantic similarity search using query vector."""
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> bool:
        """Remove all vector chunks associated with a specific document ID."""
        pass
