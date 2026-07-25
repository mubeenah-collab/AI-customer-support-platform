from unittest.mock import MagicMock, patch
import pytest
from backend.src.ai.embeddings.base_embedding import EmbeddingServiceError
from backend.src.ai.embeddings.gemini_embedding import (
    GeminiEmbeddingService,
    GEMINI_EMBEDDING_DIMENSION,
)
from backend.src.workers.embedding_worker import generate_chunk_embeddings

DIM = GEMINI_EMBEDDING_DIMENSION  # 3072 for gemini-embedding-001


def test_gemini_embedding_dimension():
    service = GeminiEmbeddingService(api_key="test_key")
    assert service.dimension == DIM


def test_gemini_embedding_missing_api_key():
    service = GeminiEmbeddingService(api_key="")
    with pytest.raises(EmbeddingServiceError) as exc_info:
        service.embed_query("test query")
    assert "Google API Key is missing" in str(exc_info.value)


@patch("backend.src.ai.embeddings.gemini_embedding.GoogleGenerativeAIEmbeddings")
def test_gemini_embedding_embed_query_mock(mock_client_cls):
    mock_client = MagicMock()
    mock_client.embed_query.return_value = [0.1] * DIM
    mock_client_cls.return_value = mock_client

    service = GeminiEmbeddingService(api_key="test_key")
    vector = service.embed_query("What is customer support policy?")

    assert len(vector) == DIM
    assert vector[0] == 0.1
    mock_client.embed_query.assert_called_once_with("What is customer support policy?")


@patch("backend.src.ai.embeddings.gemini_embedding.GoogleGenerativeAIEmbeddings")
def test_gemini_embedding_embed_documents_mock(mock_client_cls):
    mock_client = MagicMock()
    mock_client.embed_documents.return_value = [[0.1] * DIM, [0.2] * DIM]
    mock_client_cls.return_value = mock_client

    service = GeminiEmbeddingService(api_key="test_key")
    vectors = service.embed_documents(["Chunk 1 text", "Chunk 2 text"])

    assert len(vectors) == 2
    assert len(vectors[0]) == DIM
    assert vectors[0][0] == 0.1
    assert vectors[1][0] == 0.2


def test_embedding_worker_function():
    mock_service = MagicMock()
    mock_service.embed_documents.return_value = [[0.5] * DIM, [0.6] * DIM]

    chunks = [("chunk_1", "text 1"), ("chunk_2", "text 2")]
    results = generate_chunk_embeddings(chunks, embedding_service=mock_service)

    assert len(results) == 2
    assert results[0][0] == "chunk_1"
    assert results[0][1][0] == 0.5
    assert results[1][0] == "chunk_2"
    assert results[1][1][0] == 0.6
