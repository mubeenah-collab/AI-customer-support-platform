import re
from dataclasses import dataclass
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class ProcessedChunk:
    chunk_index: int
    content: str
    token_count: int
    page_number: Optional[int] = None


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable control characters."""
    if not text:
        return ""
    # Strip null bytes and non-printable controls except newline/tab
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    # Collapse multiple consecutive blank spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    # Collapse 3 or more newlines into 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


class DocumentTextSplitter:
    """Splits document text into overlapping chunks using LangChain RecursiveCharacterTextSplitter."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split_text(
        self,
        text: str,
        page_number: Optional[int] = None,
        start_index: int = 0,
    ) -> List[ProcessedChunk]:
        cleaned = clean_text(text)
        if not cleaned:
            return []

        raw_chunks = self.splitter.split_text(cleaned)
        processed: List[ProcessedChunk] = []

        for idx, chunk_str in enumerate(raw_chunks, start=start_index):
            # Estimate token count (rough rule of thumb: ~4 characters per token)
            token_est = max(1, len(chunk_str) // 4)
            processed.append(
                ProcessedChunk(
                    chunk_index=idx,
                    content=chunk_str,
                    token_count=token_est,
                    page_number=page_number,
                )
            )

        return processed
