import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from backend.src.app import app
from backend.src.infrastructure.database.base import Base
from backend.src.infrastructure.database.session import get_async_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_test_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(async_test_session):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_async_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_full_flow(async_client: AsyncClient):
    # 1. Register User
    register_payload = {
        "email": "user@example.com",
        "password": "Password123!",
        "full_name": "Jane Support",
        "role": "customer",
    }
    response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "user@example.com"
    assert user_data["full_name"] == "Jane Support"
    assert "id" in user_data

    # 2. Duplicate Registration Failure
    dup_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert dup_response.status_code == 400

    # 3. Login
    login_payload = {
        "email": "user@example.com",
        "password": "Password123!",
    }
    login_response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 4. Get Profile (/me)
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "user@example.com"

    # 5. Refresh Token
    refresh_response = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
