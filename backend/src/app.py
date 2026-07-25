import sys
import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.presentation.api.v1.auth_router import auth_router
from backend.src.presentation.api.v1.chat_router import router as chat_router
from backend.src.presentation.api.v1.document_router import document_router
from backend.src.presentation.api.v1.health_router import router as health_router
from backend.src.presentation.api.v1.report_router import router as report_router
from backend.src.presentation.api.v1.search_router import router as search_router
from backend.src.presentation.api.v1.user_router import router as user_router
from backend.src.presentation.middleware.exception_handler import register_exception_handlers
from backend.src.presentation.middleware.rate_limiter import RateLimiterMiddleware
from backend.src.presentation.middleware.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger("app")

# Enforce Python 3.12 Target Compatibility
TARGET_PYTHON_MAJOR = 3
TARGET_PYTHON_MINOR = 12

if sys.version_info.major != TARGET_PYTHON_MAJOR or sys.version_info.minor != TARGET_PYTHON_MINOR:
    logger.warning(
        f"Python Version Mismatch: Platform target is Python {TARGET_PYTHON_MAJOR}.{TARGET_PYTHON_MINOR}, "
        f"but current runtime environment is Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}. "
        "Production deployments (Docker) MUST strictly run Python 3.12."
    )

from backend.src.config.settings import settings

show_docs = settings.ENABLE_DOCS or settings.APP_ENV.lower() != "production"

app = FastAPI(
    title="AI Customer Support Platform API",
    description="Enterprise-grade RAG + LangGraph + CrewAI + Gemini Customer Support Platform",
    version="1.0.0",
    docs_url="/docs" if show_docs else None,
    redoc_url="/redoc" if show_docs else None,
    openapi_url="/openapi.json" if show_docs else None,
)

# Register Global Exception Handlers
register_exception_handlers(app)

# Register API v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

# Register Custom Security & Rate Limiting Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware, max_requests=120, window_seconds=60)

from backend.src.config.settings import settings

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify system status."""
    return {
        "status": "healthy",
        "service": "AI Customer Support Platform API",
        "timestamp": time.time(),
        "version": "1.0.0",
    }
