"""Session persistence - save, load, and list debugging sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from ..types import (
    BehaviorTag,
    Quote,
    SCHEMA_VERSION,
    Session,
    SkillScores,
    Turn,
)

SESSIONS_DIR = ".nietzschian/sessions"


def _get_sessions_path() -> Path:
    """Get the sessions directory path."""
    return Path(os.getcwd()) / SESSIONS_DIR


def _session_to_dict(session: Session) -> dict[str, Any]:
    """Serialize a Session to a JSON-compatible dict."""
    return {
        "schemaVersion": session.schema_version,
        "id": session.id,
        "timestamp": session.timestamp,
        "endTimestamp": session.end_timestamp,
        "problemDescription": session.problem_description,
        "intensity": session.intensity,
        "outcome": session.outcome,
        "questionsToRootCause": session.questions_to_root_cause,
        "codeFiles": session.code_files,
        "transcript": [
            {
                "turnNumber": t.turn_number,
                "question": t.question,
                "response": t.response,
                "model": t.model,
                "quoteUsed": (
                    {
                        "text": t.quote_used.text,
                        "philosopher": t.quote_used.philosopher,
                        "context": t.quote_used.context,
                        "source": t.quote_used.source,
                    }
                    if t.quote_used
                    else None
                ),
                "behaviorTags": t.behavior_tags,
                "timestamp": t.timestamp,
            }
            for t in session.transcript
        ],
        "skillScores": {
            "assumptionChecking": session.skill_scores.assumption_checking,
            "evidenceGathering": session.skill_scores.evidence_gathering,
            "rootCauseSpeed": session.skill_scores.root_cause_speed,
        },
        "behaviorTags": [
            {
                "turnNumber": bt.turn_number,
                "tag": bt.tag,
                "dimension": bt.dimension,
            }
            for bt in session.behavior_tags
        ],
    }


def _dict_to_session(data: dict[str, Any]) -> Session:
    """Deserialize a dict to a Session, with migration for older schemas."""
    version = data.get("schemaVersion", 0)

    # Migrate if needed
    if version < SCHEMA_VERSION:
        data = {
            "schemaVersion": SCHEMA_VERSION,
            "id": data.get("id", ""),
            "timestamp": data.get("timestamp", ""),
            "endTimestamp": data.get("endTimestamp", ""),
            "problemDescription": data.get("problemDescription", ""),
            "intensity": data.get("intensity", "nietzsche"),
            "outcome": data.get("outcome", "abandoned"),
            "questionsToRootCause": data.get("questionsToRootCause", 0),
            "codeFiles": data.get("codeFiles", []),
            "transcript": data.get("transcript", []),
            "skillScores": data.get(
                "skillScores",
                {"assumptionChecking": 5, "evidenceGathering": 5, "rootCauseSpeed": 5},
            ),
            "behaviorTags": data.get("behaviorTags", []),
        }

    skill_data = data.get("skillScores", {})
    skill_scores = SkillScores(
        assumption_checking=skill_data.get("assumptionChecking", 5),
        evidence_gathering=skill_data.get("evidenceGathering", 5),
        root_cause_speed=skill_data.get("rootCauseSpeed", 5),
    )

    transcript: list[Turn] = []
    for t in data.get("transcript", []):
        quote_data = t.get("quoteUsed")
        quote_used = (
            Quote(
                text=quote_data["text"],
                philosopher=quote_data["philosopher"],
                context=quote_data["context"],
                source=quote_data["source"],
            )
            if quote_data
            else None
        )
        transcript.append(
            Turn(
                turn_number=t.get("turnNumber", 0),
                question=t.get("question", ""),
                response=t.get("response", ""),
                model=t.get("model", ""),
                quote_used=quote_used,
                behavior_tags=t.get("behaviorTags", []),
                timestamp=t.get("timestamp", ""),
            )
        )

    behavior_tags: list[BehaviorTag] = []
    for bt in data.get("behaviorTags", []):
        behavior_tags.append(
            BehaviorTag(
                turn_number=bt.get("turnNumber", 0),
                tag=bt.get("tag", ""),
                dimension=bt.get("dimension", "evidenceGathering"),
            )
        )

    return Session(
        schema_version=data.get("schemaVersion", SCHEMA_VERSION),
        id=data.get("id", ""),
        timestamp=data.get("timestamp", ""),
        end_timestamp=data.get("endTimestamp", ""),
        problem_description=data.get("problemDescription", ""),
        intensity=data.get("intensity", "nietzsche"),
        outcome=data.get("outcome", "abandoned"),
        questions_to_root_cause=data.get("questionsToRootCause", 0),
        code_files=data.get("codeFiles", []),
        transcript=transcript,
        skill_scores=skill_scores,
        behavior_tags=behavior_tags,
    )


async def ensure_sessions_dir() -> None:
    """Ensure the sessions directory exists."""
    sessions_path = _get_sessions_path()
    sessions_path.mkdir(parents=True, exist_ok=True)


async def save_session(session: Session) -> str:
    """Save a session to disk, returning the file path."""
    await ensure_sessions_dir()
    file_path = _get_sessions_path() / f"{session.id}.json"
    file_path.write_text(
        json.dumps(_session_to_dict(session), indent=2),
        encoding="utf-8",
    )
    return str(file_path)


async def load_session(session_id: str) -> Optional[Session]:
    """Load a session by ID."""
    try:
        file_path = _get_sessions_path() / f"{session_id}.json"
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
        return _dict_to_session(data)
    except Exception:
        return None


async def list_sessions() -> list[Session]:
    """List all sessions, sorted by timestamp."""
    try:
        sessions_path = _get_sessions_path()
        if not sessions_path.exists():
            return []

        json_files = [f for f in sessions_path.iterdir() if f.suffix == ".json"]
        sessions: list[Session] = []

        for file_path in json_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                data = json.loads(content)
                sessions.append(_dict_to_session(data))
            except Exception:
                # Skip corrupted files
                continue

        sessions.sort(key=lambda s: s.timestamp)
        return sessions
    except Exception:
        return []
