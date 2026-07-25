from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import get_current_active_user
from backend.src.presentation.api.v1.chat_router import get_chat_service
from backend.src.presentation.api.v1.report_router import get_report_service
from backend.src.presentation.api.v1.search_router import get_search_service
from backend.src.presentation.api.v1.health_router import get_health_service
from backend.src.presentation.schemas.health_schemas import ComponentHealth


@pytest.fixture
def mock_user():
    return User(
        id="usr_e2e_999",
        email="e2e_test@example.com",
        hashed_password="hashed_sample_password",
        full_name="E2E Tester",
        role="admin",
        is_active=True,
    )


def test_full_platform_e2e_flow(mock_user):
    """End-to-end integration test verifying auth, chat, search, reports, profile, and monitoring."""
    client = TestClient(app)

    # 1. Health Liveness Check
    liveness_res = client.get("/api/v1/health/live")
    assert liveness_res.status_code == 200
    assert liveness_res.json()["status"] == "healthy"

    # 2. Dependency Overrides for Mocked Services
    mock_chat_svc = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.id = "msg_e2e_1"
    mock_msg.conversation_id = "conv_e2e_1"
    mock_msg.sender_type = "assistant"
    mock_msg.content = "Based on official support documentation, password reset requires 2FA confirmation."
    mock_msg.sources = [
        {
            "citation_index": 1,
            "document_id": "doc_e2e_1",
            "document_name": "Security_Policy.pdf",
            "snippet": "Password reset procedure requires 2FA verification.",
            "relevance_percentage": "95.0%",
        }
    ]
    mock_msg.created_at = "2026-07-25T12:00:00"
    mock_chat_svc.process_user_question.return_value = mock_msg

    mock_search_svc = MagicMock()
    mock_search_svc.semantic_search.return_value = {
        "query": "password reset",
        "results": [
            {
                "chunk_id": "chunk_100",
                "document_id": "doc_e2e_1",
                "document_name": "Security_Policy.pdf",
                "content": "Password reset procedure requires 2FA verification.",
                "relevance_score": 0.95,
                "relevance_percentage": "95.0%",
                "metadata": {"filename": "Security_Policy.pdf"},
            }
        ],
        "total_results": 1,
        "search_mode": "semantic",
    }

    mock_report_svc = AsyncMock()
    mock_report_svc.generate_document_summary.return_value = {
        "document_id": "doc_e2e_1",
        "document_name": "Security_Policy.pdf",
        "summary": "This document covers enterprise security protocols.",
        "key_points": ["2FA required for password reset", "Session timeout at 60 mins"],
        "title": "Summary: Security_Policy.pdf",
    }

    mock_health_svc = AsyncMock()
    mock_health_svc.get_readiness_status.return_value = (
        "healthy",
        [
            ComponentHealth(name="database", status="healthy", details="PostgreSQL connected"),
            ComponentHealth(name="vector_store", status="healthy", details="ChromaDB online"),
        ],
    )
    mock_health_svc.get_system_metrics = MagicMock(
        return_value={
            "cpu_usage_percent": 12.0,
            "memory_usage_percent": 35.0,
            "disk_usage_percent": 25.0,
            "active_db_pool_status": "connected",
            "timestamp": 1000.0,
        }
    )

    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_svc
    app.dependency_overrides[get_search_service] = lambda: mock_search_svc
    app.dependency_overrides[get_report_service] = lambda: mock_report_svc
    app.dependency_overrides[get_health_service] = lambda: mock_health_svc

    # 3. Authenticated User Profile Check
    me_res = client.get("/api/v1/users/me")
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "e2e_test@example.com"

    # 4. Chat Q&A Interaction
    chat_res = client.post("/api/v1/chat/message", data={"query": "How do I reset my password?"})
    assert chat_res.status_code == 201
    chat_data = chat_res.json()
    assert "2FA confirmation" in chat_data["content"]
    assert len(chat_data["citations"]) == 1

    # 5. Semantic Vector Search
    search_res = client.post("/api/v1/search/semantic", json={"query": "password reset", "top_k": 5})
    assert search_res.status_code == 200
    assert len(search_res.json()["results"]) == 1

    # 6. Document Summarization Report
    report_res = client.post("/api/v1/reports/document-summary", json={"document_id": "doc_e2e_1"})
    assert report_res.status_code == 200
    assert report_res.json()["document_name"] == "Security_Policy.pdf"

    # 7. System Readiness & Metrics Verification
    ready_res = client.get("/api/v1/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "healthy"

    metrics_res = client.get("/api/v1/health/metrics")
    assert metrics_res.status_code == 200
    assert metrics_res.json()["cpu_usage_percent"] == 12.0

    app.dependency_overrides.clear()
