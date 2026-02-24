---
id: "004"
title: CLI Framework Research ESM TypeScript
stage: general
date: 2026-02-25
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-debug-mode
user: DilawarShafiq
command: research
labels: ["research","cli","esm","typescript","commander","yargs","citty","clipanion","readline","inquirer"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

Research lightweight CLI frameworks for a TypeScript Node.js CLI tool. The constraints are:
- Must work with ESM modules ("type": "module")
- Must work with Node.js >= 18.0.0
- Must support subcommands (e.g., `nietzschian debug "problem"`)
- Must support flags (e.g., `--intensity socrates`)
- Must support interactive REPL-like sessions (user types, tool responds, loop)
- Must be lightweight (minimal dependencies preferred per project constitution)
- TypeScript support required

Compare these options:
1. Commander.js
2. yargs
3. Node.js built-in parseArgs (util.parseArgs from Node 18.3+)
4. citty (by unjs)
5. clipanion

For each, note: ESM support, size/dependencies, interactive session support, TypeScript types.

Also research: What's the best way to do interactive terminal input in Node.js ESM? (readline, readline/promises, inquirer, etc.)

For the interactive REPL loop specifically, research `readline/promises` (Node.js built-in) vs `inquirer` vs `prompts` npm package.

This is research only, not implementation.

## Response snapshot

Full comparison of 5 CLI frameworks and 3 interactive input approaches. See main response for detailed findings. Summary: Commander.js v12 (Node 18+) is the most battle-tested with zero dependencies; citty is the lightest modern ESM-first option; parseArgs is viable for simple cases but requires manual subcommand routing. For interactive REPL, readline/promises (built-in) is recommended for minimal-dependency projects.

## Outcome

- Impact: Research findings documented to inform CLI framework and interactive input selection for the debug-mode feature build.
- Tests: none — research task only
- Files: none — research task only
- Next prompts: Use findings to select framework and design CLI entry point architecture; potentially trigger `/sp.adr` for framework choice.
- Reflection: All five frameworks are ESM-compatible in current versions, but with notable caveats: Commander 15 requires Node 22+, yargs 18 has ESM friction, clipanion v4 is in RC. Commander 12/13 + readline/promises is the lowest-risk combination for Node 18 ESM projects.

## Evaluation notes (flywheel)

- Failure modes observed: npm page WebFetch returned 403; relied on WebSearch results and cross-referencing multiple sources.
- Graders run and results (PASS/FAIL): none — research task
- Prompt variant (if applicable): none
- Next experiment: Prototype Commander.js v13 with readline/promises REPL loop to validate interactive session ergonomics before committing.
