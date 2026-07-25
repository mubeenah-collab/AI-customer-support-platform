from unittest.mock import MagicMock, patch
from backend.src.ai.llm.conversation_context import ChatMessageItem, format_conversation_history
from backend.src.ai.llm.gemini_llm import GeminiLLMService
from backend.src.ai.prompts.compare_prompt import compare_prompt_template
from backend.src.ai.prompts.report_prompt import report_prompt_template
from backend.src.ai.prompts.summary_prompt import summary_prompt_template
from backend.src.presentation.schemas.ai_schemas import ComparisonResponseSchema, SummaryResponseSchema


def test_format_conversation_history_truncation():
    msgs = [
        ChatMessageItem(sender_type="user", content=f"Question {i}")
        for i in range(10)
    ]
    formatted = format_conversation_history(msgs, max_turns=4)

    assert "Question 6" in formatted
    assert "Question 9" in formatted
    assert "Question 0" not in formatted


def test_summary_and_compare_prompt_templates():
    sum_p = summary_prompt_template.format(text_content="Sample doc text")
    assert "TEXT TO SUMMARIZE:" in sum_p
    assert "Sample doc text" in sum_p

    cmp_p = compare_prompt_template.format(doc_a="Doc A text", doc_b="Doc B text")
    assert "DOCUMENT A:" in cmp_p
    assert "Doc A text" in cmp_p
    assert "Doc B text" in cmp_p


@patch("backend.src.ai.llm.gemini_llm.ChatGoogleGenerativeAI")
def test_gemini_synthesis_methods(mock_chat_cls):
    mock_chat = MagicMock()
    mock_res = MagicMock()
    mock_res.content = "Summary result text"
    mock_chat.invoke.return_value = mock_res
    mock_chat_cls.return_value = mock_chat

    service = GeminiLLMService(api_key="test_key")

    # Test report generation
    report = service.generate_report("Refunds", "Context details", "Chat history")
    assert report == "Summary result text"
