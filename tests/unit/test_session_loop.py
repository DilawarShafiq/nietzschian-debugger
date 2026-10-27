"""Tests for session-loop error handling."""

from __future__ import annotations

import asyncio

from nietzschian_debugger.core import session_loop
from nietzschian_debugger.core.session import create_session


def test_opening_question_error_is_handled(monkeypatch) -> None:
    # A failure generating the FIRST question (bad model, rate limit, a dead
    # provider like "model not found") must end the session cleanly as abandoned,
    # not raise a raw traceback at the user.
    def boom(*args, **kwargs):
        raise RuntimeError("provider exploded")

    monkeypatch.setattr(session_loop, "_generate_valid_question", boom)
    session = create_session("some bug with no file paths", "nietzsche")
    result = asyncio.run(session_loop.run_session_loop(session))
    assert result.outcome == "abandoned"
