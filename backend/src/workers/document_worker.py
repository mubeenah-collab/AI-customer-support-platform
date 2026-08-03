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
    """Background worker task processing uploaded document: loader -> clean -> chunk -> embeddings -> ChromaDB -> DB save -> READY."""
    logger.info(f"========== [START PROCESSING] Document ID: '{document_id}' ==========")
    doc = None

    # Retry loop in case HTTP session commit is in-flight
    for attempt in range(1, 4):
        async with session_factory() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalars().first()
            if doc:
                break
        logger.warning(f"[RETRY {attempt}/3] Document '{document_id}' not visible in DB yet. Waiting 0.5s...")
        await asyncio.sleep(0.5)

    if not doc:
        logger.error(f"[FAILURE] Document worker error: Document '{document_id}' not found after 3 retries.")
        return False

    async with session_factory() as session:
        # Fetch fresh doc attached to current session
        stmt = select(Document).where(Document.id == document_id)
        res = await session.execute(stmt)
        doc = res.scalars().first()

        try:
            # STEP 1: Mark status as PROCESSING
            logger.info(f"[STEP 1/7] [UPDATE DATABASE] Updating status to 'processing' for '{document_id}'...")
            doc.status = "processing"
            await session.commit()

            # STEP 2: Resolve file path on disk
            rel_path = Path(doc.file_path)
            if rel_path.is_absolute():
                full_file_path = rel_path
            elif rel_path.parts and rel_path.parts[0] == base_dir.name:
                full_file_path = (base_dir.parent / rel_path).resolve()
            else:
                full_file_path = (base_dir / rel_path).resolve()

            logger.info(f"[STEP 2/7] [SAVE/RESOLVE FILE] Physical file path: '{full_file_path}'")
            if not full_file_path.exists():
                raise FileNotFoundError(f"File not found on disk at '{full_file_path}'.")

            # STEP 3: Extract text from file using Loader Factory
            logger.info(f"[STEP 3/7] [EXTRACT TEXT] Extracting text content from '{doc.filename}'...")
            extracted_chunks = DocumentLoaderFactory.load_document(full_file_path)
            logger.info(f"[EXTRACT TEXT SUCCESS] Extracted {len(extracted_chunks)} section(s) from '{doc.filename}'.")

            # STEP 4: Chunk document text into tokens
            logger.info(f"[STEP 4/7] [CHUNK DOCUMENT] Chunking text content (chunk_size=1000, overlap=150)...")
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

            logger.info(f"[CHUNK DOCUMENT SUCCESS] Created {len(chunk_records)} text chunk(s). Saving chunks to DB...")

            # Save chunks to PostgreSQL / SQLite database
            for c in chunk_records:
                session.add(c)
            doc.chunk_count = len(chunk_records)
            await session.commit()

            # STEP 5 & 6: Generate Gemini Embeddings & Store in ChromaDB
            if chunk_records and (settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY):
                logger.info(f"[STEP 5/7] [GENERATE EMBEDDINGS] Requesting Gemini embedding vectors for {len(chunk_records)} chunk(s)...")
                from backend.src.ai.embeddings.gemini_embedding import GeminiEmbeddingService
                from backend.src.ai.rag.base_vector_store import VectorChunk
                from backend.src.ai.rag.chroma_vector_store import ChromaVectorStore
                from backend.src.workers.embedding_worker import generate_chunk_embeddings

                embed_service = GeminiEmbeddingService()
                chroma_store = ChromaVectorStore()

                chunk_tuples = [(c.id, c.content) for c in chunk_records]
                id_vector_list = generate_chunk_embeddings(chunk_tuples, embedding_service=embed_service)
                logger.info(f"[GENERATE EMBEDDINGS SUCCESS] Received {len(id_vector_list)} vector(s) from Gemini API.")

                logger.info(f"[STEP 6/7] [STORE VECTORS] Storing vector embeddings in ChromaDB Persistent Store...")
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
                logger.info(f"[STORE VECTORS SUCCESS] Stored {len(v_chunks)} chunk vectors in ChromaDB collection.")

            # STEP 7: Mark Document Status as READY / COMPLETED
            logger.info(f"[STEP 7/7] [MARK READY] Updating document '{doc.id}' status to 'ready' (completed)...")
            doc.status = "ready"
            doc.error_message = None
            await session.commit()

            logger.info(f"========== [SUCCESS] Document '{doc.filename}' ({document_id}) is READY with {len(chunk_records)} chunk(s) stored. ==========")
            return True

        except Exception as e:
            await session.rollback()
            import traceback
            err_trace = traceback.format_exc()
            logger.exception(f"[FAILURE] Document worker processing failed for '{document_id}':\n{err_trace}")

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
