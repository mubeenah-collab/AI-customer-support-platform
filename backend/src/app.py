import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
