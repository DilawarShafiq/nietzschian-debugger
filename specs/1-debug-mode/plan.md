# Implementation Plan: Debug Mode

**Branch**: `1-debug-mode` | **Date**: 2026-02-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/1-debug-mode/spec.md`

## Summary

Build the core debug command — an interactive CLI session where the Nietzschian Debugger asks confrontational, code-aware questions instead of giving answers. The developer describes a problem, the tool interrogates their reasoning through a REPL loop powered by Claude API (Haiku for conversation, Sonnet for code analysis), and the session ends with a visual growth score. Three intensity levels (socrates/nietzsche/zarathustra) shape the questioning persona. Sessions are persisted per-project for longitudinal tracking.

## Technical Context

**Language/Version**: TypeScript 5.x (strict mode, no `any` types) on Node.js >= 20 LTS
**Primary Dependencies**: `@anthropic-ai/sdk` (^0.78.0), `commander` (^12.0.0)
**Storage**: JSON files in `.nietzschian/sessions/` (per-project, CWD)
**Testing**: vitest
**Target Platform**: Cross-platform CLI (macOS, Linux, Windows) via Node.js
**Project Type**: Single CLI application
**Performance Goals**: Streaming responses with perceived <1s latency to first token; session end summary renders in <500ms
**Constraints**: Zero telemetry, zero network requests beyond Anthropic API, Unicode terminal support assumed
**Scale/Scope**: Single developer per instance, ~100 sessions before considering cleanup tooling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Never Give Answers | PASS | FR-005 + post-processing validator enforce 100% question-only responses |
| II. Build Developer Intuition | PASS | LLM behavior tagging (FR-017) targets reasoning gaps; growth score tracks improvement |
| III. Evidence-Based Questioning | PASS | FR-006 reads actual code; system prompt requires specific references |
| IV. Adaptive Difficulty | PASS | Three intensity levels (FR-002); intensity escalation on answer requests (FR-007) |
| V. Session Memory | PASS | Per-project JSON persistence (FR-009); historical comparison (FR-013) |
| VI. Privacy-First | PASS | FR-014 prohibits all non-API network requests; local-only storage |
| TypeScript strict, no `any` | PASS | Enforced in tsconfig.json |
| ESM modules | PASS | `"type": "module"` in package.json |
| Minimal dependencies | PASS | 2 runtime deps: `@anthropic-ai/sdk`, `commander`. Both zero-dep themselves |
| vitest for testing | PASS | Configured in package.json |

**Post-Phase 1 re-check**: All gates still pass. Design introduces no new dependencies beyond the two listed. No constitution violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/1-debug-mode/
├── plan.md              # This file
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: dev setup guide
├── contracts/
│   └── cli-contract.md  # Phase 1: CLI interface + API contracts
└── tasks.md             # Phase 2: /sp.tasks output (not yet created)
```

### Source Code (repository root)

```text
src/
├── cli.ts                  # Entry point: Commander setup, arg parsing
├── commands/
│   └── debug.ts            # Debug command handler
├── core/
│   ├── session.ts          # Session lifecycle (create, update, finalize)
│   ├── session-loop.ts     # Interactive REPL loop (readline/promises)
│   └── context-manager.ts  # Sliding window + token counting + summarization
├── llm/
│   ├── client.ts           # Anthropic SDK wrapper (model routing)
│   ├── prompts.ts          # System prompt templates (3 intensities)
│   └── validator.ts        # Response validation (no-answer enforcement)
├── scoring/
│   ├── behavior-tagger.ts  # LLM-based behavior tagging per turn
│   ├── skill-scorer.ts     # Normalize tags → 1-10 scores
│   └── growth-profile.ts   # Aggregate across historical sessions
├── quotes/
│   ├── corpus.ts           # Static quote database with context tags
│   └── selector.ts         # Contextual quote matching
├── storage/
│   ├── session-store.ts    # Read/write .nietzschian/sessions/*.json
│   └── file-reader.ts      # Read developer's code files
└── ui/
    ├── renderer.ts         # Terminal output formatting + streaming
    └── growth-display.ts   # Unicode bar charts, growth summary

tests/
├── unit/
│   ├── validator.test.ts
│   ├── skill-scorer.test.ts
│   ├── context-manager.test.ts
│   ├── quote-selector.test.ts
│   └── session-store.test.ts
├── integration/
│   ├── session-loop.test.ts
│   └── debug-command.test.ts
└── fixtures/
    ├── sample-sessions/
    └── sample-code-files/
```

**Structure Decision**: Single project layout. This is a CLI tool with no frontend/backend split. All source lives in `src/` with domain-organized subdirectories. Tests mirror source structure under `tests/`.

## Architecture Decisions

### 1. Model Routing Strategy

**Haiku for all conversational turns** — fast, cheap, sufficient for question generation.
**Sonnet for first code analysis per file** — deeper reasoning needed to understand code structure, identify weak spots, and generate code-specific questions.

The `client.ts` module tracks which files have been analyzed (by path). On first encounter of a file path, it routes to Sonnet. All subsequent turns about that file use Haiku with the Sonnet analysis cached in the conversation context.

### 2. Response Validation Pipeline

Every LLM response passes through `validator.ts` before display:
1. Check for at least one `?` in response
2. Regex filter for answer patterns (code blocks with fixes, "the fix is...", "try doing X")
3. If validation fails: re-prompt LLM once with behavioral reminder
4. If re-prompt fails: fall back to a generic intensity-appropriate question

This is the defense-in-depth layer that achieves SC-002 (100% question-only responses).

### 3. System Prompt Architecture

Three intensity-specific system prompts stored as TypeScript template literals in `prompts.ts`. Each defines:
- Persona voice and tone
- Question style rules
- Escalation behavior
- Example question patterns

Common behavioral constraints (XML tags) are shared across all three. The intensity-specific section is injected per-session.

### 4. Sliding Context Window

`context-manager.ts` handles long sessions:
1. Before each API call, estimate token count (chars/4 heuristic as pre-check)
2. If approaching 80% of 200K (160K tokens): call `count_tokens` API for exact count
3. If over threshold: summarize oldest turns via Haiku into a single paragraph
4. Always preserve: system prompt, problem description, code context, last 8 turns verbatim
5. Summary replaces oldest turns in the message array

### 5. Streaming Output

All LLM responses use `client.messages.stream()` with `.on('text', cb)` piped to `process.stdout.write()`. The developer sees questions forming word-by-word. After stream completes, the full response is captured for the session transcript.

### 6. Session Lifecycle

1. CLI parses args → creates Session object (UUID, timestamp, intensity)
2. If file paths detected → read files, route first analysis to Sonnet
3. Enter REPL loop: display question → read input → process → repeat
4. On "solved"/"found it" → mark solved
5. On exit/quit/Ctrl+C → mark abandoned
6. Post-session: run behavior tagger on full transcript → compute skill scores → render growth display → write session JSON

### 7. Philosophy Quote Integration

`corpus.ts` contains a static array of Quote objects, each tagged with `context` (avoidance, overwhelm, strategy, etc.). `selector.ts` matches context to the current session state:
- Developer deflecting → avoidance → Nietzsche quotes
- Developer says "I don't know" repeatedly → overwhelm → Seneca quotes
- Developer needs to narrow their approach → strategy → Sun Tzu quotes
- Session end → victory (if solved) or perseverance (if abandoned)

Quotes are injected into the LLM's context as a suggested quote to weave into the response, not displayed separately. This keeps them natural.

## Dependency Map

```
cli.ts
└── commands/debug.ts
    ├── core/session.ts
    │   └── storage/session-store.ts
    ├── core/session-loop.ts
    │   ├── llm/client.ts
    │   │   └── @anthropic-ai/sdk
    │   ├── llm/prompts.ts
    │   ├── llm/validator.ts
    │   ├── core/context-manager.ts
    │   │   └── llm/client.ts (token counting)
    │   ├── storage/file-reader.ts
    │   ├── quotes/selector.ts
    │   │   └── quotes/corpus.ts
    │   └── ui/renderer.ts
    ├── scoring/behavior-tagger.ts
    │   └── llm/client.ts
    ├── scoring/skill-scorer.ts
    ├── scoring/growth-profile.ts
    │   └── storage/session-store.ts
    └── ui/growth-display.ts
```

## Complexity Tracking

No constitution violations. No complexity justifications needed.

| Check | Result |
|-------|--------|
| Runtime dependencies | 2 (`@anthropic-ai/sdk`, `commander`) — minimal |
| Abstractions | Domain-driven modules, no premature generalization |
| External services | Anthropic API only — single integration point |
| Storage | Flat JSON files — simplest viable approach |
