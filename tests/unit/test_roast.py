"""Tests for roast mode. The roast itself needs a key, but the prompt contract and
the file guards are checked here with no key."""

from __future__ import annotations

import pytest

from nietzschian_debugger.commands import roast


def test_roast_prompt_is_in_voice_and_withholds_the_fix() -> None:
    # One or two lines, a roast, never a fix and never a question.
    assert "ROAST mode" in roast.ROAST_SYSTEM
    assert "two sentences" in roast.ROAST_SYSTEM.lower()
    assert "do not fix it" in roast.ROAST_SYSTEM.lower()
    assert "do not ask a question" in roast.ROAST_SYSTEM.lower()
    # 0.5.2: output rules forbid the structured blobs weak/code models emit.
    assert "no json" in roast.ROAST_SYSTEM.lower()


def test_empty_file_exits_before_any_api_call(tmp_path) -> None:
    f = tmp_path / "empty.py"
    f.write_text("   \n", encoding="utf-8")
    with pytest.raises(SystemExit):
        roast.roast_command(str(f))


def test_missing_file_exits(tmp_path) -> None:
    with pytest.raises(SystemExit):
        roast.roast_command(str(tmp_path / "nope.py"))


def test_clean_roast_strips_markdown_bold_litter() -> None:
    # A real qwen2.5-coder:7b roast sprayed **bold** into a terminal that can't
    # render it. Scrub the markers but keep every word.
    ugly = "**WRONG.** The **`except:`** clause is a **swallowhole**, choking the truth."
    clean = roast._clean_roast(ugly)
    assert "**" not in clean
    assert "WRONG." in clean and "swallowhole" in clean


def test_clean_roast_caps_at_two_sentences() -> None:
    four = "First cut. Second cut. Third cut. Fourth cut."
    clean = roast._clean_roast(four)
    assert clean == "First cut. Second cut."


def test_clean_roast_leaves_dunder_names_intact() -> None:
    # __init__ is a name, not bold — don't eat its underscores.
    assert "__init__" in roast._clean_roast("Your __init__ does nothing honest.")


def test_looks_structured_catches_predict_style_and_json() -> None:
    # The exact thing qwen2.5-coder:7b did: answer a roast with a DARE/CALL blob.
    assert roast._looks_structured('DARE: what does f() return?\nCALL: {"function": "len", "args": [""]}')
    assert roast._looks_structured('{"function": "x", "args": []}')
    assert roast._looks_structured("```json\n{}\n```")
    # A real roast is prose — not structured.
    assert not roast._looks_structured("Your helper is a euphemism for a vague crutch.")
