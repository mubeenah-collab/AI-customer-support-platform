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
