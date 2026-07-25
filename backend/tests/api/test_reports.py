from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import get_current_active_user
from backend.src.presentation.api.v1.report_router import get_report_service


@pytest.fixture
def mock_active_user():
    return User(
        id="usr_report_123",
        email="report_user@example.com",
        hashed_password="hashed_password_sample",
        full_name="Report User",
        is_active=True,
    )


def test_document_summary_unauthenticated():
    client = TestClient(app)
    response = client.post("/api/v1/reports/document-summary", json={"document_id": "doc_1"})
    assert response.status_code == 401


def test_document_summary_authenticated(mock_active_user):
    mock_service = AsyncMock()
    mock_service.generate_document_summary.return_value = {
        "document_id": "doc_1",
        "document_name": "Manual.pdf",
        "summary": "This document outlines product manual instructions.",
        "key_points": ["Installation steps", "Maintenance schedule"],
        "title": "Summary: Manual.pdf",
    }

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_report_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/api/v1/reports/document-summary", json={"document_id": "doc_1"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["document_name"] == "Manual.pdf"
    assert len(data["key_points"]) == 2


def test_support_report_authenticated(mock_active_user):
    mock_service = AsyncMock()
    mock_report = MagicMock()
    mock_report.id = "rep_100"
    mock_report.user_id = mock_active_user.id
    mock_report.title = "Support Report: Billing Errors"
    mock_report.report_type = "support_analytics"
    mock_report.content = "Detailed analysis of customer billing inquiries..."
    mock_report.created_at = "2026-07-25T12:00:00"

    mock_service.generate_support_report.return_value = mock_report

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_report_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/api/v1/reports/support-report", json={"topic": "Billing Errors"})

    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "rep_100"
    assert "Billing Errors" in data["title"]
