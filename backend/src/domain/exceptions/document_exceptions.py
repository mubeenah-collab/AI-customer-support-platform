class DocumentException(Exception):
    """Base domain exception for document operations."""

    def __init__(self, message: str = "Document processing error"):
        self.message = message
        super().__init__(self.message)


class InvalidFileTypeError(DocumentException):
    """Raised when an uploaded file extension or MIME type is not allowed."""

    def __init__(self, details: str = "Unsupported file type"):
        super().__init__(f"Invalid file type: {details}")


class FileTooLargeError(DocumentException):
    """Raised when an uploaded file exceeds the maximum allowed size limit."""

    def __init__(self, file_size_mb: float, max_size_mb: int):
        super().__init__(f"File size {file_size_mb:.2f}MB exceeds maximum limit of {max_size_mb}MB.")


class PathTraversalError(DocumentException):
    """Raised when a file path attempts to escape the root upload directory."""

    def __init__(self, path: str = "Invalid file path"):
        super().__init__(f"Security error: Path traversal detected in filename/path '{path}'.")


class DocumentNotFoundError(DocumentException):
    """Raised when a requested document ID does not exist."""

    def __init__(self, document_id: str):
        super().__init__(f"Document with ID '{document_id}' not found.")


class FileStorageError(DocumentException):
    """Raised when an error occurs during file storage I/O."""

    def __init__(self, message: str = "Failed to store file"):
        super().__init__(message)
