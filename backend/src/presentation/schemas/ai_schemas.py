from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CitationSchema(BaseModel):
    citation_index: int
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    relevance_percentage: str
    snippet: str


class ChatResponseSchema(BaseModel):
    answer: str
    citations: List[CitationSchema] = Field(default_factory=list)
    confidence_score: float = 1.0
    has_sufficient_context: bool = True

    model_config = ConfigDict(from_attributes=True)


class SummaryResponseSchema(BaseModel):
    summary: str
    key_points: List[str] = Field(default_factory=list)
    title: Optional[str] = None


class ComparisonResponseSchema(BaseModel):
    comparison_summary: str
    key_differences: List[str] = Field(default_factory=list)
    key_similarities: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
