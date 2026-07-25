import logging
from typing import Any, Dict, Optional
from langgraph.graph import END, START, StateGraph

from backend.src.ai.llm.base_llm import ILLMService
from backend.src.ai.orchestration.nodes import SupportGraphNodes
from backend.src.ai.orchestration.state import SupportState
from backend.src.ai.rag.rag_pipeline import RAGPipeline
from backend.src.ai.vlm.base_vlm import IVisionService

logger = logging.getLogger("support_graph")


def should_run_vision(state: SupportState) -> str:
    """Conditional edge router: Check if visual image analysis is required."""
    if state.get("image_bytes") or state.get("image_path"):
        return "vision_analysis"
    return "synthesize_response"


def build_support_graph(
    rag_pipeline: RAGPipeline,
    llm_service: ILLMService,
    vision_service: Optional[IVisionService] = None,
) -> StateGraph:
    """Build and compile the LangGraph stateful support workflow."""
    nodes = SupportGraphNodes(
        rag_pipeline=rag_pipeline,
        llm_service=llm_service,
        vision_service=vision_service,
    )

    # Initialize StateGraph with SupportState schema
    builder = StateGraph(SupportState)

    # Add Nodes
    builder.add_node("query_analysis", nodes.query_analysis)
    builder.add_node("retrieve_context", nodes.retrieve_context)
    builder.add_node("vision_analysis", nodes.vision_analysis)
    builder.add_node("synthesize_response", nodes.synthesize_response)
    builder.add_node("quality_check", nodes.quality_check)
    builder.add_node("finalize_response", nodes.finalize_response)

    # Wire Edges
    builder.add_edge(START, "query_analysis")
    builder.add_edge("query_analysis", "retrieve_context")

    # Conditional Routing for Vision Node
    builder.add_conditional_edges(
        "retrieve_context",
        should_run_vision,
        {
            "vision_analysis": "vision_analysis",
            "synthesize_response": "synthesize_response",
        },
    )

    builder.add_edge("vision_analysis", "synthesize_response")
    builder.add_edge("synthesize_response", "quality_check")
    builder.add_edge("quality_check", "finalize_response")
    builder.add_edge("finalize_response", END)

    # Compile Graph
    graph = builder.compile()
    logger.info("LangGraph Support Workflow state machine compiled successfully.")
    return graph
