"""Tests for quote selector."""

import pytest

from nietzschian_debugger.quotes.selector import (
    detect_context,
    select_quote,
    select_closing_quote,
)


class TestDetectContext:
    def test_detects_avoidance_from_just_tell_me(self) -> None:
        assert detect_context("just tell me the answer") == "avoidance"

    def test_detects_avoidance_from_cant_you_just(self) -> None:
        assert detect_context("can't you just fix it") == "avoidance"

    def test_detects_avoidance_from_whats_the_fix(self) -> None:
        assert detect_context("what's the fix") == "avoidance"

    def test_detects_avoidance_from_skip(self) -> None:
        assert detect_context("skip this question") == "avoidance"

    def test_detects_avoidance_from_whatever(self) -> None:
        assert detect_context("whatever, move on") == "avoidance"

    def test_detects_overwhelm_from_i_dont_know(self) -> None:
        assert detect_context("I don't know") == "overwhelm"

    def test_detects_overwhelm_from_im_lost(self) -> None:
        assert detect_context("I'm lost") == "overwhelm"

    def test_detects_overwhelm_from_im_stuck(self) -> None:
        assert detect_context("I'm stuck on this") == "overwhelm"

    def test_detects_overwhelm_from_no_idea(self) -> None:
        assert detect_context("I have no idea") == "overwhelm"

    def test_detects_overwhelm_from_i_cant_figure(self) -> None:
        assert detect_context("I can't figure this out") == "overwhelm"

    def test_detects_overwhelm_from_help(self) -> None:
        assert detect_context("help me understand") == "overwhelm"

    def test_detects_overwhelm_from_give_up(self) -> None:
        assert detect_context("I want to give up") == "overwhelm"

    def test_detects_strategy_from_where_do_i_start(self) -> None:
        assert detect_context("where do i start") == "strategy"

    def test_detects_strategy_from_so_many_options(self) -> None:
        assert detect_context("There are so many options") == "strategy"

    def test_detects_strategy_from_or_maybe(self) -> None:
        assert detect_context("or maybe it is the database") == "strategy"

    def test_detects_strategy_from_could_be_anything(self) -> None:
        assert detect_context("could be anything at this point") == "strategy"

    def test_returns_none_for_technical_response(self) -> None:
        assert detect_context("I checked the logs and found a timeout at line 42") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert detect_context("") is None


class TestSelectQuote:
    def test_returns_quote_for_avoidance(self) -> None:
        quote = select_quote("just tell me the answer")
        assert quote is not None
        assert quote.context == "avoidance"
        assert quote.philosopher == "Friedrich Nietzsche"

    def test_returns_quote_for_overwhelm(self) -> None:
        quote = select_quote("I don't know what to do")
        assert quote is not None
        assert quote.context == "overwhelm"
        assert quote.philosopher == "Seneca"

    def test_returns_quote_for_strategy(self) -> None:
        quote = select_quote("where should i start debugging")
        assert quote is not None
        assert quote.context == "strategy"
        assert quote.philosopher == "Sun Tzu"

    def test_returns_none_when_no_context_matches(self) -> None:
        quote = select_quote("I checked the logs and found a 500 error on line 42")
        assert quote is None


class TestSelectClosingQuote:
    def test_returns_victory_quote_for_solved(self) -> None:
        quote = select_closing_quote("solved")
        assert quote is not None
        assert quote.context == "victory"

    def test_returns_perseverance_quote_for_abandoned(self) -> None:
        quote = select_closing_quote("abandoned")
        assert quote is not None
        assert quote.context == "perseverance"
