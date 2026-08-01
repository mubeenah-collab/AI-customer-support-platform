import math
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.src.ai.rag.base_vector_store import (
    IVectorStore,
    RetrievedChunk,
    VectorChunk,
    VectorStoreError,
)
from backend.src.config.settings import settings

logger = logging.getLogger("chroma_vector_store")

COLLECTION_NAME = "knowledge_base"


def calculate_safe_similarity(dist: Any) -> float:
    """Safely calculate relevance similarity score [0.0, 1.0] from vector distance, handling None, NaN, Inf, or negative values."""
    if dist is None:
        return 0.0
    try:
        dist_float = float(dist)
    except (ValueError, TypeError):
        return 0.0

    if math.isnan(dist_float) or math.isinf(dist_float):
        return 0.0

    if dist_float <= 0.0:
        return 1.0

    if dist_float <= 1.0:
        sim = 1.0 - dist_float
    else:
        sim = max(0.0, 1.0 - (dist_float / 2.0))

    return max(0.0, min(1.0, round(sim, 4)))


class ChromaVectorStore(IVectorStore):
    """Concrete implementation of IVectorStore using ChromaDB persistent or ephemeral client."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        client: Optional[chromadb.ClientAPI] = None,
    ):
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY

        if client is not None:
            self.client = client
        elif settings.CHROMA_USE_HTTP_CLIENT:
            try:
                self.client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
            except Exception as e:
                logger.error(f"ChromaDB HttpClient connection failed: {str(e)}")
                raise VectorStoreError(f"ChromaDB HTTP connection failure: {str(e)}") from e
        else:
            try:
                # Ensure local persist directory exists
                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
            except Exception as e:
                # ChromaDB Rust bindings can panic on stale/incompatible SQLite files (e.g. version mismatch).
                # Fall back to an ephemeral in-memory client so the service degrades gracefully rather than
                # crashing the process. A full rebuild of the persistent store can be triggered by deleting
                # the .chroma directory and re-uploading documents.
                logger.warning(
                    f"ChromaDB PersistentClient failed ({type(e).__name__}: {str(e)}). "
                    "Falling back to ephemeral in-memory client. "
                    "Delete the .chroma directory and re-index documents to restore persistence."
                )
                try:
                    self.client = chromadb.EphemeralClient(
                        settings=ChromaSettings(anonymized_telemetry=False),
                    )
                except Exception as fallback_err:
                    logger.error(f"ChromaDB EphemeralClient fallback also failed: {str(fallback_err)}")
                    raise VectorStoreError(f"ChromaDB initialization failure: {str(e)}") from e

        try:
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.error(f"Failed to get/create ChromaDB collection '{COLLECTION_NAME}': {str(e)}")
            raise VectorStoreError(f"ChromaDB collection error: {str(e)}") from e

    def add_chunks(self, chunks: List[VectorChunk]) -> List[str]:
        if not chunks:
            return []

        ids: List[str] = []
        embeddings: List[List[float]] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for c in chunks:
            ids.append(c.chunk_id)
            embeddings.append(c.embedding)
            documents.append(c.content)
            meta: Dict[str, Any] = {
                "document_id": c.document_id,
                "document_name": c.document_name,
                "chunk_index": c.chunk_index,
                "page_number": c.page_number if c.page_number is not None else 0,
            }
            if c.metadata:
                for k, v in c.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        meta[f"extra_{k}"] = v
            metadatas.append(meta)

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"Successfully added {len(ids)} chunk vectors to ChromaDB collection.")
            return ids
        except Exception as e:
            logger.error(f"ChromaDB add_chunks failed: {str(e)}")
            raise VectorStoreError(f"Failed to insert vectors into ChromaDB: {str(e)}") from e

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        if not query_embedding:
            return []

        where_clause = filter_metadata if filter_metadata else None

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error(f"ChromaDB similarity_search failed: {str(e)}")
            raise VectorStoreError(f"ChromaDB query failure: {str(e)}") from e

        retrieved: List[RetrievedChunk] = []
        if not results or "ids" not in results or not results["ids"] or not results["ids"][0]:
            return []

        ids_list = results["ids"][0]
        docs_list = results["documents"][0] if results.get("documents") else []
        metas_list = results["metadatas"][0] if results.get("metadatas") else []
        dists_list = results["distances"][0] if results.get("distances") else []

        for i in range(len(ids_list)):
            c_id = ids_list[i]
            c_doc = docs_list[i] if i < len(docs_list) else ""
            c_meta = metas_list[i] if i < len(metas_list) else {}
            dist = dists_list[i] if i < len(dists_list) else 1.0
            similarity = calculate_safe_similarity(dist)

            if similarity >= score_threshold:
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=c_id,
                        content=c_doc,
                        document_id=c_meta.get("document_id", ""),
                        document_name=c_meta.get("document_name", "Unknown Document"),
                        page_number=c_meta.get("page_number") if c_meta.get("page_number") != 0 else None,
                        relevance_score=similarity,
                        metadata=c_meta,
                    )
                )

        return retrieved

    def delete_by_document_id(self, document_id: str) -> bool:
        try:
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted vector chunks for document_id '{document_id}' from ChromaDB.")
            return True
        except Exception as e:
            logger.error(f"ChromaDB delete_by_document_id failed: {str(e)}")
            raise VectorStoreError(f"Failed to delete document vectors from ChromaDB: {str(e)}") from e
