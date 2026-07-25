from pathlib import Path
from typing import List
import docx
from backend.src.infrastructure.storage.loaders.base_loader import BaseDocumentLoader, ExtractedChunk


class DocxDocumentLoader(BaseDocumentLoader):
    """Loader strategy for extracting text from DOCX files using python-docx."""

    def load(self, file_path: Path) -> List[ExtractedChunk]:
        doc = docx.Document(str(file_path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        full_text = "\n\n".join(paragraphs)
        if not full_text.strip():
            return []

        return [
            ExtractedChunk(
                content=full_text,
                page_number=1,
                metadata={"paragraph_count": len(paragraphs)},
            )
        ]
