import logging
from pathlib import Path
from typing import Optional

try:
    from crewai import Agent
except ImportError:
    class Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

from backend.src.ai.vlm.base_vlm import IVisionService, VisionAnalysisResult
from backend.src.ai.vlm.vlm_pipeline import VLMPipeline

logger = logging.getLogger("vision_agent")


class VisionAgent:
    """CrewAI Vision Agent responsible for inspecting customer images, screenshots, charts, and diagrams."""

    def __init__(self, vision_service: IVisionService):
        self.vlm_pipeline = VLMPipeline(vision_service)
        self.crew_agent = Agent(
            role="Technical Image and Diagram Vision Specialist",
            goal="Understand visual information, technical diagrams, flowcharts, charts, and error screenshots provided by customers",
            backstory="Expert in Visual Language Models (VLM) specializing in inspecting support screenshots, error codes, and technical diagrams.",
            verbose=False,
            allow_delegation=False,
        )

    def execute_vision_analysis(
        self,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[Path] = None,
        user_query: Optional[str] = None,
    ) -> Optional[VisionAnalysisResult]:
        """Execute visual understanding task using VLM pipeline."""
        if not image_bytes and not image_path:
            return None

        logger.info("VisionAgent executing visual analysis task...")
        return self.vlm_pipeline.process_image_context(
            image_bytes=image_bytes,
            image_path=image_path,
            user_query=user_query,
        )
