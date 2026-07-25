from pathlib import Path
from typing import List
from backend.src.domain.exceptions.document_exceptions import InvalidFileTypeError
from backend.src.infrastructure.storage.loaders.base_loader import BaseDocumentLoader, ExtractedChunk
from backend.src.infrastructure.storage.loaders.docx_loader import DocxDocumentLoader
from backend.src.infrastructure.storage.loaders.excel_loader import ExcelCsvDocumentLoader
from backend.src.infrastructure.storage.loaders.image_loader import ImageDocumentLoader
from backend.src.infrastructure.storage.loaders.pdf_loader import PDFDocumentLoader
from backend.src.infrastructure.storage.loaders.pptx_loader import PPTXDocumentLoader
from backend.src.infrastructure.storage.loaders.text_loader import TextDocumentLoader


class DocumentLoaderFactory:
    """Factory creating appropriate loader based on file extension."""

    @staticmethod
    def get_loader(file_extension: str) -> BaseDocumentLoader:
        ext = file_extension.lower()
        if not ext.startswith("."):
            ext = f".{ext}"

        if ext == ".pdf":
            return PDFDocumentLoader()
        elif ext == ".docx":
            return DocxDocumentLoader()
        elif ext == ".pptx":
            return PPTXDocumentLoader()
        elif ext in (".csv", ".xlsx"):
            return ExcelCsvDocumentLoader()
        elif ext == ".txt":
            return TextDocumentLoader()
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            return ImageDocumentLoader()
        else:
            raise InvalidFileTypeError(f"No document loader registered for extension '{ext}'")

    @classmethod
    def load_document(cls, file_path: Path) -> List[ExtractedChunk]:
        loader = cls.get_loader(file_path.suffix)
        return loader.load(file_path)
