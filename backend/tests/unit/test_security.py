import pytest
from backend.src.infrastructure.security.password import hash_password, verify_password
from backend.src.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_token


def test_password_hashing_and_verification():
    plain = "SuperSecretPassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_access_token_creation_and_decoding():
    data = {"sub": "user-uuid-1234", "email": "test@example.com", "role": "customer"}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload["sub"] == "user-uuid-1234"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"


def test_jwt_refresh_token_creation_and_decoding():
    data = {"sub": "user-uuid-1234"}
    token = create_refresh_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "user-uuid-1234"
    assert payload["type"] == "refresh"


def test_jwt_invalid_token():
    with pytest.raises(ValueError):
        decode_token("invalid.jwt.token")


def test_jwt_expired_token():
    from datetime import timedelta
    data = {"sub": "user-uuid-expired", "role": "customer"}
    expired_token = create_access_token(data, expires_delta=timedelta(seconds=-10))
    with pytest.raises(ValueError) as exc_info:
        decode_token(expired_token)
    assert "Invalid token" in str(exc_info.value)


@pytest.mark.asyncio
async def test_cross_user_document_authorization_boundary():
    from unittest.mock import AsyncMock
    from backend.src.domain.entities.user import User
    from backend.src.domain.entities.document import Document
    from backend.src.domain.exceptions.auth_exceptions import ForbiddenError
    from backend.src.application.services.document_service import DocumentService

    user_a = User(id="user-a-id", email="usera@example.com", hashed_password="hash", role="customer")
    user_b = User(id="user-b-id", email="userb@example.com", hashed_password="hash", role="customer")

    doc_b = Document(id="doc-b-id", title="Doc B", filename="doc_b.pdf", file_path="uploads/raw/doc_b.pdf", file_type="pdf", file_size=100, mime_type="application/pdf", user_id=user_b.id)

    mock_doc_repo = AsyncMock()
    mock_doc_repo.get_by_id.return_value = doc_b
    mock_storage = AsyncMock()

    service = DocumentService(mock_doc_repo, mock_storage)

    # User A tries to view User B's document -> ForbiddenError
    with pytest.raises(ForbiddenError):
        await service.get_document_by_id(user_a, "doc-b-id")

    # User A tries to delete User B's document -> ForbiddenError
    with pytest.raises(ForbiddenError):
        await service.delete_document(user_a, "doc-b-id")

