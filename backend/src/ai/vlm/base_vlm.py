from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class VisionServiceError(Exception):
    """Exception raised when Gemini Vision analysis fails."""

    def __init__(self, message: str = "Vision analysis failure"):
        self.message = message
        super().__init__(self.message)


@dataclass
class VisionAnalysisResult:
    description: str
    key_observations: List[str] = field(default_factory=list)
    diagram_type: Optional[str] = None  # screenshot, chart, graph, flowchart, diagram, product
    extracted_text: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IVisionService(ABC):
    """Abstract interface defining contract for Visual Language Model (VLM) image analysis."""

    @abstractmethod
    def analyze_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None,
        mime_type: str = "image/png",
    ) -> VisionAnalysisResult:
        """Analyze raw image bytes using Gemini Vision VLM."""
        pass

    @abstractmethod
    def analyze_image_path(
        self,
        image_path: Path,
        prompt: Optional[str] = None,
    ) -> VisionAnalysisResult:
        """Analyze an image file at a given physical path using Gemini Vision VLM."""
        pass
