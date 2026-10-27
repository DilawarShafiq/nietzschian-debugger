"""`predict` mode — dare the developer to say what their code does, then RUN it.

The lesson from the first prototype: a model *reasoning* about behaviour can be
confidently wrong, and a tool about not fooling yourself must never fool you. So
here the truth comes from **executing the code**, not from the model. The model
only (1) picks a non-obvious call to dare you with, and (2) frames the gap between
your guess and the real result. The real result is whatever the function actually
returns (or raises), shown to you plainly.

Execution runs in a separate Python process with a timeout — it's your own code,
run the way you'd run it yourself.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from ..llm.client import call_llm, get_client, get_conversation_model, MissingApiKeyError
from ..ui.renderer import console, display_api_key_help, display_dim, display_error, new_line

_MAX_CODE_CHARS = 12000
_TIMEOUT_SECONDS = 5

DARE_SYSTEM = (
    "You are the Nietzschian Debugger in PREDICT mode, in Nietzsche's voice. Given "
    "a file of code, choose ONE function that can be called with SIMPLE, LITERAL "
    "arguments only (strings, numbers, booleans, None, lists, dicts — no objects, "
    "no file/network I/O, no arguments you'd have to construct). Pick the call MOST "
    "LIKELY to make them wrong: a result that is counterintuitive and NOT guessable "
    "from the function's name — an edge case, empty input, a boundary, an early "
    "return, a falsy default, a surprising type. Avoid softballs whose answer is "
    "obvious.\n\n"
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
    "reasoning of your own. Compare their prediction to the real result:\n"
    "- If they were RIGHT: say so in ONE sharp line. Do NOT flatter, and do NOT "
    "invent a flaw, a lesson, or a 'but' that isn't there. If the case was easy, "
    "say it was easy and dare them toward a harder truth. Never manufacture a gap.\n"
    "- If they were WRONG: in two or three merciless sentences, name the EXACT thing "
    "they misread — the line, the branch, the assumption — and what that gap reveals "
    "about how they read code.\n"
    "Never apologise, never hedge, never pad."
)


def _module_spec(file_path: str) -> tuple[str, str | None]:
    """Return (dir_to_put_on_sys_path, dotted_module_name) so relative imports work.

    Walks up through package dirs (those with __init__.py). For a plain script the
    module is just its stem.
    """
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


def execute_call(syspath: str, module: str, func: str, args: list) -> dict:
    """Run module.func(*args) in a separate process with a timeout. Returns a dict:
    {stage: "ran", returned|raised: str} on execution, or {stage: "setup", error} otherwise.
    """
    payload = json.dumps({"syspath": syspath, "module": module, "func": func, "args": args})
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _RUNNER],
            input=payload,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"stage": "setup", "error": f"timed out after {_TIMEOUT_SECONDS}s (possible infinite loop)"}
    for line in reversed((proc.stdout or "").strip().splitlines()):
        try:
            return json.loads(line)
        except Exception:
            continue
    return {"stage": "setup", "error": (proc.stderr or "no output from the call").strip()[:200]}


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


def is_callable_top_level(syspath: str, module: str, func: str) -> bool:
    """True if `func` is a directly-callable top-level name in the module.

    Guards against the model daring with a method or something needing an object.
    """
    payload = json.dumps({"syspath": syspath, "module": module, "func": func})
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _CHECK], input=payload, capture_output=True, text=True, timeout=_TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired:
        return False
    for line in reversed((proc.stdout or "").strip().splitlines()):
        try:
            return bool(json.loads(line).get("ok"))
        except Exception:
            continue
    return False


def _parse_dare(text: str) -> tuple[str, dict | None]:
    """Split the model output into (human dare, {function, args}) ; call is None if unparseable."""
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
    dare = re.sub(r"^\s*DARE:\s*", "", dare.strip()).strip()
    return dare, call


def predict_command(file_path: str) -> None:
    """Run one predict round: dare -> your guess -> the REAL (executed) result."""
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
    console.print("\n[bold cyan]Nietzschian Debugger[/bold cyan] [dim][predict mode][/dim]\n")

    syspath, module = _module_spec(file_path)
    if module is None:
        module = Path(file_path).stem

    # Dare with a call we can actually RUN. If the model picks a method or anything
    # not callable at top level, re-dare (up to a few tries) — no dud dares.
    user_msg = f"The file ({file_path}):\n\n{code[:_MAX_CODE_CHARS]}"
    dare: str | None = None
    call: dict | None = None
    retry = ""
    for _ in range(3):
        try:
            raw = call_llm(DARE_SYSTEM + retry, [{"role": "user", "content": user_msg}], model)
        except Exception as error:
            display_error(f"predict ended unexpectedly: {error}")
            sys.exit(1)
        parsed_dare, parsed_call = _parse_dare(raw)
        if (
            parsed_call
            and parsed_call.get("function")
            and is_callable_top_level(syspath, module, parsed_call["function"])
        ):
            dare, call = parsed_dare, parsed_call
            break
        retry = (
            "\n\nYour previous pick was NOT a directly callable top-level function "
            "(no methods, nothing that needs an object constructed). Choose a plain "
            "module-level function."
        )

    if not call:
        display_error(
            "Couldn't get a runnable challenge — try a file with simple, top-level "
            "functions (or a stronger model)."
        )
        return

    new_line()
    print(dare)
    new_line()
    try:
        guess = input("your prediction > ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not guess:
        new_line()
        console.print("[dim]No prediction, no reckoning. Come back when you'll commit to an answer.[/dim]")
        return

    # The truth comes from RUNNING the code, never from the model.
    outcome = execute_call(syspath, module, call["function"], call.get("args", []))

    if outcome.get("stage") == "setup":
        display_error(
            f"Couldn't run {call['function']}(...): {outcome['error']}. "
            "Pick a function with simple literal arguments."
        )
        return

    truth = (
        f"returned {outcome['returned']}" if "returned" in outcome else f"raised {outcome['raised']}"
    )

    try:
        verdict = call_llm(
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
        sys.exit(1)

    new_line()
    print(verdict.strip())
    new_line()
    # Show the ground truth plainly — so a fuzzy verdict can never misteach you.
    display_dim(f"Actual result (executed): {truth}")
    new_line()
