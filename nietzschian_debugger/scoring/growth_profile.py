"""Growth profile computation across sessions."""

from __future__ import annotations

from typing import Optional

from ..types import GrowthProfile, Session, SkillScores, Trend, TrendMap
from ..storage.session_store import list_sessions


async def compute_growth_profile() -> Optional[GrowthProfile]:
    """Compute growth profile from all stored sessions."""
    sessions = await list_sessions()
    if not sessions:
        return None
    return compute_from_sessions(sessions)


def compute_from_sessions(sessions: list[Session]) -> GrowthProfile:
    """Compute growth profile from a list of sessions."""
    total_sessions = len(sessions)
    solved_count = sum(1 for s in sessions if s.outcome == "solved")
    abandoned_count = total_sessions - solved_count

    average_scores = _compute_average_scores(sessions)
    recent_trend = _compute_trends(sessions)

    return GrowthProfile(
        total_sessions=total_sessions,
        solved_count=solved_count,
        abandoned_count=abandoned_count,
        average_scores=average_scores,
        recent_trend=recent_trend,
    )


def _compute_average_scores(sessions: list[Session]) -> SkillScores:
    """Compute average skill scores across sessions."""
    if not sessions:
        return SkillScores(assumption_checking=5, evidence_gathering=5, root_cause_speed=5)

    sums = {"assumption_checking": 0, "evidence_gathering": 0, "root_cause_speed": 0}

    for s in sessions:
        sums["assumption_checking"] += s.skill_scores.assumption_checking
        sums["evidence_gathering"] += s.skill_scores.evidence_gathering
        sums["root_cause_speed"] += s.skill_scores.root_cause_speed

    n = len(sessions)
    return SkillScores(
        assumption_checking=round(sums["assumption_checking"] / n),
        evidence_gathering=round(sums["evidence_gathering"] / n),
        root_cause_speed=round(sums["root_cause_speed"] / n),
    )


def _compute_trends(sessions: list[Session]) -> TrendMap:
    """Compute trends by comparing recent vs previous sessions."""
    if len(sessions) < 2:
        return TrendMap(
            assumption_checking="stable",
            evidence_gathering="stable",
            root_cause_speed="stable",
        )

    recent = sessions[-5:]
    previous = sessions[-10:-5]

    if not previous:
        return TrendMap(
            assumption_checking="stable",
            evidence_gathering="stable",
            root_cause_speed="stable",
        )

    recent_avg = _compute_average_scores(recent)
    previous_avg = _compute_average_scores(previous)

    return TrendMap(
        assumption_checking=_compute_trend(
            recent_avg.assumption_checking, previous_avg.assumption_checking
        ),
        evidence_gathering=_compute_trend(
            recent_avg.evidence_gathering, previous_avg.evidence_gathering
        ),
        root_cause_speed=_compute_trend(
            recent_avg.root_cause_speed, previous_avg.root_cause_speed
        ),
    )


def _compute_trend(recent: int, previous: int) -> Trend:
    """Compute trend direction from recent vs previous scores."""
    delta = recent - previous
    if delta > 1:
        return "improving"
    if delta < -1:
        return "declining"
    return "stable"
