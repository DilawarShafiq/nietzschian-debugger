"""0.5.2 cross-model robustness: reasoning-tag stripping and the thinking spinner."""

from __future__ import annotations

from nietzschian_debugger.llm import client
from nietzschian_debugger.ui import renderer


def test_strip_reasoning_removes_think_blocks() -> None:
    # A reasoning model that inlines its chain-of-thought must never show it —
    # and in predict it would literally reason the answer out loud.
    raw = "<think>The user probably expects 5, but len('') is 0.</think>Your guess betrays you."
    assert client._strip_reasoning(raw) == "Your guess betrays you."


def test_strip_reasoning_handles_thinking_and_reasoning_tags() -> None:
    assert client._strip_reasoning("<thinking>x</thinking>A") == "A"
    assert client._strip_reasoning("<reasoning>y</reasoning>B") == "B"
    # No tags: untouched (just trimmed).
    assert client._strip_reasoning("  plain prose  ") == "plain prose"


def test_thinking_spinner_yields_and_never_swallows_errors() -> None:
    # The spinner is best-effort cosmetics; it must not hide a real failure.
    ran = []
    with renderer.thinking("Revaluing"):
        ran.append(True)
    assert ran == [True]

    import pytest

    with pytest.raises(ValueError):
        with renderer.thinking():
            raise ValueError("boom")
