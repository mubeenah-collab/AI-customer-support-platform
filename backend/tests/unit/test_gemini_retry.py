"""
Unit tests for gemini_retry.py — exponential backoff, rate limiting (429), permanent error short-circuit.
Uses mocks to ensure no real Gemini API calls are made and no API quota is consumed.
"""
from unittest.mock import MagicMock, patch
import pytest

from backend.src.ai.gemini_retry import (
    _compute_delay,
    _is_transient,
    call_with_retry,
    with_gemini_retry,
)


def test_is_transient_detection():
    # Transient errors
    assert _is_transient(Exception("429 RESOURCE_EXHAUSTED: Quota exceeded")) is True
    assert _is_transient(Exception("503 Service Unavailable")) is True
    assert _is_transient(Exception("Too many requests, please retry")) is True

    # Permanent errors
    assert _is_transient(Exception("404 NOT_FOUND: Model gemini-1.5-pro not found")) is False
    assert _is_transient(Exception("401 UNAUTHENTICATED: Invalid API key")) is False
    assert _is_transient(Exception("400 INVALID_ARGUMENT")) is False
    assert _is_transient(Exception("General unexpected TypeError")) is False


def test_compute_delay_bounds():
    delay = _compute_delay(attempt=0, base=2.0, factor=2.0, cap=60.0)
    assert 0 <= delay <= 2.0

    delay_att2 = _compute_delay(attempt=2, base=2.0, factor=2.0, cap=60.0)
    assert 0 <= delay_att2 <= 8.0


@patch("backend.src.ai.gemini_retry.time.sleep")
def test_retry_success_after_transient_failures(mock_sleep):
    mock_fn = MagicMock(side_effect=[
        Exception("429 RESOURCE_EXHAUSTED"),
        Exception("503 Service Unavailable"),
        "Success Result",
    ])

    result = call_with_retry(
        mock_fn,
        "arg1",
        max_retries=3,
        base_delay=0.1,
        max_delay=1.0,
    )

    assert result == "Success Result"
    assert mock_fn.call_count == 3
    assert mock_sleep.call_count == 2


@patch("backend.src.ai.gemini_retry.time.sleep")
def test_retry_permanent_error_no_retries(mock_sleep):
    mock_fn = MagicMock(side_effect=Exception("404 NOT_FOUND: model not found"))

    with pytest.raises(Exception) as exc_info:
        call_with_retry(
            mock_fn,
            max_retries=3,
            base_delay=0.1,
        )

    assert "404 NOT_FOUND" in str(exc_info.value)
    assert mock_fn.call_count == 1
    assert mock_sleep.call_count == 0


@patch("backend.src.ai.gemini_retry.time.sleep")
def test_retry_exhaustion_raises_last_error(mock_sleep):
    mock_fn = MagicMock(side_effect=Exception("429 RESOURCE_EXHAUSTED persistent"))

    with pytest.raises(Exception) as exc_info:
        call_with_retry(
            mock_fn,
            max_retries=2,
            base_delay=0.1,
        )

    assert "429 RESOURCE_EXHAUSTED persistent" in str(exc_info.value)
    assert mock_fn.call_count == 3  # initial + 2 retries
    assert mock_sleep.call_count == 2


@patch("backend.src.ai.gemini_retry.time.sleep")
def test_decorator_syntax(mock_sleep):
    mock_inner = MagicMock(side_effect=[Exception("503 Unavailable"), "Deco OK"])

    @with_gemini_retry(max_retries=2, base_delay=0.01)
    def decorated_call():
        return mock_inner()

    res = decorated_call()
    assert res == "Deco OK"
    assert mock_inner.call_count == 2
