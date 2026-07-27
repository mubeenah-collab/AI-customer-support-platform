import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
)
from backend.src.presentation.api.v1.search_router import get_search_service


@pytest.fixture
def admin_user():
    return User(
        id="admin_inspect_123",
        email="admin_inspect@example.com",
        hashed_password="hashed_pwd",
        full_name="Inspect Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )


@pytest.fixture
def customer_user():
    return User(
        id="customer_inspect_123",
        email="customer_inspect@example.com",
        hashed_password="hashed_pwd",
        full_name="Inspect Customer",
        role="customer",
        is_active=True,
    )


def test_unauthenticated_inspect_retrieval_returns_401():
    client = TestClient(app)
    app.dependency_overrides.clear()
    res = client.post("/api/v1/search/inspect", json={"query": "refund policy"})
    assert res.status_code == 401


def test_customer_inspect_retrieval_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.post("/api/v1/search/inspect", json={"query": "refund policy"})
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_admin_inspect_retrieval_success(admin_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user

    mock_svc = MagicMock()
    mock_inspection = {
        "query": "refund policy",
        "total_chunks_retrieved": 1,
        "raw_matches": [
            {
                "chunk_id": "chunk_101",
                "content_snippet": "Standard products are eligible for refund within 30 days...",
                "document_id": "doc_999",
                "document_name": "ReturnPolicy.pdf",
                "similarity_score": 0.92,
                "distance": 0.08,
                "relevance_percentage": "92%",
                "metadata": {"category": "policy"},
            }
        ],
        "formatted_prompt": "=== SYSTEM PROMPT ===\nYou are a helpful customer support assistant...",
        "context_window_length": 450,
        "estimated_context_tokens": 112,
    }
    mock_svc.inspect_retrieval.return_value = mock_inspection
    app.dependency_overrides[get_search_service] = lambda: mock_svc

    res = client.post("/api/v1/search/inspect", json={"query": "refund policy", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "refund policy"
    assert data["total_chunks_retrieved"] == 1
    assert data["raw_matches"][0]["chunk_id"] == "chunk_101"
    assert data["raw_matches"][0]["similarity_score"] == 0.92
    assert "=== SYSTEM PROMPT ===" in data["formatted_prompt"]
