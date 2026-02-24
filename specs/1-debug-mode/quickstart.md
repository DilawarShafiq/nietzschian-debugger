# Quickstart: Debug Mode Development

**Branch**: `1-debug-mode` | **Date**: 2026-02-25

## Prerequisites

- Node.js >= 20 LTS
- npm
- An Anthropic API key (`ANTHROPIC_API_KEY`)

## Setup

```bash
git checkout 1-debug-mode
npm install
```

## Key Dependencies

```json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.78.0",
    "commander": "^12.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^2.0.0",
    "@types/node": "^20.0.0"
  }
}
```

## Project Structure

```
src/
├── cli.ts                  # Entry point: Commander setup, arg parsing
├── commands/
│   └── debug.ts            # Debug command handler
├── core/
│   ├── session.ts          # Session lifecycle management
│   ├── session-loop.ts     # Interactive REPL loop
│   └── context-manager.ts  # Sliding window context management
├── llm/
│   ├── client.ts           # Anthropic SDK wrapper (Haiku + Sonnet routing)
│   ├── prompts.ts          # System prompt templates per intensity
│   └── validator.ts        # Response validation (no-answer enforcement)
├── scoring/
│   ├── behavior-tagger.ts  # LLM-based behavior tagging per turn
│   ├── skill-scorer.ts     # Normalize behavior tags → 1-10 scores
│   └── growth-profile.ts   # Aggregate scores across sessions
├── quotes/
│   ├── corpus.ts           # Quote database with context tags
│   └── selector.ts         # Contextual quote selection logic
├── storage/
│   ├── session-store.ts    # Read/write session JSON files
│   └── file-reader.ts      # Read user's code files for analysis
└── ui/
    ├── renderer.ts         # Terminal output formatting
    └── growth-display.ts   # Unicode bar charts, growth score display

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

## Build & Run

```bash
# Build
npm run build

# Run locally (dev)
npx ts-node --esm src/cli.ts debug "My API is slow"

# Run with intensity
npx ts-node --esm src/cli.ts debug --intensity zarathustra "Auth fails in ./src/auth.ts"

# Run tests
npm test

# Type check
npx tsc --noEmit
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |

## Development Flow

1. **Core loop first**: `cli.ts` → `debug.ts` → `session-loop.ts` → `client.ts`
2. **Add intensity**: `prompts.ts` with three system prompt variants
3. **Add code reading**: `file-reader.ts` → inject into system prompt
4. **Add validation**: `validator.ts` to enforce no-answer rule
5. **Add scoring**: `behavior-tagger.ts` → `skill-scorer.ts` → `growth-display.ts`
6. **Add quotes**: `corpus.ts` → `selector.ts` → integrate into session loop
7. **Add persistence**: `session-store.ts` → `growth-profile.ts`

## Key Architecture Decisions

- **Streaming responses**: All LLM responses stream to terminal in real-time via `process.stdout.write()`
- **Haiku for conversation, Sonnet for code**: `client.ts` routes based on whether this is a first-time code analysis
- **Post-processing validator**: Every LLM response passes through `validator.ts` before display
- **Sliding context window**: `context-manager.ts` summarizes old turns when approaching 80% of 200K token limit
- **Per-project sessions**: `.nietzschian/sessions/` in CWD, not user home
