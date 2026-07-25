from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.src.config.settings import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """OWASP Recommended Security Headers Middleware with route-scoped CSP for OpenAPI documentation."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        path = request.url.path
        show_docs = settings.ENABLE_DOCS or (settings.APP_ENV and settings.APP_ENV.lower() != "production")

        if show_docs and path in ("/docs", "/redoc", "/openapi.json"):
            # Permit narrow external assets required by Swagger UI / ReDoc when docs are enabled
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
                "frame-ancestors 'none';"
            )
        else:
            # Strict production CSP for all API endpoints and when docs are disabled
            response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"

        return response
