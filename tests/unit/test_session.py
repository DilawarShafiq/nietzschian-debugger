"""Tests for session management."""

import pytest

from nietzschian_debugger.core.session import (
    create_session,
    add_turn,
    finalize_session,
    add_code_file,
)


class TestCreateSession:
    def test_creates_session_with_correct_defaults(self) -> None:
        session = create_session("My API is slow", "nietzsche")
        assert session.problem_description == "My API is slow"
        assert session.intensity == "nietzsche"
        assert session.outcome == "abandoned"
        assert session.schema_version == 1
        assert session.id
        assert session.timestamp
        assert session.transcript == []
        assert session.code_files == []
        assert session.skill_scores.assumption_checking == 5
        assert session.skill_scores.evidence_gathering == 5
        assert session.skill_scores.root_cause_speed == 5

    def test_creates_unique_ids_for_each_session(self) -> None:
        s1 = create_session("Problem 1", "socrates")
        s2 = create_session("Problem 2", "zarathustra")
        assert s1.id != s2.id


class TestAddTurn:
    def test_adds_turn_to_transcript(self) -> None:
        session = create_session("Test", "nietzsche")
        turn = add_turn(session, "What happened?", "I got a 500 error", "claude-haiku-4-5-20251001")
        assert len(session.transcript) == 1
        assert turn.turn_number == 1
        assert turn.question == "What happened?"
        assert turn.response == "I got a 500 error"
        assert turn.model == "claude-haiku-4-5-20251001"
        assert turn.timestamp

    def test_increments_turn_numbers(self) -> None:
        session = create_session("Test", "nietzsche")
        add_turn(session, "Q1?", "R1", "model")
        add_turn(session, "Q2?", "R2", "model")
        add_turn(session, "Q3?", "R3", "model")
        assert session.transcript[0].turn_number == 1
        assert session.transcript[1].turn_number == 2
        assert session.transcript[2].turn_number == 3

    def test_updates_questions_to_root_cause(self) -> None:
        session = create_session("Test", "nietzsche")
        add_turn(session, "Q?", "R", "model")
        assert session.questions_to_root_cause == 1
        add_turn(session, "Q2?", "R2", "model")
        assert session.questions_to_root_cause == 2


class TestFinalizeSession:
    def test_sets_outcome_and_end_timestamp(self) -> None:
        session = create_session("Test", "nietzsche")
        finalize_session(session, "solved")
        assert session.outcome == "solved"
        assert session.end_timestamp

    def test_updates_skill_scores_when_provided(self) -> None:
        from nietzschian_debugger.types import SkillScores
        session = create_session("Test", "nietzsche")
        finalize_session(
            session,
            "solved",
            SkillScores(assumption_checking=8, evidence_gathering=7, root_cause_speed=9),
        )
        assert session.skill_scores.assumption_checking == 8


class TestAddCodeFile:
    def test_adds_file_to_session(self) -> None:
        session = create_session("Test", "nietzsche")
        add_code_file(session, "./src/auth.ts")
        assert "./src/auth.ts" in session.code_files

    def test_does_not_duplicate_files(self) -> None:
        session = create_session("Test", "nietzsche")
        add_code_file(session, "./src/auth.ts")
        add_code_file(session, "./src/auth.ts")
        assert len(session.code_files) == 1
