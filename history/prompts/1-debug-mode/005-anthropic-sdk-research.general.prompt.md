---
id: 005
title: Anthropic SDK Research for CLI Tool
stage: general
date: 2026-02-25
surface: agent
model: claude-sonnet-4-6
feature: 1-debug-mode
branch: 1-debug-mode
user: DilawarShafiq
command: research
labels: ["research","anthropic-sdk","typescript","streaming","error-handling","model-ids"]
links:
  spec: specs/1-debug-mode/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/1-debug-mode/005-anthropic-sdk-research.general.prompt.md
tests:
  - none
---

## Prompt

Research the Anthropic TypeScript/Node.js SDK for use in a CLI tool. I need concrete, actionable details:

1. What is the npm package name and latest version?
2. How do you initialize the client with an API key from environment variable?
3. How do you make a messages API call with a system prompt?
4. What are the exact model IDs for Claude Haiku and Claude Sonnet (latest versions as of Feb 2026)?
5. How does streaming work? (for real-time terminal output)
6. What errors does the SDK throw? (auth errors, rate limits, network errors)
7. What is the minimum Node.js version required by the SDK?
8. Does it support ESM imports?

Provide code snippets where possible. This is for research only, not implementation.

## Response snapshot

Comprehensive SDK research completed. Findings documented with code snippets for all 8 questions:
- Package: `@anthropic-ai/sdk` v0.78.0
- Model IDs: `claude-haiku-4-5-20251001` and `claude-sonnet-4-6`
- Streaming via `messages.stream()` with `.on("text", cb)` event handler
- 12 error subclasses mapped to HTTP status codes
- Node.js >= 20 LTS required; dual ESM + CJS module support

## Outcome

- Impact: All SDK integration questions answered with exact API surface for implementation
- Tests: none — research only
- Files: history/prompts/1-debug-mode/005-anthropic-sdk-research.general.prompt.md
- Next prompts: Implementation of Anthropic SDK client wrapper; architecture for Haiku/Sonnet routing
- Reflection: SDK is well-designed for CLI use. The `messages.stream()` high-level helper is the correct choice for terminal streaming. Note: spec says Node >= 18 but SDK requires Node >= 20 — this constraint must be updated in the spec.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A — research task
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): implement client initialization module and test ANTHROPIC_API_KEY validation path
