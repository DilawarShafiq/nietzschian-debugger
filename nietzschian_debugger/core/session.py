"""Session creation and management."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from ..types import (
    BehaviorTag,
    Intensity,
    Quote,
    SCHEMA_VERSION,
    Session,
    SessionOutcome,
    SkillScores,
    Turn,
)


def create_session(problem_description: str, intensity: Intensity) -> Session:
    """Create a new debugging session."""
    return Session(
        schema_version=SCHEMA_VERSION,
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        end_timestamp="",
        problem_description=problem_description,
        intensity=intensity,
        outcome="abandoned",
        questions_to_root_cause=0,
        code_files=[],
        transcript=[],
        skill_scores=SkillScores(
            assumption_checking=5,
            evidence_gathering=5,
            root_cause_speed=5,
        ),
        behavior_tags=[],
    )


def add_turn(
    session: Session,
    question: str,
    response: str,
    model: str,
    behavior_tags: Optional[list[str]] = None,
    quote_used: Optional[Quote] = None,
) -> Turn:
    """Add a turn to the session transcript."""
    turn = Turn(
        turn_number=len(session.transcript) + 1,
        question=question,
        response=response,
        model=model,
        quote_used=quote_used,
        behavior_tags=behavior_tags or [],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    session.transcript.append(turn)
    session.questions_to_root_cause = len(session.transcript)
    return turn


def finalize_session(
    session: Session,
    outcome: SessionOutcome,
    skill_scores: Optional[SkillScores] = None,
    behavior_tags: Optional[list[BehaviorTag]] = None,
) -> None:
    """Finalize a session with outcome and scores."""
    session.end_timestamp = datetime.now(timezone.utc).isoformat()
    session.outcome = outcome
    if skill_scores is not None:
        session.skill_scores = skill_scores
    if behavior_tags is not None:
        session.behavior_tags = behavior_tags


def add_code_file(session: Session, file_path: str) -> None:
    """Add a code file to the session if not already present."""
    if file_path not in session.code_files:
        session.code_files.append(file_path)
