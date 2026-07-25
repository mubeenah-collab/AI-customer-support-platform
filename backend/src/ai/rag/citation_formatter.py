from typing import Any, Dict, List
from backend.src.ai.rag.base_vector_store import RetrievedChunk


def format_citations(chunks: List[RetrievedChunk]) -> List[Dict[str, Any]]:
    """Format retrieved chunks into structured JSON-compatible citation dictionaries."""
    citations: List[Dict[str, Any]] = []

    for idx, chunk in enumerate(chunks, start=1):
        score_pct = f"{int(round(chunk.relevance_score * 100))}%"
        snippet = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content

        citation_entry = {
            "citation_index": idx,
            "document_id": chunk.document_id,
            "document_name": chunk.document_name,
            "page_number": chunk.page_number,
            "relevance_score": chunk.relevance_score,
            "relevance_percentage": score_pct,
            "snippet": snippet,
        }
        citations.append(citation_entry)

    return citations


def format_citations_text(citations: List[Dict[str, Any]]) -> str:
    """Format citation dictionaries into human-readable source citations section for display."""
    if not citations:
        return ""

    lines = ["\n\nSources:"]
    for c in citations:
        page_str = f" - Page {c['page_number']}" if c.get("page_number") else ""
        score_str = f" (Relevance: {c['relevance_percentage']})" if c.get("relevance_percentage") else ""
        lines.append(f"{c['citation_index']}. {c['document_name']}{page_str}{score_str}")

    return "\n".join(lines)
