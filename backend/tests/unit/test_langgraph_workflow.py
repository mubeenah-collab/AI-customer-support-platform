from unittest.mock import MagicMock
from backend.src.ai.orchestration.nodes import SupportGraphNodes
from backend.src.ai.orchestration.state import SupportState
from backend.src.ai.orchestration.support_graph import build_support_graph, should_run_vision
from backend.src.ai.rag.base_vector_store import RetrievedChunk
from backend.src.ai.rag.rag_pipeline import RAGPipeline


def test_should_run_vision_conditional_router():
    state_no_img: SupportState = {"query": "What is refund policy?"}
    assert should_run_vision(state_no_img) == "synthesize_response"

    state_with_img: SupportState = {"query": "Check screenshot", "image_bytes": b"fake_png"}
    assert should_run_vision(state_with_img) == "vision_analysis"


def test_support_graph_nodes_standalone():
    mock_rag = MagicMock()
    mock_rag.run_retrieval.return_value = MagicMock(
        context="Retrieved knowledge about returns",
        chunks=[
            RetrievedChunk(
                chunk_id="c1",
                content="Return window is 30 days",
                document_id="d1",
                document_name="Policy.pdf",
                page_number=1,
                relevance_score=0.9,
            )
        ],
        citations=[
            {
                "citation_index": 1,
                "document_id": "d1",
                "document_name": "Policy.pdf",
                "page_number": 1,
                "relevance_percentage": "90%",
                "snippet": "Return window is 30 days",
            }
        ],
        has_sufficient_context=True,
    )

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "The return window is 30 days."

    nodes = SupportGraphNodes(rag_pipeline=mock_rag, llm_service=mock_llm)
    state: SupportState = {"query": "What is the return window?"}

    res_analysis = nodes.query_analysis(state)
    assert res_analysis["intent"] == "general_support"

    res_retrieve = nodes.retrieve_context(state)
    assert res_retrieve["has_sufficient_context"] is True
    assert len(res_retrieve["citations"]) == 1

    state.update(res_retrieve)
    res_synth = nodes.synthesize_response(state)
    assert "return window is 30 days" in res_synth["draft_response"]


def test_compiled_support_graph_end_to_end():
    mock_rag = MagicMock()
    mock_rag.run_retrieval.return_value = MagicMock(
        context="Standard warranty duration is 1 year.",
        chunks=[],
        citations=[],
        has_sufficient_context=True,
    )

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Our standard product warranty lasts for 1 year."

    graph = build_support_graph(rag_pipeline=mock_rag, llm_service=mock_llm)

    initial_state: SupportState = {
        "user_id": "usr_100",
        "conversation_id": "conv_200",
        "query": "How long is the warranty?",
    }

    final_state = graph.invoke(initial_state)

    assert "final_response" in final_state
    assert "standard product warranty" in final_state["final_response"]
    assert final_state["confidence"] > 0.5
