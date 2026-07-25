from pathlib import Path
from typing import List, Optional
from backend.src.domain.entities.document import Document
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.auth_exceptions import ForbiddenError
from backend.src.domain.exceptions.document_exceptions import DocumentNotFoundError
from backend.src.domain.repositories.document_repository import IDocumentRepository
from backend.src.infrastructure.storage.storage_service import StorageService
from backend.src.presentation.schemas.document_schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)


class DocumentService:
    """Application Service handling document upload, retrieval, and deletion workflows."""

    def __init__(
        self,
        document_repo: IDocumentRepository,
        storage_service: StorageService,
    ):
        self.document_repo = document_repo
        self.storage_service = storage_service

    async def upload_document(
        self,
        user: User,
        filename: str,
        content: bytes,
        content_type: str,
        title: Optional[str] = None,
    ) -> DocumentUploadResponse:
        stored_filename, relative_path, file_size, sanitized_name = await self.storage_service.save_raw_file(
            filename=filename,
            content=content,
            content_type=content_type,
        )

        doc_title = title or sanitized_name
        ext = Path(sanitized_name).suffix.lstrip(".").lower()

        new_doc = Document(
            title=doc_title,
            filename=sanitized_name,
            file_path=relative_path,
            file_type=ext,
            file_size=file_size,
            mime_type=content_type or "application/octet-stream",
            status="pending",
            user_id=user.id,
        )

        created_doc = await self.document_repo.create(new_doc)
        doc_response = DocumentResponse.model_validate(created_doc)

        return DocumentUploadResponse(
            message="Document uploaded successfully and queued for background processing",
            document=doc_response,
        )

    async def list_user_documents(self, user: User, skip: int = 0, limit: int = 100) -> DocumentListResponse:
        if user.role == "admin" or user.is_superuser:
            documents = await self.document_repo.get_all(skip=skip, limit=limit)
        else:
            documents = await self.document_repo.get_by_user_id(user.id, skip=skip, limit=limit)

        doc_responses = [DocumentResponse.model_validate(d) for d in documents]
        return DocumentListResponse(documents=doc_responses, total=len(doc_responses))

    async def get_document_by_id(self, user: User, document_id: str) -> DocumentResponse:
        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(document_id)

        if doc.user_id != user.id and user.role != "admin" and not user.is_superuser:
            raise ForbiddenError("You do not have permission to view this document.")

        return DocumentResponse.model_validate(doc)

    async def delete_document(self, user: User, document_id: str) -> bool:
        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(document_id)

        if doc.user_id != user.id and user.role != "admin" and not user.is_superuser:
            raise ForbiddenError("You do not have permission to delete this document.")

        # Remove physical file
        self.storage_service.delete_file(doc.file_path)

        # Delete database record
        return await self.document_repo.delete(document_id)
