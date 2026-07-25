from unittest.mock import MagicMock
from backend.src.ai.agents.research_agent import ResearchAgent
from backend.src.ai.agents.support_crew import SupportAgentCrew
from backend.src.ai.agents.synthesis_agent import SynthesisAgent
from backend.src.ai.agents.vision_agent import VisionAgent
from backend.src.ai.rag.base_vector_store import RetrievedChunk
from backend.src.ai.rag.rag_pipeline import RAGResult
from backend.src.ai.vlm.base_vlm import VisionAnalysisResult


def test_research_agent():
    mock_rag = MagicMock()
    mock_rag.run_retrieval.return_value = RAGResult(
        query="Refund query",
        context="30 day refund policy.",
        chunks=[
            RetrievedChunk(
                chunk_id="c1",
                content="30 day refund policy.",
                document_id="d1",
                document_name="Refund.pdf",
                page_number=1,
                relevance_score=0.9,
            )
        ],
        citations=[
            {
                "citation_index": 1,
                "document_id": "d1",
                "document_name": "Refund.pdf",
                "page_number": 1,
                "relevance_percentage": "90%",
                "snippet": "30 day refund policy.",
            }
        ],
        citations_text="Sources:\n1. Refund.pdf",
        has_sufficient_context=True,
    )

    agent = ResearchAgent(mock_rag)
    res = agent.execute_research("Refund query")
    assert res.has_sufficient_context is True
    assert len(res.chunks) == 1


def test_vision_agent():
    mock_vlm = MagicMock()
    mock_vlm.process_image_context.return_value = VisionAnalysisResult(
        description="Error 500 screenshot",
        diagram_type="error_screenshot",
    )

    agent = VisionAgent(vision_service=MagicMock())
    agent.vlm_pipeline = mock_vlm

    res = agent.execute_vision_analysis(image_bytes=b"png", user_query="Check error")
    assert res is not None
    assert res.diagram_type == "error_screenshot"


def test_synthesis_agent():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "The refund window is 30 days."

    rag_res = RAGResult(
        query="Refund query",
        context="30 day refund policy.",
        chunks=[],
        citations=[],
        citations_text="",
        has_sufficient_context=True,
    )

    agent = SynthesisAgent(mock_llm)
    res = agent.execute_synthesis("Refund query", rag_res)

    assert "refund window is 30 days" in res.answer
    assert res.has_sufficient_context is True


def test_support_agent_crew_sequential_flow():
    mock_rag = MagicMock()
    mock_rag.run_retrieval.return_value = RAGResult(
        query="Warranty query",
        context="1 year warranty.",
        chunks=[],
        citations=[],
        citations_text="",
        has_sufficient_context=True,
    )

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Product has a 1 year warranty."

    mock_vision = MagicMock()

    crew = SupportAgentCrew(
        rag_pipeline=mock_rag,
        llm_service=mock_llm,
        vision_service=mock_vision,
    )

    response = crew.process_customer_query("Warranty query")
    assert "1 year warranty" in response.answer
