import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image
import io

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.src.ai.gemini_retry import call_with_retry
from backend.src.ai.prompts.vision_prompt import vision_prompt_template
from backend.src.ai.vlm.base_vlm import IVisionService, VisionAnalysisResult, VisionServiceError
from backend.src.config.settings import settings

logger = logging.getLogger("gemini_vision")


class GeminiVisionService(IVisionService):
    """Concrete implementation of IVisionService using Gemini Vision (gemini-1.5-flash)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = settings.GOOGLE_API_KEY if api_key is None else api_key
        self.model_name = model_name or settings.GEMINI_VISION_MODEL
        self._vlm_client: Optional[ChatGoogleGenerativeAI] = None

        if self.api_key:
            try:
                self._vlm_client = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.1,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ChatGoogleGenerativeAI vision client: {str(e)}")

    def _get_client(self) -> ChatGoogleGenerativeAI:
        if not self._vlm_client:
            if not self.api_key:
                raise VisionServiceError("Google API Key is missing. Set GOOGLE_API_KEY environment variable.")
            try:
                self._vlm_client = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.1,
                )
            except Exception as e:
                raise VisionServiceError(f"Failed to initialize ChatGoogleGenerativeAI vision client: {str(e)}") from e
        return self._vlm_client

    def analyze_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None,
        mime_type: str = "image/png",
    ) -> VisionAnalysisResult:
        if not image_bytes:
            raise VisionServiceError("Image content bytes cannot be empty.")

        # Validate image format using PIL
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                width, height = img.size
                img_format = img.format or "PNG"
        except Exception as e:
            raise VisionServiceError(f"Invalid image binary payload: {str(e)}") from e

        user_prompt_text = prompt or "Describe this support image in detail and extract all visible text, diagrams, or errors."
        prompt_content = vision_prompt_template.format(user_prompt=user_prompt_text)

        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64_data}"

        multimodal_message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_content},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]
        )

        client = self._get_client()
        try:
            response = call_with_retry(client.invoke, [multimodal_message])
            if not response or not response.content:
                raise VisionServiceError("Gemini Vision returned an empty response.")

            description_text = str(response.content)

            # Classify diagram type heuristic
            diag_type = "screenshot"
            desc_lower = description_text.lower()
            if "chart" in desc_lower or "graph" in desc_lower:
                diag_type = "chart"
            elif "flowchart" in desc_lower or "diagram" in desc_lower:
                diag_type = "flowchart"
            elif "error" in desc_lower or "exception" in desc_lower:
                diag_type = "error_screenshot"

            return VisionAnalysisResult(
                description=description_text,
                key_observations=[line.strip("- ") for line in description_text.splitlines() if line.strip().startswith("-")],
                diagram_type=diag_type,
                extracted_text=description_text,
                confidence=0.95,
                metadata={"width": width, "height": height, "format": img_format, "mime_type": mime_type},
            )
        except VisionServiceError:
            raise
        except Exception as e:
            logger.error("Gemini Vision API failure: %s", type(e).__name__)
            raise VisionServiceError(f"Gemini Vision error: {type(e).__name__}") from e

    def analyze_image_path(
        self,
        image_path: Path,
        prompt: Optional[str] = None,
    ) -> VisionAnalysisResult:
        if not image_path.exists():
            raise VisionServiceError(f"Image file does not exist at path '{image_path}'.")

        ext = image_path.suffix.lower()
        mime_type = "image/png"
        if ext in (".jpg", ".jpeg"):
            mime_type = "image/jpeg"
        elif ext == ".webp":
            mime_type = "image/webp"

        with open(image_path, "rb") as f:
            content = f.read()

        return self.analyze_image(image_bytes=content, prompt=prompt, mime_type=mime_type)
