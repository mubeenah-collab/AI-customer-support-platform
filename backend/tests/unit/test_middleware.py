from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from backend.src.app import app
from backend.src.domain.exceptions.auth_exceptions import UnauthorizedError
from backend.src.domain.exceptions.document_exceptions import DocumentNotFoundError
from backend.src.presentation.middleware.exception_handler import register_exception_handlers
from backend.src.presentation.middleware.rate_limiter import RateLimiterMiddleware
from backend.src.presentation.middleware.security_headers import SecurityHeadersMiddleware


def test_security_headers_middleware():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert response.headers.get("Content-Security-Policy") == "default-src 'self'; frame-ancestors 'none';"


def test_csp_docs_route_when_enabled():
    from backend.src.config.settings import settings
    original_docs = settings.ENABLE_DOCS
    try:
        settings.ENABLE_DOCS = True
        client = TestClient(app)
        res = client.get("/docs")
        assert res.status_code == 200
        csp = res.headers.get("Content-Security-Policy", "")
        assert "https://cdn.jsdelivr.net" in csp
        assert "https://fastapi.tiangolo.com" in csp
        assert "'unsafe-eval'" not in csp
        assert "script-src *" not in csp
    finally:
        settings.ENABLE_DOCS = original_docs


def test_strict_csp_on_api_endpoints():
    client = TestClient(app)
    res = client.get("/health")
    csp = res.headers.get("Content-Security-Policy", "")
    assert csp == "default-src 'self'; frame-ancestors 'none';"
    assert "https://cdn.jsdelivr.net" not in csp



def test_rate_limiter_middleware_throttling():
    test_app = FastAPI()
    test_app.add_middleware(RateLimiterMiddleware, max_requests=2, window_seconds=60)

    @test_app.get("/test-endpoint")
    def sample_route():
        return {"status": "ok"}

    client = TestClient(test_app)

    res1 = client.get("/test-endpoint")
    assert res1.status_code == 200

    res2 = client.get("/test-endpoint")
    assert res2.status_code == 200

    res3 = client.get("/test-endpoint")
    assert res3.status_code == 429
    assert "Rate limit exceeded" in res3.json()["detail"]


def test_global_exception_handlers():
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/raise-unauthorized")
    def raise_unauthorized():
        raise UnauthorizedError("Token is invalid")

    @test_app.get("/raise-not-found")
    def raise_not_found():
        raise DocumentNotFoundError("doc_abc")

    client = TestClient(test_app)

    res_unauth = client.get("/raise-unauthorized")
    assert res_unauth.status_code == 401
    assert "Token is invalid" in res_unauth.json()["detail"]

    res_not_found = client.get("/raise-not-found")
    assert res_not_found.status_code == 404
    assert "doc_abc" in res_not_found.json()["detail"]
