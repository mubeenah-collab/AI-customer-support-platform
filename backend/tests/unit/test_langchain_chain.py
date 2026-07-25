from unittest.mock import MagicMock, patch
import pytest
from backend.src.ai.llm.base_llm import LLMServiceError
from backend.src.ai.llm.gemini_llm import GeminiLLMService
from backend.src.ai.rag.base_vector_store import RetrievedChunk
from backend.src.ai.rag.rag_chain import RAGChain
from backend.src.ai.rag.rag_pipeline import RAGPipeline
from backend.src.presentation.schemas.ai_schemas import SummaryResponseSchema


def test_gemini_llm_missing_key():
    service = GeminiLLMService(api_key="")
    with pytest.raises(LLMServiceError):
        service.generate("Hello")


@patch("backend.src.ai.llm.gemini_llm.ChatGoogleGenerativeAI")
def test_gemini_llm_generate_mock(mock_chat_cls):
    mock_chat = MagicMock()
    mock_res = MagicMock()
    mock_res.content = "Gemini LLM answer text"
    mock_chat.invoke.return_value = mock_res
    mock_chat_cls.return_value = mock_chat

    service = GeminiLLMService(api_key="test_key")
    output = service.generate("Explain RAG pipeline")
    assert output == "Gemini LLM answer text"


@patch("backend.src.ai.llm.gemini_llm.ChatGoogleGenerativeAI")
def test_gemini_llm_stream_mock(mock_chat_cls):
    mock_chat = MagicMock()
    c1, c2 = MagicMock(), MagicMock()
    c1.content = "Hello "
    c2.content = "world!"
    mock_chat.stream.return_value = [c1, c2]
    mock_chat_cls.return_value = mock_chat

    service = GeminiLLMService(api_key="test_key")
    streamed = list(service.stream("Stream test"))
    assert streamed == ["Hello ", "world!"]


def test_rag_chain_execution():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="c1",
            content="Support team contact is support@company.com",
            document_id="doc1",
            document_name="Contact_Guide.pdf",
            page_number=1,
            relevance_score=0.95,
        )
    ]

    pipeline = RAGPipeline(mock_retriever)
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "The contact email is support@company.com based on Contact_Guide.pdf."

    chain = RAGChain(pipeline, mock_llm)
    response = chain.invoke("How do I contact support?")

    assert response.has_sufficient_context is True
    assert "support@company.com" in response.answer
    assert len(response.citations) == 1
    assert response.citations[0].document_name == "Contact_Guide.pdf"
