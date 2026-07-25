from pathlib import Path
from typing import List
from backend.src.infrastructure.storage.loaders.base_loader import BaseDocumentLoader, ExtractedChunk


class TextDocumentLoader(BaseDocumentLoader):
    """Loader strategy for extracting plain text files."""

    def load(self, file_path: Path) -> List[ExtractedChunk]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if not content.strip():
            return []

        return [ExtractedChunk(content=content, page_number=1)]
