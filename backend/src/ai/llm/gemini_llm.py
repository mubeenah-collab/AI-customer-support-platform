import logging
from typing import Any, Dict, Generator, Optional, Type, TypeVar
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from backend.src.ai.gemini_retry import call_with_retry
from backend.src.ai.llm.base_llm import ILLMService, LLMServiceError
from backend.src.config.settings import settings
from backend.src.presentation.schemas.ai_schemas import ComparisonResponseSchema, SummaryResponseSchema

logger = logging.getLogger("gemini_llm")

T = TypeVar("T", bound=BaseModel)


class GeminiLLMService(ILLMService):
    """Concrete implementation of ILLMService using ChatGoogleGenerativeAI (Gemini LLM)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
    ):
        self.api_key = settings.GOOGLE_API_KEY if api_key is None else api_key
        self.model_name = model_name or settings.GEMINI_LLM_MODEL
        self.temperature = temperature
        self._llm_client: Optional[ChatGoogleGenerativeAI] = None

        if self.api_key:
            try:
                self._llm_client = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=self.temperature,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ChatGoogleGenerativeAI client: {str(e)}")

    def _get_client(self) -> ChatGoogleGenerativeAI:
        if not self._llm_client:
            if not self.api_key:
                raise LLMServiceError("Google API Key is missing. Set GOOGLE_API_KEY environment variable.")
            try:
                self._llm_client = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=self.temperature,
                )
            except Exception as e:
                raise LLMServiceError(f"Failed to initialize ChatGoogleGenerativeAI: {str(e)}") from e
        return self._llm_client

    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate plain text completion using Gemini LLM."""
        if not prompt or not prompt.strip():
            raise LLMServiceError("Prompt cannot be empty.")

        client = self._get_client()
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        try:
            response = call_with_retry(client.invoke, messages)
            if not response or not response.content:
                raise LLMServiceError("Gemini API returned empty response.")
            if isinstance(response.content, list):
                parts = []
                for p in response.content:
                    if isinstance(p, dict) and "text" in p:
                        parts.append(p["text"])
                    elif isinstance(p, str):
                        parts.append(p)
                return "\n".join(parts) if parts else str(response.content)
            return str(response.content)
        except LLMServiceError:
            raise
        except Exception as e:
            err_str = str(e)
            fallback_models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
            for fb_model in fallback_models:
                if fb_model == self.model_name:
                    continue
                try:
                    logger.warning(f"Model {self.model_name} error ({err_str[:60]}). Retrying with fallback model {fb_model}...")
                    fallback_client = ChatGoogleGenerativeAI(
                        model=fb_model,
                        google_api_key=self.api_key,
                        temperature=self.temperature,
                    )
                    fb_response = call_with_retry(fallback_client.invoke, messages, max_retries=1)
                    if fb_response and fb_response.content:
                        return str(fb_response.content)
                except Exception as fb_err:
                    logger.error(f"Fallback model {fb_model} failed: {str(fb_err)[:80]}")

            logger.error("Gemini LLM generate error: %s", type(e).__name__)
            raise LLMServiceError(f"Gemini API error during generation: {err_str}") from e

    def generate_structured(self, prompt: str, response_schema: Type[T]) -> T:
        """Generate structured Pydantic output using PydanticOutputParser."""
        client = self._get_client()
        parser = PydanticOutputParser(pydantic_object=response_schema)
        formatting_instructions = parser.get_format_instructions()

        full_prompt = f"{prompt}\n\n{formatting_instructions}"
        try:
            raw_text = self.generate(full_prompt)
            parsed_object = parser.parse(raw_text)
            return parsed_object
        except Exception as e:
            logger.error(f"Gemini LLM generate_structured error: {str(e)}")
            raise LLMServiceError(f"Failed to generate structured response: {str(e)}") from e

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream generated response chunks from Gemini LLM."""
        if not prompt or not prompt.strip():
            raise LLMServiceError("Prompt cannot be empty.")

        client = self._get_client()
        try:
            # Streaming is not retried mid-stream to avoid duplicate content;
            # the initial connection attempt uses retry.
            for chunk in call_with_retry(client.stream, [HumanMessage(content=prompt)]):
                if chunk and chunk.content:
                    yield str(chunk.content)
        except LLMServiceError:
            raise
        except Exception as e:
            logger.error("Gemini LLM stream error: %s", type(e).__name__)
            raise LLMServiceError(f"Gemini API error during streaming: {type(e).__name__}") from e

    def summarize_text(self, text: str) -> SummaryResponseSchema:
        """Summarize text content using Gemini LLM."""
        from backend.src.ai.prompts.summary_prompt import summary_prompt_template

        prompt = summary_prompt_template.format(text_content=text)
        return self.generate_structured(prompt, SummaryResponseSchema)

    def compare_documents(self, doc_a: str, doc_b: str) -> ComparisonResponseSchema:
        """Compare two documents using Gemini reasoning."""
        from backend.src.ai.prompts.compare_prompt import compare_prompt_template

        prompt = compare_prompt_template.format(doc_a=doc_a, doc_b=doc_b)
        return self.generate_structured(prompt, ComparisonResponseSchema)

    def generate_report(self, topic: str, context: str, chat_history: str = "") -> str:
        """Generate structured support report using Gemini LLM."""
        from backend.src.ai.prompts.report_prompt import report_prompt_template

        prompt = report_prompt_template.format(topic=topic, context=context, chat_history=chat_history)
        return self.generate(prompt)
