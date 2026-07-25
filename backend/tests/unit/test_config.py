from backend.src.config.settings import Settings


def test_settings_default_values():
    settings = Settings()
    assert settings.APP_NAME == "AI Customer Support Platform"
    assert settings.APP_ENV == "development"
    assert settings.PORT == 8000
    assert "postgresql://" in settings.sync_database_url
    assert "postgresql+asyncpg://" in settings.async_database_url


def test_custom_database_url_property():
    settings = Settings(DATABASE_URL="postgresql://user:pass@localhost:5432/mydb")
    assert settings.sync_database_url == "postgresql://user:pass@localhost:5432/mydb"
    assert settings.async_database_url == "postgresql+asyncpg://user:pass@localhost:5432/mydb"
