from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.app import app
from backend.src.domain.entities.user import User
from backend.src.presentation.api.v1.chat_router import get_chat_service
from backend.src.presentation.api.v1.dependencies import get_current_active_user


@pytest.fixture
def mock_active_user():
    return User(
        id="usr_chat_123",
        email="chat_user@example.com",
        hashed_password="hashed_password_sample",
        full_name="Chat User",
        is_active=True,
    )


def test_send_chat_message_unauthenticated():
    client = TestClient(app)
    response = client.post("/api/v1/chat/message", data={"query": "Hello"})
    assert response.status_code == 401


def test_send_chat_message_authenticated(mock_active_user):
    mock_service = AsyncMock()
    mock_msg = MagicMock()
    mock_msg.id = "msg_1"
    mock_msg.conversation_id = "conv_1"
    mock_msg.sender_type = "assistant"
    mock_msg.content = "Support answer from AI."
    mock_msg.sources = []
    mock_msg.created_at = "2026-07-25T12:00:00"

    mock_service.process_user_question.return_value = mock_msg

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/api/v1/chat/message", data={"query": "What are your support hours?"})

    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Support answer from AI."
    assert data["conversation_id"] == "conv_1"


def test_list_conversations_authenticated(mock_active_user):
    mock_service = AsyncMock()
    mock_conv = MagicMock()
    mock_conv.id = "conv_1"
    mock_conv.user_id = mock_active_user.id
    mock_conv.title = "Support Chat"
    mock_conv.created_at = "2026-07-25T12:00:00"
    mock_conv.updated_at = "2026-07-25T12:00:00"

    mock_service.list_user_conversations.return_value = [mock_conv]

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    client = TestClient(app)
    response = client.get("/api/v1/chat/conversations")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == "conv_1"


def test_stream_chat_message_sse(mock_active_user):
    mock_service = MagicMock()
    mock_llm = MagicMock()
    mock_llm.stream.return_value = ["Hello ", "streaming ", "world!"]
    mock_service.llm_service = mock_llm

    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/api/v1/chat/stream", json={"query": "Hello stream"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    body = response.text
    assert "data: {\"type\": \"start\"" in body
    assert "Hello " in body
    assert "streaming " in body
    assert "data: {\"type\": \"done\"" in body

