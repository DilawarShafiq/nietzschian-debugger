"""Adaptive-lens state: read the developer's state each turn, pick the lens.

Three developer states map to three lenses; Nietzsche (avoiding) is home. The
model emits an explicit ``[state: ...]`` tag each turn; this module parses it and
applies hysteresis, so the lens shifts only on sustained or strong evidence --
it reads you without flip-flopping, and the judgment stays visible (auditable).
"""

from __future__ import annotations

import re
from typing import Optional

# developer state -> lens (persona key)
STATE_TO_LENS = {
    "confused": "socrates",
    "avoiding": "nietzsche",
    "defeated": "zarathustra",
}
HOME_LENS = "nietzsche"
VALID_STATES = set(STATE_TO_LENS)

# a leading tag on its own line, e.g. "[state: avoiding]"
_TAG = re.compile(
    r"^\s*[\[(]?\s*state\s*[:=]\s*(confused|avoiding|defeated)\s*[\])]?\s*",
    re.IGNORECASE,
)

# Weak models sometimes echo an option's DESCRIPTION instead of emitting the tag.
# Map the tell-tale phrases back to a state so we can strip the junk line AND
# still read the signal, rather than leaking prompt text into the question.
_DESC_TO_STATE = [
    ("know what they mean", "confused"),
    ("vague", "confused"),
    ("hiding in an assumption", "avoiding"),
    ("an assumption or comfort", "avoiding"),
    ("comfort they", "avoiding"),
    ("ready to give up", "defeated"),
    ("ready to quit", "defeated"),
    ("give up", "defeated"),
]


def parse_state_tag(text: str) -> tuple[Optional[str], str]:
    """Extract and strip a leading state tag; return (state_or_None, clean_text).

    Handles the clean tag (``[state: X]``, ``STATE: X``, ``(state=X)``) and, for a
    weak model that echoes an option's description instead, strips that leading
    junk line and infers the state from it. Never leaks the tag/preamble into the
    displayed question.
    """
    match = _TAG.match(text)
    if match:
        return match.group(1).lower(), text[match.end():].lstrip("\n ")

    # Robustness: a first line that echoes a description (dash/bracket-led, no '?').
    parts = text.split("\n", 1)
    first = parts[0].strip()
    rest = parts[1].lstrip("\n ") if len(parts) > 1 else ""
    low = first.lower()
    looks_meta = (first[:1] in ("—", "-", "[", "(") or low.startswith("state")) and "?" not in first
    if looks_meta and rest.strip():
        for needle, state in _DESC_TO_STATE:
            if needle in low:
                return state, rest
    return None, text


class LensTracker:
    """Choose the current lens with hysteresis.

    - ``forced``: if set, that lens is always used (manual ``--lens``), and reads
      are ignored.
    - adaptive: start at HOME (nietzsche). Move to a non-home lens only when the
      last two reads agree on it (sustained). Return to home on a single home
      read. A strong signal (e.g. the developer typing "I give up") switches
      immediately.
    """

    def __init__(self, forced: Optional[str] = None) -> None:
        self.forced = forced
        self.current = forced or HOME_LENS
        self._recent: list[str] = []

    @property
    def lens(self) -> str:
        return self.current

    def observe(self, state: Optional[str], strong: bool = False) -> None:
        if self.forced or state is None or state not in VALID_STATES:
            return
        self._recent.append(state)
        self._recent = self._recent[-3:]
        target = STATE_TO_LENS[state]
        if strong:
            self.current = target
            return
        if target == HOME_LENS:
            self.current = HOME_LENS
            return
        # Move to a non-home lens only on two consecutive agreeing reads.
        if len(self._recent) >= 2 and self._recent[-1] == self._recent[-2] == state:
            self.current = target
