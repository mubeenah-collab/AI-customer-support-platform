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


@pytest.fixture
def customer_user():
    return User(
        id="cust_ticket_123",
        email="cust_ticket@example.com",
        hashed_password="hashed_pwd",
        full_name="Ticket Customer",
        role="customer",
        is_active=True,
    )


@pytest.fixture
def admin_user():
    return User(
        id="admin_ticket_123",
        email="admin_ticket@example.com",
        hashed_password="hashed_pwd",
        full_name="Ticket Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
    )


def test_unauthenticated_ticket_request_returns_401():
    client = TestClient(app)
    app.dependency_overrides.clear()
    res = client.get("/api/v1/tickets")
    assert res.status_code == 401


def test_customer_create_ticket_success(customer_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    mock_svc = AsyncMock()
    mock_ticket = MagicMock()
    mock_ticket.id = "tick_1"
    mock_ticket.user_id = customer_user.id
    mock_ticket.subject = "Billing Inquiry"
    mock_ticket.description = "Need invoice clarification."
    mock_ticket.status = "open"
    mock_ticket.priority = "high"
    mock_ticket.category = "billing"
    mock_ticket.created_at = "2026-07-26T12:00:00"
    mock_ticket.updated_at = "2026-07-26T12:00:00"

    mock_svc.create_ticket.return_value = mock_ticket
    app.dependency_overrides[get_ticket_service] = lambda: mock_svc

    res = client.post(
        "/api/v1/tickets",
        json={"subject": "Billing Inquiry", "description": "Need invoice clarification.", "priority": "high", "category": "billing"},
    )
    assert res.status_code == 201
    assert res.json()["id"] == "tick_1"
    assert res.json()["status"] == "open"


def test_admin_update_ticket_status_allowed(admin_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user

    mock_svc = AsyncMock()
    mock_ticket = MagicMock()
    mock_ticket.id = "tick_1"
    mock_ticket.user_id = "cust_ticket_123"
    mock_ticket.subject = "Billing Inquiry"
    mock_ticket.description = "Need invoice clarification."
    mock_ticket.status = "in_progress"
    mock_ticket.priority = "high"
    mock_ticket.category = "billing"
    mock_ticket.created_at = "2026-07-26T12:00:00"
    mock_ticket.updated_at = "2026-07-26T12:05:00"

    mock_svc.update_ticket.return_value = mock_ticket
    app.dependency_overrides[get_ticket_service] = lambda: mock_svc

    res = client.patch(
        "/api/v1/tickets/tick_1",
        json={"status": "in_progress"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_customer_updating_ticket_status_returns_403(customer_user):
    client = TestClient(app)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_active_user] = lambda: customer_user

    res = client.patch(
        "/api/v1/tickets/tick_1",
        json={"status": "resolved"},
    )
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]
