import sys
import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(
    title="AI Customer Support Platform API",
    description="Enterprise-grade RAG + LangGraph + CrewAI + Gemini Customer Support Platform",
    version="1.0.0",
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # To be restricted in production config
    allow_credentials=True,
    allow_methods=["*"],
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
