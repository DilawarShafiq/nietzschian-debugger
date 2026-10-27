# Changelog

All notable changes to this project are documented here.

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
