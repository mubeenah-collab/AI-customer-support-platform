from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.application.services.document_service import DocumentService
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.auth_exceptions import ForbiddenError
from backend.src.domain.exceptions.document_exceptions import (
    DocumentException,
    DocumentNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    PathTraversalError,
)
from backend.src.infrastructure.database.session import AsyncSessionFactory, get_async_db
from backend.src.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from backend.src.infrastructure.storage.storage_service import StorageService
from backend.src.presentation.api.v1.dependencies import get_current_active_user
from backend.src.presentation.schemas.document_schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from backend.src.workers.document_worker import process_document_background

document_router = APIRouter(prefix="/documents", tags=["Documents"])


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return AsyncSessionFactory


def get_document_service(session: AsyncSession = Depends(get_async_db)) -> DocumentService:
    doc_repo = SQLAlchemyDocumentRepository(session)
    storage_service = StorageService()
    return DocumentService(doc_repo, storage_service)


@document_router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    doc_service: DocumentService = Depends(get_document_service),
    session_factory: async_sessionmaker[AsyncSession] = Depends(get_session_factory),
):
    """Upload a knowledge base document for background parsing and embedding."""
    try:
        content = await file.read()
        res = await doc_service.upload_document(
            user=current_user,
            filename=file.filename or "uploaded_file",
            content=content,
            content_type=file.content_type or "application/octet-stream",
            title=title,
        )

        # Trigger background document processing task
        background_tasks.add_task(
            process_document_background,
            document_id=res.document.id,
            base_dir=doc_service.storage_service.base_dir,
            session_factory=session_factory,
        )

        return res
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except FileTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=e.message)
    except PathTraversalError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DocumentException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@document_router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    doc_service: DocumentService = Depends(get_document_service),
):
    """List uploaded documents for current user or all documents for admins."""
    return await doc_service.list_user_documents(current_user, skip=skip, limit=limit)


@document_router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Retrieve details of a specific document by ID."""
    try:
        return await doc_service.get_document_by_id(current_user, document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@document_router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Delete a document and its stored physical file."""
    try:
        success = await doc_service.delete_document(current_user, document_id)
        return {"message": "Document deleted successfully", "id": document_id, "success": success}
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
