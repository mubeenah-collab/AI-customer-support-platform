from backend.src.config.settings import Settings


def test_settings_default_values():
    settings = Settings()
    assert settings.APP_NAME == "AI Customer Support Platform"
    assert settings.APP_ENV == "development"
    assert settings.PORT == 8000
    assert settings.sync_database_url is not None
    assert settings.async_database_url is not None


def test_custom_database_url_property():
    settings = Settings(DATABASE_URL="postgresql://user:pass@localhost:5432/mydb")
    assert settings.sync_database_url == "postgresql://user:pass@localhost:5432/mydb"
    assert settings.async_database_url == "postgresql+asyncpg://user:pass@localhost:5432/mydb"


def test_production_settings_validation_rejects_default_secret():
    import pytest
    with pytest.raises(ValueError) as exc_info:
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="development-secret-key-change-in-production-32-bytes-min",
            GOOGLE_API_KEY="test_key",
        )
    assert "JWT_SECRET_KEY is using a default development key" in str(exc_info.value)


def test_production_settings_validation_requires_api_key():
    import pytest
    with pytest.raises(ValueError) as exc_info:
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="super-secure-production-secret-key-32bytes!",
            GOOGLE_API_KEY="",
            GEMINI_API_KEY="",
        )
    assert "GOOGLE_API_KEY / GEMINI_API_KEY is not set" in str(exc_info.value)


def test_production_settings_valid_config():
    s = Settings(
        APP_ENV="production",
        JWT_SECRET_KEY="super-secure-production-secret-key-32bytes!",
        GOOGLE_API_KEY="valid_production_api_key",
    )
    assert s.APP_ENV == "production"
    assert s.GOOGLE_API_KEY == "valid_production_api_key"


def test_cors_origins_parsing():
    s = Settings(CORS_ORIGINS="http://localhost:3100, https://support.example.com")
    assert s.CORS_ORIGINS == ["http://localhost:3100", "https://support.example.com"]

