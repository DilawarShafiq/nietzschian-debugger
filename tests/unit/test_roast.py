"""Tests for roast mode. The roast itself needs a key, but the prompt contract and
the file guards are checked here with no key."""

from __future__ import annotations

import pytest

from nietzschian_debugger.commands import roast


def test_roast_prompt_is_in_voice_and_withholds_the_fix() -> None:
    # One or two lines, a roast, never a fix and never a question.
    assert "ROAST mode" in roast.ROAST_SYSTEM
    assert "two lines" in roast.ROAST_SYSTEM.lower()
    assert "do not fix it" in roast.ROAST_SYSTEM.lower()
    assert "do not ask a question" in roast.ROAST_SYSTEM.lower()


def test_empty_file_exits_before_any_api_call(tmp_path) -> None:
    f = tmp_path / "empty.py"
    f.write_text("   \n", encoding="utf-8")
    with pytest.raises(SystemExit):
        roast.roast_command(str(f))


def test_missing_file_exits(tmp_path) -> None:
    with pytest.raises(SystemExit):
        roast.roast_command(str(tmp_path / "nope.py"))
