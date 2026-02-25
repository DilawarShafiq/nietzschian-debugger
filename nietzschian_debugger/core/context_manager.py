"""Context window management for long debugging sessions."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from ..types import Turn
from ..llm.client import call_llm, get_conversation_model, count_tokens

TOKEN_THRESHOLD_RATIO = 0.8
MAX_CONTEXT_TOKENS = 200_000
TOKEN_THRESHOLD = int(MAX_CONTEXT_TOKENS * TOKEN_THRESHOLD_RATIO)  # 160K
CHARS_PER_TOKEN = 4
PRESERVE_RECENT_TURNS = 8

SUMMARY_SYSTEM_PROMPT = """You are a precise conversation summarizer. Compress the following debug session turns into a single paragraph that preserves:
- The developer's key hypotheses (stated and rejected)
- Observable behaviors (guessing without evidence, checking assumptions, etc.)
- The current state of understanding at the end of these turns
- Any files or code elements mentioned

Do not editorialize. Do not add new information. Output only the summary paragraph."""


@dataclass
class MessageArray:
    messages: list[dict[str, str]]
    rolling_summary: Optional[str] = None


def build_message_array(
    turns: list[Turn],
    rolling_summary: Optional[str] = None,
) -> MessageArray:
    """Build a message array from turns for LLM input."""
    messages: list[dict[str, str]] = []

    for turn in turns:
        if turn.question:
            messages.append({"role": "assistant", "content": turn.question})
        if turn.response:
            messages.append({"role": "user", "content": turn.response})

    return MessageArray(messages=messages, rolling_summary=rolling_summary)


def estimate_tokens(
    system_prompt: str,
    messages: list[dict[str, str]],
) -> int:
    """Estimate token count from character count (~4 chars per token)."""
    total_chars = len(system_prompt)
    for msg in messages:
        total_chars += len(msg["content"])
    return math.ceil(total_chars / CHARS_PER_TOKEN)


def should_summarize(estimated_tokens: int) -> bool:
    """Determine if the context should be summarized."""
    return estimated_tokens > TOKEN_THRESHOLD


async def summarize_old_turns(
    turns: list[Turn],
    existing_summary: Optional[str] = None,
) -> tuple[str, list[Turn]]:
    """Summarize older turns, preserving recent ones.

    Returns (summary, recent_turns).
    """
    if len(turns) <= PRESERVE_RECENT_TURNS:
        return (existing_summary or "", turns)

    old_turns = turns[:-PRESERVE_RECENT_TURNS]
    recent_turns = turns[-PRESERVE_RECENT_TURNS:]

    turns_text = "\n\n".join(
        f"Turn {t.turn_number}:\nQuestion: {t.question}\nDeveloper: {t.response}"
        for t in old_turns
    )

    if existing_summary:
        to_summarize = (
            f"Previous summary: {existing_summary}\n\n"
            f"New turns to incorporate:\n{turns_text}"
        )
    else:
        to_summarize = turns_text

    summary = call_llm(
        SUMMARY_SYSTEM_PROMPT,
        [{"role": "user", "content": to_summarize}],
        get_conversation_model(),
    )

    return (summary, recent_turns)


async def check_and_summarize(
    system_prompt: str,
    turns: list[Turn],
    existing_summary: Optional[str] = None,
) -> tuple[list[Turn], Optional[str]]:
    """Check context size and summarize if needed.

    Returns (turns, summary).
    """
    msg_array = build_message_array(turns, existing_summary)
    estimated = estimate_tokens(system_prompt, msg_array.messages)

    if not should_summarize(estimated):
        return (turns, existing_summary)

    # Verify with exact count
    try:
        exact = count_tokens(system_prompt, msg_array.messages, get_conversation_model())
        if exact <= TOKEN_THRESHOLD:
            return (turns, existing_summary)
    except Exception:
        # If count_tokens fails, proceed with summarization based on estimate
        pass

    summary, recent_turns = await summarize_old_turns(turns, existing_summary)
    return (recent_turns, summary)
