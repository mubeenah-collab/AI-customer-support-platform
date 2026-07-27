import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
)
from backend.src.presentation.api.v1.report_router import get_report_service


@pytest.fixture
def admin_user():
    return User(
        id="admin_pdf_123",
        email="admin_pdf@example.com",
        hashed_password="hashed_pwd",
        full_name="PDF Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )


@pytest.fixture
def customer_user():
    return User(
        id="customer_pdf_123",
        email="customer_pdf@example.com",
        hashed_password="hashed_pwd",
        full_name="PDF Customer",
        role="customer",
        is_active=True,
    )


def test_export_report_pdf_unauthenticated_returns_401():
    client = TestClient(app)
    app.dependency_overrides.clear()
    res = client.get("/api/v1/reports/rep_123/export/pdf")
    assert res.status_code == 401


def test_export_report_pdf_customer_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.get("/api/v1/reports/rep_123/export/pdf")
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_export_report_pdf_admin_success(admin_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user

    mock_svc = AsyncMock()
    mock_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    mock_svc.export_report_pdf.return_value = mock_pdf_bytes
    app.dependency_overrides[get_report_service] = lambda: mock_svc

    res = client.get("/api/v1/reports/rep_123/export/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-1.4")
