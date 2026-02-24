# Research: Debug Mode

**Branch**: `1-debug-mode` | **Date**: 2026-02-25

## Decision Log

### 1. Anthropic SDK

- **Decision**: Use `@anthropic-ai/sdk` (latest: 0.78.0)
- **Rationale**: Official SDK, auto-reads `ANTHROPIC_API_KEY`, built-in streaming via `messages.stream()`, typed error hierarchy (`AuthenticationError`, `RateLimitError`, `APIConnectionError`), automatic retry with backoff, ESM support via `.mjs` export.
- **Alternatives considered**: Raw `fetch` calls — rejected because SDK handles auth, retries, streaming, and error typing for free.
- **Model IDs**: `claude-haiku-4-5-20251001` (Haiku), `claude-sonnet-4-6` (Sonnet)
- **Breaking constraint**: SDK requires **Node.js >= 20 LTS**. Constitution and spec say >= 18. Must update to >= 20.

### 2. CLI Framework

- **Decision**: Commander.js v12 (or v13)
- **Rationale**: Zero runtime dependencies, full ESM support (dual CJS/ESM), first-class subcommands and flags, bundled TypeScript types, largest community and documentation. Battle-tested in 115K+ downstream packages.
- **Alternatives considered**:
  - citty (unjs): Smaller (45KB vs 230KB), ESM-first, zero deps. Rejected because Commander's documentation depth and community troubleshooting resources are significantly broader for a CLI that will grow to 3+ subcommands.
  - clipanion v3: Strongest TypeScript ergonomics (decorator-based). Rejected because decorator pattern requires `experimentalDecorators` and adds API complexity without proportional benefit at current scale.
  - yargs 18: Rejected — ESM issues, 1.31MB dependency weight, ongoing migration problems.
  - Node.js `util.parseArgs`: Rejected — no subcommand dispatch, no help generation, too much boilerplate.

### 3. Interactive Terminal Input

- **Decision**: Node.js built-in `readline/promises`
- **Rationale**: Zero dependencies, native ESM, async/await compatible, stable since Node 17. Sufficient for the "user types → tool responds" loop. No wizard-style prompts needed.
- **Alternatives considered**:
  - inquirer / @inquirer/prompts: Rich prompt types (multi-select, autocomplete) but overkill for text-in/text-out REPL. Latest requires Node >= 20; older v9 adds unnecessary dependency weight.
  - prompts (npm): Abandoned (last publish 2021), CJS-only. Rejected.

### 4. Context Window Management

- **Decision**: Sliding window with Haiku-powered summarization at 80% context threshold
- **Rationale**: Both Haiku and Sonnet have 200K context windows. At 80% (160K tokens), trigger summarization of older turns. Always preserve: system prompt, original problem, code context, last 6-10 turns verbatim. Use `POST /v1/messages/count_tokens` for exact token counting; `chars/4` as fast pre-check.
- **Alternatives considered**:
  - Hard cap (force session end): Rejected — breaks user flow, arbitrary limit.
  - Truncation (drop old turns): Rejected — loses reasoning history needed for growth scoring.
  - Observation masking: Competitive with summarization for efficiency but loses nuance needed for behavior tagging.

### 5. Token Estimation

- **Decision**: Anthropic `count_tokens` API endpoint (primary), `characters / 4` heuristic (fast pre-check)
- **Rationale**: The count_tokens endpoint is cheap, exact, and already in the API call chain. The heuristic avoids unnecessary API calls when clearly under threshold.
- **Alternatives considered**: ctoc (reverse-engineered offline estimator, ~96% accuracy) — viable fallback but adds a dependency.

### 6. System Prompt Architecture (Persona Enforcement)

- **Decision**: XML behavioral tags + role contract + escalation-on-violation + post-processing validator
- **Rationale**: No system prompt technique is 100% reliable (~78% bypass rate without guardrails). Defense in depth: structured XML tags help Claude parse behavioral rules, escalation rules handle "just tell me" attempts, and a post-processing validator catches any slip-through before display.
- **Post-processing validator checks**: Every response must end with `?` or contain at least one question. Regex filters for answer patterns ("The fix is", "You should change", "The problem is X because Y"). If validation fails: re-prompt once with behavioral reminder.
- **Alternatives considered**: Caps-lock emphasis ("NEVER do X") — doesn't work reliably. Long prohibition lists — cause stochastic failures. "Stay in character" without behavioral definition — too vague.

### 7. Streaming Output

- **Decision**: Use SDK's `messages.stream()` with `.on('text', cb)` for real-time terminal output
- **Rationale**: Shows question text as it's generated, reducing perceived latency. Developer sees the question forming word-by-word instead of waiting for the full response. Uses `process.stdout.write()` for inline character streaming.
- **Alternatives considered**: Non-streaming (wait for full response) — rejected because CLI tools feel dead during 2-5 second waits.

## Node.js Version Update Required

The Anthropic SDK (`@anthropic-ai/sdk`) requires **Node.js >= 20 LTS**. The constitution and spec currently specify >= 18.0.0. This must be updated in:
- `.specify/memory/constitution.md` — Technology Stack section
- `specs/1-debug-mode/spec.md` — Assumptions and Dependencies sections
- `package.json` — engines field
