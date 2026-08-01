import os
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Customer Support Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    ENABLE_DOCS: bool = True
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3100",
        "http://127.0.0.1:3100",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    ALLOWED_ORIGINS: Optional[Union[str, List[str]]] = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security & JWT
    SECRET_KEY: Optional[str] = None
    JWT_SECRET_KEY: str = "development-secret-key-change-in-production-32-bytes-min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "customer_support_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            elif "postgresql+asyncpg://" in url:
                url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
            return url
        try:
            import psycopg2
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        except ImportError:
            return "sqlite:///./app.db"

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        try:
            import asyncpg
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        except ImportError:
            return "sqlite+aiosqlite:///./app.db"

    # ChromaDB Vector Store
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIRECTORY: str = ".chroma"
    CHROMA_USE_HTTP_CLIENT: bool = False

    # Google Gemini AI
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_LLM_MODEL: str = "gemini-2.5-pro"
    GEMINI_VISION_MODEL: str = "gemini-2.5-pro"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # Storage
    UPLOAD_DIR: str = "uploads"
    UPLOAD_BASE_DIR: Optional[str] = None
    MAX_UPLOAD_SIZE_MB: int = 20

    def model_post_init(self, __context):
        # Handle env variable aliases
        if self.SECRET_KEY and (not self.JWT_SECRET_KEY or "development-secret-key" in self.JWT_SECRET_KEY):
            self.JWT_SECRET_KEY = self.SECRET_KEY
        if self.UPLOAD_BASE_DIR:
            self.UPLOAD_DIR = self.UPLOAD_BASE_DIR

        if self.ALLOWED_ORIGINS:
            if isinstance(self.ALLOWED_ORIGINS, str):
                origins = [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
            else:
                origins = list(self.ALLOWED_ORIGINS)
            for o in origins:
                if o not in self.CORS_ORIGINS:
                    self.CORS_ORIGINS.append(o)

        if not self.GOOGLE_API_KEY and self.GEMINI_API_KEY:
            self.GOOGLE_API_KEY = self.GEMINI_API_KEY
        elif not self.GEMINI_API_KEY and self.GOOGLE_API_KEY:
            self.GEMINI_API_KEY = self.GOOGLE_API_KEY

        if self.APP_ENV and self.APP_ENV.lower() == "production":
            insecure_secret_keywords = ["development-secret-key", "replace-this-with-a-secure-random-secret-key", "change-in-production"]
            if any(kw in self.JWT_SECRET_KEY for kw in insecure_secret_keywords):
                raise ValueError("Production environment detected but JWT_SECRET_KEY is using a default development key. Set a secure secret key in .env.")
            if not self.GOOGLE_API_KEY:
                raise ValueError("Production environment detected but GOOGLE_API_KEY / GEMINI_API_KEY is not set.")

    # RAG Configuration
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SCORE_THRESHOLD: float = 0.15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()

