from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
import io

from backend.src.ai.vlm.base_vlm import VisionServiceError
from backend.src.ai.vlm.gemini_vision import GeminiVisionService
from backend.src.ai.vlm.vlm_pipeline import VLMPipeline


def create_dummy_png_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_gemini_vision_missing_key():
    service = GeminiVisionService(api_key="")
    dummy_bytes = create_dummy_png_bytes()
    with pytest.raises(VisionServiceError):
        service.analyze_image(dummy_bytes)


def test_gemini_vision_invalid_image_payload():
    service = GeminiVisionService(api_key="test_key")
    with pytest.raises(VisionServiceError) as exc_info:
        service.analyze_image(b"invalid corrupt bytes")
    assert "Invalid image binary payload" in str(exc_info.value)


@patch("backend.src.ai.vlm.gemini_vision.ChatGoogleGenerativeAI")
def test_gemini_vision_analyze_image_mock(mock_chat_cls):
    mock_chat = MagicMock()
    mock_res = MagicMock()
    mock_res.content = "Analysis: This is a system architecture diagram showing server components."
    mock_chat.invoke.return_value = mock_res
    mock_chat_cls.return_value = mock_chat

    service = GeminiVisionService(api_key="test_key")
    dummy_bytes = create_dummy_png_bytes()
    result = service.analyze_image(dummy_bytes, prompt="Analyze diagram")

    assert result.diagram_type == "flowchart" or result.diagram_type == "screenshot"
    assert "system architecture diagram" in result.description
    assert result.metadata["width"] == 100
    assert result.metadata["height"] == 100


def test_vlm_pipeline_optional_execution():
    pipeline = VLMPipeline()
    assert pipeline.process_image_context() is None

    mock_vision = MagicMock()
    mock_vision.analyze_image.side_effect = VisionServiceError("API Failure")
    pipeline_err = VLMPipeline(vision_service=mock_vision)
    # Should safely return None on vision error
    res = pipeline_err.process_image_context(image_bytes=b"dummy")
    assert res is None
