"""Core types for the Nietzschian Debugger."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

Intensity = Literal["socrates", "nietzsche", "zarathustra"]
SessionOutcome = Literal["solved", "abandoned"]
QuoteContext = Literal["avoidance", "overwhelm", "strategy", "victory", "defeat", "perseverance"]
Trend = Literal["improving", "declining", "stable"]

SCHEMA_VERSION = 1


@dataclass
class Quote:
    text: str
    philosopher: str
    context: QuoteContext
    source: str


@dataclass
class BehaviorTag:
    turn_number: int
    tag: str
    dimension: Literal["assumptionChecking", "evidenceGathering", "rootCauseSpeed"]


@dataclass
class Turn:
    turn_number: int
    question: str
    response: str
    model: str
    quote_used: Optional[Quote]
    behavior_tags: list[str]
    timestamp: str


@dataclass
class SkillScores:
    assumption_checking: int = 5
    evidence_gathering: int = 5
    root_cause_speed: int = 5


@dataclass
class Session:
    schema_version: int
    id: str
    timestamp: str
    end_timestamp: str
    problem_description: str
    intensity: Intensity
    outcome: SessionOutcome
    questions_to_root_cause: int
    code_files: list[str]
    transcript: list[Turn]
    skill_scores: SkillScores
    behavior_tags: list[BehaviorTag]


@dataclass
class TrendMap:
    assumption_checking: Trend = "stable"
    evidence_gathering: Trend = "stable"
    root_cause_speed: Trend = "stable"


@dataclass
class GrowthProfile:
    total_sessions: int
    solved_count: int
    abandoned_count: int
    average_scores: SkillScores
    recent_trend: TrendMap
