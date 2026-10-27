# Contributing

Thanks for wanting to make the Nietzschian Debugger sharper. It's a small,
focused tool — contributions that keep it that way are the most welcome.

## Setup

```bash
git clone https://github.com/DilawarShafiq/nietzschian-debugger.git
cd nietzschian-debugger
pip install -e ".[dev]"        # add [providers] too for non-Claude models
pytest                          # run the suite — should be all green
```

Try it with no API key at all:

```bash
nietzschian demo
```

## Project layout

| Path | What lives there |
|---|---|
| `nietzschian_debugger/llm/prompts.py` | The personas — the philosophy (Socrates / Nietzsche / Zarathustra) |
| `nietzschian_debugger/llm/validator.py` | The one-question + no-answer enforcement, and the leak judge |
| `nietzschian_debugger/llm/providers.py` | Model providers (OpenAI-compatible; Claude is default) |
| `nietzschian_debugger/core/lens_state.py` | Adaptive-lens state detection + hysteresis |
| `nietzschian_debugger/core/session_loop.py` | The interactive session loop |
| `tests/` | `pytest` unit tests |

## Good first contributions

- **Add an LLM provider** — usually one row each in `providers.py` (base URL, key
  env var, default model). Any OpenAI-compatible endpoint works.
- **Sharpen a persona** in `prompts.py` — keep the voice (see below).
- **Add session examples / test fixtures.**

## The one rule: it never gives answers

Every change must preserve the core promise — **the tool asks questions; it never
hands over the fix.** If you touch the prompts or the validator, run a real
session and confirm it still refuses to solve the bug for you.

## Voice

The personas have a voice — Nietzsche's tuning fork, Socratic elenchus,
Zarathustran affirmation. Keep questions **pointed and in character**: seize a
specific word, name a specific assumption, point at a specific line. No flat
help-desk questions ("what exactly are you seeing?").

## Pull requests

- Branch off `main`; keep each PR focused on one thing.
- Add or update tests; **`pytest` must pass.**
- Say what changed and why. Small, testable diffs get merged fastest.
