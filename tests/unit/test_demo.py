"""Tests for the no-key demo session."""

from __future__ import annotations

from nietzschian_debugger.commands import demo


def test_demo_script_is_well_formed() -> None:
    assert demo.PROBLEM
    assert len(demo.SCRIPT) >= 3
    for question, reply in demo.SCRIPT:
        # Every turn ends on exactly one question -- the demo must obey the same
        # discipline the real tool enforces.
        assert question.count("?") == 1
        assert reply


def test_run_demo_does_not_raise(monkeypatch) -> None:
    # No network, no key, and no real pauses during the test.
    monkeypatch.setattr(demo.time, "sleep", lambda *_: None)
    demo.run_demo()
