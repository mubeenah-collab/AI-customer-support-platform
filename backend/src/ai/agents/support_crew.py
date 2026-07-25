import logging
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from crewai import Crew, Process, Task
except ImportError:
    class Crew:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    class Process:
        sequential = "sequential"
    class Task:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

from backend.src.ai.agents.research_agent import ResearchAgent
from backend.src.ai.agents.synthesis_agent import SynthesisAgent
from backend.src.ai.agents.vision_agent import VisionAgent
from backend.src.ai.llm.base_llm import ILLMService
from backend.src.ai.rag.rag_pipeline import RAGPipeline, RAGResult
from backend.src.ai.vlm.base_vlm import IVisionService
from backend.src.presentation.schemas.ai_schemas import ChatResponseSchema

logger = logging.getLogger("support_crew")


class SupportAgentCrew:
    """Orchestrator class managing the three specialized CrewAI agents (Research, Vision, Synthesis)."""

    def __init__(
        self,
        rag_pipeline: RAGPipeline,
        llm_service: ILLMService,
        vision_service: IVisionService,
    ):
        self.research_agent = ResearchAgent(rag_pipeline)
        self.vision_agent = VisionAgent(vision_service)
        self.synthesis_agent = SynthesisAgent(llm_service)

    def process_customer_query(
        self,
        query: str,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[Path] = None,
        chat_history: str = "None",
    ) -> ChatResponseSchema:
        """Run the 3-agent Crew workflow sequentially."""
        logger.info(f"SupportAgentCrew processing query: '{query[:30]}...'")

        # Step 1: Research Agent
        rag_result: RAGResult = self.research_agent.execute_research(query)

        # Step 2: Vision Agent (Conditional)
        visual_context: Optional[Dict[str, Any]] = None
        vlm_res = self.vision_agent.execute_vision_analysis(
            image_bytes=image_bytes,
            image_path=image_path,
            user_query=query,
        )
        if vlm_res:
            visual_context = {
                "description": vlm_res.description,
                "diagram_type": vlm_res.diagram_type,
            }

        # Step 3: Synthesis Agent
        response = self.synthesis_agent.execute_synthesis(
            query=query,
            rag_result=rag_result,
            visual_context=visual_context,
            chat_history=chat_history,
        )

        return response
