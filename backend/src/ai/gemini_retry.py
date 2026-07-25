"""
gemini_retry.py — Shared Gemini API retry utility with exponential backoff.

Handles transient Gemini errors (429 RESOURCE_EXHAUSTED, 503 UNAVAILABLE)
with configurable exponential backoff. Permanent errors (400, 401, 403, 404)
are re-raised immediately without retrying.

Design constraints:
- No new external dependencies (uses stdlib time/random only).
- No infinite loops — hard cap at MAX_RETRIES.
- Does NOT retry permanent errors to avoid wasting quota.
- Caller receives a clean, user-facing error after retries exhausted.
"""
import logging
import random
import time
from functools import wraps
from typing import Callable, Optional, Tuple, Type, TypeVar

logger = logging.getLogger("gemini_retry")

# Transient HTTP-status codes that should trigger a retry.
_RETRYABLE_STATUS_CODES: Tuple[int, ...] = (429, 500, 502, 503, 504)

# Strings present in transient Gemini error messages.
_RETRYABLE_PHRASES: Tuple[str, ...] = (
    "RESOURCE_EXHAUSTED",
    "UNAVAILABLE",
    "INTERNAL",
    "overloaded",
    "quota",
    "rate limit",
    "too many requests",
    "retry",
)

# Strings that indicate permanent, non-retryable errors.
_PERMANENT_PHRASES: Tuple[str, ...] = (
    "NOT_FOUND",
    "INVALID_ARGUMENT",
    "PERMISSION_DENIED",
    "UNAUTHENTICATED",
    "API key",
    "invalid",
)

# Production defaults — kept conservative to respect free-tier limits.
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_BASE_DELAY_S: float = 2.0   # base wait before first retry
DEFAULT_MAX_DELAY_S: float = 60.0   # cap on single wait duration
DEFAULT_BACKOFF_FACTOR: float = 2.0


def _is_transient(error: Exception) -> bool:
    """Return True if the exception looks like a transient Gemini API error."""
    msg = str(error).lower()

    # Check for retryable phrases first.
    if any(phrase.lower() in msg for phrase in _RETRYABLE_PHRASES):
        # But never retry if it's definitely a permanent error.
        if any(phrase.lower() in msg for phrase in _PERMANENT_PHRASES):
            return False
        return True

    # Check status codes embedded in error message strings (e.g. "429").
    for code in _RETRYABLE_STATUS_CODES:
        if str(code) in msg:
            return True

    return False


def _compute_delay(attempt: int, base: float, factor: float, cap: float) -> float:
    """Full-jitter exponential backoff: avoids thundering herd."""
    max_sleep = min(cap, base * (factor ** attempt))
    return random.uniform(0, max_sleep)


def with_gemini_retry(
    func: Optional[Callable] = None,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY_S,
    max_delay: float = DEFAULT_MAX_DELAY_S,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
):
    """
    Decorator that wraps any Gemini API call with exponential-backoff retry.

    Usage:
        @with_gemini_retry
        def call_gemini(...): ...

        @with_gemini_retry(max_retries=2, base_delay=1.0)
        def call_gemini(...): ...

    Supports both @with_gemini_retry and @with_gemini_retry(...) forms.
    """
    def decorator(fn: Callable) -> Callable:
        fn_name = getattr(fn, "__name__", getattr(type(fn), "__name__", "callable"))

        def wrapper(*args, **kwargs):
            last_error: Optional[Exception] = None
            for attempt in range(max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last_error = exc
                    if not _is_transient(exc):
                        # Permanent error — re-raise immediately.
                        logger.debug(
                            "Gemini permanent error on %s (attempt %d/%d): %s",
                            fn_name, attempt + 1, max_retries + 1, type(exc).__name__,
                        )
                        raise

                    if attempt >= max_retries:
                        # Retries exhausted.
                        logger.warning(
                            "Gemini transient error on %s — retries exhausted (%d/%d): %s",
                            fn_name, attempt + 1, max_retries + 1, str(exc)[:200],
                        )
                        break

                    delay = _compute_delay(attempt, base_delay, backoff_factor, max_delay)
                    logger.warning(
                        "Gemini transient error on %s (attempt %d/%d) — retrying in %.1fs: %s",
                        fn_name, attempt + 1, max_retries + 1, delay, str(exc)[:200],
                    )
                    time.sleep(delay)

            # All retries exhausted — raise the last captured error.
            raise last_error  # type: ignore[misc]

        if hasattr(fn, "__name__") and not isinstance(getattr(fn, "__name__"), MagicMock if "MagicMock" in globals() else type):
            try:
                wraps(fn)(wrapper)
            except Exception:
                pass

        return wrapper

    # Support both bare @with_gemini_retry and @with_gemini_retry(...)
    if func is not None:
        return decorator(func)
    return decorator


def call_with_retry(
    fn: Callable,
    *args,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY_S,
    max_delay: float = DEFAULT_MAX_DELAY_S,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    **kwargs,
):
    """
    Functional interface — call fn(*args, **kwargs) with retry.

    Example:
        result = call_with_retry(client.embed_query, text, max_retries=2)
    """
    return with_gemini_retry(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
    )(fn)(*args, **kwargs)
