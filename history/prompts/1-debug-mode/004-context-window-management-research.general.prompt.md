---
id: "004"
title: Context Window Management Research
stage: general
date: 2026-02-25
surface: agent
model: claude-sonnet-4-6
feature: 1-debug-mode
branch: 1-debug-mode
user: TechTiesIbrahim
command: manual research prompt
labels: ["context-window","sliding-window","token-counting","summarization","system-prompt","persona-enforcement"]
links:
  spec: specs/1-debug-mode/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - null
tests:
  - null
---

## Prompt

Research strategies for managing conversation context windows in LLM-powered CLI tools. Specifically:

1. What are the context window sizes for Claude Haiku and Claude Sonnet (latest models as of Feb 2026)?
2. How do you implement a sliding window strategy for long conversations?
   - Keep: system prompt + initial context + recent N turns
   - Summarize: older turns compressed into a summary
   - What's a good threshold for when to trigger summarization?
3. How do you estimate token counts without calling the API? (tiktoken equivalent for Claude, or simple heuristic)
4. What's a good approach for the summarization call itself? (use same model? separate call?)

Also research: best practices for structuring system prompts for Claude that enforce behavior (like "never give direct answers"). Any known techniques for making Claude strictly follow character/persona rules?

This is research only, not implementation.

## Response snapshot

Comprehensive research findings delivered covering: Claude model context sizes (Haiku 200K standard, Sonnet 4.6 1M token beta), sliding window implementation strategies with 80% threshold recommendation, token estimation heuristics (3.5 chars/token or chars/4), summarization call model recommendations (Haiku for cost efficiency), and system prompt persona enforcement techniques using XML tags, role definition, and behavioral contracts.

## Outcome

- Impact: Research findings inform implementation of FR-018 (sliding context window) and FR-005 (never give direct answers) from the debug-mode spec
- Tests: None — research only
- Files: None — research only
- Next prompts: /sp.plan to translate findings into concrete implementation decisions for context management and system prompt design
- Reflection: The 80% threshold for triggering summarization is the consensus across multiple production CLI tools (goose, Claude Code, Roo Code). The key insight that "never" constraints in system prompts are soft and require a post-processing validation layer aligns with the risk already documented in spec.md ("LLM compliance risk").

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A — research task
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Prototype a system prompt using XML behavioral tags and test against FR-005 (zero direct answers)
