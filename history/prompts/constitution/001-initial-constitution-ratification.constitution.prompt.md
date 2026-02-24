---
id: 001
title: Initial Constitution Ratification
stage: constitution
date: 2026-02-24
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: Dilawar Gopang
command: /sp.constitution
labels: ["constitution", "principles", "ratification", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Write the constitution for the socratic-debugger project.

1. Read the existing template at C:\Users\TechTiesIbrahim\socratic-debugger\.specify\memory\constitution.md
2. Read the README at C:\Users\TechTiesIbrahim\socratic-debugger\README.md for project context
3. The existing constitution.md may already have content (it was written earlier). Read it and enhance it to the full template format. The project is:

**Socratic Debugger** — The anti-AI debugger. Won't fix your bugs — teaches you to. Socratic questioning for developers.

Core principles:
1. **Never Give Answers** — The tool MUST never directly fix bugs or provide solutions. It MUST only ask questions that guide the developer toward understanding. Hints are allowed only after the developer demonstrates effort.
2. **Build Developer Intuition** — Every session MUST make the developer stronger. Questions MUST target the developer's reasoning gaps, not just the surface symptoms.
3. **Evidence-Based Questioning** — Questions MUST always reference specific code, logs, error messages, or data. Never ask vague or hand-wavy questions. Point to the evidence.
4. **Adaptive Difficulty** — MUST adjust questioning depth based on the developer's demonstrated skill level. Junior developers get more scaffolding; senior developers get harder challenges.
5. **Session Memory** — MUST track debugging sessions over time. Show the developer their growth patterns, common reasoning mistakes, and areas of improvement.
6. **Privacy-First** — All session data stays local. Code snippets and debugging context MUST never leave the user's machine.

Tech stack: TypeScript, Node.js, npm distribution. Testing: vitest. Code quality: strict TypeScript, ESM modules.

4. Write the completed constitution to C:\Users\TechTiesIbrahim\socratic-debugger\.specify\memory\constitution.md

Include the Sync Impact Report as HTML comment at top. Version 1.0.0, ratified 2026-02-24.

5. Create the PHR directory and file.
6. Stage and commit everything.

## Response snapshot

Ratified the Socratic Debugger constitution v1.0.0 with 6 core principles:

1. **Never Give Answers** — Tool must only ask questions; hints allowed after demonstrated effort with gradual escalation (nudge, pointed question, narrow hint, broad hint).
2. **Build Developer Intuition** — Questions progress broad-to-narrow, target reasoning gaps, end with reflection prompts, and surface anti-patterns over time.
3. **Evidence-Based Questioning** — Every question must reference specific code, logs, error messages, or data. Questions must be falsifiable.
4. **Adaptive Difficulty** — Skill inferred from responses (not self-reported). Adjusts within sessions. Junior gets scaffolding, senior gets counter-factuals.
5. **Session Memory** — Local JSON storage in `.socratic/sessions/`. Cross-session pattern analysis. Concrete growth metrics.
6. **Privacy-First** — Zero network requests, zero telemetry, fully offline, sharing is explicit user action only.

Enhanced from draft skeleton to full constitution format with Sync Impact Report, Technology Stack, Development Workflow, and Governance sections.

## Outcome

- Impact: Constitution ratified — establishes authoritative principles for all Socratic Debugger development decisions
- Tests: none (documentation artifact)
- Files: 1 created/updated (.specify/memory/constitution.md), 1 created (PHR)
- Next prompts: Define first feature spec (debug mode), create project scaffolding (package.json, tsconfig.json, vitest config)
- Reflection: The "Never Give Answers" principle is the most critical and differentiating — it must be defended in every feature design review

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS — all 6 principles expanded with actionable MUST constraints
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution compliance in first feature spec
