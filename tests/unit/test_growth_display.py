"""Tests for growth display rendering."""

import pytest

from nietzschian_debugger.ui.growth_display import render_growth_score
from nietzschian_debugger.types import (
    GrowthProfile,
    Quote,
    Session,
    SkillScores,
    TrendMap,
)


def make_session(**overrides: object) -> Session:
    """Create a test session."""
    defaults = dict(
        schema_version=1,
        id="test-id",
        timestamp="2024-01-01T00:00:00.000Z",
        end_timestamp="2024-01-01T01:00:00.000Z",
        problem_description="test",
        intensity="nietzsche",
        outcome="solved",
        questions_to_root_cause=5,
        code_files=[],
        transcript=[],
        skill_scores=SkillScores(assumption_checking=7, evidence_gathering=6, root_cause_speed=8),
        behavior_tags=[],
    )
    defaults.update(overrides)
    return Session(**defaults)  # type: ignore[arg-type]


class TestRenderGrowthScore:
    def test_renders_session_outcome_and_question_count(self) -> None:
        session = make_session(outcome="solved", questions_to_root_cause=5)
        output = render_growth_score(session)
        assert "5 questions to root cause" in output
        assert "Solved" in output

    def test_renders_abandoned_outcome(self) -> None:
        session = make_session(outcome="abandoned")
        output = render_growth_score(session)
        assert "Abandoned" in output

    def test_renders_skill_dimension_labels(self) -> None:
        session = make_session()
        output = render_growth_score(session)
        assert "Assumption-checking" in output
        assert "Evidence-gathering" in output
        assert "Root cause speed" in output

    def test_renders_unicode_bar_charts(self) -> None:
        session = make_session()
        output = render_growth_score(session)
        assert "\u2588" in output  # FILLED
        assert "\u2591" in output  # EMPTY

    def test_renders_score_descriptors(self) -> None:
        session = make_session(
            skill_scores=SkillScores(assumption_checking=9, evidence_gathering=5, root_cause_speed=2)
        )
        output = render_growth_score(session)
        assert "strong" in output
        assert "moderate" in output
        assert "weak" in output

    def test_includes_trend_information_with_growth_profile(self) -> None:
        session = make_session()
        profile = GrowthProfile(
            total_sessions=10,
            solved_count=7,
            abandoned_count=3,
            average_scores=SkillScores(assumption_checking=6, evidence_gathering=7, root_cause_speed=5),
            recent_trend=TrendMap(
                assumption_checking="improving",
                evidence_gathering="declining",
                root_cause_speed="stable",
            ),
        )
        output = render_growth_score(session, profile)
        assert "improving" in output
        assert "declining" in output
        assert "10 sessions total" in output
        assert "7 solved" in output
        assert "3 abandoned" in output

    def test_includes_closing_quote(self) -> None:
        session = make_session()
        quote = Quote(
            text="What does not kill me makes me stronger.",
            philosopher="Friedrich Nietzsche",
            context="victory",
            source="Twilight of the Idols",
        )
        output = render_growth_score(session, None, quote)
        assert "What does not kill me makes me stronger." in output
        assert "Friedrich Nietzsche" in output

    def test_renders_without_growth_profile_or_quote(self) -> None:
        session = make_session()
        output = render_growth_score(session)
        assert "Debugging Profile" in output
        assert "sessions total" not in output
