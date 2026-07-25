from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatMessageItem:
    sender_type: str  # user, assistant, system
    content: str


def format_conversation_history(
    messages: List[ChatMessageItem],
    max_turns: int = 6,
    max_chars: int = 3000,
) -> str:
    """Format and truncate multi-turn conversation history for LLM prompt context."""
    if not messages:
        return "No prior conversation history."

    # Keep only the last N turns
    truncated_messages = messages[-max_turns:] if len(messages) > max_turns else messages

    lines: List[str] = []
    total_chars = 0

    # Build from newest to oldest up to max_chars, then reverse
    for msg in reversed(truncated_messages):
        sender = msg.sender_type.capitalize()
        entry = f"{sender}: {msg.content.strip()}"
        if total_chars + len(entry) > max_chars:
            break
        lines.append(entry)
        total_chars += len(entry)

    lines.reverse()
    return "\n".join(lines)
