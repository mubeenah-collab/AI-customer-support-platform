from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ExtractedChunk:
    content: str
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDocumentLoader(ABC):
    """Abstract base class for all document loader strategy implementations."""

    @abstractmethod
    def load(self, file_path: Path) -> List[ExtractedChunk]:
        """Extract text chunks and metadata from a target file."""
        pass
