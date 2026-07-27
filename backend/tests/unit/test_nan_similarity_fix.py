import math
import pytest
from backend.src.ai.rag.chroma_vector_store import calculate_safe_similarity


def test_calculate_safe_similarity_none():
    assert calculate_safe_similarity(None) == 0.0


def test_calculate_safe_similarity_nan():
    assert calculate_safe_similarity(float("nan")) == 0.0


def test_calculate_safe_similarity_inf():
    assert calculate_safe_similarity(float("inf")) == 0.0
    assert calculate_safe_similarity(float("-inf")) == 0.0


def test_calculate_safe_similarity_negative():
    assert calculate_safe_similarity(-0.5) == 1.0


def test_calculate_safe_similarity_zero():
    assert calculate_safe_similarity(0.0) == 1.0


def test_calculate_safe_similarity_standard():
    assert calculate_safe_similarity(0.2) == 0.8
    assert calculate_safe_similarity(0.5) == 0.5
    assert calculate_safe_similarity(1.0) == 0.0


def test_calculate_safe_similarity_oversized_distance():
    assert calculate_safe_similarity(1.5) == 0.25
    assert calculate_safe_similarity(2.5) == 0.0


def test_calculate_safe_similarity_invalid_string():
    assert calculate_safe_similarity("not_a_number") == 0.0
