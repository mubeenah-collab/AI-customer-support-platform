import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
)
from backend.src.presentation.api.v1.ticket_router import get_ticket_service
from backend.src.presentation.api.v1.search_router import get_search_service
from backend.src.presentation.api.v1.report_router import get_report_service


@pytest.fixture
def e2e_admin_user():
    return User(
        id="e2e_admin_999",
        email="e2e_admin@enterprise.com",
        hashed_password="hashed_password_123",
        full_name="E2E Executive Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )


@pytest.fixture
def e2e_customer_user():
    return User(
        id="e2e_customer_888",
        email="e2e_customer@enterprise.com",
        hashed_password="hashed_password_123",
        full_name="E2E Customer User",
        role="customer",
        is_active=True,
        is_superuser=False,
    )


def test_e2e_rbac_security_isolation(e2e_customer_user):
    """E2E Test: Customer attempting to access admin endpoints receives 403 Forbidden."""
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: e2e_customer_user

    # 1. Admin document upload endpoint
    res1 = client.get("/api/v1/documents")
    assert res1.status_code == 403

    # 2. Admin search console endpoint
    res2 = client.post("/api/v1/search/semantic", json={"query": "test query"})
    assert res2.status_code == 403

    # 3. Admin reports endpoint
    res3 = client.get("/api/v1/reports")
    assert res3.status_code == 403

    # 4. Admin search inspector endpoint
    res4 = client.post("/api/v1/search/inspect", json={"query": "test query"})
    assert res4.status_code == 403


def test_e2e_full_support_ticket_lifecycle(e2e_customer_user, e2e_admin_user):
    """E2E Test: Customer creates support ticket, Admin lists ticket queue and updates lifecycle status."""
    client = TestClient(app)

    # Step 1: Customer creates ticket
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: e2e_customer_user

    mock_ticket_svc = AsyncMock()
    mock_ticket = MagicMock()
    mock_ticket.id = "ticket_e2e_001"
    mock_ticket.user_id = e2e_customer_user.id
    mock_ticket.subject = "Hardware Failure"
    mock_ticket.description = "Device power switch un-responsive."
    mock_ticket.status = "open"
    mock_ticket.priority = "high"
    mock_ticket.category = "hardware"
    mock_ticket.created_at = "2026-07-26T12:00:00"
    mock_ticket.updated_at = "2026-07-26T12:00:00"

    mock_ticket_svc.create_ticket.return_value = mock_ticket
    app.dependency_overrides[get_ticket_service] = lambda: mock_ticket_svc

    res1 = client.post(
        "/api/v1/tickets",
        json={"subject": "Hardware Failure", "description": "Device power switch un-responsive.", "priority": "high", "category": "hardware"},
    )
    assert res1.status_code == 201
    assert res1.json()["id"] == "ticket_e2e_001"

    # Step 2: Admin updates ticket status to 'in_progress'
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: e2e_admin_user
    app.dependency_overrides[require_admin] = lambda: e2e_admin_user

    mock_ticket.status = "in_progress"
    mock_ticket_svc.update_ticket.return_value = mock_ticket
    app.dependency_overrides[get_ticket_service] = lambda: mock_ticket_svc

    res2 = client.patch("/api/v1/tickets/ticket_e2e_001", json={"status": "in_progress"})
    assert res2.status_code == 200
    assert res2.json()["status"] == "in_progress"


def test_e2e_admin_retrieval_inspector_flow(e2e_admin_user):
    """E2E Test: Admin performs deep retrieval inspection on raw vector distances and formatted prompt."""
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: e2e_admin_user
    app.dependency_overrides[require_admin] = lambda: e2e_admin_user

    mock_search_svc = MagicMock()
    mock_search_svc.inspect_retrieval.return_value = {
        "query": "warranty claims",
        "total_chunks_retrieved": 1,
        "raw_matches": [
            {
                "chunk_id": "chunk_99",
                "content_snippet": "Standard products are eligible for 30-day warranty...",
                "document_id": "doc_10",
                "document_name": "WarrantyPolicy.pdf",
                "similarity_score": 0.88,
                "distance": 0.12,
                "relevance_percentage": "88%",
                "metadata": {"section": "warranty"},
            }
        ],
        "formatted_prompt": "=== SYSTEM PROMPT ===\nYou are an AI support assistant...\n\n=== CONTEXT PAYLOAD ===\n...",
        "context_window_length": 350,
        "estimated_context_tokens": 87,
    }
    app.dependency_overrides[get_search_service] = lambda: mock_search_svc

    res = client.post("/api/v1/search/inspect", json={"query": "warranty claims", "top_k": 5})
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "warranty claims"
    assert data["raw_matches"][0]["similarity_score"] == 0.88
    assert "=== SYSTEM PROMPT ===" in data["formatted_prompt"]


def test_e2e_executive_pdf_report_export_flow(e2e_admin_user):
    """E2E Test: Admin generates support report and exports executive PDF binary stream."""
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: e2e_admin_user
    app.dependency_overrides[require_admin] = lambda: e2e_admin_user

    mock_report_svc = AsyncMock()
    mock_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    mock_report_svc.export_report_pdf.return_value = mock_pdf_bytes
    app.dependency_overrides[get_report_service] = lambda: mock_report_svc

    res = client.get("/api/v1/reports/rep_999/export/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-1.4")
