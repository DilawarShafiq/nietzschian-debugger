"""Tests for session store."""

import json
import os
import shutil
from pathlib import Path

import pytest

from nietzschian_debugger.storage.session_store import (
    save_session,
    load_session,
    list_sessions,
)
from nietzschian_debugger.core.session import create_session, finalize_session

TEST_SESSIONS_DIR = Path(os.getcwd()) / ".nietzschian" / "sessions"


@pytest.fixture(autouse=True)
def cleanup_sessions_dir():
    """Clean up sessions directory before and after each test."""
    if TEST_SESSIONS_DIR.exists():
        shutil.rmtree(TEST_SESSIONS_DIR, ignore_errors=True)
    yield
    if TEST_SESSIONS_DIR.exists():
        shutil.rmtree(TEST_SESSIONS_DIR, ignore_errors=True)


class TestSessionStore:
    @pytest.mark.asyncio
    async def test_saves_session_and_creates_directory(self) -> None:
        session = create_session("Test problem", "nietzsche")
        finalize_session(session, "solved")

        file_path = await save_session(session)
        assert session.id in file_path

        files = list(TEST_SESSIONS_DIR.iterdir())
        file_names = [f.name for f in files]
        assert f"{session.id}.json" in file_names

    @pytest.mark.asyncio
    async def test_loads_saved_session_identically(self) -> None:
        session = create_session("Load test", "zarathustra")
        finalize_session(session, "abandoned")

        await save_session(session)
        loaded = await load_session(session.id)

        assert loaded is not None
        assert loaded.id == session.id
        assert loaded.problem_description == "Load test"
        assert loaded.intensity == "zarathustra"
        assert loaded.outcome == "abandoned"
        assert loaded.schema_version == session.schema_version

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_session(self) -> None:
        TEST_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        loaded = await load_session("non-existent-id")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_lists_sessions_sorted_by_timestamp(self) -> None:
        s1 = create_session("First", "socrates")
        s2 = create_session("Second", "nietzsche")
        s3 = create_session("Third", "zarathustra")

        # Force distinct timestamps
        s1.timestamp = "2024-01-01T00:00:00.000Z"
        s2.timestamp = "2024-01-02T00:00:00.000Z"
        s3.timestamp = "2024-01-03T00:00:00.000Z"

        await save_session(s1)
        await save_session(s2)
        await save_session(s3)

        sessions = await list_sessions()
        assert len(sessions) == 3
        assert sessions[0].problem_description == "First"
        assert sessions[1].problem_description == "Second"
        assert sessions[2].problem_description == "Third"

    @pytest.mark.asyncio
    async def test_auto_creates_directory_when_missing(self) -> None:
        session = create_session("Auto-create dir", "nietzsche")
        await save_session(session)

        files = list(TEST_SESSIONS_DIR.iterdir())
        assert len(files) > 0

    @pytest.mark.asyncio
    async def test_handles_corrupted_json_gracefully(self) -> None:
        session = create_session("Valid session", "nietzsche")
        await save_session(session)

        # Write a corrupted file
        corrupted_path = TEST_SESSIONS_DIR / "corrupted.json"
        corrupted_path.write_text("not valid json{{{", encoding="utf-8")

        sessions = await list_sessions()
        assert len(sessions) == 1
        assert sessions[0].id == session.id

    @pytest.mark.asyncio
    async def test_returns_empty_array_when_no_sessions_exist(self) -> None:
        sessions = await list_sessions()
        assert sessions == []
