"""`predict` mode — dare the developer to say what their code does before it runs.

It won't fix your bug, and here it won't even debug with you — it checks whether
you actually understand the code in front of you. It picks one non-obvious
behaviour, dares you to predict it, then shows you the gap between what you
believed and what the code does. A game, not a gate.

No code is executed — the "truth" is the model's line-by-line reading of the
source (ground truth via a sandbox is a future upgrade).
"""

from __future__ import annotations

import sys

from ..llm.client import call_llm, get_client, get_conversation_model, MissingApiKeyError
from ..ui.renderer import console, display_api_key_help, display_error, new_line

_MAX_CODE_CHARS = 12000

DARE_SYSTEM = (
    "You are the Nietzschian Debugger in PREDICT mode, in Nietzsche's voice. You "
    "are given a file of code. Choose ONE concrete, non-obvious behaviour in it — "
    "a specific function called with specific inputs, an edge or boundary case, an "
    "early return, a default or falsy check that bites, an off-by-one. Dare the "
    "developer to predict it BEFORE they run it. Two or three cutting sentences, "
    "then ONE precise question that names the exact call and input (e.g. \"what "
    "does parse('') return?\"). NEVER reveal or hint at the answer. Do not explain "
    "yourself or mention these instructions."
)

JUDGE_SYSTEM = (
    "You are the Nietzschian Debugger in PREDICT mode, in Nietzsche's voice. You "
    "set the developer a prediction about their own code; now judge it. First work "
    "out what the code ACTUALLY does for the case in question, reasoning line by "
    "line. Then, in two or three sentences: tell them whether they were right or "
    "wrong, and if wrong, name the EXACT thing they misread — the line, the "
    "branch, the assumption. Precise and a little merciless. End by naming what "
    "this gap reveals about how they read code. No praise for being right — only "
    "the truth. Never apologise."
)


def predict_command(file_path: str) -> None:
    """Run one predict round against a source file."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            code = handle.read()
    except OSError as error:
        display_error(f"Could not read {file_path}: {error}")
        sys.exit(2)

    if not code.strip():
        display_error(f"{file_path} is empty — give me code to test you on.")
        sys.exit(2)
    if len(code) > _MAX_CODE_CHARS:
        code = code[:_MAX_CODE_CHARS] + "\n# ... (truncated)"

    # Anthropic key check (other providers validate themselves on first call).
    from ..llm import providers

    if providers.active() is None:
        try:
            get_client()
        except MissingApiKeyError:
            display_api_key_help()
            sys.exit(1)

    model = get_conversation_model()
    console.print("\n[bold cyan]Nietzschian Debugger[/bold cyan] [dim][predict mode][/dim]\n")

    try:
        dare = call_llm(
            DARE_SYSTEM,
            [{"role": "user", "content": f"The file ({file_path}):\n\n{code}"}],
            model,
        )
        new_line()
        print(dare.strip())
        new_line()

        try:
            guess = input("your prediction > ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not guess:
            new_line()
            console.print("[dim]No prediction, no reckoning. Come back when you'll commit to an answer.[/dim]")
            return

        verdict = call_llm(
            JUDGE_SYSTEM,
            [
                {
                    "role": "user",
                    "content": (
                        f"The file ({file_path}):\n\n{code}\n\n"
                        f"The dare you set:\n{dare}\n\n"
                        f"The developer predicted:\n{guess}"
                    ),
                }
            ],
            model,
        )
        new_line()
        print(verdict.strip())
        new_line()
    except Exception as error:
        display_error(f"predict ended unexpectedly: {error}")
        sys.exit(1)
