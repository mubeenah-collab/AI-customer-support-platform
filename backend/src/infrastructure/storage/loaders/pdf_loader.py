from pathlib import Path
from typing import List
import pypdf
from backend.src.infrastructure.storage.loaders.base_loader import BaseDocumentLoader, ExtractedChunk


class PDFDocumentLoader(BaseDocumentLoader):
    """Loader strategy for extracting text from PDF files using pypdf."""

    def load(self, file_path: Path) -> List[ExtractedChunk]:
        chunks: List[ExtractedChunk] = []
        reader = pypdf.PdfReader(str(file_path))

        for page_idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                chunks.append(
                    ExtractedChunk(
                        content=text,
                        page_number=page_idx,
                        metadata={"total_pages": len(reader.pages)},
                    )
                )

        return chunks
