from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of relevant chunks to return")
    score_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum relevance score threshold")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filter (e.g. document_id)")


class SearchResultItem(BaseModel):
    chunk_id: str
    content: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    relevance_score: float
    relevance_percentage: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total_results: int

    model_config = ConfigDict(from_attributes=True)
