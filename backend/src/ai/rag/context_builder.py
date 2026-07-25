from typing import List
from backend.src.ai.rag.base_vector_store import RetrievedChunk


def build_rag_context(chunks: List[RetrievedChunk]) -> str:
    """Build formatted context string from retrieved document chunks for LLM prompt inclusion."""
    if not chunks:
        return "NO RELEVANT KNOWLEDGE BASE DOCUMENTS FOUND."

    context_blocks: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        page_info = f" | Page: {chunk.page_number}" if chunk.page_number else ""
        header = f"[Source #{idx}: {chunk.document_name}{page_info} | Doc ID: {chunk.document_id}]"
        block = f"{header}\n{chunk.content}"
        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)
