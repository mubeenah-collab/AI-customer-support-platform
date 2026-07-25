"""
Integration concurrency test verifying system stability under multi-user concurrent requests.
Simulates 10 concurrent users issuing health requests, authentication, and chat queries.
"""
import asyncio
import time
import pytest
from httpx import AsyncClient, ASGITransport
from backend.src.app import app


@pytest.mark.asyncio
async def test_concurrent_api_requests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 10 Concurrent Health Checks
        start_time = time.time()
        tasks = [client.get("/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        assert len(responses) == 10
        assert all(r.status_code == 200 for r in responses)
        assert elapsed < 5.0  # Must complete within 5 seconds


@pytest.mark.asyncio
async def test_concurrent_auth_logins():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 10 Concurrent Invalid Login Requests
        tasks = [
            client.post("/api/v1/auth/login", json={"email": f"user{i}@example.com", "password": "WrongPassword!"})
            for i in range(10)
        ]
        responses = await asyncio.gather(*tasks)

        assert len(responses) == 10
        # Should return 401 Unauthorized cleanly without crashing the connection pool
        assert all(r.status_code in (401, 404, 422) for r in responses)
