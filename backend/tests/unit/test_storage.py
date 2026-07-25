from pathlib import Path
import pytest
from backend.src.domain.exceptions.document_exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    PathTraversalError,
)
from backend.src.infrastructure.storage.file_validator import (
    sanitize_filename,
    validate_file_path_containment,
    validate_uploaded_file,
)
from backend.src.infrastructure.storage.storage_service import StorageService


def test_sanitize_filename_valid():
    name = sanitize_filename("my_manual-v1.2.pdf")
    assert name == "my_manual-v1.2.pdf"


def test_sanitize_filename_path_traversal_rejection():
    with pytest.raises(PathTraversalError):
        sanitize_filename("../../../etc/passwd")

    with pytest.raises(PathTraversalError):
        sanitize_filename("..\\..\\windows\\system32\\config")


def test_validate_uploaded_file_valid():
    name, ext = validate_uploaded_file("document.pdf", "application/pdf", 1024 * 1024)
    assert name == "document.pdf"
    assert ext == ".pdf"


def test_validate_uploaded_file_unsupported_type():
    with pytest.raises(InvalidFileTypeError):
        validate_uploaded_file("script.exe", "application/octet-stream", 1024)


def test_validate_uploaded_file_oversized():
    # 25 MB file should exceed default 20MB limit
    oversized_bytes = 25 * 1024 * 1024
    with pytest.raises(FileTooLargeError):
        validate_uploaded_file("huge.pdf", "application/pdf", oversized_bytes)


def test_validate_uploaded_file_empty():
    with pytest.raises(InvalidFileTypeError) as exc_info:
        validate_uploaded_file("empty.pdf", "application/pdf", 0)
    assert "cannot be empty" in str(exc_info.value)


def test_validate_file_path_containment(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()

    valid_file = base_dir / "raw" / "safe.pdf"
    valid_file.parent.mkdir()
    valid_file.write_text("dummy")

    resolved = validate_file_path_containment(valid_file, base_dir)
    assert resolved == valid_file.resolve()

    # Escape attempt
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret")
    with pytest.raises(PathTraversalError):
        validate_file_path_containment(outside_file, base_dir)
