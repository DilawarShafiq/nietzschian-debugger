"""Quote selection based on developer response context."""

from __future__ import annotations

import random
import re
from typing import Optional

from ..types import Quote, QuoteContext, SessionOutcome
from .corpus import QUOTES

AVOIDANCE_PATTERNS = [
    re.compile(r"\bi don'?t (?:want to|care|think)\b", re.IGNORECASE),
    re.compile(r"\bcan'?t you just\b", re.IGNORECASE),
    re.compile(r"\bjust tell me\b", re.IGNORECASE),
    re.compile(r"\bwhat'?s the (?:fix|answer|solution)\b", re.IGNORECASE),
    re.compile(r"\bi'?m not sure (?:why|how)\b", re.IGNORECASE),
    re.compile(r"\bthat'?s not (?:relevant|important)\b", re.IGNORECASE),
    re.compile(r"\bskip\b", re.IGNORECASE),
    re.compile(r"\bwhatever\b", re.IGNORECASE),
]

OVERWHELM_PATTERNS = [
    re.compile(r"\bi don'?t know\b", re.IGNORECASE),
    re.compile(r"\bi'?m (?:lost|confused|stuck|overwhelmed)\b", re.IGNORECASE),
    re.compile(r"\bno idea\b", re.IGNORECASE),
    re.compile(r"\bthis is too\b", re.IGNORECASE),
    re.compile(r"\bi can'?t figure\b", re.IGNORECASE),
    re.compile(r"\bhelp\b", re.IGNORECASE),
    re.compile(r"\bi'?m not getting\b", re.IGNORECASE),
    re.compile(r"\bgive up\b", re.IGNORECASE),
]

STRATEGY_PATTERNS = [
    re.compile(r"\bwhere (?:do i|should i) start\b", re.IGNORECASE),
    re.compile(r"\bso many (?:things|options|possibilities)\b", re.IGNORECASE),
    re.compile(r"\bmaybe (?:it'?s|i should)\b", re.IGNORECASE),
    re.compile(r"\bor maybe\b", re.IGNORECASE),
    re.compile(r"\bcould be (?:this|that|anything)\b", re.IGNORECASE),
    re.compile(r"\bnot sure which\b", re.IGNORECASE),
]


def detect_context(response: str) -> Optional[QuoteContext]:
    """Detect the emotional context of a developer response."""
    for pattern in AVOIDANCE_PATTERNS:
        if pattern.search(response):
            return "avoidance"
    for pattern in OVERWHELM_PATTERNS:
        if pattern.search(response):
            return "overwhelm"
    for pattern in STRATEGY_PATTERNS:
        if pattern.search(response):
            return "strategy"
    return None


def select_quote(response: str) -> Optional[Quote]:
    """Select a contextually appropriate quote based on the developer response."""
    context = detect_context(response)
    if context is None:
        return None

    matching = [q for q in QUOTES if q.context == context]
    if not matching:
        return None

    return random.choice(matching)


def select_closing_quote(outcome: SessionOutcome) -> Quote:
    """Select a closing quote based on session outcome."""
    context: QuoteContext = "victory" if outcome == "solved" else "perseverance"
    matching = [q for q in QUOTES if q.context == context]
    return random.choice(matching)
