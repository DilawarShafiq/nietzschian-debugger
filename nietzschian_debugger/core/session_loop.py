"""Interactive session loop for the debugging session."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

from ..types import Session, SessionOutcome
from ..llm.client import stream_question, get_conversation_model, get_model_for_file, StreamCallbacks
from ..llm.prompts import get_system_prompt
from ..llm.validator import validate_response, reprompt_if_invalid, get_fallback_question
from ..storage.file_reader import detect_file_paths, read_code_file, format_code_context
from .session import add_turn, add_code_file
from .context_manager import check_and_summarize, build_message_array
from ..quotes.selector import select_quote
from ..ui.renderer import (
    stream_to_terminal,
    new_line,
    display_session_header,
    display_dim,
)

EXIT_COMMANDS = {"exit", "quit"}
SOLVE_COMMANDS = {"solved", "found it"}


@dataclass
class SessionLoopResult:
    outcome: SessionOutcome


async def run_session_loop(session: Session) -> SessionLoopResult:
    """Run the interactive debugging session loop."""
    code_files: dict[str, str] = {}
    rolling_summary: Optional[str] = None
    lifeline_offered = False

    display_session_header(session.intensity)

    # Read initial code files from problem description
    initial_paths = detect_file_paths(session.problem_description)
    for file_path in initial_paths:
        content = await read_code_file(file_path)
        if content:
            code_files[file_path] = content
            add_code_file(session, file_path)

    # Generate opening question
    model = get_model_for_file(initial_paths[0]) if initial_paths else get_conversation_model()
    code_context = format_code_context(code_files)
    system_prompt = get_system_prompt(
        session.intensity,
        session.problem_description,
        code_context or None,
        rolling_summary,
        1,
    )

    opening_question = _generate_valid_question(
        system_prompt,
        [{"role": "user", "content": session.problem_description}],
        model,
        session.intensity,
    )

    new_line()
    display_dim("[Turn 1]")
    print(opening_question)
    new_line()

    current_question = opening_question

    try:
        while True:
            try:
                raw_input = input("> ")
            except EOFError:
                return SessionLoopResult(outcome="abandoned")

            trimmed = raw_input.strip()
            if not trimmed:
                continue

            lower = trimmed.lower()

            # Check exit commands
            if lower in EXIT_COMMANDS:
                add_turn(session, current_question, "[exited]", model)
                return SessionLoopResult(outcome="abandoned")

            # Check solve commands
            if lower in SOLVE_COMMANDS:
                add_turn(session, current_question, "[solved]", model)
                return SessionLoopResult(outcome="solved")

            # Check "I give up"
            if lower == "i give up":
                if not lifeline_offered:
                    lifeline_offered = True
                    add_turn(session, current_question, trimmed, model)

                    # Generate one lifeline question
                    lifeline_prompt = get_system_prompt(
                        session.intensity,
                        session.problem_description,
                        code_context or None,
                        rolling_summary,
                        len(session.transcript) + 1,
                    )
                    messages = _build_conversation_messages(session, trimmed)
                    lifeline_q = _generate_valid_question(
                        lifeline_prompt,
                        [*messages, {"role": "user", "content": "I give up. I cannot figure this out."}],
                        get_conversation_model(),
                        session.intensity,
                    )

                    new_line()
                    display_dim("[Lifeline -- one more question before you go]")
                    print(lifeline_q)
                    new_line()
                    current_question = lifeline_q
                    continue
                else:
                    add_turn(session, current_question, "[gave up]", model)
                    return SessionLoopResult(outcome="abandoned")

            # Normal response
            add_turn(session, current_question, trimmed, model)

            # Check for new file paths in response
            new_paths = detect_file_paths(trimmed)
            for file_path in new_paths:
                if file_path not in code_files:
                    content = await read_code_file(file_path)
                    if content:
                        code_files[file_path] = content
                        add_code_file(session, file_path)

            # Check context window
            context_turns, context_summary = await check_and_summarize(
                system_prompt,
                session.transcript,
                rolling_summary,
            )
            rolling_summary = context_summary

            # Select contextual quote
            quote = select_quote(trimmed)
            suggested_quote_text = quote.text if quote else None

            # Build next turn
            turn_number = len(session.transcript) + 1
            updated_code_context = format_code_context(code_files)
            system_prompt = get_system_prompt(
                session.intensity,
                session.problem_description,
                updated_code_context or None,
                rolling_summary,
                turn_number,
                suggested_quote_text,
            )

            # Determine model
            model = get_model_for_file(new_paths[0]) if new_paths else get_conversation_model()

            messages = _build_conversation_messages(session)
            next_question = _generate_valid_question(
                system_prompt,
                messages,
                model,
                session.intensity,
            )

            new_line()
            display_dim(f"[Turn {turn_number}]")
            print(next_question)
            new_line()
            current_question = next_question

    except KeyboardInterrupt:
        return SessionLoopResult(outcome="abandoned")
    except Exception:
        return SessionLoopResult(outcome="abandoned")


def _generate_valid_question(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str,
    intensity: str,
) -> str:
    """Generate a valid question, with reprompt and fallback."""
    full_text = ""

    def on_text(text: str) -> None:
        stream_to_terminal(text)

    def on_complete(text: str) -> None:
        nonlocal full_text
        full_text = text

    def on_error(error: Exception) -> None:
        pass

    stream_question(
        system_prompt,
        messages,
        model,
        StreamCallbacks(on_text=on_text, on_complete=on_complete, on_error=on_error),
    )

    # Clear the streamed output line
    sys.stdout.write("\r\033[K")

    validation = validate_response(full_text)
    if validation.valid:
        return full_text

    # Try reprompt
    reprompted = reprompt_if_invalid(system_prompt, messages, full_text)
    if reprompted:
        return reprompted

    # Fallback
    return get_fallback_question(intensity)  # type: ignore[arg-type]


def _build_conversation_messages(
    session: Session,
    current_response: Optional[str] = None,
) -> list[dict[str, str]]:
    """Build the conversation message history for the LLM."""
    messages: list[dict[str, str]] = [
        {"role": "user", "content": session.problem_description},
    ]

    for turn in session.transcript:
        messages.append({"role": "assistant", "content": turn.question})
        if turn.response and not turn.response.startswith("["):
            messages.append({"role": "user", "content": turn.response})

    if current_response:
        messages.append({"role": "user", "content": current_response})

    return messages
