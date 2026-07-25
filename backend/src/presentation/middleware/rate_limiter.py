import time
from collections import defaultdict
from typing import Dict, List
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window Rate Limiting Middleware."""

    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_history: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Exempt health check endpoints from rate limiting
        if request.url.path.startswith("/health") or request.url.path == "/":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean expired timestamps outside current window
        cutoff = now - self.window_seconds
        self.request_history[client_ip] = [
            t for t in self.request_history[client_ip] if t > cutoff
        ]

        if len(self.request_history[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        self.request_history[client_ip].append(now)
        return await call_next(request)
