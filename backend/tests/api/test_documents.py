import io
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.app import app
from backend.src.infrastructure.database.base import Base
from backend.src.infrastructure.database.session import get_async_db
from backend.src.presentation.api.v1.document_router import get_session_factory

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
    engine = async_test_session.bind
    test_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        yield async_test_session

    def override_get_factory():
        return test_factory

    app.dependency_overrides[get_async_db] = override_get_db
    app.dependency_overrides[get_session_factory] = override_get_factory
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_document_upload_list_delete_flow(async_client: AsyncClient):
    # 1. Register & Login User
    register_payload = {
        "email": "docuser@example.com",
        "password": "Password123!",
        "full_name": "Doc User",
        "role": "admin",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_res = await async_client.post("/api/v1/auth/login", json={"email": "docuser@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload PDF Document
    file_content = b"%PDF-1.4 sample pdf content for testing document upload"
    files = {"file": ("manual.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"title": "Sample Knowledge Base"}

    upload_res = await async_client.post("/api/v1/documents/upload", headers=headers, files=files, data=data)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert "document" in upload_data
    doc_id = upload_data["document"]["id"]
    assert upload_data["document"]["title"] == "Sample Knowledge Base"
    assert upload_data["document"]["file_type"] == "pdf"

    # 3. List Documents
    list_res = await async_client.get("/api/v1/documents", headers=headers)
    assert list_res.status_code == 200
    docs_list = list_res.json()["documents"]
    assert len(docs_list) == 1
    assert docs_list[0]["id"] == doc_id

    # 4. Get Document by ID
    get_res = await async_client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == doc_id

    # 4b. Download Document File
    dl_res = await async_client.get(f"/api/v1/documents/{doc_id}/download", headers=headers)
    assert dl_res.status_code == 200
    assert file_content in dl_res.content

    # 5. Delete Document
    del_res = await async_client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 6. Verify Deletion
    list_res2 = await async_client.get("/api/v1/documents", headers=headers)
    assert len(list_res2.json()["documents"]) == 0


@pytest.mark.asyncio
async def test_document_upload_invalid_type_rejected(async_client: AsyncClient):
    await async_client.post("/api/v1/auth/register", json={"email": "admin_uploader@example.com", "password": "Password123!", "role": "admin"})
    login_res = await async_client.post("/api/v1/auth/login", json={"email": "admin_uploader@example.com", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    files = {"file": ("malicious.exe", io.BytesIO(b"binary content"), "application/x-msdownload")}
    upload_res = await async_client.post("/api/v1/documents/upload", headers=headers, files=files)
    assert upload_res.status_code == 400
    assert "Invalid file type" in upload_res.json()["detail"]
