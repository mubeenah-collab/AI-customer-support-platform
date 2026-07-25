from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentSummaryRequest(BaseModel):
    document_id: str = Field(..., description="ID of processed document to summarize")


class DocumentSummaryResponse(BaseModel):
    document_id: str
    document_name: str
    summary: str
    key_points: List[str] = Field(default_factory=list)
    title: Optional[str] = None


class SupportReportRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="Topic or prompt focus for the support report")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to ground the report context")


class SupportReportResponse(BaseModel):
    id: str
    user_id: str
    title: str
    report_type: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: List[SupportReportResponse]
    total: int
