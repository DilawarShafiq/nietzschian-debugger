# Tasks: Debug Mode

**Input**: Design documents from `specs/1-debug-mode/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-contract.md, research.md, quickstart.md

**Tests**: Included where required by constitution (questioning strategies, adaptive difficulty, all public APIs).

**Organization**: Tasks grouped by user story. US1+US2+US7 combined into MVP phase (architecturally inseparable — the debug loop requires API key config and intensity levels determine the system prompt).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: TypeScript project scaffolding, dependencies, build configuration

- [X] T001 Initialize TypeScript project: create `tsconfig.json` with `strict: true`, `noImplicitAny: true`, `module: "NodeNext"`, `moduleResolution: "NodeNext"`, `target: "ES2022"`, `outDir: "dist"`, `rootDir: "src"` at repository root
- [X] T002 Update `package.json`: add `"type": "module"`, dependencies `@anthropic-ai/sdk@^0.78.0` and `commander@^12.0.0`, devDependencies `typescript@^5.0.0`, `vitest@^2.0.0`, `@types/node@^20.0.0`, update `"dev"` script to use Node loader
- [X] T003 Run `npm install` to generate `node_modules/` and `package-lock.json`
- [X] T004 [P] Create `vitest.config.ts` at repository root with TypeScript ESM configuration
- [X] T005 [P] Create directory structure: `src/commands/`, `src/core/`, `src/llm/`, `src/scoring/`, `src/quotes/`, `src/storage/`, `src/ui/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/sample-sessions/`, `tests/fixtures/sample-code-files/`
- [X] T006 [P] Add `.nietzschian/` to `.gitignore` (session data is per-project, not committed)

**Checkpoint**: `npm run build` succeeds with zero errors (empty project). `npm test` runs vitest with no tests found.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared type definitions and core infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Define TypeScript interfaces for all data model entities in `src/types.ts`: `Session`, `Turn`, `SkillScores`, `BehaviorTag`, `Quote`, `GrowthProfile`, `Intensity` type union, `SessionOutcome` type union, `QuoteContext` type union — per data-model.md
- [X] T008 Implement Anthropic SDK wrapper in `src/llm/client.ts`: initialize client from `ANTHROPIC_API_KEY` env var, export `streamQuestion()` using `messages.stream()` with `.on('text', cb)`, export `analyzeCode()` routing to Sonnet, export `countTokens()` wrapping the count_tokens API, track analyzed file paths in a `Set<string>` for model routing — per cli-contract.md API contract
- [X] T009 [P] Implement session storage in `src/storage/session-store.ts`: `createSession()`, `updateSession()`, `finalizeSession()`, `loadSession()`, `listSessions()` — read/write JSON files to `.nietzschian/sessions/`, auto-create directory if missing, handle schema versioning (check `schemaVersion` field) — per data-model.md Session entity
- [X] T010 [P] Implement terminal renderer in `src/ui/renderer.ts`: `streamToTerminal()` accepting text deltas and writing to `process.stdout`, `displayMessage()` for formatted output with ANSI styling, `displayError()` for error messages — per plan.md streaming output architecture

**Checkpoint**: Types compile. LLM client can be imported. Session store can write/read a JSON file. Renderer outputs to terminal.

---

## Phase 3: Core Debug Session — US1 + US2 + US7 (Priority: P1) MVP

**Goal**: A developer runs `nietzschian debug --intensity nietzsche "My API is slow"`, gets a confrontational opening question, and engages in a back-and-forth REPL session. The tool never gives answers. Three distinct intensity personas. API key validated on startup.

**Independent Test**: Run `nietzschian debug "test problem"` with a valid API key → receive a question (not an answer) → type a response → receive a follow-up question → type `solved` → session ends gracefully.

### Tests for US1+US2+US7 (Constitution requires tests for questioning strategies and adaptive difficulty)

- [X] T011 [P] [US1] Write unit tests for response validator in `tests/unit/validator.test.ts`: test that responses with `?` pass, responses without `?` fail, answer patterns ("The fix is...", "Try doing X", code blocks with fixes) are detected and rejected, re-prompt produces valid output — per cli-contract.md Response Validation Contract
- [X] T012 [P] [US2] Write unit tests for system prompts in `tests/unit/prompts.test.ts`: test that each intensity level (socrates, nietzsche, zarathustra) produces a distinct system prompt containing the correct XML tags, behavioral constraints, and intensity-specific instructions — per cli-contract.md System Prompt Contract

### Implementation for US1+US2+US7

- [X] T013 Implement response validator in `src/llm/validator.ts`: `validateResponse()` checking for question mark presence, regex filtering answer patterns (code blocks with fixes, "The fix is...", "You should change", "Try doing X"), `repromptIfInvalid()` that re-prompts LLM once with behavioral reminder, `getFallbackQuestion()` returning intensity-appropriate generic question — per cli-contract.md Response Validation Contract
- [X] T014 Implement system prompt templates in `src/llm/prompts.ts`: export `getSystemPrompt(intensity, problemDescription, codeContext?, rollingSummary?, turnNumber?)` returning XML-structured system prompt with `<persona>`, `<behavioral_constraints>`, `<intensity_rules>`, `<code_context>`, `<session_context>` sections — three intensity variants per cli-contract.md System Prompt Contract. Include escalation instructions for when developer asks for answers.
- [X] T015 Implement session lifecycle in `src/core/session.ts`: `createSession(problemDescription, intensity)` returning new Session with UUID and timestamp, `addTurn(session, question, response, model, behaviorTags)`, `finalizeSession(session, outcome)` setting endTimestamp and outcome — per data-model.md Session entity and lifecycle
- [X] T016 Implement interactive REPL loop in `src/core/session-loop.ts`: use `readline/promises` for input, detect session commands (`solved`, `found it`, `exit`, `quit`, `I give up`), pipe each user response through LLM client with streaming output, run response through validator before display, handle Ctrl+C/Ctrl+D via `rl.on('close')`, track turn count — per spec.md US1 acceptance scenarios and cli-contract.md Session Commands
- [X] T017 Implement debug command handler in `src/commands/debug.ts`: validate `ANTHROPIC_API_KEY` exists (exit 1 if missing), validate intensity flag (exit 2 if invalid), validate problem description is non-empty (exit 2 if empty), create session, call session-loop, finalize session on completion — per cli-contract.md exit codes and spec.md US7 acceptance scenarios
- [X] T018 Implement CLI entry point in `src/cli.ts`: configure Commander with `nietzschian` program name, register `debug` subcommand with `--intensity` option (choices: socrates/nietzsche/zarathustra, default: nietzsche), `--help`, `--version` from package.json, wire to debug command handler — per cli-contract.md Command Interface
- [X] T019 [US1] Add `"bin": {"nietzschian": "dist/cli.js"}` verification: ensure `npm run build` produces `dist/cli.js`, test `node dist/cli.js debug --help` outputs usage — per package.json

**Checkpoint**: MVP functional. `npx nietzschian debug "My API is slow"` → confrontational question → interactive loop → `solved` → session ends. Three distinct intensity levels work. Missing API key shows clear error. This is demoable.

---

## Phase 4: User Story 3 — Real Code Reading (Priority: P1)

**Goal**: When the developer references a file path in their problem or responses, the tool reads the actual file and asks questions about THEIR specific code — not generic advice.

**Independent Test**: Run `nietzschian debug "Auth fails in ./src/auth.ts"` with a real file → the opening question references specific function names or line numbers from that file.

### Implementation for User Story 3

- [X] T020 [P] [US3] Implement file reader in `src/storage/file-reader.ts`: `detectFilePaths(text)` using regex to find file paths in user input, `readCodeFile(path)` reading file contents with line numbers, `truncateToRelevantSection(content, maxTokens)` extracting the most relevant function/class if file is too large — per spec.md US3 acceptance scenarios and edge case for large files
- [X] T021 [P] [US3] Write unit test for file path detection in `tests/unit/file-reader.test.ts`: test regex matches `./src/auth.ts`, `src/models/user.ts`, `/absolute/path.js`, paths with spaces, paths in quotes, multiple paths in one string, no false positives on English sentences
- [X] T022 [US3] Integrate file reading into session loop in `src/core/session-loop.ts`: on session start, scan problem description for file paths → read files → inject into system prompt's `<code_context>` section. On each user response, scan for new file paths → read and inject. Route first analysis of each new file through Sonnet via `client.ts` — per plan.md Architecture Decision 1 (Model Routing Strategy)
- [X] T023 [US3] Write integration test for code-aware questioning in `tests/integration/debug-command.test.ts`: create a fixture file in `tests/fixtures/sample-code-files/auth.ts`, run debug command referencing it, verify the LLM response includes specific identifiers from the fixture file

**Checkpoint**: `nietzschian debug "Bug in ./tests/fixtures/sample-code-files/auth.ts"` produces questions that reference specific code from that file. Sonnet used for first analysis, Haiku for follow-ups.

---

## Phase 5: User Story 6 — Session Persistence (Priority: P2)

**Goal**: Sessions auto-save to `.nietzschian/sessions/` as JSON. Data persists across sessions and tool upgrades.

**Independent Test**: Complete a session → verify `.nietzschian/sessions/{uuid}.json` exists and contains all required fields per data-model.md.

### Implementation for User Story 6

- [X] T024 [P] [US6] Write unit tests for session store in `tests/unit/session-store.test.ts`: test `createSession` writes valid JSON, `loadSession` reads it back identically, `listSessions` returns all sessions sorted by date, directory auto-creation when `.nietzschian/sessions/` is missing, schema version migration (older schema gets default values for missing fields), graceful handling of corrupted JSON files
- [X] T025 [US6] Integrate session persistence into debug command in `src/commands/debug.ts`: after session finalization (from `session-loop.ts`), call `sessionStore.save(session)` to write the completed session JSON to `.nietzschian/sessions/{id}.json` — per data-model.md Session storage contract
- [X] T026 [US6] Create sample session fixture in `tests/fixtures/sample-sessions/sample-v1.json` matching the exact schema from data-model.md with realistic data (5 turns, mixed behavior tags, skill scores) — used by future growth profile tests

**Checkpoint**: Complete a debug session → `.nietzschian/sessions/` contains a valid JSON file with all fields from data-model.md. Delete the directory → next session recreates it.

---

## Phase 6: User Story 5 — Philosophy Quotes in Context (Priority: P2)

**Goal**: Contextually relevant philosophy quotes woven into session interactions — Nietzsche for avoidance, Seneca for overwhelm, Sun Tzu for strategy.

**Independent Test**: In a session, give "I don't know" responses → Seneca quotes appear. Deflect from hard questions → Nietzsche quotes appear.

### Implementation for User Story 5

- [X] T027 [P] [US5] Create philosophy quote corpus in `src/quotes/corpus.ts`: export `QUOTES` array of `Quote` objects (minimum 30 quotes: 10+ Nietzsche, 10+ Seneca, 5+ Sun Tzu, 5+ others). Each quote tagged with `context` (avoidance, overwhelm, strategy, victory, defeat, perseverance) and `source` (book/work). Quotes must be real, correctly attributed, and relevant to debugging/problem-solving moments — per data-model.md Quote entity
- [X] T028 [P] [US5] Implement quote selector in `src/quotes/selector.ts`: `selectQuote(sessionState)` analyzing developer responses for contextual cues (deflection → avoidance, "I don't know" → overwhelm, need to narrow approach → strategy), `selectClosingQuote(outcome)` choosing victory quote for solved sessions and perseverance quote for abandoned. Return `null` if no quote fits well (avoid forced quotes) — per spec.md US5 acceptance scenarios
- [X] T029 [P] [US5] Write unit tests for quote selector in `tests/unit/quote-selector.test.ts`: test avoidance detection (deflection phrases), overwhelm detection ("I don't know", "I'm lost"), strategy detection (broad unfocused responses), closing quote selection for solved/abandoned outcomes, null return when no context match
- [X] T030 [US5] Integrate quotes into session loop in `src/core/session-loop.ts`: after analyzing developer response, call `selectQuote()` to get contextual quote. If quote returned, inject into system prompt as `<suggested_quote>` tag so the LLM naturally weaves it into its response — per plan.md Architecture Decision 7

**Checkpoint**: During sessions, quotes appear naturally within the LLM's responses at contextually appropriate moments. No quotes forced where they don't fit.

---

## Phase 7: User Story 4 — Growth Score and Session Tracking (Priority: P2)

**Goal**: After each session, display a visual debugging profile with Unicode bar charts, skill dimension ratings, comparison to historical sessions, and a closing philosophy quote.

**Independent Test**: Complete 3 sessions → the third session's growth score shows trends (improving/declining) compared to the first two.

### Implementation for User Story 4

- [X] T031 [P] [US4] Implement behavior tagger in `src/scoring/behavior-tagger.ts`: `tagSessionBehaviors(transcript)` sending the full session transcript to Haiku with a structured prompt requesting behavior tags per turn (guessed-without-evidence, checked-logs, questioned-assumption, assumed-without-checking, narrowed-scope, went-broad-unnecessarily, asked-for-answer) — return `BehaviorTag[]` per data-model.md
- [X] T032 [P] [US4] Implement skill scorer in `src/scoring/skill-scorer.ts`: `computeSkillScores(behaviorTags)` normalizing tagged behaviors to 1-10 scale per dimension (assumptionChecking, evidenceGathering, rootCauseSpeed). Positive tags increase score, negative tags decrease. Base score of 5, clamped to 1-10 range — per data-model.md SkillScores entity
- [X] T033 [P] [US4] Write unit tests for skill scorer in `tests/unit/skill-scorer.test.ts`: test scoring with all positive tags (high scores), all negative (low scores), mixed (mid scores), empty tags (baseline 5), clamping at 1 and 10 boundaries
- [X] T034 [P] [US4] Implement growth profile aggregator in `src/scoring/growth-profile.ts`: `computeGrowthProfile(sessions)` loading all sessions from `.nietzschian/sessions/`, computing `GrowthProfile` with totalSessions, solvedCount, averageScores, and recentTrend (compare last 5 vs previous 5 sessions per dimension, delta > +1 = improving, < -1 = declining, else stable) — per data-model.md GrowthProfile entity
- [X] T035 [P] [US4] Implement growth score display in `src/ui/growth-display.ts`: `renderGrowthScore(session, growthProfile?, closingQuote?)` rendering Unicode bar chart (`█` for filled, `░` for empty, 10 chars per bar), skill labels with descriptors, trend arrows if historical data exists, closing philosophy quote — match exact format from cli-contract.md Growth Score Display Contract
- [X] T036 [US4] Integrate scoring pipeline into debug command in `src/commands/debug.ts`: after session finalization, run `tagSessionBehaviors()` → `computeSkillScores()` → update session with scores → save session → load growth profile → `selectClosingQuote()` → `renderGrowthScore()` — per plan.md Architecture Decision 6 (Session Lifecycle step 6)
- [X] T037 [US4] Write integration test for growth score display in `tests/integration/session-loop.test.ts`: load sample sessions from fixtures, compute growth profile, render growth score, verify output contains Unicode bars, skill labels, and trend indicators

**Checkpoint**: Complete a session → see visual growth score with bar charts. Complete 3+ sessions → see trend comparison. Closing philosophy quote appears at every session end.

---

## Phase 8: Context Window Management (Cross-cutting)

**Purpose**: Implement sliding context window for long sessions — required by FR-018

- [X] T038 [P] Implement context manager in `src/core/context-manager.ts`: `buildMessageArray(systemPrompt, turns, codeContext)` assembling the messages array for each API call, `estimateTokens(messages)` using chars/4 heuristic, `shouldSummarize(estimatedTokens)` checking against 80% of 200K threshold (160K), `summarizeOldTurns(turns, client)` calling Haiku to compress oldest turns into a single summary paragraph while preserving last 8 turns verbatim — per plan.md Architecture Decision 4
- [X] T039 [P] Write unit tests for context manager in `tests/unit/context-manager.test.ts`: test token estimation accuracy, threshold detection, message array construction (system prompt + summary + recent turns), preservation of last 8 turns, correct summary placement
- [X] T040 Integrate context manager into session loop in `src/core/session-loop.ts`: before each LLM call, run `buildMessageArray()` → if `shouldSummarize()` → call `summarizeOldTurns()` → rebuild message array with summary replacing old turns — per spec.md US1 acceptance scenario 6

**Checkpoint**: Sessions of 30+ turns don't crash or degrade. Older turns are transparently summarized.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Error handling hardening, edge cases, final integration

- [X] T041 [P] Implement API error handling in `src/llm/client.ts`: catch `AuthenticationError` → exit 1 with clear message, `RateLimitError` → auto-retry (SDK handles) then exit 3 if exhausted, `APIConnectionError` → exit 3 with connection error message — per cli-contract.md Error Handling table
- [X] T042 [P] Handle "I give up" lifeline flow in `src/core/session-loop.ts`: detect "I give up" input → generate one final pointed question as lifeline → if developer still quits → mark abandoned — per spec.md edge case
- [X] T043 [P] Handle empty/whitespace problem description in `src/commands/debug.ts`: if description is empty or whitespace-only, display usage help via Commander and exit 2 — per spec.md edge case
- [X] T044 [P] Handle large error/stack trace pasting in `src/core/session-loop.ts`: detect stack trace patterns in user input, include only the most relevant frames in the context rather than the full paste — per spec.md edge case
- [X] T045 Update `README.md` with installation instructions (`npm install -g nietzschian-debugger` or `npx nietzschian`), API key setup, usage examples for all three intensity levels, and the example session output from the original vision
- [X] T046 Run full test suite (`npm test`), fix any failures, ensure `npm run build` produces zero errors and zero warnings — per constitution Development Workflow
- [X] T047 Run `npx nietzschian debug "test problem"` end-to-end at each intensity level to verify the complete flow: API key check → opening question → interactive loop → solved → growth score with bar charts and philosophy quote

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1+US2+US7 (Phase 3)**: Depends on Phase 2 — this is the MVP
- **US3 (Phase 4)**: Depends on Phase 3 (extends the session loop)
- **US6 (Phase 5)**: Depends on Phase 2 (session store already exists, just wire it in)
- **US5 (Phase 6)**: Depends on Phase 3 (needs session loop to integrate into)
- **US4 (Phase 7)**: Depends on Phase 5 (needs session persistence for historical data) + Phase 6 (needs quotes for closing quote)
- **Context Window (Phase 8)**: Depends on Phase 3 (extends session loop and LLM client)
- **Polish (Phase 9)**: Depends on all previous phases

### User Story Dependencies

```
Phase 1 (Setup)
    │
Phase 2 (Foundational)
    │
Phase 3 (US1+US2+US7 — MVP)
    ├──────────────┬──────────────┐
Phase 4 (US3)    Phase 5 (US6)  Phase 6 (US5)
    │              │              │
    │              └──────┬───────┘
    │                     │
    │              Phase 7 (US4)
    │                     │
    └──────────┬──────────┘
               │
        Phase 8 (Context Window)
               │
        Phase 9 (Polish)
```

### Parallel Opportunities

**Within Phase 1**: T004, T005, T006 can run in parallel
**Within Phase 2**: T009, T010 can run in parallel (T007 first, T008 second, then T009/T010)
**Within Phase 3**: T011, T012 can run in parallel (tests first). Then T013, T014 in parallel.
**After Phase 3**: Phase 4 (US3), Phase 5 (US6), and Phase 6 (US5) can run in parallel
**Within Phase 7**: T031, T032, T033, T034, T035 can all run in parallel
**Within Phase 8**: T038, T039 can run in parallel

---

## Parallel Example: Phase 7 (Growth Score)

```bash
# Launch all parallel tasks for Growth Score together:
Task: "Implement behavior tagger in src/scoring/behavior-tagger.ts"         # T031
Task: "Implement skill scorer in src/scoring/skill-scorer.ts"               # T032
Task: "Write unit tests for skill scorer in tests/unit/skill-scorer.test.ts" # T033
Task: "Implement growth profile in src/scoring/growth-profile.ts"           # T034
Task: "Implement growth display in src/ui/growth-display.ts"                # T035

# Then sequentially:
Task: "Integrate scoring pipeline into debug command"                        # T036
Task: "Write integration test for growth score"                              # T037
```

---

## Implementation Strategy

### MVP First (Phase 1 + 2 + 3 Only)

1. Complete Phase 1: Setup → project compiles
2. Complete Phase 2: Foundational → core infrastructure ready
3. Complete Phase 3: US1+US2+US7 → **STOP and VALIDATE**
4. Test: `nietzschian debug --intensity zarathustra "My API is slow"` → full interactive session
5. **This is demoable and useful.** Ship it, get feedback.

### Incremental Delivery

1. MVP (Phase 1-3) → Core debug loop with 3 intensity levels
2. Add US3 (Phase 4) → Code-aware questioning (the differentiator)
3. Add US6 (Phase 5) → Sessions persist to disk
4. Add US5 (Phase 6) → Philosophy quotes appear in sessions
5. Add US4 (Phase 7) → Growth score with visual bar charts
6. Add Context Window (Phase 8) → Long sessions work flawlessly
7. Polish (Phase 9) → Error handling, edge cases, README
8. Each phase adds value without breaking previous phases

### Suggested Commit Points

- After Phase 1: `feat: initialize TypeScript project with dependencies`
- After Phase 2: `feat: add foundational types, LLM client, session store, renderer`
- After Phase 3: `feat: implement core debug session with intensity levels (MVP)`
- After Phase 4: `feat: add real code reading and code-aware questioning`
- After Phase 5: `feat: add session persistence to .nietzschian/sessions/`
- After Phase 6: `feat: add contextual philosophy quotes`
- After Phase 7: `feat: add growth score with visual bar charts and trend tracking`
- After Phase 8: `feat: add sliding context window for long sessions`
- After Phase 9: `feat: polish error handling, edge cases, and README`

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 47 |
| Phase 1 (Setup) | 6 |
| Phase 2 (Foundational) | 4 |
| Phase 3 (US1+US2+US7 MVP) | 9 |
| Phase 4 (US3 Code Reading) | 4 |
| Phase 5 (US6 Persistence) | 3 |
| Phase 6 (US5 Quotes) | 4 |
| Phase 7 (US4 Growth Score) | 7 |
| Phase 8 (Context Window) | 3 |
| Phase 9 (Polish) | 7 |
| Parallel opportunities | 28 tasks marked [P] |
| MVP scope | Phases 1-3 (19 tasks) |

## Notes

- [P] tasks = different files, no dependencies
- Constitution mandates tests for questioning strategies (T011, T012) and all public APIs
- US1+US2+US7 are combined because they are architecturally inseparable: you cannot demo the debug loop without an API key, and intensity levels determine the system prompt
- US4 (Growth Score) depends on US6 (Persistence) for historical data and US5 (Quotes) for closing quotes
- Each checkpoint is independently demoable
- Commit after each phase for clean git history
