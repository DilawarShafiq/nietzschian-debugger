"""Tests for skill scorer."""

import pytest

from nietzschian_debugger.scoring.skill_scorer import compute_skill_scores
from nietzschian_debugger.types import BehaviorTag


class TestComputeSkillScores:
    def test_returns_baseline_scores_with_empty_tags(self) -> None:
        scores = compute_skill_scores([])
        assert scores.assumption_checking == 5
        assert scores.evidence_gathering == 5
        assert scores.root_cause_speed == 5

    def test_increases_evidence_gathering_with_checked_logs(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="checked-logs", dimension="evidenceGathering"),
            BehaviorTag(turn_number=2, tag="checked-logs", dimension="evidenceGathering"),
            BehaviorTag(turn_number=3, tag="checked-logs", dimension="evidenceGathering"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.evidence_gathering == 8

    def test_decreases_evidence_gathering_with_guessed_without_evidence(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="guessed-without-evidence", dimension="evidenceGathering"),
            BehaviorTag(turn_number=2, tag="guessed-without-evidence", dimension="evidenceGathering"),
            BehaviorTag(turn_number=3, tag="guessed-without-evidence", dimension="evidenceGathering"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.evidence_gathering == 2

    def test_increases_assumption_checking_with_questioned_assumption(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="questioned-assumption", dimension="assumptionChecking"),
            BehaviorTag(turn_number=2, tag="questioned-assumption", dimension="assumptionChecking"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.assumption_checking == 7

    def test_decreases_assumption_checking_with_assumed_without_checking(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="assumed-without-checking", dimension="assumptionChecking"),
            BehaviorTag(turn_number=2, tag="assumed-without-checking", dimension="assumptionChecking"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.assumption_checking == 3

    def test_increases_root_cause_speed_with_narrowed_scope(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="narrowed-scope", dimension="rootCauseSpeed"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.root_cause_speed == 6

    def test_decreases_root_cause_speed_with_went_broad_unnecessarily(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="went-broad-unnecessarily", dimension="rootCauseSpeed"),
            BehaviorTag(turn_number=2, tag="went-broad-unnecessarily", dimension="rootCauseSpeed"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.root_cause_speed == 3

    def test_handles_mixed_positive_and_negative_tags(self) -> None:
        tags = [
            BehaviorTag(turn_number=1, tag="checked-logs", dimension="evidenceGathering"),
            BehaviorTag(turn_number=2, tag="guessed-without-evidence", dimension="evidenceGathering"),
            BehaviorTag(turn_number=3, tag="questioned-assumption", dimension="assumptionChecking"),
            BehaviorTag(turn_number=4, tag="narrowed-scope", dimension="rootCauseSpeed"),
        ]
        scores = compute_skill_scores(tags)
        assert scores.evidence_gathering == 5  # +1 -1 = 0 from baseline
        assert scores.assumption_checking == 6  # +1
        assert scores.root_cause_speed == 6  # +1

    def test_clamps_scores_at_minimum_one(self) -> None:
        tags = [
            BehaviorTag(turn_number=i + 1, tag="guessed-without-evidence", dimension="evidenceGathering")
            for i in range(10)
        ]
        scores = compute_skill_scores(tags)
        assert scores.evidence_gathering == 1

    def test_clamps_scores_at_maximum_ten(self) -> None:
        tags = [
            BehaviorTag(turn_number=i + 1, tag="checked-logs", dimension="evidenceGathering")
            for i in range(10)
        ]
        scores = compute_skill_scores(tags)
        assert scores.evidence_gathering == 10
