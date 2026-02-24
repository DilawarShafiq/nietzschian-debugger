---
id: 002
title: Debug Mode Feature Specification
stage: spec
date: 2026-02-25
surface: agent
model: claude-opus-4-6
feature: 1-debug-mode
branch: 1-debug-mode
user: Dilawar Shafiq
command: /sp.specify
labels: ["debug-mode", "specification", "core-feature", "intensity-levels", "session-tracking"]
links:
  spec: specs/1-debug-mode/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-debug-mode/spec.md
  - specs/1-debug-mode/checklists/requirements.md
tests:
  - none (specification phase)
---

## Prompt

Here's my vision for what makes this a star-magnet:

The Core Bet

Every AI tool gives answers. This is the only one that refuses to. That's not a gimmick — it's a category. "AI-assisted learning through adversarial questioning." Nobody else is doing this.

My Recommendations

LLM: Claude API (Haiku for speed, Sonnet for depth). You're already in the Anthropic ecosystem. Users bring their own API key — ANTHROPIC_API_KEY. Zero cost to you.

Intensity Levels — this is the killer feature:
- Socrates — Gentle. Guides with warm questions. For juniors.
- Nietzsche — Default. Direct, confrontational, no hand-holding.
- Zarathustra — Brutal. Actively hostile to weak reasoning. For seniors who want pain.

nietzschian debug --intensity zarathustra "My API is slow"

It MUST read actual code — this is what separates it from "ChatGPT but mean". When you say nietzschian investigate ./src/auth.ts, it reads the file, finds the weak spots, and asks you questions about YOUR specific code. Not generic advice.

Build order: debug mode first → investigate second → reflect last. Debug is the hook that gets people to try it.

Session tracking with a growth score — after each session, it rates your debugging process:
Session Complete — 4 questions to root cause

Your Debugging Profile:
┣ Assumption-checking:  ██████████░  strong
┣ Evidence-gathering:   ████░░░░░░  weak — you guessed 3x before checking logs
┣ Root cause speed:     ████████░░  improving (+2 from last session)

"The higher we soar, the smaller we appear to those who cannot fly."

Philosophy quotes woven into every interaction — not decoration, actually relevant to the debugging moment. Nietzsche when you're avoiding the hard question, Seneca when you're overwhelmed, Sun Tzu when you need strategy.

Free, open source, CLI-first — same playbook as Unworldly. Stars first.

The cross-sell with Unworldly — Unworldly watches everything the AI agent does (files + commands). Nietzschian Debugger makes the developer understand WHY things went wrong. They're companion tools — "Unworldly watches the agent. Nietzschian Debugger watches YOU." Future integration: nietzschian review --unworldly-session latest reads an Unworldly session and questions the developer about the agent's decisions. But that's v2 — not now. Proceed with /sp.specify for Debug Mode.

## Response snapshot

Created comprehensive Debug Mode specification with 7 user stories (4 at P1, 3 at P2), 15 functional requirements, 7 measurable success criteria, 8 edge cases, and a passing quality checklist. Key design decisions: three intensity levels (socrates/nietzsche/zarathustra) as co-P1 with the core debug loop, real code reading as co-P1, Claude Haiku for speed + Sonnet for depth, session persistence to `.nietzschian/sessions/`, contextual philosophy quotes from Nietzsche/Seneca/Sun Tzu. Explicitly scoped out: investigate mode, reflect mode, Unworldly integration (all future).

## Outcome

- ✅ Impact: Full feature specification for Debug Mode — the product's core hook and first feature to build
- 🧪 Tests: none (specification phase — tests defined in acceptance scenarios for implementation)
- 📁 Files: specs/1-debug-mode/spec.md, specs/1-debug-mode/checklists/requirements.md
- 🔁 Next prompts: `/sp.clarify` to refine any underspecified areas, then `/sp.plan` to architect the implementation
- 🧠 Reflection: User provided exceptionally clear vision with specific examples. Minimal clarification needed — all decisions had clear defaults from the user's input. The "never give answers" principle from the constitution directly maps to FR-005.

## Evaluation notes (flywheel)

- Failure modes observed: None — user input was comprehensive enough to resolve all potential NEEDS CLARIFICATION markers
- Graders run and results (PASS/FAIL): Specification quality checklist — PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.clarify to surface any blind spots not caught by the quality checklist
