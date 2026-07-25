import asyncio
import logging
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.src.ai.rag.text_splitter import DocumentTextSplitter
from backend.src.config.settings import settings
from backend.src.domain.entities.chunk import Chunk
from backend.src.domain.entities.document import Document
from backend.src.infrastructure.storage.loaders.document_loader_factory import DocumentLoaderFactory

logger = logging.getLogger("document_worker")


async def process_document_background(
    document_id: str,
    base_dir: Path,
    session_factory: async_sessionmaker[AsyncSession],
) -> bool:
    """Background worker task processing uploaded document: loader -> clean -> chunk -> DB save."""
    async with session_factory() as session:
        # Fetch document
        stmt = select(Document).where(Document.id == document_id)
        result = await session.execute(stmt)
        doc = result.scalars().first()

        if not doc:
            logger.error(f"Document worker error: Document '{document_id}' not found.")
            return False

        try:
            # Update status to processing
            doc.status = "processing"
            await session.commit()

            # Resolve physical file path safely
            rel_path = Path(doc.file_path)
            if rel_path.is_absolute():
                full_file_path = rel_path
            elif rel_path.parts and rel_path.parts[0] == base_dir.name:
                full_file_path = (base_dir.parent / rel_path).resolve()
            else:
                full_file_path = (base_dir / rel_path).resolve()

            if not full_file_path.exists():
                raise FileNotFoundError(f"File not found on disk at '{full_file_path}'.")

            # Extract raw chunks via strategy factory
            extracted_chunks = DocumentLoaderFactory.load_document(full_file_path)

            text_splitter = DocumentTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunk_records: list[Chunk] = []
            chunk_index = 0

            for ext_chunk in extracted_chunks:
                split_chunks = text_splitter.split_text(
                    text=ext_chunk.content,
                    page_number=ext_chunk.page_number,
                    start_index=chunk_index,
                )

                for chunk_item in split_chunks:
                    new_chunk = Chunk(
                        document_id=doc.id,
                        chunk_index=chunk_item.chunk_index,
                        content=chunk_item.content,
                        token_count=chunk_item.token_count,
                        page_number=chunk_item.page_number,
                        extra_metadata=ext_chunk.metadata,
                    )
                    chunk_records.append(new_chunk)
                    chunk_index += 1

            # Save chunks to PostgreSQL database
            for c in chunk_records:
                session.add(c)

            doc.status = "completed"
            doc.chunk_count = len(chunk_records)
            await session.commit()

            # Attempt Vector DB Indexing (Gemini Embeddings -> ChromaDB)
            if chunk_records and (settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY):
                try:
                    from backend.src.ai.embeddings.gemini_embedding import GeminiEmbeddingService
                    from backend.src.ai.rag.base_vector_store import VectorChunk
                    from backend.src.ai.rag.chroma_vector_store import ChromaVectorStore
                    from backend.src.workers.embedding_worker import generate_chunk_embeddings

                    embed_service = GeminiEmbeddingService()
                    chroma_store = ChromaVectorStore()

                    chunk_tuples = [(c.id, c.content) for c in chunk_records]
                    id_vector_list = generate_chunk_embeddings(chunk_tuples, embedding_service=embed_service)

                    v_chunks = []
                    for c, (c_id, vector) in zip(chunk_records, id_vector_list):
                        v_chunks.append(
                            VectorChunk(
                                chunk_id=c.id,
                                content=c.content,
                                embedding=vector,
                                document_id=doc.id,
                                document_name=doc.filename,
                                chunk_index=c.chunk_index,
                                page_number=c.page_number,
                            )
                        )

                    chroma_store.add_chunks(v_chunks)
                    logger.info(f"Indexed {len(v_chunks)} chunks in ChromaDB for document '{document_id}'.")
                except Exception as embed_err:
                    logger.warning(f"Vector DB indexing skipped/failed for document '{document_id}': {str(embed_err)}")

            logger.info(f"Document worker success: Document '{document_id}' processed into {len(chunk_records)} chunks.")
            return True

        except Exception as e:
            await session.rollback()
            logger.exception(f"Document worker failed for document '{document_id}': {str(e)}")

            # Update document to failed state
            async with session_factory() as fail_session:
                stmt_fail = select(Document).where(Document.id == document_id)
                res_fail = await fail_session.execute(stmt_fail)
                failed_doc = res_fail.scalars().first()
                if failed_doc:
                    failed_doc.status = "failed"
                    failed_doc.error_message = str(e)
                    await fail_session.commit()
            return False


async def run_worker_daemon() -> None:
    """Continuous background worker daemon polling database for pending documents."""
    from backend.src.infrastructure.database.session import AsyncSessionFactory

    base_dir = Path("uploads").resolve()
    logger.info("Document worker daemon initialized. Polling database for pending documents...")

    while True:
        try:
            async with AsyncSessionFactory() as session:
                stmt = select(Document.id).where(Document.status == "pending")
                result = await session.execute(stmt)
                pending_ids = result.scalars().all()

                if pending_ids:
                    logger.info(f"Document worker found {len(pending_ids)} pending document(s). Processing...")
                    for doc_id in pending_ids:
                        await process_document_background(
                            document_id=doc_id,
                            base_dir=base_dir,
                            session_factory=AsyncSessionFactory,
                        )
        except Exception as poll_err:
            logger.error(f"Error in document worker polling loop: {str(poll_err)}")

        await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    try:
        asyncio.run(run_worker_daemon())
    except KeyboardInterrupt:
        logger.info("Document worker daemon stopped by user.")
