import logging
from pathlib import Path
from typing import Optional
from backend.src.ai.vlm.base_vlm import IVisionService, VisionAnalysisResult, VisionServiceError
from backend.src.ai.vlm.gemini_vision import GeminiVisionService

logger = logging.getLogger("vlm_pipeline")


class VLMPipeline:
    """Optional VLM pipeline module analyzing uploaded image context for multimodal queries."""

    def __init__(self, vision_service: Optional[IVisionService] = None):
        self.vision_service = vision_service or GeminiVisionService()

    def process_image_context(
        self,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[Path] = None,
        user_query: Optional[str] = None,
    ) -> Optional[VisionAnalysisResult]:
        """Process image inputs and return visual understanding context."""
        if not image_bytes and not image_path:
            return None

        try:
            if image_bytes:
                return self.vision_service.analyze_image(
                    image_bytes=image_bytes,
                    prompt=user_query,
                )
            elif image_path:
                return self.vision_service.analyze_image_path(
                    image_path=image_path,
                    prompt=user_query,
                )
        except VisionServiceError as e:
            logger.error(f"VLM Pipeline error during image analysis: {e.message}")
            return None

        return None
