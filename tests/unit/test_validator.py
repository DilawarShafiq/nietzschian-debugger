"""Tests for response validator."""

import pytest

from nietzschian_debugger.llm.validator import validate_response, get_fallback_question


class TestValidateResponse:
    def test_passes_response_with_question_mark(self) -> None:
        result = validate_response("Have you checked the logs?")
        assert result.valid is True

    def test_fails_response_with_no_question_mark(self) -> None:
        result = validate_response("The problem is in your auth middleware.")
        assert result.valid is False
        assert "no question" in (result.reason or "")

    def test_fails_the_fix_is_pattern(self) -> None:
        result = validate_response("The fix is to change the timeout. Do you see?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_you_should_change_pattern(self) -> None:
        result = validate_response("You should change the port. What do you think?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_try_doing_pattern(self) -> None:
        result = validate_response("Try doing a restart. Would that help?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_heres_the_fix_pattern(self) -> None:
        result = validate_response("Here's the fix -- does it look right?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_the_solution_is_pattern(self) -> None:
        result = validate_response("The solution is clear. Can you see it?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_just_change_pattern(self) -> None:
        result = validate_response("Just change the import path. Agreed?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_you_need_to_change_pattern(self) -> None:
        result = validate_response("You need to change line 42. Right?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_to_fix_this_pattern(self) -> None:
        result = validate_response("To fix this, update config. Okay?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_try_changing_pattern(self) -> None:
        result = validate_response("Try changing the env variable. Sound good?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_try_replacing_pattern(self) -> None:
        result = validate_response("Try replacing the function. Would that work?")
        assert result.valid is False
        assert "answer pattern" in (result.reason or "")

    def test_fails_code_fix_block(self) -> None:
        response = "Look at this:\n```js\n// fix: change timeout\nsetTimeout(cb, 1000)\n```\nDoes this help?"
        result = validate_response(response)
        assert result.valid is False
        assert "code fix" in (result.reason or "")

    def test_passes_pure_question(self) -> None:
        result = validate_response(
            "What does the error message say when you run the test? Have you looked at the stack trace?"
        )
        assert result.valid is True

    def test_passes_question_mentioning_code_without_fix(self) -> None:
        result = validate_response(
            "I see you have a `setTimeout` on line 42. What value is the delay parameter set to?"
        )
        assert result.valid is True

    def test_passes_challenging_question_about_code(self) -> None:
        result = validate_response(
            "What evidence do you have that the database connection is the bottleneck? Have you actually measured it?"
        )
        assert result.valid is True


class TestGetFallbackQuestion:
    def test_returns_string_for_socrates(self) -> None:
        q = get_fallback_question("socrates")
        assert isinstance(q, str)
        assert len(q) > 0
        assert "?" in q

    def test_returns_string_for_nietzsche(self) -> None:
        q = get_fallback_question("nietzsche")
        assert isinstance(q, str)
        assert len(q) > 0
        assert "?" in q

    def test_returns_string_for_zarathustra(self) -> None:
        q = get_fallback_question("zarathustra")
        assert isinstance(q, str)
        assert len(q) > 0
        assert "?" in q
