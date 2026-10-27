"""Optional non-Anthropic providers (OpenAI, Ollama, Gemini) via the OpenAI API.

Claude is the default and the tuned experience. These are BYOK alternatives for
people who insist -- selected with `--model openai:gpt-4o-mini`, `ollama:llama3`,
`gemini:gemini-1.5-flash`. Honest caveat: the "never give answers" discipline is
sharpest on Claude; a small local model will leak and over-ask more (which is
partly why the validator/judge exist).

The Anthropic path never touches this module -- it stays fully in client.py, so
the default behaviour (and every existing test) is unchanged.
"""

from __future__ import annotations

import os
from typing import Optional

# Any provider with an OpenAI-compatible API works -- which, today, is almost all
# of them. Each needs one row here: base URL, key env var, and a default model.
# provider -> OpenAI-compatible base URL (None = OpenAI's own default)
_BASE_URLS = {
    "openai": None,
    "ollama": "http://localhost:11434/v1",
    "lmstudio": "http://localhost:1234/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "deepseek": "https://api.deepseek.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "mistral": "https://api.mistral.ai/v1",
    "together": "https://api.together.xyz/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "xai": "https://api.x.ai/v1",
    # 'custom' resolves its base URL from NIETZSCHIAN_BASE_URL -- any other
    # OpenAI-compatible endpoint (vLLM, Fireworks, Perplexity, Azure, ...).
    "custom": None,
}
# provider -> env var holding its key (None = no key needed, e.g. local)
_KEY_ENVS = {
    "openai": "OPENAI_API_KEY",
    "ollama": None,
    "lmstudio": None,
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "together": "TOGETHER_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "xai": "XAI_API_KEY",
    "custom": "NIETZSCHIAN_API_KEY",
}
_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "ollama": "llama3",
    "lmstudio": "local-model",
    "gemini": "gemini-1.5-flash",
    "deepseek": "deepseek-chat",
    "groq": "llama-3.3-70b-versatile",
    "mistral": "mistral-small-latest",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "openrouter": "openai/gpt-4o-mini",
    "xai": "grok-2-latest",
    "custom": "",
}

_provider: Optional[str] = None
_model: str = ""
_client_obj = None


class ProviderError(Exception):
    """Raised when a selected provider can't be used (missing package or key)."""


def configure(spec: Optional[str]) -> None:
    """Set the active provider from a --model spec.

    '', None, 'anthropic', 'claude', or an unknown name -> stay on Anthropic.
    'openai:MODEL' / 'ollama:MODEL' / 'gemini:MODEL' (model optional) -> switch.
    """
    global _provider, _model, _client_obj
    _client_obj = None
    if not spec or spec.lower() in ("anthropic", "claude", "default"):
        _provider = None
        return
    name, _, model = spec.partition(":")
    name = name.lower()
    if name not in _BASE_URLS:
        _provider = None  # treat unknown as an Anthropic model name; don't switch
        return
    _provider = name
    _model = model or _DEFAULT_MODELS[name]


def active() -> Optional[str]:
    """The active non-Anthropic provider, or None when using Claude."""
    return _provider


def model_name() -> str:
    return _model


def _client():
    global _client_obj
    if _client_obj is not None:
        return _client_obj
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - import-time guard
        raise ProviderError(
            f"The '{_provider}' provider needs the 'openai' package: "
            "pip install nietzschian-debugger[providers]"
        ) from exc
    key_env = _KEY_ENVS[_provider]
    api_key = os.environ.get(key_env) if key_env else None
    if key_env and not api_key:
        raise ProviderError(f"{key_env} is not set for the '{_provider}' provider.")
    base_url = _BASE_URLS[_provider]
    if _provider == "custom":
        base_url = os.environ.get("NIETZSCHIAN_BASE_URL")
        if not base_url:
            raise ProviderError("NIETZSCHIAN_BASE_URL is not set for the 'custom' provider.")
    _client_obj = OpenAI(base_url=base_url, api_key=api_key or "local")
    return _client_obj


def _msgs(system: str, messages: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"role": "system", "content": system}, *messages]


def stream(system: str, messages: list[dict[str, str]], model: str, callbacks) -> str:
    client = _client()
    full = ""
    try:
        response = client.chat.completions.create(
            model=model or _model,
            messages=_msgs(system, messages),
            stream=True,
            max_tokens=1024,
        )
        for chunk in response:
            choices = getattr(chunk, "choices", None)
            delta = (choices[0].delta.content or "") if choices else ""
            if delta:
                full += delta
                callbacks.on_text(delta)
        callbacks.on_complete(full)
        return full
    except Exception as error:
        callbacks.on_error(error if isinstance(error, Exception) else Exception(str(error)))
        raise


def complete(system: str, messages: list[dict[str, str]], model: str) -> str:
    client = _client()
    response = client.chat.completions.create(
        model=model or _model,
        messages=_msgs(system, messages),
        max_tokens=1024,
    )
    choices = getattr(response, "choices", None)
    return (choices[0].message.content or "") if choices else ""


def estimate_tokens(system: str, messages: list[dict[str, str]]) -> int:
    """Rough token estimate (no count endpoint on the OpenAI-compatible API)."""
    total = len(system) + sum(len(m.get("content", "")) for m in messages)
    return total // 4
