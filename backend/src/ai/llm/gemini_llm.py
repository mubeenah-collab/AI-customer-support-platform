import logging
from typing import Any, Dict, Generator, Optional, Type, TypeVar
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

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
        self.api_key = api_key or settings.GOOGLE_API_KEY
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
            response = client.invoke(messages)
            if not response or not response.content:
                raise LLMServiceError("Gemini API returned empty response.")
            return str(response.content)
        except Exception as e:
            logger.error(f"Gemini LLM generate error: {str(e)}")
            raise LLMServiceError(f"Gemini API error during generation: {str(e)}") from e

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
            for chunk in client.stream([HumanMessage(content=prompt)]):
                if chunk and chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            logger.error(f"Gemini LLM stream error: {str(e)}")
            raise LLMServiceError(f"Gemini API error during streaming: {str(e)}") from e

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
