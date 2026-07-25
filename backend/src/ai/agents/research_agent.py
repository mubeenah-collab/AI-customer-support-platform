import logging
from typing import Any, Dict, List, Optional

try:
    from crewai import Agent
except ImportError:
    class Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

from backend.src.ai.rag.rag_pipeline import RAGPipeline, RAGResult

logger = logging.getLogger("research_agent")


class ResearchAgent:
    """CrewAI Research Agent responsible for analyzing customer queries and retrieving relevant knowledge."""

    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.crew_agent = Agent(
            role="Senior Knowledge Base Research Agent",
            goal="Analyze customer query and retrieve relevant organizational knowledge and evidence",
            backstory="Specialist in information retrieval and factual evidence extraction from vector stores and organizational documentation.",
            verbose=False,
            allow_delegation=False,
        )

    def execute_research(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> RAGResult:
        """Execute research task: retrieve knowledge chunks and format context."""
        logger.info(f"ResearchAgent executing retrieval for query: '{query[:40]}...'")
        return self.rag_pipeline.run_retrieval(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            filter_metadata=filter_metadata,
        )
