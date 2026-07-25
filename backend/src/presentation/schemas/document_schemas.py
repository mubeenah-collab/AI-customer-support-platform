from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    mime_type: str
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    message: str = "Document uploaded successfully"
    document: DocumentResponse


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
