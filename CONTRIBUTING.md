# Contributing

Thanks for wanting to make the Nietzschian Debugger sharper. It's a small,
focused tool — contributions that keep it that way are the most welcome.

## Finding something to work on

- Issues labelled [`good first issue`](https://github.com/DilawarShafiq/nietzschian-debugger/labels/good%20first%20issue)
  are small and self-contained, a good way to learn the codebase.
- Issues labelled [`help wanted`](https://github.com/DilawarShafiq/nietzschian-debugger/labels/help%20wanted)
  are bigger features the project wants and the maintainer won't get to soon.
- **Comment on the issue before you start** so two people don't build the same
  thing. You'll get a reply, and the issue is yours.
- Have your own idea? Open a [feature issue](https://github.com/DilawarShafiq/nietzschian-debugger/issues/new/choose)
  or start a [discussion](https://github.com/DilawarShafiq/nietzschian-debugger/discussions)
  first, so we can agree on the shape before you write code.

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
| `nietzschian_debugger/commands/` | One file per command: `debug`, `predict`, `roast`, `demo`, `share` |
| `nietzschian_debugger/quotes/corpus.py` | The philosopher quote collection |
| `plugins/nietzschian/` | The Claude Code plugin (an output style) |
| `tests/` | `pytest` unit tests |

## Good first contributions

- **Add an LLM provider** — usually one row each in `providers.py` (base URL, key
  env var, default model). Any OpenAI-compatible endpoint works.
- **Sharpen a persona** in `prompts.py` — keep the voice (see below).
- **Improve the quote collection** in `quotes/corpus.py` — every quote needs a
  real, checkable source.
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
- Add or update tests; **`pytest` must pass.** CI runs the suite on Linux,
  macOS and Windows for every PR.
- Say what changed and why. Small, testable diffs get merged fastest.
- Add a line to `CHANGELOG.md` for anything a user would notice.
- Every merged contributor is credited in the release notes.

By contributing you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
Found a security problem? See [SECURITY.md](SECURITY.md) instead of opening an issue.
