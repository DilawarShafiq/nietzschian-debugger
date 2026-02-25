"""Tests for context manager."""

import math

import pytest

from nietzschian_debugger.core.context_manager import (
    build_message_array,
    estimate_tokens,
    should_summarize,
)
from nietzschian_debugger.types import Turn


def make_turn(n: int, question: str, response: str) -> Turn:
    """Create a test turn."""
    return Turn(
        turn_number=n,
        question=question,
        response=response,
        model="claude-haiku-4-5-20251001",
        quote_used=None,
        behavior_tags=[],
        timestamp="2024-01-01T00:00:00.000Z",
    )


class TestEstimateTokens:
    def test_estimates_one_token_per_four_characters(self) -> None:
        system = "a" * 400  # 100 tokens
        messages = [{"role": "user", "content": "b" * 400}]  # 100 tokens
        estimate = estimate_tokens(system, messages)
        assert estimate == 200

    def test_handles_empty_messages(self) -> None:
        estimate = estimate_tokens("system", [])
        assert estimate == 2  # ceil(6/4) = 2

    def test_sums_tokens_across_multiple_messages(self) -> None:
        messages = [
            {"role": "user", "content": "a" * 100},
            {"role": "assistant", "content": "b" * 100},
        ]
        estimate = estimate_tokens("", messages)
        assert estimate == 50  # 200 chars / 4


class TestShouldSummarize:
    def test_returns_false_below_threshold(self) -> None:
        assert should_summarize(100_000) is False

    def test_returns_true_above_threshold(self) -> None:
        assert should_summarize(170_000) is True

    def test_returns_false_at_exactly_the_threshold(self) -> None:
        assert should_summarize(160_000) is False

    def test_returns_true_at_threshold_plus_one(self) -> None:
        assert should_summarize(160_001) is True


class TestBuildMessageArray:
    def test_builds_messages_from_turns(self) -> None:
        turns = [
            make_turn(1, "What happened?", "I got a 500 error"),
            make_turn(2, "Where did you see it?", "In the API call"),
        ]
        result = build_message_array(turns)
        assert len(result.messages) == 4  # 2 turns x (question + response)
        assert result.messages[0]["role"] == "assistant"
        assert result.messages[0]["content"] == "What happened?"
        assert result.messages[1]["role"] == "user"
        assert result.messages[1]["content"] == "I got a 500 error"

    def test_handles_empty_turns(self) -> None:
        result = build_message_array([])
        assert len(result.messages) == 0

    def test_preserves_rolling_summary_in_return_value(self) -> None:
        result = build_message_array([], "Previous summary text")
        assert result.rolling_summary == "Previous summary text"

    def test_handles_turns_with_empty_responses(self) -> None:
        turns = [make_turn(1, "Question?", "")]
        result = build_message_array(turns)
        # Question is there, but empty response is skipped by the implementation
        assert len(result.messages) == 1
        assert result.messages[0]["role"] == "assistant"
