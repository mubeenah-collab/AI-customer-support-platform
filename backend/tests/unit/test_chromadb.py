import chromadb
from backend.src.ai.rag.base_vector_store import VectorChunk
from backend.src.ai.rag.chroma_vector_store import ChromaVectorStore


def test_chroma_vector_store_add_search_delete():
    # Use EphemeralClient for isolated in-memory test
    ephemeral_client = chromadb.EphemeralClient()
    store = ChromaVectorStore(client=ephemeral_client)

    # 1. Add Chunks with orthogonal vectors
    dummy_vec_1 = [1.0 if i < 1536 else 0.0 for i in range(3072)]
    dummy_vec_2 = [0.0 if i < 1536 else 1.0 for i in range(3072)]

    chunks = [
        VectorChunk(
            chunk_id="c1",
            content="Customer refund policy is valid for 30 days.",
            embedding=dummy_vec_1,
            document_id="doc_1",
            document_name="Refund_Policy.pdf",
            chunk_index=0,
            page_number=1,
        ),
        VectorChunk(
            chunk_id="c2",
            content="Technical hardware specifications and maintenance guide.",
            embedding=dummy_vec_2,
            document_id="doc_2",
            document_name="Hardware_Guide.pdf",
            chunk_index=0,
            page_number=5,
        ),
    ]

    added_ids = store.add_chunks(chunks)
    assert len(added_ids) == 2
    assert "c1" in added_ids

    # 2. Similarity Search matching dummy_vec_1
    retrieved = store.similarity_search(query_embedding=dummy_vec_1, top_k=2, score_threshold=0.0)
    assert len(retrieved) > 0
    top_match = retrieved[0]
    assert top_match.document_id == "doc_1"
    assert "refund policy" in top_match.content.lower()

    # 3. Threshold Filtering
    high_threshold_results = store.similarity_search(query_embedding=dummy_vec_1, top_k=2, score_threshold=0.99)
    assert len(high_threshold_results) <= 1

    # 4. Delete by Document ID
    deleted = store.delete_by_document_id("doc_1")
    assert deleted is True

    post_delete_res = store.similarity_search(query_embedding=dummy_vec_1, top_k=2, score_threshold=0.0)
    # Remaining result should only be doc_2
    for r in post_delete_res:
        assert r.document_id != "doc_1"
