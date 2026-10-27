"""Export a finished session as shareable markdown.

The tool's sessions are screenshot-bait by design -- this makes them one command
to post. Reads a saved session from .nietzschian/sessions/ and prints clean
markdown (or writes it to a file).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..storage.session_store import list_sessions, load_session
from ..types import Session
from ..ui.renderer import console, display_error

_FILLED = "█"
_EMPTY = "░"


def _bar(score: int) -> str:
    n = max(1, min(10, round(score)))
    return _FILLED * n + _EMPTY * (10 - n)


def _label(score: int) -> str:
    if score >= 8:
        return "strong"
    if score >= 5:
        return "moderate"
    return "weak"


def format_session_markdown(session: Session) -> str:
    """Render a saved session as a self-contained markdown block."""
    out: list[str] = []
    out.append(f"## Nietzschian Debugger — {session.intensity} mode")
    out.append("")
    out.append(f"**The bug:** {session.problem_description}")
    out.append("")

    for turn in session.transcript:
        out.append(f"**[Turn {turn.turn_number}]**")
        out.append("")
        out.append(turn.question)
        out.append("")
        # Skip control markers like [solved] / [exited]; show real replies.
        if turn.response and not turn.response.startswith("["):
            for line in turn.response.splitlines() or [""]:
                out.append(f"> {line}")
            out.append("")

    outcome = "Solved" if session.outcome == "solved" else "Abandoned"
    out.append(
        f"**Session Complete — {session.questions_to_root_cause} "
        f"questions to root cause ({outcome})**"
    )
    out.append("")
    s = session.skill_scores
    out.append("```")
    out.append(f"Assumption-checking  {_bar(s.assumption_checking)}  {_label(s.assumption_checking)}")
    out.append(f"Evidence-gathering   {_bar(s.evidence_gathering)}  {_label(s.evidence_gathering)}")
    out.append(f"Root cause speed     {_bar(s.root_cause_speed)}  {_label(s.root_cause_speed)}")
    out.append("```")
    out.append("")
    out.append(
        "— [Nietzschian Debugger](https://github.com/DilawarShafiq/nietzschian-debugger) "
        "· `pip install nietzschian-debugger`"
    )
    return "\n".join(out)


async def share_session(session_id: Optional[str] = None, out_path: Optional[str] = None) -> None:
    """Share one saved session: the given id, or the most recent."""
    if session_id:
        session = await load_session(session_id)
    else:
        sessions = await list_sessions()
        session = max(
            sessions, key=lambda s: s.end_timestamp or s.timestamp or ""
        ) if sessions else None

    if session is None:
        display_error("No session found to share. Run a debug session first.")
        return

    markdown = format_session_markdown(session)
    if out_path:
        Path(out_path).write_text(markdown, encoding="utf-8")
        console.print(f"[green]Saved session to {out_path}[/green]")
    else:
        print(markdown)
