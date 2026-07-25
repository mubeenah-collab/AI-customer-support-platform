from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.dependencies import get_current_active_user
from backend.src.presentation.api.v1.user_router import get_user_service


from datetime import datetime, timezone

@pytest.fixture
def mock_active_user():
    now = datetime.now(timezone.utc)
    return User(
        id="usr_profile_123",
        email="profile_user@example.com",
        hashed_password="hashed_password_sample",
        full_name="Alice User",
        role="customer",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def test_get_me_unauthenticated():
    client = TestClient(app)
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_me_authenticated(mock_active_user):
    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user

    client = TestClient(app)
    response = client.get("/api/v1/users/me")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile_user@example.com"
    assert data["full_name"] == "Alice User"


def test_update_me_authenticated(mock_active_user):
    mock_service = AsyncMock()
    updated_user = User(
        id=mock_active_user.id,
        email=mock_active_user.email,
        hashed_password="hashed_password_sample",
        full_name="Alice Smith",
        role="customer",
        is_active=True,
    )
    mock_service.update_profile.return_value = updated_user

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_user_service] = lambda: mock_service

    client = TestClient(app)
    response = client.put("/api/v1/users/me", json={"full_name": "Alice Smith"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Alice Smith"


def test_list_users_authenticated(mock_active_user):
    mock_service = AsyncMock()
    mock_service.list_users.return_value = [mock_active_user]

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_user_service] = lambda: mock_service

    client = TestClient(app)
    response = client.get("/api/v1/users")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "profile_user@example.com"
