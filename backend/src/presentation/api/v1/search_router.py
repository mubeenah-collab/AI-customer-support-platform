import logging
from fastapi import APIRouter, Depends, status
from backend.src.ai.embeddings.gemini_embedding import GeminiEmbeddingService
from backend.src.ai.rag.chroma_vector_store import ChromaVectorStore
from backend.src.ai.rag.retriever import KnowledgeBaseRetriever
from backend.src.application.services.search_service import SearchService
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import get_current_active_user, require_admin
from backend.src.presentation.schemas.search_schemas import (
    SemanticSearchRequest,
    SearchResponse,
    RetrievalInspectionResponse,
)

logger = logging.getLogger("search_router")

router = APIRouter(prefix="/search", tags=["Search & Knowledge Base"])


def get_search_service() -> SearchService:
    """Dependency provider building SearchService with Gemini Embeddings and ChromaDB Vector Store."""
    embed_service = GeminiEmbeddingService()
    chroma_store = ChromaVectorStore()
    retriever = KnowledgeBaseRetriever(embedding_service=embed_service, vector_store=chroma_store)
    return SearchService(retriever=retriever)


@router.get(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic search via query parameter (Admin only)",
)
async def get_semantic_search(
    query: str,
    top_k: int = 5,
    current_user: User = Depends(require_admin),
    search_service: SearchService = Depends(get_search_service),
):
    return search_service.semantic_search(query=query, top_k=top_k)


@router.post(
    "/semantic",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic vector search across knowledge base chunks (Admin only)",
)
async def semantic_search(
    request: SemanticSearchRequest,
    current_user: User = Depends(require_admin),
    search_service: SearchService = Depends(get_search_service),
):
    return search_service.semantic_search(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        filter_metadata=request.filter_metadata,
    )


@router.post(
    "/hybrid",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Hybrid keyword + semantic vector search across knowledge base chunks (Admin only)",
)
async def hybrid_search(
    request: SemanticSearchRequest,
    current_user: User = Depends(require_admin),
    search_service: SearchService = Depends(get_search_service),
):
    return search_service.hybrid_search(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        filter_metadata=request.filter_metadata,
    )


@router.post(
    "/inspect",
    response_model=RetrievalInspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Inspect raw vector similarity matches, prompt text formatting, and LLM context (Admin only)",
)
async def inspect_retrieval(
    request: SemanticSearchRequest,
    current_user: User = Depends(require_admin),
    search_service: SearchService = Depends(get_search_service),
):
    return search_service.inspect_retrieval(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        filter_metadata=request.filter_metadata,
    )
