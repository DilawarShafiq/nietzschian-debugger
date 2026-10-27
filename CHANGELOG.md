# Changelog

All notable changes to this project are documented here.

## [0.2.4] — 2026-10-28

### Fixed
- **Every error path crashed instead of showing its message.** `display_error`
  and `display_warning` passed `stderr=True` to Rich's `Console.print()`, which
  does not accept it — so an invalid API key, a rate limit, or any caught session
  error raised a `TypeError` traceback instead of the intended message. Errors now
  render through a stderr-configured console.

## [0.2.3] — 2026-10-27

### Changed
- **Exactly one question per turn is now enforced in code**, not just requested
  in the prompt. A response with more than one question is reprompted once; if it
  still over-asks, the model's own contextual response is kept — two real
  questions beat a canned non-sequitur.
- **No-answer enforcement hardened with a model-judge.** The cheap keyword check
  runs first; on turns that read like a diagnosis it escalates to a cheap model
  that judges whether the answer was handed over. A leak that can't be reprompted
  out falls back to a safe question — the one promise the tool makes is kept.

### UX
- The `[Turn N]` header now prints the instant you answer, before the (silent)
  generation — the pause reads as thinking, not a hang. No spinner by design.

## [0.2.2] — 2026-10-27

### Fixed
- **Windows crash at the "you solved it" screen.** The box-drawing characters
  (┣ ┗) in the Growth Profile and em-dashes in questions crashed with
  `UnicodeEncodeError` on cp1252 consoles (and whenever output was piped).
  Output is now forced to UTF-8 at startup, so it renders on every terminal.

## [0.2.1] — 2026-10-27

### Fixed
- `--version` reported `0.1.0` — now correctly reports the installed version.
- Removed the last "anti-AI" wording from the CLI (`--help`) and package docstring.
- Session errors are now surfaced to the developer instead of failing silently
  as "abandoned."

## [0.2.0] — 2026-10-27

The ground-up Python rewrite. The original `0.1.0` was a TypeScript/npm build;
this is the real tool, now on PyPI (`pip install nietzschian-debugger`).

### Added
- **"Tuning fork" Nietzsche persona** — it taps the assumption you're proudest
  of and listens for the one that rings hollow, instead of running a generic
  checklist. Grounded in *Twilight of the Idols* and the *Genealogy*.
- One worked example baked into the persona so the voice stays consistent.

### Changed
- **One question per turn** — no more menu of questions to dodge. It asks a
  single question you can't step around, then builds the next on your answer.
- Retired the "anti-AI" framing: it runs on Claude on purpose; it's
  anti-*outsourcing-your-thinking*. Every other tool hands you the answer —
  this one hands the question back.
- API-key setup help now shows PowerShell and CMD variants, not just bash.
- New public-domain banner (Curt Stoeving's portrait of Nietzsche).

### Fixed
- Questions were printed twice per turn (a multi-line response couldn't be
  cleared by a single-line escape). Now printed exactly once.

### Deprecated
- The npm package `nietzschian-debugger@0.1.0`. Use `pip install nietzschian-debugger`.

## [0.1.0] — 2026-02-25

- Initial release (TypeScript/npm): Debug Mode.

[0.2.0]: https://github.com/DilawarShafiq/nietzschian-debugger/releases/tag/v0.2.0
[0.1.0]: https://github.com/DilawarShafiq/nietzschian-debugger/releases/tag/v0.1.0
