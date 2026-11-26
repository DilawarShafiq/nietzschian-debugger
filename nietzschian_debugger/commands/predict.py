"""`predict` mode — prove you understand your code before you run it.

Several rounds: each one dares you to predict a non-obvious behaviour, then RUNS
the code for the truth (never a model guessing — that can be confidently wrong),
and names the gap between what you believed and what the code does. At the end, a
Proof-of-Understanding report names the *pattern* in your misses — not a score, a
pattern. "You keep missing early returns" is worth more than "73%".

Execution runs in a separate Python process with a timeout. It is NOT a sandbox:
the code can read your files and use the network, exactly as if you ran it
yourself. Secrets (API keys, tokens, passwords) are stripped from the child's
environment so a stray import can't read the key this tool runs on.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ..llm.client import call_llm, get_client, get_conversation_model, MissingApiKeyError
from ..ui.renderer import console, display_api_key_help, display_dim, display_error, new_line, thinking

_MAX_CODE_CHARS = 12000
_TIMEOUT_SECONDS = 5
_MAX_ROUNDS = 10

DARE_SYSTEM = (
    "You are the Nietzschian Debugger in PREDICT mode, in Nietzsche's voice. Given "
    "a file of code, choose ONE function that can be called with SIMPLE, LITERAL "
    "arguments only (strings, numbers, booleans, None, lists, dicts — no objects, "
    "no file/network I/O, no arguments you'd have to construct). Pick the call MOST "
    "LIKELY to make them wrong: a result that is counterintuitive and NOT guessable "
    "from the function's name — an edge case, empty input, a boundary, an early "
    "return, a falsy default, a surprising type. Avoid softballs whose answer is "
    "obvious.\n\n"
    "VOICE: aphoristic, metaphoric, and gleeful — you DELIGHT in the trap you lay. "
    "Never a flat quiz question ('what does f() return?'); make them feel the dare, "
    "with menace and a grin.\n\n"
    "Output EXACTLY two lines and nothing else:\n"
    "DARE: <2-3 cutting sentences in Nietzsche's voice, then one precise question "
    "naming the exact call, e.g. what does slugify('  Hi  ') return?>\n"
    "CALL: {\"function\": \"<name>\", \"args\": [<json literal args>]}\n\n"
    "The CALL line must be valid one-line JSON. Never reveal or hint at the answer."
)

JUDGE_SYSTEM = (
    "You are the Nietzschian Debugger in PREDICT mode, in Nietzsche's voice. You "
    "dared the developer to predict what their code does; the code has now been RUN "
    "and you are told the REAL result — that is the truth, trust it over any "
    "reasoning of your own.\n"
    "Your FIRST line must be exactly one of: 'MATCH: yes' (their prediction matched "
    "the real result) or 'MATCH: no' (it did not). Then a blank line, then:\n"
    "- If MATCH yes: ONE sharp line. Do NOT flatter, do NOT invent a flaw or a 'but' "
    "that isn't there. If the case was easy, say it was easy.\n"
    "- If MATCH no: two or three merciless sentences naming the EXACT thing they "
    "misread — the line, the branch, the assumption — and what the gap reveals.\n"
    "When they miss, RELISH it — wound to elevate, with a laugh, never a lecture; "
    "there is sunlight in the cut. Never apologise, never hedge, never pad."
)

REPORT_SYSTEM = (
    "You are the Nietzschian Debugger delivering a PROOF OF UNDERSTANDING verdict in "
    "Nietzsche's voice, after several prediction rounds on the developer's own code. "
    "You are given each round: the function, whether they were right, and (if wrong) "
    "the blind spot. Write 2-4 sentences. State how many they got right out of the "
    "total. Then name the PATTERN in their misses — the recurring KIND of thing they "
    "misread (early returns, falsy defaults, mutation, types, boundaries, empty "
    "input, stripped whitespace). If they missed nothing, say so and name the kind of "
    "code that would actually trip them. NEVER give a percentage or a grade — name "
    "the pattern, not a number. Aphoristic and a little exultant — this is their "
    "reckoning; make it ring, with wit and no mercy for comfort. End with one line "
    "they will carry."
)


def _module_spec(file_path: str) -> tuple[str, str | None]:
    """Return (dir_for_sys_path, dotted_module_name) so relative imports work."""
    p = Path(file_path).resolve()
    if p.suffix != ".py":
        return str(p.parent), None
    parts = [p.stem]
    d = p.parent
    while (d / "__init__.py").exists():
        parts.append(d.name)
        d = d.parent
    return str(d), ".".join(reversed(parts))


_RUNNER = r"""
import sys, json, importlib
p = json.load(sys.stdin)
try:
    sys.path.insert(0, p["syspath"])
    mod = importlib.import_module(p["module"])
    func = getattr(mod, p["func"])
except Exception as e:
    print(json.dumps({"stage": "setup", "error": type(e).__name__ + ": " + str(e)}))
    sys.exit(0)
try:
    result = func(*p["args"])
    print(json.dumps({"stage": "ran", "returned": repr(result)}))
except Exception as e:
    print(json.dumps({"stage": "ran", "raised": type(e).__name__ + ": " + str(e)}))
"""

_CHECK = r"""
import sys, json, importlib
p = json.load(sys.stdin)
try:
    sys.path.insert(0, p["syspath"])
    mod = importlib.import_module(p["module"])
    print(json.dumps({"ok": callable(getattr(mod, p["func"], None))}))
except Exception:
    print(json.dumps({"ok": False}))
"""


# Environment variables whose names look secret are not passed to the child.
_SECRET_NAME = re.compile(
    r"KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|COOKIE|SESSION|PRIVATE",
    re.IGNORECASE,
)
_SECRET_PREFIXES = ("AWS_", "AZURE_", "GOOGLE_APPLICATION_", "GH_", "GITHUB_", "NIETZSCHIAN_")


def _child_env() -> dict[str, str]:
    """The caller's environment minus anything that looks like a secret."""
    env = {
        name: value
        for name, value in os.environ.items()
        if not _SECRET_NAME.search(name) and not name.upper().startswith(_SECRET_PREFIXES)
    }
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _run_subprocess(script: str, payload: dict) -> dict | None:
    # Force the child to UTF-8 and decode its output as UTF-8 with errors replaced,
    # so code that prints emoji or accented text can't crash the reader with a
    # Windows cp1252 UnicodeDecodeError. We only parse our own ASCII JSON line.
    child_env = _child_env()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps(payload),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=_TIMEOUT_SECONDS,
            env=child_env,
        )
    except subprocess.TimeoutExpired:
        return {"stage": "setup", "error": f"timed out after {_TIMEOUT_SECONDS}s"}
    for line in reversed((proc.stdout or "").strip().splitlines()):
        try:
            return json.loads(line)
        except Exception:
            continue
    return None


def execute_call(syspath: str, module: str, func: str, args: list) -> dict:
    """Run module.func(*args) in a separate process. Returns {stage: ran, returned|raised}
    or {stage: setup, error}."""
    out = _run_subprocess(_RUNNER, {"syspath": syspath, "module": module, "func": func, "args": args})
    return out or {"stage": "setup", "error": "no output from the call"}


def is_callable_top_level(syspath: str, module: str, func: str) -> bool:
    """True if `func` is a directly callable top-level name in the module."""
    out = _run_subprocess(_CHECK, {"syspath": syspath, "module": module, "func": func})
    return bool(out and out.get("ok"))


def _strip_fences(text: str) -> str:
    """Remove a wrapping code fence and markdown bold a model adds around prose.

    Weak models wrap prose in ``` fences and spray **bold** that a terminal can't
    render; strip both so dares and verdicts read clean. (Leave __dunder__ alone.)
    """
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z]*\s*\n?", "", t)
    t = re.sub(r"\n?```\s*$", "", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.DOTALL)
    t = t.replace("**", "")
    return t.strip()


def _parse_dare(text: str) -> tuple[str, dict | None]:
    """Split model output into (human dare, {function, args})."""
    call = None
    match = re.search(r"CALL:\s*(\{.*\})", text, re.DOTALL)
    dare = text
    if match:
        try:
            call = json.loads(match.group(1))
        except Exception:
            inner = re.search(r"\{.*?\}", match.group(1), re.DOTALL)
            if inner:
                try:
                    call = json.loads(inner.group(0))
                except Exception:
                    call = None
        dare = text[: match.start()]
    # Strip the DARE: label wherever it lands (weak models sometimes write a
    # preamble before it, so it isn't always leading).
    dare = _strip_fences(re.sub(r"\bDARE:\s*", "", dare))
    return dare, call


def _parse_match(text: str) -> tuple[bool | None, str]:
    """Pull a leading 'MATCH: yes|no' tag. Returns (correct_or_None, clean_text)."""
    m = re.match(r"\s*MATCH:\s*(yes|no)\b[.:]?", text, re.IGNORECASE)
    if not m:
        return None, text
    return m.group(1).lower() == "yes", text[m.end():].lstrip("\n .")


_DARE_ATTEMPTS = 3  # the first ask, then two firmer retries

_FIRM_NOTES = {
    "empty": "Your last answer was empty.",
    "no_call": "Your last answer had no CALL: line.",
    "bad_call": (
        "Your last CALL: line was not valid one-line JSON of the shape "
        '{{"function": "<name>", "args": [...]}} with args as a JSON list.'
    ),
    "not_callable": "`{name}` is not a directly callable top-level function of this file.",
    "used": "`{name}` was already used.",
    "no_dare": "Your last answer had a CALL: line but no DARE: to go with it.",
}

_GAVE_UP = (
    "This model could not lay a runnable dare on this file, even when pressed — so no "
    "round this time. Try again, or a coding model (e.g. ollama:qwen2.5-coder or claude)."
)


def _check_dare(raw: str, dare: str, call: dict | None, avoid: list[str], syspath: str, module: str) -> str | None:
    """Why a dare can't be used (a _FIRM_NOTES key), or None when it is runnable."""
    if not (raw or "").strip():
        return "empty"
    if not re.search(r"CALL:", raw):
        return "no_call"
    if (
        not isinstance(call, dict)
        or not isinstance(call.get("function"), str)
        or not call["function"].strip()
        or not isinstance(call.get("args", []), list)
    ):
        return "bad_call"
    if not dare.strip():
        return "no_dare"
    if call["function"] in avoid:
        return "used"
    if not is_callable_top_level(syspath, module, call["function"]):
        return "not_callable"
    return None


def _firm_note(reason: str, name: str = "") -> str:
    return (
        "\n\nYour last answer broke the rules: "
        + _FIRM_NOTES[reason].format(name=name)
        + " Choose a plain, unused module-level function of this file and output EXACTLY "
        "the two lines DARE: and CALL:, nothing else."
    )


def _ask_dare(
    code: str, file_path: str, model: str, syspath: str, module: str, avoid: list[str]
) -> tuple[str, dict] | None:
    """Ask for a dare until one names a runnable call. Each failed attempt is retried
    with a firmer note, and a rejected function name joins the avoid list so it isn't
    picked again. None when every attempt failed (or the model call raised)."""
    rejected: list[str] = []
    firm = ""
    for _ in range(_DARE_ATTEMPTS):
        banned = list(avoid) + [n for n in rejected if n not in avoid]
        why = "already used or not callable" if rejected else "already used"
        avoid_note = f"\n\nDo NOT choose any of these functions ({why}): {', '.join(banned)}." if banned else ""
        user_msg = f"The file ({file_path}):\n\n{code[:_MAX_CODE_CHARS]}{avoid_note}"
        try:
            with thinking():
                raw = call_llm(DARE_SYSTEM + firm, [{"role": "user", "content": user_msg}], model)
        except Exception as error:
            display_error(f"predict ended unexpectedly: {error}")
            return None
        raw = raw or ""
        dare, call = _parse_dare(raw)
        reason = _check_dare(raw, dare, call, banned, syspath, module)
        if reason is None:
            return dare, call
        name = call["function"] if reason in ("used", "not_callable") else ""
        if name and name not in rejected:
            rejected.append(name)
        firm = _firm_note(reason, name)
    display_dim(_GAVE_UP)
    return None


def _run_round(code: str, file_path: str, model: str, syspath: str, module: str, avoid: list[str]) -> dict | None:
    """One dare → guess → executed truth → verdict. Returns the round result or None
    (developer quit, or no runnable dare could be found)."""
    asked = _ask_dare(code, file_path, model, syspath, module, avoid)
    if asked is None:
        return None
    dare, call = asked

    new_line()
    print(dare)
    new_line()
    try:
        guess = input("your prophecy > ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    if not guess or guess.lower() in {"quit", "exit"}:
        return None

    outcome = execute_call(syspath, module, call["function"], call.get("args", []))
    if outcome.get("stage") == "setup":
        display_error(f"Couldn't run {call['function']}(...): {outcome['error']}")
        return None
    truth = f"returned {outcome['returned']}" if "returned" in outcome else f"raised {outcome['raised']}"

    try:
        with thinking():
            verdict_raw = call_llm(
                JUDGE_SYSTEM,
                [
                    {
                        "role": "user",
                        "content": (
                            f"The dare: {dare}\n\n"
                            f"The call: {call['function']}({', '.join(map(repr, call.get('args', [])))})\n"
                            f"The REAL result (from running it): {truth}\n\n"
                            f"The developer predicted: {guess}"
                        ),
                    }
                ],
                model,
            )
    except Exception as error:
        display_error(f"predict ended unexpectedly: {error}")
        return None

    correct, verdict = _parse_match(verdict_raw)
    verdict = _strip_fences(verdict)
    if not verdict:
        # Weak models sometimes emit the MATCH tag and no prose — never show blank.
        verdict = "Right — that is exactly what it does." if correct else "Wrong. Look again at what you assumed."
    new_line()
    print(verdict)
    new_line()
    display_dim(f"The truth, once run — it {truth}.")
    new_line()
    return {"function": call["function"], "correct": correct, "verdict": verdict.strip()}


def _pou_report(results: list[dict], model: str) -> None:
    total = len(results)
    right = sum(1 for r in results if r["correct"] is True)
    lines = [
        f"- {r['function']}: RIGHT" if r["correct"] else f"- {r['function']}: WRONG — {r['verdict'][:240]}"
        for r in results
    ]
    report = None
    try:
        with thinking("Reckoning"):
            report = call_llm(
                REPORT_SYSTEM,
                [{"role": "user", "content": f"Rounds: {total}. Right: {right} of {total}.\n" + "\n".join(lines)}],
                model,
            )
    except Exception:
        report = None

    new_line()
    console.print("[bold cyan]Proof of Understanding[/bold cyan]")
    new_line()
    print((report or f"{right} of {total} predicted correctly.").strip())
    new_line()


def predict_command(file_path: str, rounds: int = 3) -> None:
    """Run `rounds` predict rounds against a file, then a Proof-of-Understanding report."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            code = handle.read()
    except OSError as error:
        display_error(f"Could not read {file_path}: {error}")
        sys.exit(2)
    if not code.strip():
        display_error(f"{file_path} is empty — give me code to test you on.")
        sys.exit(2)

    from ..llm import providers

    if providers.active() is None:
        try:
            get_client()
        except MissingApiKeyError:
            display_api_key_help()
            sys.exit(1)

    model = get_conversation_model()
    syspath, module = _module_spec(file_path)
    if module is None:
        module = Path(file_path).stem

    console.print("\n[bold cyan]Nietzschian Debugger[/bold cyan] [dim][predict mode][/dim]\n")

    display_dim(
        "predict runs functions from this file on your machine. It is not sandboxed: "
        "the code can read files and use the network. Secrets are stripped from its "
        "environment. Only run code you trust."
    )
    rounds = max(1, min(rounds, _MAX_ROUNDS))
    display_dim(f"{rounds} rounds — type 'quit' (or press Ctrl+C) to stop early.\n")
    avoid: list[str] = []
    results: list[dict] = []
    for i in range(1, rounds + 1):
        if rounds > 1:
            display_dim(f"── Round {i} of {rounds} ──")
        result = _run_round(code, file_path, model, syspath, module, avoid)
        if result is None:
            break
        avoid.append(result["function"])
        results.append(result)

    if results:
        _pou_report(results, model)
