from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Generator, Optional, Type, TypeVar
from pydantic import BaseModel


class LLMServiceError(Exception):
    """Exception raised when LLM generation fails."""

    def __init__(self, message: str = "LLM generation failure"):
        self.message = message
        super().__init__(self.message)


T = TypeVar("T", bound=BaseModel)


class ILLMService(ABC):
    """Abstract contract for Language Model text generation and structured outputs."""

    @abstractmethod
    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate plain text completion for a given prompt."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, response_schema: Type[T]) -> T:
        """Generate structured Pydantic output matching a specified schema."""
        pass

    @abstractmethod
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream generated text tokens progressively."""
        pass
