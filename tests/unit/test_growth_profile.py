"""Tests for growth profile computation."""

import uuid

import pytest

from nietzschian_debugger.scoring.growth_profile import compute_from_sessions
from nietzschian_debugger.types import Session, SkillScores


def make_session(**overrides: object) -> Session:
    """Create a test session."""
    defaults = dict(
        schema_version=1,
        id=str(uuid.uuid4()),
        timestamp="2024-01-01T00:00:00.000Z",
        end_timestamp="2024-01-01T01:00:00.000Z",
        problem_description="test",
        intensity="nietzsche",
        outcome="solved",
        questions_to_root_cause=5,
        code_files=[],
        transcript=[],
        skill_scores=SkillScores(assumption_checking=5, evidence_gathering=5, root_cause_speed=5),
        behavior_tags=[],
    )
    defaults.update(overrides)
    return Session(**defaults)  # type: ignore[arg-type]


class TestComputeFromSessions:
    def test_returns_correct_counts_for_solved_vs_abandoned(self) -> None:
        sessions = [
            make_session(outcome="solved"),
            make_session(outcome="solved"),
            make_session(outcome="abandoned"),
        ]
        profile = compute_from_sessions(sessions)
        assert profile.total_sessions == 3
        assert profile.solved_count == 2
        assert profile.abandoned_count == 1

    def test_computes_average_scores(self) -> None:
        sessions = [
            make_session(
                skill_scores=SkillScores(assumption_checking=8, evidence_gathering=6, root_cause_speed=4)
            ),
            make_session(
                skill_scores=SkillScores(assumption_checking=4, evidence_gathering=8, root_cause_speed=6)
            ),
        ]
        profile = compute_from_sessions(sessions)
        assert profile.average_scores.assumption_checking == 6
        assert profile.average_scores.evidence_gathering == 7
        assert profile.average_scores.root_cause_speed == 5

    def test_returns_stable_trends_with_fewer_than_two_sessions(self) -> None:
        sessions = [make_session()]
        profile = compute_from_sessions(sessions)
        assert profile.recent_trend.assumption_checking == "stable"
        assert profile.recent_trend.evidence_gathering == "stable"
        assert profile.recent_trend.root_cause_speed == "stable"

    def test_returns_stable_trends_when_no_previous_group(self) -> None:
        sessions = [make_session() for _ in range(3)]
        profile = compute_from_sessions(sessions)
        assert profile.recent_trend.assumption_checking == "stable"

    def test_detects_improving_trend(self) -> None:
        old = [
            make_session(
                skill_scores=SkillScores(assumption_checking=3, evidence_gathering=3, root_cause_speed=3)
            )
            for _ in range(5)
        ]
        recent = [
            make_session(
                skill_scores=SkillScores(assumption_checking=8, evidence_gathering=8, root_cause_speed=8)
            )
            for _ in range(5)
        ]
        profile = compute_from_sessions(old + recent)
        assert profile.recent_trend.assumption_checking == "improving"
        assert profile.recent_trend.evidence_gathering == "improving"
        assert profile.recent_trend.root_cause_speed == "improving"

    def test_detects_declining_trend(self) -> None:
        old = [
            make_session(
                skill_scores=SkillScores(assumption_checking=8, evidence_gathering=8, root_cause_speed=8)
            )
            for _ in range(5)
        ]
        recent = [
            make_session(
                skill_scores=SkillScores(assumption_checking=3, evidence_gathering=3, root_cause_speed=3)
            )
            for _ in range(5)
        ]
        profile = compute_from_sessions(old + recent)
        assert profile.recent_trend.assumption_checking == "declining"
        assert profile.recent_trend.evidence_gathering == "declining"
        assert profile.recent_trend.root_cause_speed == "declining"

    def test_detects_stable_when_delta_within_threshold(self) -> None:
        old = [
            make_session(
                skill_scores=SkillScores(assumption_checking=5, evidence_gathering=5, root_cause_speed=5)
            )
            for _ in range(5)
        ]
        recent = [
            make_session(
                skill_scores=SkillScores(assumption_checking=6, evidence_gathering=5, root_cause_speed=4)
            )
            for _ in range(5)
        ]
        profile = compute_from_sessions(old + recent)
        # delta of 1 - should be stable (threshold is > 1)
        assert profile.recent_trend.assumption_checking == "stable"
        assert profile.recent_trend.evidence_gathering == "stable"
        assert profile.recent_trend.root_cause_speed == "stable"
