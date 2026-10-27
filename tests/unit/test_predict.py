"""Tests for predict mode (structure; the live LLM round needs a key/live test)."""

from __future__ import annotations

import pytest

from nietzschian_debugger.commands import predict


def test_prompts_are_in_voice_and_withhold_the_answer() -> None:
    assert "PREDICT mode" in predict.DARE_SYSTEM
    assert "PREDICT mode" in predict.JUDGE_SYSTEM
    # The dare must never reveal the answer.
    assert "NEVER reveal" in predict.DARE_SYSTEM


def test_empty_file_exits_before_any_api_call(tmp_path) -> None:
    f = tmp_path / "empty.py"
    f.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit):
        predict.predict_command(str(f))


def test_missing_file_exits(tmp_path) -> None:
    with pytest.raises(SystemExit):
        predict.predict_command(str(tmp_path / "does_not_exist.py"))
