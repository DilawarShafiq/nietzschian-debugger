"""`roast` mode — one or two lines of Nietzschian contempt for your code.

No session, no questions, no fix. You point it at a file; it reads the code's
cowardice and laughs. "Not by wrath does one kill, but by laughter." A roast is
an aphorism written in blood — it belongs to this tool as much as the question
does.
"""

from __future__ import annotations

import sys

from ..llm.client import call_llm, get_client, get_conversation_model, MissingApiKeyError
from ..ui.renderer import console, display_api_key_help, display_error

_MAX_CODE_CHARS = 12000

ROAST_SYSTEM = (
    "You are the Nietzschian Debugger in ROAST mode, in Nietzsche's voice. You are "
    "shown a file of code. Deliver a ROAST: ONE or TWO lines, never more.\n\n"
    "Seize something SPECIFIC and real in the code and hold it up to the light — the "
    "bare `except:` that swallows every truth, the TODO fossilised from years ago, the "
    "function named `helper` or `util` that dares not say what it does, the mutable "
    "default, the nested ternary, the block commented-out 'just in case', the variable "
    "named `data`, `temp`, `x2`. Name THAT thing — never a generic jab that would fit "
    "any file.\n\n"
    "You do NOT fix it. You do NOT ask a question. You judge its character and you "
    "laugh — aphoristic, metaphoric, merciless, and funny. 'Not by wrath does one "
    "kill, but by laughter.' Roast the CODE and the comfort it was written from, never "
    "the person. End on a line that stings and grins. Two lines maximum. No preamble, "
    "no 'here is your roast', no quotation marks around the whole thing."
)


def roast_command(file_path: str) -> None:
    """Read a file and print one or two lines of Nietzschian roast. One shot, no session."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            code = handle.read()
    except OSError as error:
        display_error(f"Could not read {file_path}: {error}")
        sys.exit(2)
    if not code.strip():
        display_error(f"{file_path} is empty — there is nothing here to despise. Even that is an achievement.")
        sys.exit(2)

    from ..llm import providers

    if providers.active() is None:
        try:
            get_client()
        except MissingApiKeyError:
            display_api_key_help()
            sys.exit(1)

    model = get_conversation_model()
    try:
        roast = call_llm(
            ROAST_SYSTEM,
            [{"role": "user", "content": f"The file ({file_path}):\n\n{code[:_MAX_CODE_CHARS]}"}],
            model,
        )
    except Exception as error:
        display_error(f"roast ended unexpectedly: {error}")
        sys.exit(1)

    console.print("\n[bold red]🔥 Nietzschian Roast[/bold red]\n")
    print(roast.strip().strip('"'))
    console.print()
