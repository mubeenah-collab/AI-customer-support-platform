import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("safety_escalation")

PROHIBITED_TERMS = [
    r"ignore previous instructions",
    r"system prompt override",
    r"bypass safety",
    r"jailbreak",
    r"drop database",
    r"rm -rf",
    r"eval\(",
    r"<script>",
    r"delete all users",
]

UNSAFE_CONTENT_KEYWORDS = [
    "bomb", "explosive", "hack password", "stolen credit card", "illegal drugs", "self-harm"
]


class SafetyCheckResult:
    def __init__(
        self,
        is_safe: bool,
        reason: Optional[str] = None,
        should_escalate: bool = False,
        suggested_ticket_category: Optional[str] = None,
    ):
        self.is_safe = is_safe
        self.reason = reason
        self.should_escalate = should_escalate
        self.suggested_ticket_category = suggested_ticket_category


class SafetyEscalator:
    """Analyzes customer inputs and RAG outputs for safety violations, prompt injection, and low confidence escalation."""

    @staticmethod
    def analyze_user_query(query: str) -> SafetyCheckResult:
        query_lower = query.lower()

        # 1. Check for prompt injection attacks
        for pattern in PROHIBITED_TERMS:
            if re.search(pattern, query_lower):
                logger.warning(f"Prompt injection attempt detected: '{query[:40]}...'")
                return SafetyCheckResult(
                    is_safe=False,
                    reason="Security Warning: System prompt override or prompt injection attempt detected.",
                    should_escalate=True,
                    suggested_ticket_category="security_flag",
                )

        # 2. Check for prohibited unsafe content keywords
        for keyword in UNSAFE_CONTENT_KEYWORDS:
            if keyword in query_lower:
                logger.warning(f"Unsafe keyword detected in query: '{keyword}'")
                return SafetyCheckResult(
                    is_safe=False,
                    reason=f"Safety Notice: Queries related to '{keyword}' are prohibited under platform safety guidelines.",
                    should_escalate=True,
                    suggested_ticket_category="safety_escalation",
                )

        return SafetyCheckResult(is_safe=True)

    @staticmethod
    def evaluate_response_confidence(
        confidence_score: float,
        has_sufficient_context: bool,
        citations: List[Any],
    ) -> Tuple[bool, Optional[str]]:
        """Determine if answer requires escalation due to low RAG confidence or insufficient knowledge base grounding."""
        if not has_sufficient_context or len(citations) == 0:
            return True, "No relevant knowledge base documents were found to answer your inquiry with high confidence."

        if confidence_score < 0.35:
            return True, f"Confidence score ({round(confidence_score * 100)}%) is below our high-quality threshold."

        return False, None
