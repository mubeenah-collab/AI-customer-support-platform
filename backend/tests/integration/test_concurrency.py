import asyncio
import time
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from backend.src.app import app
from backend.src.infrastructure.database.base import Base
from backend.src.infrastructure.database.session import get_async_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_async_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    await engine.dispose()


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

