"""Tests for predict mode. The LLM dare/verdict needs a key, but the part that
matters most — execution as ground truth — is tested here with no key."""

from __future__ import annotations

import pytest

from nietzschian_debugger.commands import predict


def test_prompts_are_in_voice_and_withhold_the_answer() -> None:
    assert "PREDICT mode" in predict.DARE_SYSTEM
    assert "PREDICT mode" in predict.JUDGE_SYSTEM
    assert "never reveal" in predict.DARE_SYSTEM.lower()
    # The judge must trust the executed result, not its own reasoning.
    assert "truth" in predict.JUDGE_SYSTEM.lower()


def test_empty_file_exits_before_any_api_call(tmp_path) -> None:
    f = tmp_path / "empty.py"
    f.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit):
        predict.predict_command(str(f))


def test_missing_file_exits(tmp_path) -> None:
    with pytest.raises(SystemExit):
        predict.predict_command(str(tmp_path / "does_not_exist.py"))


def test_module_spec_for_package_file() -> None:
    _syspath, module = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    assert module == "nietzschian_debugger.core.lens_state"


def test_parse_dare_extracts_call_and_cleans_the_dare() -> None:
    text = 'DARE: You think you know it? what does f(0) return?\nCALL: {"function": "f", "args": [0]}'
    dare, call = predict._parse_dare(text)
    assert call == {"function": "f", "args": [0]}
    assert "what does f(0) return" in dare
    assert "CALL" not in dare and "DARE:" not in dare


def test_execution_is_ground_truth() -> None:
    # This is the whole point: the reasoning-only prototype said the answer was
    # ('avoiding', ' ') — a space. RUNNING the code gives the real answer. No model,
    # no guessing, no fooling yourself.
    syspath, module = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    out = predict.execute_call(syspath, module, "parse_state_tag", ["[STATE: AVOIDING] "])
    assert out["stage"] == "ran"
    assert out["returned"] == "('avoiding', '')"


def test_guard_rejects_methods_and_accepts_functions() -> None:
    # The 7B dared with `observe` — a METHOD of LensTracker, not runnable alone.
    # The guard must reject it and accept a real top-level function.
    syspath, module = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    assert predict.is_callable_top_level(syspath, module, "parse_state_tag") is True
    assert predict.is_callable_top_level(syspath, module, "observe") is False


def test_parse_dare_strips_label_even_after_a_preamble() -> None:
    # Regression: the 7B wrote a gleeful line BEFORE "DARE:", so the label wasn't
    # leading and leaked into the question.
    text = 'I bet you a golden coin!\n\nDARE: what does f() return?\nCALL: {"function": "f", "args": []}'
    dare, call = predict._parse_dare(text)
    assert call == {"function": "f", "args": []}
    assert "DARE:" not in dare
    assert "golden coin" in dare and "what does f() return" in dare


def test_parse_match_tag() -> None:
    correct, verdict = predict._parse_match("MATCH: no\n\nWrong — you skipped the early return.")
    assert correct is False
    assert verdict.startswith("Wrong")
    correct, _ = predict._parse_match("MATCH: yes\nRight, and it was easy.")
    assert correct is True
    correct, text = predict._parse_match("no tag at all?")
    assert correct is None and text == "no tag at all?"


def test_execution_captures_a_raise() -> None:
    # A function that raises is a legitimate "behaviour" — captured, not crashed.
    syspath, module = predict._module_spec("nietzschian_debugger/llm/validator.py")
    out = predict.execute_call(syspath, module, "get_fallback_question", ["not-a-real-intensity"])
    assert out["stage"] == "ran"
    assert "raised" in out  # KeyError on the unknown intensity
