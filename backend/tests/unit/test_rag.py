from unittest.mock import MagicMock
from backend.src.ai.prompts.rag_prompt import rag_prompt_template
from backend.src.ai.rag.base_vector_store import RetrievedChunk
from backend.src.ai.rag.citation_formatter import format_citations, format_citations_text
from backend.src.ai.rag.context_builder import build_rag_context
from backend.src.ai.rag.rag_pipeline import RAGPipeline
from backend.src.ai.rag.retriever import KnowledgeBaseRetriever


def test_citation_formatting():
    chunks = [
        RetrievedChunk(
            chunk_id="c1",
            content="Support team operates 24/7.",
            document_id="doc100",
            document_name="Support_Policy.pdf",
            page_number=3,
            relevance_score=0.88,
        ),
    ]

    formatted = format_citations(chunks)
    assert len(formatted) == 1
    assert formatted[0]["document_name"] == "Support_Policy.pdf"
    assert formatted[0]["relevance_percentage"] == "88%"

    text_citations = format_citations_text(formatted)
    assert "Sources:" in text_citations
    assert "Support_Policy.pdf - Page 3 (Relevance: 88%)" in text_citations


def test_context_building():
    chunks = [
        RetrievedChunk(
            chunk_id="c1",
            content="Return window is 30 days.",
            document_id="doc101",
            document_name="Return_Policy.pdf",
            page_number=1,
            relevance_score=0.92,
        ),
    ]

    context = build_rag_context(chunks)
    assert "[Source #1: Return_Policy.pdf | Page: 1 | Doc ID: doc101]" in context
    assert "Return window is 30 days." in context

    empty_context = build_rag_context([])
    assert "NO RELEVANT KNOWLEDGE BASE DOCUMENTS FOUND" in empty_context


def test_retriever_and_rag_pipeline():
    mock_embed = MagicMock()
    mock_embed.embed_query.return_value = [0.1] * 3072

    mock_vstore = MagicMock()
    mock_vstore.similarity_search.return_value = [
        RetrievedChunk(
            chunk_id="c1",
            content="Standard warranty is 1 year.",
            document_id="doc102",
            document_name="Warranty.pdf",
            page_number=2,
            relevance_score=0.95,
        )
    ]

    retriever = KnowledgeBaseRetriever(mock_embed, mock_vstore)
    pipeline = RAGPipeline(retriever)

    result = pipeline.run_retrieval("What is the warranty period?")
    assert result.has_sufficient_context is True
    assert len(result.chunks) == 1
    assert len(result.citations) == 1
    assert "Warranty.pdf" in result.context


def test_rag_prompt_template_formatting():
    prompt_res = rag_prompt_template.format(
        context="Sample context info",
        chat_history="User: Hello",
        query="What are support hours?",
    )

    assert "RETRIEVED KNOWLEDGE CONTEXT:" in prompt_res
    assert "Sample context info" in prompt_res
    assert "What are support hours?" in prompt_res
