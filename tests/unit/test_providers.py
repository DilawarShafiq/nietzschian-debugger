"""Tests for multi-model provider selection.

Only the selection/config logic is tested here -- the actual network calls need
real keys or a running local model, so they're validated with a live smoke test,
not in CI.
"""

from __future__ import annotations

import pytest

from nietzschian_debugger.llm import providers


@pytest.fixture(autouse=True)
def _reset_provider():
    # Never let a set provider leak into other tests (which use the Claude path).
    yield
    providers.configure(None)


def test_default_is_anthropic() -> None:
    providers.configure(None)
    assert providers.active() is None
    providers.configure("claude")
    assert providers.active() is None


def test_known_providers_parse() -> None:
    providers.configure("deepseek:deepseek-chat")
    assert providers.active() == "deepseek"
    assert providers.model_name() == "deepseek-chat"

    providers.configure("ollama")  # model omitted -> default
    assert providers.active() == "ollama"
    assert providers.model_name() == "llama3"

    providers.configure("openai:gpt-4o-mini")
    assert providers.active() == "openai"
    assert providers.model_name() == "gpt-4o-mini"


def test_unknown_name_stays_on_anthropic() -> None:
    providers.configure("notaprovider:x")
    assert providers.active() is None


def test_estimate_tokens_is_nonnegative() -> None:
    n = providers.estimate_tokens("system prompt", [{"role": "user", "content": "hello there"}])
    assert isinstance(n, int) and n >= 0


def test_openai_uses_max_completion_tokens() -> None:
    # Issue #7: newer OpenAI models reject 'max_tokens' with HTTP 400.
    providers.configure("openai:gpt-4o")
    assert providers._limit(1024) == {"max_completion_tokens": 1024}


@pytest.mark.parametrize("spec", ["ollama:llama3", "groq:llama-3.1-8b-instant"])
def test_compatible_servers_keep_max_tokens(spec: str) -> None:
    # OpenAI-compatible servers vary; they keep the widely-supported 'max_tokens'.
    providers.configure(spec)
    assert providers._limit(1024) == {"max_tokens": 1024}
