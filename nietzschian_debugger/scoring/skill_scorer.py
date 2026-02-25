"""Skill scoring based on behavior tags."""

from __future__ import annotations

from ..types import BehaviorTag, SkillScores

POSITIVE_TAGS: dict[str, str] = {
    "checked-logs": "evidenceGathering",
    "questioned-assumption": "assumptionChecking",
    "narrowed-scope": "rootCauseSpeed",
}

NEGATIVE_TAGS: dict[str, str] = {
    "guessed-without-evidence": "evidenceGathering",
    "assumed-without-checking": "assumptionChecking",
    "asked-for-answer": "assumptionChecking",
    "went-broad-unnecessarily": "rootCauseSpeed",
}

BASE_SCORE = 5
POSITIVE_WEIGHT = 1.0
NEGATIVE_WEIGHT = 1.0


def _clamp(value: float) -> int:
    """Clamp a value between 1 and 10, rounded."""
    return max(1, min(10, round(value)))


def compute_skill_scores(behavior_tags: list[BehaviorTag]) -> SkillScores:
    """Compute skill scores from behavior tags."""
    scores: dict[str, float] = {
        "assumptionChecking": BASE_SCORE,
        "evidenceGathering": BASE_SCORE,
        "rootCauseSpeed": BASE_SCORE,
    }

    for bt in behavior_tags:
        dim = bt.dimension
        if bt.tag in POSITIVE_TAGS:
            scores[dim] += POSITIVE_WEIGHT
        elif bt.tag in NEGATIVE_TAGS:
            scores[dim] -= NEGATIVE_WEIGHT

    return SkillScores(
        assumption_checking=_clamp(scores["assumptionChecking"]),
        evidence_gathering=_clamp(scores["evidenceGathering"]),
        root_cause_speed=_clamp(scores["rootCauseSpeed"]),
    )
