import os
import uuid
from pathlib import Path
from typing import Tuple
from backend.src.config.settings import settings
from backend.src.domain.exceptions.document_exceptions import FileStorageError, PathTraversalError
from backend.src.infrastructure.storage.file_validator import (
    sanitize_filename,
    validate_file_path_containment,
    validate_uploaded_file,
)


class StorageService:
    """Storage infrastructure service for managing physical files under uploads directory."""

    def __init__(self, base_upload_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_upload_dir).resolve()
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.cache_dir = self.base_dir / "cache"

        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def save_raw_file(
        self,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> Tuple[str, str, int, str]:
        """Validate and save raw uploaded file content. Returns (stored_filename, relative_path, file_size, sanitized_name)."""
        file_size = len(content)
        sanitized_name, ext = validate_uploaded_file(filename, content_type, file_size)

        unique_id = str(uuid.uuid4())
        stored_filename = f"{unique_id}_{sanitized_name}"
        target_path = self.raw_dir / stored_filename

        # Security check: containment
        validated_path = validate_file_path_containment(target_path, self.base_dir)

        try:
            with open(validated_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise FileStorageError(f"Failed to write file to disk: {str(e)}") from e

        relative_path = str(validated_path.relative_to(self.base_dir.parent))
        return stored_filename, relative_path, file_size, sanitized_name

    def delete_file(self, relative_path: str) -> bool:
        """Safely delete a stored file given its relative path."""
        try:
            target_path = (self.base_dir.parent / relative_path).resolve()
            validated_path = validate_file_path_containment(target_path, self.base_dir)

            if validated_path.exists():
                validated_path.unlink()
                return True
            return False
        except (PathTraversalError, Exception):
            return False
