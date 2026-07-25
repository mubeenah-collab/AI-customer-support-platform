from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.ai.rag.base_vector_store import RetrievedChunk
from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import get_current_active_user
from backend.src.presentation.api.v1.search_router import get_search_service


@pytest.fixture
def mock_active_user():
    return User(
        id="usr_search_123",
        email="search_user@example.com",
        hashed_password="hashed_password_sample",
        full_name="Search User",
        is_active=True,
    )


def test_semantic_search_unauthenticated():
    client = TestClient(app)
    response = client.post("/api/v1/search/semantic", json={"query": "refund policy"})
    assert response.status_code == 401


def test_semantic_search_authenticated(mock_active_user):
    mock_service = MagicMock()
    mock_service.semantic_search.return_value = {
        "query": "refund policy",
        "results": [
            {
                "chunk_id": "c1",
                "content": "Customers can request a refund within 30 days.",
                "document_id": "doc_1",
                "document_name": "Refund_Policy.pdf",
                "page_number": 2,
                "relevance_score": 0.92,
                "relevance_percentage": "92%",
                "metadata": {},
            }
        ],
        "total_results": 1,
    }

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_search_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/api/v1/search/semantic", json={"query": "refund policy", "top_k": 3})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 1
    assert data["results"][0]["document_name"] == "Refund_Policy.pdf"
    assert data["results"][0]["relevance_percentage"] == "92%"


def test_hybrid_search_authenticated(mock_active_user):
    mock_service = MagicMock()
    mock_service.hybrid_search.return_value = {
        "query": "warranty claims",
        "results": [
            {
                "chunk_id": "c2",
                "content": "Hardware warranty claims are valid for 1 year.",
                "document_id": "doc_2",
                "document_name": "Warranty.pdf",
                "page_number": 1,
                "relevance_score": 0.97,
                "relevance_percentage": "97%",
                "metadata": {},
            }
        ],
        "total_results": 1,
    }

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_search_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/api/v1/search/hybrid", json={"query": "warranty claims"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 1
    assert "Warranty.pdf" in data["results"][0]["document_name"]
