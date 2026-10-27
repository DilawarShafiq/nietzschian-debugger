"""Tests for session-sharing markdown export."""

from __future__ import annotations

from nietzschian_debugger.commands.share import format_session_markdown
from nietzschian_debugger.types import Session, SkillScores, Turn


def _session() -> Session:
    return Session(
        schema_version=1,
        id="s1",
        timestamp="2026-10-28T00:00:00",
        end_timestamp="2026-10-28T00:05:00",
        problem_description="login 403 for old users only",
        intensity="nietzsche",
        outcome="solved",
        questions_to_root_cause=2,
        code_files=[],
        transcript=[
            Turn(turn_number=1, question="What changed last week?", response="nothing in the code", model="m", quote_used=None, behavior_tags=[], timestamp="t"),
            Turn(turn_number=2, question="What field differs on old accounts?", response="[solved]", model="m", quote_used=None, behavior_tags=[], timestamp="t"),
        ],
        skill_scores=SkillScores(assumption_checking=8, evidence_gathering=6, root_cause_speed=7),
        behavior_tags=[],
    )


def test_format_session_markdown() -> None:
    md = format_session_markdown(_session())
    assert "Nietzschian Debugger" in md
    assert "What changed last week?" in md
    assert "> nothing in the code" in md
    assert "Solved" in md
    assert "pip install nietzschian-debugger" in md
    # Control markers must not leak into the shared output.
    assert "[solved]" not in md
