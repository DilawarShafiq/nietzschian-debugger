"""Tests for adaptive-lens state detection and hysteresis."""

from __future__ import annotations

from nietzschian_debugger.core.lens_state import LensTracker, parse_state_tag


class TestParseStateTag:
    def test_parses_and_strips_tag(self) -> None:
        state, clean = parse_state_tag("[state: avoiding]\nWhy do you trust that?")
        assert state == "avoiding"
        assert clean.strip() == "Why do you trust that?"

    def test_no_tag_returns_none_and_original(self) -> None:
        state, clean = parse_state_tag("Just a plain question?")
        assert state is None
        assert clean == "Just a plain question?"

    def test_tag_is_case_insensitive(self) -> None:
        state, _ = parse_state_tag("[STATE: Defeated] keep going?")
        assert state == "defeated"


class TestLensTracker:
    def test_default_home_is_nietzsche(self) -> None:
        assert LensTracker().lens == "nietzsche"

    def test_forced_lens_never_changes(self) -> None:
        t = LensTracker(forced="zarathustra")
        t.observe("confused")
        t.observe("confused")
        assert t.lens == "zarathustra"

    def test_hysteresis_requires_two_agreeing_reads(self) -> None:
        t = LensTracker()
        t.observe("confused")          # one read -> no switch yet
        assert t.lens == "nietzsche"
        t.observe("confused")          # two agreeing -> switch
        assert t.lens == "socrates"

    def test_returns_home_on_single_home_read(self) -> None:
        t = LensTracker()
        t.observe("confused")
        t.observe("confused")
        assert t.lens == "socrates"
        t.observe("avoiding")          # home read -> back home immediately
        assert t.lens == "nietzsche"

    def test_strong_signal_switches_immediately(self) -> None:
        t = LensTracker()
        t.observe("defeated", strong=True)
        assert t.lens == "zarathustra"

    def test_unknown_state_is_ignored(self) -> None:
        t = LensTracker()
        t.observe("gibberish")
        assert t.lens == "nietzsche"
