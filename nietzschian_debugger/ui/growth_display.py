"""Growth score display for session completion."""

from __future__ import annotations

from typing import Optional

from ..types import GrowthProfile, Quote, Session, SkillScores, Trend

FILLED = "\u2588"
EMPTY = "\u2591"
BAR_LENGTH = 10

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
GREEN = "\x1b[32m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"


def _render_bar(score: int) -> str:
    """Render a Unicode bar chart for a score (1-10)."""
    clamped = max(1, min(10, round(score)))
    return FILLED * clamped + EMPTY * (BAR_LENGTH - clamped)


def _score_label(score: int) -> str:
    """Return a text label for a score."""
    if score >= 8:
        return "strong"
    if score >= 5:
        return "moderate"
    return "weak"


def _trend_indicator(trend: Trend, delta: Optional[int] = None) -> str:
    """Render a colored trend indicator."""
    if trend == "improving":
        d = f" (+{delta})" if delta is not None else ""
        return f"{GREEN}improving{d}{RESET}"
    if trend == "declining":
        d = f" ({delta})" if delta is not None else ""
        return f"{RED}declining{d}{RESET}"
    return f"{DIM}stable{RESET}"


def render_growth_score(
    session: Session,
    growth_profile: Optional[GrowthProfile] = None,
    closing_quote: Optional[Quote] = None,
) -> str:
    """Render the growth score display for a completed session."""
    lines: list[str] = []

    outcome_label = "Solved" if session.outcome == "solved" else "Abandoned"
    lines.append(
        f"\n{BOLD}Session Complete -- {session.questions_to_root_cause} questions "
        f"to root cause ({outcome_label}){RESET}"
    )
    lines.append("")
    lines.append(f"{BOLD}Your Debugging Profile:{RESET}")

    scores = session.skill_scores
    dims = [
        ("Assumption-checking", scores.assumption_checking, "assumption_checking"),
        ("Evidence-gathering", scores.evidence_gathering, "evidence_gathering"),
        ("Root cause speed", scores.root_cause_speed, "root_cause_speed"),
    ]

    for i, (name, score, key) in enumerate(dims):
        bar = _render_bar(score)
        connector = "\u2523" if i < len(dims) - 1 else "\u2517"
        line = f"{connector} {name:<22} {bar}  {_score_label(score)}"

        if growth_profile:
            trend = getattr(growth_profile.recent_trend, key)
            if trend != "stable":
                line += f" -- {_trend_indicator(trend)}"

        lines.append(line)

    if growth_profile and growth_profile.total_sessions > 1:
        lines.append("")
        lines.append(
            f"{DIM}{growth_profile.total_sessions} sessions total | "
            f"{growth_profile.solved_count} solved | "
            f"{growth_profile.abandoned_count} abandoned{RESET}"
        )

    if closing_quote:
        lines.append("")
        lines.append(f'{DIM}"{closing_quote.text}"{RESET}')
        lines.append(f"{DIM} -- {closing_quote.philosopher}{RESET}")

    lines.append("")
    return "\n".join(lines)
