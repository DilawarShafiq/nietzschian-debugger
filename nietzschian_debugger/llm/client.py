"""Anthropic LLM client for the Nietzschian Debugger."""

from __future__ import annotations

import os
import re
from typing import Callable, Optional

import anthropic

from . import providers

HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-6"

# Reasoning models sometimes inline their chain-of-thought in the response as
# <think>…</think> (Ollama separates it into a field, but other OpenAI-compatible
# servers don't). Strip it so the oracle's thinking never shows — and never
# spoils a `predict` by reasoning the answer out loud.
_REASONING_TAGS = re.compile(r"<(think|thinking|reasoning)>.*?</\1>", re.DOTALL | re.IGNORECASE)


def _strip_reasoning(text: str) -> str:
    """Remove inline <think>…</think> reasoning blocks from a model response."""
    return _REASONING_TAGS.sub("", text).strip()

_client: Optional[anthropic.Anthropic] = None
_analyzed_files: set[str] = set()


class MissingApiKeyError(Exception):
    """Raised when ANTHROPIC_API_KEY is not set."""

    def __init__(self) -> None:
        super().__init__("ANTHROPIC_API_KEY environment variable is not set.")


def get_client() -> anthropic.Anthropic:
    """Get or create the Anthropic client singleton."""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise MissingApiKeyError()
        _client = anthropic.Anthropic(api_key=api_key, max_retries=2)
    return _client


def get_model_for_file(file_path: str) -> str:
    """Return Sonnet for first analysis of a file, Haiku for subsequent."""
    if providers.active() is not None:
        return providers.model_name()
    if file_path in _analyzed_files:
        return HAIKU_MODEL
    _analyzed_files.add(file_path)
    return SONNET_MODEL


def get_conversation_model() -> str:
    """Return the model used for general conversation turns."""
    if providers.active() is not None:
        return providers.model_name()
    return HAIKU_MODEL


class StreamCallbacks:
    """Callbacks for streaming LLM responses."""

    def __init__(
        self,
        on_text: Callable[[str], None],
        on_complete: Callable[[str], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        self.on_text = on_text
        self.on_complete = on_complete
        self.on_error = on_error


def stream_question(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str,
    callbacks: StreamCallbacks,
) -> str:
    """Stream a question from the LLM, calling callbacks for each text chunk."""
    if providers.active() is not None:
        return providers.stream(system_prompt, messages, model, callbacks)
    client = get_client()
    full_text = ""

    try:
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,  # type: ignore[arg-type]
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                callbacks.on_text(text)

        callbacks.on_complete(full_text)
        return full_text
    except Exception as error:
        callbacks.on_error(error if isinstance(error, Exception) else Exception(str(error)))
        raise


def count_tokens(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str,
) -> int:
    """Count tokens for the given prompt and messages."""
    if providers.active() is not None:
        return providers.estimate_tokens(system_prompt, messages)
    client = get_client()
    result = client.messages.count_tokens(
        model=model,
        system=system_prompt,
        messages=messages,  # type: ignore[arg-type]
    )
    return result.input_tokens


def call_llm(
    system_prompt: str,
    messages: list[dict[str, str]],
    model: str,
) -> str:
    """Make a non-streaming LLM call and return the text response."""
    if providers.active() is not None:
        return providers.complete(system_prompt, messages, model)
    client = get_client()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,  # type: ignore[arg-type]
    )
    block = response.content[0]
    if block.type == "text":
        return block.text
    return ""


def reset_analyzed_files() -> None:
    """Clear the set of analyzed files."""
    _analyzed_files.clear()
