# Feature Specification: Debug Mode

**Feature Branch**: `1-debug-mode`
**Created**: 2026-02-25
**Status**: Draft
**Input**: User description: "Debug Mode — the core feature and primary hook of Nietzschian Debugger"

## Clarifications

### Session 2026-02-25

- Q: Where should session data live — current working directory or user home? → A: Per-project in current working directory (`.nietzschian/sessions/`).
- Q: How does a session end as "solved" — developer declares, LLM detects, or either? → A: Developer explicitly declares (e.g., `solved`, `found it`).
- Q: How are skill dimension scores calculated? → A: LLM evaluates reasoning quality per-turn, tags behaviors, normalizes to 1-10 scale per dimension.
- Q: When does the tool route to Sonnet vs Haiku? → A: Sonnet for first code analysis per file only; Haiku for all conversational turns.
- Q: How should long sessions handle context window limits? → A: Sliding window — keep problem + code + recent turns, summarize older turns automatically.

## User Scenarios & Testing

### User Story 1 — Start a Debug Session (Priority: P1)

A developer encounters a bug and runs `nietzschian debug "My API returns 500 on POST /users"`. The tool reads the problem description, asks a confrontational opening question that forces the developer to examine their assumptions, and begins an interactive back-and-forth session. The developer responds, the tool evaluates their reasoning and asks sharper follow-up questions. This continues until the developer reaches the root cause themselves.

**Why this priority**: This is the entire product. Without the core debug loop, nothing else matters. A user who runs the command and gets one great question is already hooked.

**Independent Test**: Can be fully tested by running the CLI with a problem description and verifying the tool produces a relevant, non-answer question and accepts user responses in a conversational loop.

**Acceptance Scenarios**:

1. **Given** a user has `ANTHROPIC_API_KEY` set, **When** they run `nietzschian debug "My API is slow"`, **Then** the tool displays a confrontational opening question relevant to API performance (not a solution).
2. **Given** an active debug session, **When** the user types a response, **Then** the tool evaluates their reasoning and responds with a follow-up question that goes deeper.
3. **Given** an active debug session, **When** the user asks "just tell me the answer", **Then** the tool refuses and the intensity of questioning increases.
4. **Given** an active debug session, **When** the user types `exit` or `quit` or presses Ctrl+C, **Then** the session ends gracefully with a summary.
5. **Given** an active debug session, **When** the developer types `solved` or `found it`, **Then** the tool marks the session outcome as "solved" and proceeds to the growth score summary.
6. **Given** a session exceeding 20 turns, **When** context approaches the model's limit, **Then** older turns are automatically summarized while preserving the problem description, code context, and recent turns.

---

### User Story 2 — Intensity Levels Shape the Experience (Priority: P1)

A developer chooses their questioning intensity. A junior runs `nietzschian debug --intensity socrates "TypeError: cannot read property of undefined"` and gets warm, scaffolded questions. A senior runs `nietzschian debug --intensity zarathustra "My API is slow"` and gets brutally direct challenges to their reasoning. The default (`nietzsche`) is confrontational but fair.

**Why this priority**: Co-P1 with the core loop. Intensity levels ARE the personality of the product. Without them, it's just "ChatGPT that asks questions." The three levels create three distinct experiences from a single tool.

**Independent Test**: Can be tested by starting sessions at each intensity level and verifying the tone, question style, and escalation behavior differ measurably between levels.

**Acceptance Scenarios**:

1. **Given** `--intensity socrates`, **When** the session starts, **Then** questions use warm, guiding language ("What do you think might happen if...?", "Have you considered looking at...?").
2. **Given** `--intensity nietzsche` (or no flag), **When** the session starts, **Then** questions are direct and confrontational ("Why haven't you checked the logs yet?", "What evidence do you have for that assumption?").
3. **Given** `--intensity zarathustra`, **When** the session starts, **Then** questions are brutally challenging ("You're guessing. What does the stack trace actually say?", "That's a weak hypothesis. Defend it.").
4. **Given** an invalid intensity value, **When** the user runs the command, **Then** the tool displays available levels and exits with a non-zero code.

---

### User Story 3 — Real Code Reading (Priority: P1)

A developer references a file in their problem description: `nietzschian debug "Auth fails in ./src/auth.ts"`. The tool reads the actual file, analyzes the code, and asks questions about THEIR specific implementation — not generic auth advice. It references specific line numbers, function names, and variable values.

**Why this priority**: Co-P1. This is what separates the tool from "ChatGPT but mean." Generic questions are worthless. Questions about YOUR code at YOUR line numbers are transformative.

**Independent Test**: Can be tested by running the command with a real file path and verifying the tool's questions reference specific elements from that file (function names, variable names, line numbers).

**Acceptance Scenarios**:

1. **Given** a problem description containing a file path that exists, **When** the session starts, **Then** the tool reads the file and incorporates specific code references into its questions.
2. **Given** a problem description containing a file path that does NOT exist, **When** the session starts, **Then** the tool asks the developer to provide the correct path or share the relevant code.
3. **Given** multiple file references, **When** the session progresses, **Then** the tool cross-references code across files to ask about interactions and dependencies.
4. **Given** a session is active, **When** the developer mentions a new file path in their response, **Then** the tool reads that file and incorporates it into subsequent questions.

---

### User Story 4 — Session Tracking and Growth Score (Priority: P2)

After a debug session ends, the developer sees a visual profile of their debugging process: how many questions it took to reach root cause, skill dimensions rated with bar charts, comparison to previous sessions, and a contextually relevant philosophy quote.

**Why this priority**: P2 because it's the retention hook. The debug loop gets them in the door; the growth score makes them come back. But the core loop must work first.

**Independent Test**: Can be tested by completing a debug session and verifying the summary displays question count, skill ratings with visual bars, session comparison data, and a philosophy quote.

**Acceptance Scenarios**:

1. **Given** a completed debug session, **When** the session ends, **Then** the tool displays a summary with: questions-to-root-cause count, skill dimension ratings, and a philosophy quote.
2. **Given** previous sessions exist in `.nietzschian/sessions/`, **When** a new session completes, **Then** the summary shows trends (improving/declining/stable) compared to past sessions.
3. **Given** no previous sessions exist, **When** the first session completes, **Then** the summary shows baseline ratings without comparison data.
4. **Given** a completed session, **When** the summary is displayed, **Then** the skill dimensions include at minimum: assumption-checking, evidence-gathering, and root-cause speed.

---

### User Story 5 — Philosophy Quotes in Context (Priority: P2)

Throughout the debug session, philosophy quotes appear at moments where they're contextually relevant. When the developer is avoiding the hard question, they get Nietzsche. When overwhelmed, Seneca. When they need strategic thinking, Sun Tzu. After the session, a closing quote matches the overall session arc.

**Why this priority**: P2 because quotes without the core loop are decoration. But quotes WITH the core loop are what make the tool memorable and shareable. They're the viral element.

**Independent Test**: Can be tested by simulating session states (avoidance, overwhelm, strategic thinking) and verifying contextually appropriate quotes appear.

**Acceptance Scenarios**:

1. **Given** the developer is deflecting or avoiding a hard question, **When** the tool responds, **Then** the response includes a Nietzsche quote about confronting difficulty.
2. **Given** the developer shows signs of being overwhelmed (long pauses, "I don't know" responses), **When** the tool responds, **Then** the response includes a Seneca quote about composure.
3. **Given** the developer needs to think strategically about their approach, **When** the tool responds, **Then** the response includes a Sun Tzu quote about strategy.
4. **Given** a completed session, **When** the growth score is displayed, **Then** a closing philosophy quote is shown that reflects the session's arc.

---

### User Story 6 — Session Persistence (Priority: P2)

Debug sessions are automatically saved to `.nietzschian/sessions/` as structured data. Sessions persist across tool upgrades. The developer's growth history accumulates over time without any manual action.

**Why this priority**: P2 because the growth score (US-4) depends on historical data. Without persistence, every session is isolated and the "getting stronger" narrative dies.

**Independent Test**: Can be tested by completing a session, verifying a file is created in `.nietzschian/sessions/`, reading it back, and confirming all session data is present and parseable.

**Acceptance Scenarios**:

1. **Given** a debug session completes, **When** the session ends, **Then** a structured data file is written to `.nietzschian/sessions/` containing the full session transcript, skill ratings, and metadata.
2. **Given** `.nietzschian/sessions/` does not exist, **When** the first session completes, **Then** the directory is created automatically.
3. **Given** session files exist from a previous tool version, **When** the tool reads them, **Then** it handles missing fields gracefully without errors.
4. **Given** a session file, **When** inspected, **Then** it contains: session ID, timestamp, problem description, intensity level, full Q&A transcript, skill dimension scores, questions-to-root-cause count, and outcome (solved/abandoned).

---

### User Story 7 — API Key Configuration (Priority: P1)

The developer sets their Anthropic API key via the `ANTHROPIC_API_KEY` environment variable. The tool validates the key on startup. If missing, it shows a clear, helpful message explaining how to set it. Zero accounts, zero sign-ups, zero server-side anything.

**Why this priority**: P1 because without a valid API key, nothing works. This is the gate. It must be frictionless.

**Independent Test**: Can be tested by running the command with and without the environment variable set and verifying appropriate behavior in each case.

**Acceptance Scenarios**:

1. **Given** `ANTHROPIC_API_KEY` is set and valid, **When** the user runs any command, **Then** the tool proceeds normally.
2. **Given** `ANTHROPIC_API_KEY` is not set, **When** the user runs any command, **Then** the tool displays a clear message explaining how to set the key and exits with a non-zero code.
3. **Given** `ANTHROPIC_API_KEY` is set but invalid, **When** the tool attempts its first API call, **Then** it displays a clear error about the invalid key and exits gracefully.

---

### Edge Cases

- What happens when the developer provides a problem description that is empty or just whitespace? Tool displays usage help and exits.
- What happens when the developer's code file is too large to fit in an API context window? Tool reads the most relevant section (function/class containing the referenced issue) rather than the entire file.
- What happens when the API rate limit is hit mid-session? Tool informs the user of the rate limit, pauses, and retries automatically with backoff.
- What happens when the developer reaches root cause very quickly (1-2 questions)? Tool acknowledges the fast solve, still provides a growth score, and challenges them with "Could you have gotten there faster? What was your first instinct?"
- What happens when the developer gives up and types "I give up"? Tool offers one final pointed question as a lifeline. If they still quit, session ends as "abandoned" with a growth score and a motivational philosophy quote.
- What happens when the developer pastes a large error/stack trace? Tool parses the trace and asks questions about the most relevant frames, not the entire trace.
- What happens if the `.nietzschian/sessions/` directory is deleted between sessions? Tool recreates it on next session. No crash, no error. Previous history is simply unavailable.
- What happens when there's no internet connection? Tool fails fast with a clear message: "Cannot reach Claude API. Check your connection."
- What happens when a session runs 30+ turns and approaches context limits? Older turns are automatically summarized into a compressed narrative; the developer sees no interruption. Problem description and code context are always preserved in full.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a problem description via `nietzschian debug "<problem>"` and start an interactive terminal session.
- **FR-002**: System MUST support `--intensity` flag with three values: `socrates`, `nietzsche` (default), `zarathustra`.
- **FR-003**: System MUST send prompts to the Claude API (Anthropic) using the user's `ANTHROPIC_API_KEY` environment variable.
- **FR-004**: System MUST use Claude Haiku for all conversational turns and Claude Sonnet only for the first code analysis of each newly referenced file.
- **FR-005**: System MUST NEVER produce a direct answer, code fix, or solution in any response. Every response MUST contain at least one question or challenge.
- **FR-006**: System MUST read local files when file paths are detected in the problem description or user responses, and incorporate specific code references (line numbers, function names, variables) into questions.
- **FR-007**: System MUST escalate intensity when the developer asks for direct answers (e.g., "just tell me", "what's the fix").
- **FR-008**: System MUST display a growth score summary at session end containing: questions-to-root-cause count, skill dimension ratings with visual bar charts, and a philosophy quote.
- **FR-009**: System MUST persist session data to `.nietzschian/sessions/` in the current working directory as per-project structured JSON files containing: session ID, timestamp, problem description, intensity level, full Q&A transcript, skill scores, and outcome.
- **FR-010**: System MUST embed contextually relevant philosophy quotes during the session: Nietzsche for avoidance, Seneca for overwhelm, Sun Tzu for strategic moments.
- **FR-011**: System MUST display a clear, actionable error message when `ANTHROPIC_API_KEY` is missing or invalid.
- **FR-012**: System MUST gracefully handle session exit via `exit`, `quit`, Ctrl+C, or Ctrl+D.
- **FR-013**: System MUST compare current session performance against historical sessions when prior data exists.
- **FR-014**: System MUST NOT make any network requests except to the Anthropic API. No telemetry, no analytics, no crash reporting.
- **FR-015**: System MUST render skill dimension ratings as Unicode block characters (e.g., `████████░░`) in the terminal.
- **FR-016**: System MUST allow the developer to explicitly end a session as "solved" by typing `solved` or `found it`. No other mechanism may mark a session as solved.
- **FR-017**: System MUST evaluate reasoning quality per-turn using the LLM, tag observable behaviors (e.g., "guessed without evidence", "checked assumptions"), and normalize scores to a 1-10 scale per skill dimension at session end.
- **FR-018**: System MUST implement a sliding context window for long sessions: preserve the original problem description, code context, and recent turns in full; automatically summarize older turns to stay within model context limits.

### Key Entities

- **Session**: A single debug interaction from start to finish. Contains problem description, intensity level, full Q&A transcript, skill scores, outcome (solved/abandoned), timestamps, and metadata.
- **Growth Profile**: Aggregated view across sessions. Tracks skill dimensions over time, session counts, solve rates, and trends.
- **Skill Dimension**: A measured aspect of debugging ability (assumption-checking, evidence-gathering, root-cause speed). Scored 1-10 per session via LLM behavior tagging, tracked over time.
- **Philosophy Quote**: A curated quote with metadata: source philosopher, applicable context (avoidance, overwhelm, strategy, victory, defeat), and the quote text.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A developer can go from `nietzschian debug "problem"` to a completed session with growth score in under 15 minutes for a typical debugging problem.
- **SC-002**: The tool produces zero direct answers or code fixes across all intensity levels — 100% question-only responses.
- **SC-003**: When a file path is provided, 100% of opening questions reference specific elements from that file (function names, line numbers, or variable names).
- **SC-004**: A developer using the tool 3+ times per week can observe measurable trends in their growth profile within 2 weeks of usage.
- **SC-005**: First-time setup (install + set API key + first debug session) completes in under 5 minutes.
- **SC-006**: Each intensity level produces a distinctly different tone and questioning style, identifiable by a blind reviewer with 90%+ accuracy.
- **SC-007**: Philosophy quotes are contextually relevant to the debugging moment at least 80% of the time, as judged by the developer.

## Assumptions

- Users have Node.js >= 18.0.0 installed.
- Users can obtain and set an Anthropic API key independently.
- The Claude Haiku model provides sufficient quality for conversational question generation. Sonnet is reserved for code analysis and complex reasoning.
- Terminal supports Unicode characters for rendering skill bar charts.
- `.nietzschian/sessions/` in the current working directory is the storage location (per-project, not global).
- The philosophy quote corpus is curated and bundled with the tool (not fetched from an external source).
- Session JSON schema will use versioning to handle forward compatibility across tool upgrades.

## Scope

### In Scope

- `nietzschian debug` command with interactive session loop
- Three intensity levels (socrates, nietzsche, zarathustra)
- Claude API integration (Haiku + Sonnet, BYOK)
- Local file reading and code-aware questioning
- Session persistence to `.nietzschian/sessions/`
- Growth score with visual bar charts at session end
- Philosophy quote integration (during session + at session end)
- Graceful error handling (missing API key, invalid key, no connection, rate limits)

### Out of Scope

- `nietzschian investigate` command (future feature)
- `nietzschian reflect` command (future feature)
- Unworldly integration / `nietzschian review` (v2)
- Team/shared session features
- Web UI or non-CLI interfaces
- Custom philosophy quote packs
- Language-specific code analysis (tool is language-agnostic; it reads files as text)
- AI model selection beyond Haiku/Sonnet (no OpenAI, no local models for v1)

## Dependencies

- Anthropic Claude API (Haiku and Sonnet models)
- Node.js >= 18.0.0 runtime
- User's terminal with Unicode support
- Local filesystem access for session storage

## Risks

- **LLM compliance risk**: Claude may occasionally produce a direct answer despite system prompts. Mitigation: post-processing validation layer that detects and filters answer-like responses before displaying to user.
- **Quote relevance risk**: Contextual quote matching may feel forced or irrelevant. Mitigation: curate a large enough corpus with fine-grained context tags; allow "no quote" as a valid outcome for turns where no quote fits well.
- **Session data growth**: Heavy users may accumulate large session directories. Mitigation: document data location; consider optional cleanup commands in future versions.
