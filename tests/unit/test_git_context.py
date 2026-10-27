"""Tests for reading git changes as debugging context."""

from __future__ import annotations

from nietzschian_debugger.storage.git_context import get_git_diff


def test_bad_ref_returns_none() -> None:
    # A ref that cannot exist must fail gracefully, not raise.
    assert get_git_diff("definitely-not-a-ref-zzz-9999") is None


def test_returns_none_or_str() -> None:
    # Whatever the repo state, it returns None or a string -- never raises.
    result = get_git_diff()
    assert result is None or isinstance(result, str)
