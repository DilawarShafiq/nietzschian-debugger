<!--
  Sync Impact Report
  ==================
  Version change: 0.0.0 (template) → 1.0.0
  Modified principles: All new (initial ratification)
  Added sections: Technology Stack, Development Workflow, Governance
  Removed sections: None (supersedes draft skeleton)
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ No update needed (Constitution Check is dynamic)
    - .specify/templates/spec-template.md ✅ No update needed (spec is principle-agnostic)
    - .specify/templates/tasks-template.md ✅ No update needed (Ship Small aligns with incremental delivery)
  Follow-up TODOs: None
-->

# Socratic Debugger Constitution

## Project Identity

- **Name**: Socratic Debugger
- **Purpose**: An anti-AI debugging tool that teaches developers to find and fix their own bugs through Socratic questioning. Makes developers stronger, not more dependent.
- **Tagline**: "I won't fix your bugs. I'll teach you to."

## Core Principles

### I. Never Give Answers

The tool MUST never directly fix bugs or provide solutions. It MUST
only ask questions that guide the developer toward understanding.

- Commands MUST NOT output code fixes, patches, or corrected snippets.
- If the developer asks "what's the fix?", the tool MUST respond with
  a question that helps them discover the fix themselves.
- Hints are allowed ONLY after the developer demonstrates effort
  (e.g., answering at least 2-3 questions in the session).
- Hint escalation MUST be gradual: nudge → pointed question →
  narrow hint → broad hint. Never jump to the answer.
- Any mode (debug, investigate, reflect) MUST adhere to this
  principle without exception.

### II. Build Developer Intuition

Every session MUST make the developer stronger. Questions MUST target
the developer's reasoning gaps, not just the surface symptoms.

- Questions MUST progress from broad ("What do you think is happening?")
  to narrow ("What does line 42 return when `user` is null?").
- The tool MUST identify patterns in the developer's reasoning and
  challenge weak spots (e.g., if they always assume the database is
  fine, ask about the database).
- Sessions MUST end with a reflection prompt: "What did you learn?
  What would you check first next time?"
- The tool MUST track and surface reasoning anti-patterns over time
  (e.g., "You tend to skip checking environment variables — 3 of
  your last 5 bugs were env-related.").

### III. Evidence-Based Questioning

Questions MUST always reference specific code, logs, error messages,
or data. Never ask vague or hand-wavy questions.

- Every question MUST point to concrete evidence: a line of code, a
  log entry, an error message, a stack trace, or a data value.
- The tool MUST NOT ask generic questions like "Have you tried
  debugging?" or "What do you think went wrong?" without context.
- When analyzing code, questions MUST reference specific files, line
  numbers, function names, or variable values.
- If the developer provides insufficient context, the tool MUST ask
  for specific evidence before proceeding ("Can you share the error
  message?" or "What does your server log show?").
- Questions MUST be falsifiable: the developer should be able to
  verify the answer by checking specific evidence.

### IV. Adaptive Difficulty

The tool MUST adjust questioning depth based on the developer's
demonstrated skill level.

- Skill assessment MUST be inferred from the developer's responses,
  not self-reported.
- Junior developers get more scaffolding: shorter reasoning chains,
  more yes/no questions, and terminology explanations when needed.
- Senior developers get harder challenges: "Why did you rule out
  X?", "What's the second-order effect of this?", counter-factual
  questions.
- Difficulty MUST adjust within a session based on response quality,
  not just at session start.
- The tool MUST never be condescending. Adaptive difficulty means
  meeting the developer where they are, not talking down to them.

### V. Session Memory

The tool MUST track debugging sessions over time. Show the developer
their growth patterns, common reasoning mistakes, and areas of
improvement.

- All session data MUST be stored locally in structured format
  (JSON files in `.socratic/sessions/`).
- The reflect mode MUST surface cross-session patterns: common bug
  categories, reasoning improvements, recurring blind spots.
- Session history MUST be queryable: by date, by bug type, by
  outcome (solved/abandoned), by reasoning pattern.
- Growth metrics MUST be concrete: "You solved 3/5 sessions
  independently this week, up from 1/5 last week."
- Session data MUST survive tool upgrades without migration pain.

### VI. Privacy-First

All session data stays local. Code snippets and debugging context
MUST never leave the user's machine.

- The tool MUST NOT make outbound network requests for any reason.
- No analytics, crash reporting, telemetry, or usage tracking.
- Session recordings (which contain code snippets and debugging
  context) MUST be stored only in local filesystem.
- The tool MUST work fully offline with zero network dependency.
- If a future feature requires network access (e.g., team sharing),
  it MUST be opt-in, clearly documented, and never enabled by
  default.
- Sharing session data MUST be an explicit user action, never
  automatic.

## Technology Stack

- **Language**: TypeScript (strict mode, no `any` types)
- **Runtime**: Node.js >= 18.0.0
- **Module system**: ESM (`"type": "module"`)
- **Distribution**: npm / npx (`npx socratic debug ...`)
- **Core dependencies**: Minimized; prefer Node.js built-in APIs.
  New dependencies MUST be justified by a clear need.
- **Testing**: vitest
- **Build**: tsc (TypeScript compiler)
- **Session storage**: JSON files in `.socratic/sessions/`

## Development Workflow

- **Code quality**: Strict TypeScript with `"strict": true`. No
  `any` types. All public APIs MUST have explicit return types.
- **Testing**: All questioning strategies MUST have unit tests.
  Adaptive difficulty logic MUST have tests covering junior, mid,
  and senior paths. New features MUST include tests.
- **Commits**: Small, atomic commits. Each commit MUST leave the
  project in a buildable, working state.
- **Branching**: Feature branches off `main`. PRs reviewed before
  merge.
- **Build verification**: `npm run build` MUST succeed with zero
  errors and zero warnings before any commit.

## Governance

This constitution is the authoritative source for all development
decisions in the Socratic Debugger project.

- All PRs and code reviews MUST verify compliance with these
  principles.
- Amendments require: (1) documented rationale, (2) approval from
  maintainers, (3) version bump per semantic versioning below.
- Versioning: MAJOR for principle removals or redefinitions, MINOR
  for new principles or material expansions, PATCH for clarifications
  and wording fixes.
- The "Never Give Answers" principle (I) is foundational and MUST NOT
  be weakened or removed without a full project re-evaluation.

**Version**: 1.0.0 | **Ratified**: 2026-02-24 | **Last Amended**: 2026-02-24
