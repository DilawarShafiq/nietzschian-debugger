"""`roast` mode — one or two lines of Nietzschian contempt for your code.

No session, no questions, no fix. You point it at a file; it reads the code's
cowardice and laughs. "Not by wrath does one kill, but by laughter." A roast is
an aphorism written in blood — it belongs to this tool as much as the question
does.
"""

from __future__ import annotations

import re
import sys

from ..llm.client import call_llm, get_client, get_conversation_model, MissingApiKeyError
from ..ui.renderer import console, display_api_key_help, display_error, thinking

_MAX_CODE_CHARS = 12000


def _clean_roast(text: str) -> str:
    """Scrub a weak model's output into clean terminal prose.

    Small local models spray markdown bold (**like this**) that a terminal can't
    render, and ramble past the one-or-two-line promise. Strip a wrapping code
    fence, drop bold/italic markers, collapse blank lines, and keep at most the
    first two sentences so the roast lands and stops.
    """
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z]*\s*\n?", "", t)
    t = re.sub(r"\n?```\s*$", "", t)
    # Collapse **bold** / *italic* pairs to their contents, then remove any
    # orphaned marker a model left unbalanced. (Leave __dunder__ names alone.)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.DOTALL)
    t = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", t, flags=re.DOTALL)
    t = t.replace("**", "")
    t = re.sub(r"[ \t]*\n[ \t\n]*", " ", t).strip()  # one flowing line
    # Split on sentence end, allowing a closing quote between the period and the
    # space (…care." "Helper…) so a quoted sentence still counts as a boundary —
    # but NOT after a merely quoted word like "helper" that ends no sentence.
    parts = re.split(r"(?<=[.!?])[\"”’']?\s+", t)
    if len(parts) > 2:
        t = " ".join(parts[:2]).strip()
    return t

ROAST_SYSTEM = (
    "You are the Nietzschian Debugger in ROAST mode, in Nietzsche's voice. You are "
    "shown a file of code. Deliver a ROAST: ONE or TWO sentences of plain prose, "
    "never more.\n\n"
    "Seize something SPECIFIC and real in the code and hold it up to the light — the "
    "bare `except:` that swallows every truth, the TODO fossilised from years ago, the "
    "function named `helper` or `util` that dares not say what it does, the mutable "
    "default, the nested ternary, the block commented-out 'just in case', the variable "
    "named `data`, `temp`, `x2`. Name THAT thing — never a generic jab that would fit "
    "any file.\n\n"
    "You do NOT fix it. You do NOT ask a question. You judge its character and you "
    "laugh — aphoristic, metaphoric, merciless, and funny. 'Not by wrath does one "
    "kill, but by laughter.' Roast the CODE and the comfort it was written from, never "
    "the person. End on a line that stings and grins.\n\n"
    "OUTPUT RULES (obey exactly): plain prose only. No question marks. No JSON, no "
    "function call, no 'DARE:' or 'CALL:' labels, no code block, no markdown, no "
    "bullet points, no preamble like 'here is your roast', no surrounding quotes. Just "
    "the one or two sentences."
)

# Weak/code models sometimes answer a roast with a predict-style function call or a
# JSON blob instead of prose. Detect that so we can retry for real contempt.
_STRUCTURED = re.compile(r'(DARE:|CALL:|```|"function"\s*:|^\s*\{)', re.IGNORECASE | re.MULTILINE)


def _looks_structured(text: str) -> bool:
    return bool(_STRUCTURED.search(text))


def _ask_roast(code: str, file_path: str, model: str, firm: bool = False) -> str:
    """One roast attempt, with the spinner. `firm` adds a sterner anti-structure nudge."""
    system = ROAST_SYSTEM
    if firm:
        system += (
            "\n\nYour last answer broke the rules. Reply with ONLY one or two plain "
            "English sentences roasting the code. Nothing else — no JSON, no labels, "
            "no questions."
        )
    with thinking():
        raw = call_llm(
            system,
            [{"role": "user", "content": f"The file ({file_path}):\n\n{code[:_MAX_CODE_CHARS]}"}],
            model,
        )
    return raw


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
        roast = _clean_roast(_ask_roast(code, file_path, model))
        # A weak or code-tuned model may answer empty, or with a JSON/DARE blob.
        # Give it exactly one firmer chance before we settle for a terse fallback.
        if not roast or _looks_structured(roast):
            roast = _clean_roast(_ask_roast(code, file_path, model, firm=True))
        if not roast or _looks_structured(roast):
            roast = "Even your code's cowardice cannot hold a shape — this model choked on contempt. Try a general chat model (e.g. ollama:llama3.1); coding models reach for JSON, not wit."
    except Exception as error:
        display_error(f"roast ended unexpectedly: {error}")
        sys.exit(1)

    console.print("\n[bold red]🔥 Nietzschian Roast[/bold red]\n")
    print(roast.strip('"'))
    console.print()
