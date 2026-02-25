"""Tests for system prompt construction."""

import pytest

from nietzschian_debugger.llm.prompts import get_system_prompt


class TestGetSystemPrompt:
    def test_produces_prompt_for_socrates(self) -> None:
        prompt = get_system_prompt("socrates", "My API is slow")
        assert "SOCRATES" in prompt
        assert "<persona>" in prompt
        assert "<behavioral_constraints>" in prompt
        assert "<intensity_rules>" in prompt
        assert "<session_context>" in prompt
        assert "My API is slow" in prompt
        assert "gentle" in prompt

    def test_produces_prompt_for_nietzsche(self) -> None:
        prompt = get_system_prompt("nietzsche", "My API is slow")
        assert "NIETZSCHE" in prompt
        assert "<persona>" in prompt
        assert "<behavioral_constraints>" in prompt
        assert "<intensity_rules>" in prompt
        assert "confrontational" in prompt

    def test_produces_prompt_for_zarathustra(self) -> None:
        prompt = get_system_prompt("zarathustra", "My API is slow")
        assert "ZARATHUSTRA" in prompt
        assert "<persona>" in prompt
        assert "<behavioral_constraints>" in prompt
        assert "<intensity_rules>" in prompt
        assert "brutal" in prompt

    def test_includes_code_context_when_provided(self) -> None:
        prompt = get_system_prompt("nietzsche", "Bug here", "1: const x = 1;\n2: const y = x + 1;")
        assert "<code_context>" in prompt
        assert "const x = 1" in prompt

    def test_omits_code_context_when_not_provided(self) -> None:
        prompt = get_system_prompt("nietzsche", "Bug here")
        assert "<code_context>" not in prompt

    def test_includes_rolling_summary_when_provided(self) -> None:
        prompt = get_system_prompt(
            "nietzsche",
            "Bug here",
            None,
            "Developer checked logs and found timeout error.",
        )
        assert "Developer checked logs" in prompt

    def test_includes_turn_number(self) -> None:
        prompt = get_system_prompt("nietzsche", "Bug here", None, None, 5)
        assert "Turn: 5" in prompt

    def test_defaults_to_turn_one(self) -> None:
        prompt = get_system_prompt("nietzsche", "Bug here")
        assert "Turn: 1" in prompt

    def test_includes_suggested_quote_when_provided(self) -> None:
        prompt = get_system_prompt(
            "nietzsche",
            "Bug here",
            None,
            None,
            1,
            "What does not kill me makes me stronger.",
        )
        assert "<suggested_quote>" in prompt
        assert "What does not kill me makes me stronger." in prompt

    def test_omits_suggested_quote_when_not_provided(self) -> None:
        prompt = get_system_prompt("nietzsche", "Bug here")
        assert "<suggested_quote>" not in prompt

    def test_contains_behavioral_constraints_for_all_intensities(self) -> None:
        for intensity in ("socrates", "nietzsche", "zarathustra"):
            prompt = get_system_prompt(intensity, "test")  # type: ignore[arg-type]
            assert "NEVER provide solutions" in prompt
            assert "Every response MUST contain at least one question" in prompt

    def test_produces_distinct_prompts_for_each_intensity(self) -> None:
        s = get_system_prompt("socrates", "test")
        n = get_system_prompt("nietzsche", "test")
        z = get_system_prompt("zarathustra", "test")
        assert s != n
        assert n != z
        assert s != z
