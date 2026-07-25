import os
import re
from pathlib import Path
from typing import Tuple
from backend.src.config.settings import settings
from backend.src.domain.exceptions.document_exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    PathTraversalError,
)

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove dangerous path traversal sequences and special characters."""
    if not filename:
        raise PathTraversalError("Empty filename")

    # Reject null bytes or path separator tricks
    if "\0" in filename or "/" in filename or "\\" in filename or ".." in filename:
        raise PathTraversalError(filename)

    # Clean non-alphanumeric characters except dot, dash, underscore
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r"[^\w\.\-]", "_", clean_name)
    if not clean_name:
        raise PathTraversalError(filename)

    return clean_name


def validate_file_path_containment(file_path: Path, base_dir: Path) -> Path:
    """Ensure resolved file path remains strictly contained within the base upload directory."""
    resolved_base = base_dir.resolve()
    resolved_target = file_path.resolve()

    try:
        resolved_target.relative_to(resolved_base)
    except ValueError as exc:
        raise PathTraversalError(str(file_path)) from exc

    return resolved_target


def validate_uploaded_file(
    filename: str,
    content_type: str,
    file_size_bytes: int,
) -> Tuple[str, str]:
    """Validate file extension, size, and content type. Returns (sanitized_filename, extension)."""
    sanitized_name = sanitize_filename(filename)
    ext = Path(sanitized_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(f"Extension '{ext}' is not supported. Allowed: {list(ALLOWED_EXTENSIONS.keys())}")

    # Empty file check
    if file_size_bytes <= 0:
        raise InvalidFileTypeError("File cannot be empty.")

    # File size validation
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        file_size_mb = file_size_bytes / (1024 * 1024)
        raise FileTooLargeError(file_size_mb, settings.MAX_UPLOAD_SIZE_MB)

    return sanitized_name, ext
