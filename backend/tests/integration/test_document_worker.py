from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.domain.entities.chunk import Chunk
from backend.src.domain.entities.document import Document
from backend.src.domain.entities.user import User
from backend.src.infrastructure.database.base import Base
from backend.src.workers.document_worker import process_document_background

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_test_setup(tmp_path: Path):
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    yield session_factory, tmp_path
    await engine.dispose()


@pytest.mark.asyncio
async def test_process_document_background_success(async_test_setup):
    session_factory, tmp_path = async_test_setup

    # Prepare directories and file inside uploads/raw structure
    base_uploads_dir = tmp_path / "uploads"
    raw_dir = base_uploads_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    sample_file = raw_dir / "uuid_kb.txt"
    sample_file.write_text("Header line.\n\nSection 1 details.\nSection 2 details.", encoding="utf-8")

    async with session_factory() as session:
        user = User(email="workeruser@example.com", hashed_password="hash", full_name="Worker User")
        session.add(user)
        await session.flush()

        relative_path = f"uploads/raw/{sample_file.name}"
        doc = Document(
            title="KB Doc",
            filename="kb.txt",
            file_path=relative_path,
            file_type="txt",
            file_size=100,
            mime_type="text/plain",
            user_id=user.id,
        )
        session.add(doc)
        await session.commit()
        doc_id = doc.id

    # Run Worker
    success = await process_document_background(
        document_id=doc_id,
        base_dir=base_uploads_dir,
        session_factory=session_factory,
    )
    assert success is True

    # Verify Database Updates
    async with session_factory() as session:
        stmt_doc = select(Document).where(Document.id == doc_id)
        res_doc = await session.execute(stmt_doc)
        updated_doc = res_doc.scalars().first()

        assert updated_doc.status in ("ready", "completed")
        assert updated_doc.chunk_count > 0

        stmt_chunks = select(Chunk).where(Chunk.document_id == doc_id)
        res_chunks = await session.execute(stmt_chunks)
        chunks = list(res_chunks.scalars().all())

        assert len(chunks) == updated_doc.chunk_count
        assert "Header line" in chunks[0].content
