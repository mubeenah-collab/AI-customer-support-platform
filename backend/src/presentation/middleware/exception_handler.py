import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.src.ai.embeddings.base_embedding import EmbeddingServiceError
from backend.src.ai.llm.base_llm import LLMServiceError
from backend.src.ai.rag.base_vector_store import VectorStoreError
from backend.src.domain.exceptions.auth_exceptions import (
    AuthException,
    ForbiddenError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.src.domain.exceptions.chat_exceptions import ConversationNotFoundError, MessageProcessingError
from backend.src.domain.exceptions.document_exceptions import DocumentException, DocumentNotFoundError
from backend.src.domain.exceptions.report_exceptions import ReportGenerationError, ReportNotFoundError

logger = logging.getLogger("exception_handler")


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application instance."""

    @app.exception_handler(UnauthorizedError)
    @app.exception_handler(InvalidCredentialsError)
    async def unauthorized_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def bad_request_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DocumentNotFoundError)
    @app.exception_handler(ConversationNotFoundError)
    @app.exception_handler(ReportNotFoundError)
    @app.exception_handler(UserNotFoundError)
    async def not_found_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(VectorStoreError)
    @app.exception_handler(EmbeddingServiceError)
    @app.exception_handler(LLMServiceError)
    @app.exception_handler(MessageProcessingError)
    @app.exception_handler(ReportGenerationError)
    async def internal_server_handler(request: Request, exc: Exception):
        logger.error(f"Internal domain error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
