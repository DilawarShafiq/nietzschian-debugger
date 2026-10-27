"""Tests for terminal rendering — guarding the error path that crashed in 0.2.3."""

from __future__ import annotations

from nietzschian_debugger.ui import renderer


class TestErrorOutput:
    def test_display_error_does_not_raise(self) -> None:
        # Regression: display_error passed stderr=True to Rich's Console.print(),
        # which raised TypeError and crashed EVERY error path (invalid key, rate
        # limit, the session-error handler). It must render, not crash.
        renderer.display_error("Invalid API key. Check your ANTHROPIC_API_KEY.")

    def test_display_warning_does_not_raise(self) -> None:
        renderer.display_warning("heads up, something looks off")

    def test_error_console_targets_stderr(self) -> None:
        assert renderer.error_console.stderr is True
