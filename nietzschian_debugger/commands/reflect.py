"""Psychology-informed reflection without diagnosis or direct advice."""

from __future__ import annotations

import sys

from ..llm.client import call_llm, get_client, get_conversation_model, MissingApiKeyError
from ..llm.validator import validate_response
from ..ui.renderer import console, display_api_key_help, display_dim, display_error, thinking

SYSTEM_PROMPT = """You are a psychology-informed reflective questioner, not a therapist.
Help the user examine a personal situation, choice, habit, or belief without
diagnosing them, assigning a disorder, or prescribing treatment.

Ask exactly ONE open-ended question per response. Do not give direct answers,
advice, interpretations presented as fact, or lists of questions. Help the user
notice assumptions, emotions, learned patterns, needs, and alternative
perspectives; stay curious and nonjudgmental. Do not shame or pressure them.

If the user describes imminent danger to themselves or another person, prioritize
briefly encouraging immediate help from local emergency services or a trusted
person over the usual question-only style. This conversation is not a substitute
for professional mental-health care. Prefix such an urgent safety response with
[SAFETY] and otherwise do not use this prefix."""

EXIT_COMMANDS = {"quit", "exit"}


def reflect_command(topic: str) -> None:
    """Run a psychology-informed reflection session on a personal topic."""
    if not topic or not topic.strip():
        display_error("Please describe a situation or pattern you want to reflect on.")
        sys.exit(2)

    from ..llm import providers

    if providers.active() is None:
        try:
            get_client()
        except MissingApiKeyError:
            display_api_key_help()
            sys.exit(1)

    model = get_conversation_model()
    messages = [{"role": "user", "content": topic.strip()}]

    console.print("\n[bold cyan]Nietzschian Reflect[/bold cyan] [dim][psychology-informed reflection][/dim]\n")
    display_dim("This is reflective conversation, not diagnosis or therapy. Type 'quit' to stop.\n")
    display_dim("Text is sent to your selected model provider; this mode does not read files or save sessions.\n")

    while True:
        try:
            with thinking():
                response = call_llm(SYSTEM_PROMPT, messages, model).strip()
                safety_response = response.startswith("[SAFETY]")
                if not safety_response and not validate_response(response).valid:
                    response = call_llm(
                        SYSTEM_PROMPT,
                        [
                            *messages,
                            {"role": "assistant", "content": response},
                            {
                                "role": "user",
                                "content": "Rewrite as exactly one reflective question without giving advice or an answer.",
                            },
                        ],
                        model,
                    ).strip()
                    safety_response = response.startswith("[SAFETY]")
                if safety_response:
                    response = response.removeprefix("[SAFETY]").strip()
                elif not validate_response(response).valid:
                    raise ValueError("Model did not return a single reflective question after retry.")
                if not response:
                    raise ValueError("Model returned an empty response.")
        except Exception as error:
            display_error(f"Reflection ended: {error}")
            sys.exit(3)
        print(response)
        messages.append({"role": "assistant", "content": response})

        while True:
            try:
                answer = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                return
            if answer.lower() in EXIT_COMMANDS:
                return
            if answer:
                messages.append({"role": "user", "content": answer})
                break
