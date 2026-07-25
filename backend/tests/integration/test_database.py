import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from backend.src.infrastructure.database.base import Base
from backend.src.domain.entities.user import User
from backend.src.domain.entities.document import Document
from backend.src.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from backend.src.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository

# In-memory SQLite for async integration testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session() -> AsyncSession:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_user_repository_crud(async_session: AsyncSession):
    repo = SQLAlchemyUserRepository(async_session)

    # Create User
    new_user = User(
        email="john.doe@example.com",
        hashed_password="secure_hash_password",
        full_name="John Doe",
        role="customer",
    )
    created_user = await repo.create(new_user)
    assert created_user.id is not None

    # Get by Email
    fetched_user = await repo.get_by_email("john.doe@example.com")
    assert fetched_user is not None
    assert fetched_user.full_name == "John Doe"

    # Get by ID
    fetched_by_id = await repo.get_by_id(created_user.id)
    assert fetched_by_id is not None
    assert fetched_by_id.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_document_repository_crud(async_session: AsyncSession):
    user_repo = SQLAlchemyUserRepository(async_session)
    doc_repo = SQLAlchemyDocumentRepository(async_session)

    user = User(
        email="admin@company.com",
        hashed_password="admin_password_hash",
        full_name="Admin User",
        role="admin",
    )
    user = await user_repo.create(user)

    doc = Document(
        title="Company Policy",
        filename="policy.pdf",
        file_path="uploads/raw/policy.pdf",
        file_type="pdf",
        file_size=2048,
        mime_type="application/pdf",
        user_id=user.id,
    )
    doc = await doc_repo.create(doc)
    assert doc.id is not None

    # Update status
    updated_doc = await doc_repo.update_status(doc.id, "processed")
    assert updated_doc is not None
    assert updated_doc.status == "processed"
