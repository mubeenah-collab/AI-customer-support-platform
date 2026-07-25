from pathlib import Path
from typing import List
from PIL import Image
from backend.src.infrastructure.storage.loaders.base_loader import BaseDocumentLoader, ExtractedChunk


class ImageDocumentLoader(BaseDocumentLoader):
    """Loader strategy for image metadata extraction (VLM processes pixel context during graph inference)."""

    def load(self, file_path: Path) -> List[ExtractedChunk]:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format or "IMAGE"
                description = f"Image file: {file_path.name} ({format_name}, {width}x{height} pixels). Prepared for Gemini Vision visual analysis."
                return [
                    ExtractedChunk(
                        content=description,
                        page_number=1,
                        metadata={"width": width, "height": height, "format": format_name},
                    )
                ]
        except Exception:
            return [ExtractedChunk(content=f"Image file: {file_path.name}", page_number=1)]
