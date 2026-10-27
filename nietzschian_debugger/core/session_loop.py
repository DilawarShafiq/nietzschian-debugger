"""Interactive session loop for the debugging session."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..types import Session, SessionOutcome
from ..llm.client import stream_question, get_conversation_model, get_model_for_file, StreamCallbacks
from ..llm.prompts import get_system_prompt
from ..llm.validator import (
    validate_response,
    reprompt_if_invalid,
    get_fallback_question,
    smells_like_diagnosis,
    judge_leaks_answer,
)
from ..storage.file_reader import detect_file_paths, read_code_file, format_code_context
from .session import add_turn, add_code_file
from .context_manager import check_and_summarize, build_message_array
from ..quotes.selector import select_quote
from ..ui.renderer import (
    new_line,
    display_session_header,
    display_dim,
    display_error,
)

EXIT_COMMANDS = {"exit", "quit"}
SOLVE_COMMANDS = {"solved", "found it"}


@dataclass
class SessionLoopResult:
    outcome: SessionOutcome


async def run_session_loop(
    session: Session, preloaded_context: Optional[dict[str, str]] = None
) -> SessionLoopResult:
    """Run the interactive debugging session loop."""
    # preloaded_context seeds extra material (e.g. the git diff) into the context
    # the LLM sees, so it can interrogate what the developer actually changed.
    code_files: dict[str, str] = dict(preloaded_context) if preloaded_context else {}
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

    try:
        new_line()
        display_dim("[Turn 1]")
        opening_question = _generate_valid_question(
            system_prompt,
            [{"role": "user", "content": session.problem_description}],
            model,
            session.intensity,
            session.problem_description,
        )
        print(opening_question)
        new_line()

        current_question = opening_question

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
                        session.problem_description,
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

            # Show the turn header the instant the developer hits enter -- the
            # scaffold is the "it's working" signal; the question fills in beneath
            # it after the (silent) generation. No spinner: the pause is the menace.
            turn_number = len(session.transcript) + 1
            new_line()
            display_dim(f"[Turn {turn_number}]")

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

            # Build next turn (turn_number + header already shown above)
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
                session.problem_description,
            )

            print(next_question)
            new_line()
            current_question = next_question

    except KeyboardInterrupt:
        return SessionLoopResult(outcome="abandoned")
    except Exception as error:
        # Don't die silently — tell the developer the session broke and why.
        display_error(f"The session ended unexpectedly: {error}")
        return SessionLoopResult(outcome="abandoned")


def _generate_valid_question(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str,
    intensity: str,
    problem_description: str,
) -> str:
    """Generate a question, enforcing one-question + no-answer with a safe fallback.

    Two failure classes, handled differently (the key to not making the tool worse):
      - Venial (over-asking: more than one question): reprompt once; if it still
        over-asks, KEEP the model's contextual response -- two real questions beat a
        canned non-sequitur about nothing.
      - Mortal (leaks the cause/fix): reprompt once; if it still leaks, drop to the
        canned fallback -- showing a leaked answer breaks the one promise the tool
        makes, so a generic question is the lesser evil.

    The leak sensor is a cheap regex first, escalated to a model-judge only on turns
    that read like a diagnosis (the regex misses leaks phrased around its banned words).
    """
    full_text = ""

    def on_text(text: str) -> None:
        # Buffer silently; the validated question is printed once by the caller
        # under the [Turn N] header (streaming it live double-printed it).
        pass

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

    validation = validate_response(full_text)

    # Second pass: catch leaks the cheap regex missed, but only pay for the judge
    # on responses that actually read like a diagnosis.
    leaked_by_judge = False
    if validation.valid and smells_like_diagnosis(full_text):
        leaked_by_judge = judge_leaks_answer(full_text, problem_description)

    if validation.valid and not leaked_by_judge:
        return full_text

    reason = validation.reason or ("judge: leaks the answer" if leaked_by_judge else "")
    is_over_asking = "more than one question" in reason

    # Reprompt once, tailored to the failure.
    reprompted = reprompt_if_invalid(system_prompt, messages, full_text, reason)
    if reprompted:
        return reprompted

    # Reprompt failed: venial -> keep the contextual response; mortal -> canned.
    if is_over_asking:
        return full_text
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
