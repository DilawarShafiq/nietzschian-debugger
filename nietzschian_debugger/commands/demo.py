"""A scripted demo session -- lets anyone feel the tool with no API key.

No network, no cost: the questions and replies are canned. It exists so a
first-time visitor can run `nietzschian demo` and be interrogated in five
seconds, instead of bouncing off the "get an API key first" wall.
"""

from __future__ import annotations

import time

from ..ui.renderer import console, display_dim, display_session_header, new_line

PROBLEM = (
    "login endpoint returns 403, but only for users who signed up before last "
    "week; new signups work; same code path; Node/Express"
)

# (the tool's question, the developer's scripted reply)
SCRIPT: list[tuple[str, str]] = [
    (
        '"Same code path" -- you said that like it absolves you of the walk\n'
        "itself. Have you actually traced a failed old-account login through your\n"
        'auth middleware and database query, line by line, or does "same" merely\n'
        "comfort you that the difference must be elsewhere?",
        "no, I haven't traced it",
    ),
    (
        "Good -- you name the avoidance honestly. What changed in your database\n"
        "between last week and now -- not in your code, in the records themselves?",
        "nothing changed in the code",
    ),
    (
        "Then the bug arrived without a cause -- code rewrote itself, databases\n"
        "mutated on their own. What field exists on old accounts that the new\n"
        "ones were never given?",
        "...old accounts carry a legacy role claim the new ones don't",
    ),
    (
        'There it is. The idol that rang hollow was "same code path" -- it was\n'
        "never the path that differed, it was the cargo the old accounts carried\n"
        "down it. Does that legacy role still serve a purpose, or can it die?",
        "found it",
    ),
]

_PROFILE = (
    "┣ Assumption-checking    ████████░░  strong\n"
    "┣ Evidence-gathering     ██████░░░░  moderate\n"
    "┗ Root cause speed       ███████░░░  strong"
)


def _pause(seconds: float) -> None:
    try:
        time.sleep(seconds)
    except Exception:
        pass


def run_demo() -> None:
    """Replay the canned interrogation -- no API key, no cost, no network."""
    console.print("[dim](demo: a scripted session -- no API key, no cost)[/dim]")
    display_session_header("nietzsche")
    console.print(f"[bold]> [/bold]{PROBLEM}")

    for i, (question, reply) in enumerate(SCRIPT, start=1):
        _pause(0.8)
        new_line()
        display_dim(f"[Turn {i}]")
        print(question)
        new_line()
        _pause(0.6)
        console.print(f"[bold]> [/bold]{reply}")

    _pause(0.8)
    new_line()
    console.print("[bold]Session Complete -- 4 questions to root cause (Solved)[/bold]")
    new_line()
    console.print("[bold]Your Debugging Profile:[/bold]")
    print(_PROFILE)
    new_line()
    console.print('[dim]"No victor believes in chance."[/dim]')
    console.print("[dim] -- Friedrich Nietzsche[/dim]")
    new_line()
    console.print(
        "[dim]That was a demo. Now bring your own bug:[/dim]\n"
        '  [bold]nietzschian debug "your bug"[/bold]'
    )
