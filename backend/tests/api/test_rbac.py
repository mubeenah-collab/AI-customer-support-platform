import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
)
from backend.src.presentation.api.v1.document_router import get_document_service
from backend.src.presentation.schemas.document_schemas import DocumentListResponse


@pytest.fixture
def customer_user():
    return User(
        id="cust_123",
        email="customer@example.com",
        hashed_password="hashed_pwd",
        full_name="Regular Customer",
        role="customer",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def admin_user():
    return User(
        id="admin_123",
        email="admin@example.com",
        hashed_password="hashed_pwd",
        full_name="System Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )


def test_unauthenticated_request_returns_401():
    client = TestClient(app)
    app.dependency_overrides.clear()
    res = client.get("/api/v1/documents")
    assert res.status_code == 401


def test_customer_accessing_admin_documents_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.get("/api/v1/documents")
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_customer_accessing_admin_search_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.get("/api/v1/search?query=test")
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_customer_accessing_admin_reports_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.get("/api/v1/reports")
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_customer_accessing_admin_users_list_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.get("/api/v1/users")
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_admin_accessing_admin_documents_allowed(admin_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user

    mock_doc_svc = AsyncMock()
    mock_doc_svc.list_user_documents.return_value = DocumentListResponse(documents=[], total=0)
    app.dependency_overrides[get_document_service] = lambda: mock_doc_svc

    res = client.get("/api/v1/documents")
    assert res.status_code == 200


def test_customer_accessing_own_profile_allowed(customer_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.get("/api/v1/users/me")
    assert res.status_code == 200
    assert res.json()["email"] == "customer@example.com"
