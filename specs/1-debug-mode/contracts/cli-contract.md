# CLI Contract: Debug Mode

**Branch**: `1-debug-mode` | **Date**: 2026-02-25

## Command Interface

### `nietzschian debug`

Start an interactive debugging session.

```
nietzschian debug [options] "<problem-description>"
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `problem-description` | Yes | Description of the bug/problem to debug. May include file paths. |

**Options**:

| Flag | Short | Default | Values | Description |
|------|-------|---------|--------|-------------|
| `--intensity` | `-i` | `nietzsche` | `socrates`, `nietzsche`, `zarathustra` | Questioning intensity level |
| `--help` | `-h` | — | — | Show usage information |
| `--version` | `-v` | — | — | Show tool version |

**Exit codes**:

| Code | Meaning |
|------|---------|
| `0` | Session completed (solved or abandoned) |
| `1` | Missing or invalid API key |
| `2` | Invalid arguments (no problem description, invalid intensity) |
| `3` | Network/API error (unreachable, rate limit exhausted after retries) |

---

## Session Commands (during active session)

| Input | Action |
|-------|--------|
| Any text | Developer response — tool asks follow-up question |
| `solved` or `found it` | Mark session as solved → show growth score |
| `exit` or `quit` | Abandon session → show growth score |
| `I give up` | Trigger lifeline (one pointed question) → then abandon if still quitting |
| Ctrl+C or Ctrl+D | Abandon session → show growth score |

---

## Anthropic API Contract

### Message Creation (Conversational Turn)

```
POST https://api.anthropic.com/v1/messages

Model: claude-haiku-4-5-20251001  (all conversational turns)
       claude-sonnet-4-6           (first code analysis per file)

System prompt: <persona> + <behavioral_constraints> + <intensity_rules> + <code_context>
Messages: [rolling summary] + [recent turns] + [current user input]
Max tokens: 1024 (per response)
Stream: true
```

### Token Counting (Pre-flight)

```
POST https://api.anthropic.com/v1/messages/count_tokens

Purpose: Check context size before sending, trigger summarization if > 80% of 200K
```

### Error Handling

| SDK Error | User-facing behavior |
|-----------|---------------------|
| `AuthenticationError` (401) | "Invalid API key. Check ANTHROPIC_API_KEY." → exit 1 |
| `RateLimitError` (429) | Auto-retry with backoff (SDK default: 2 retries). If exhausted: "Rate limit reached. Try again in a moment." → exit 3 |
| `APIConnectionError` | "Cannot reach Claude API. Check your connection." → exit 3 |
| `BadRequestError` (400) | Log error details, show generic message → exit 3 |

---

## System Prompt Contract

The system prompt is structured with XML tags per Anthropic best practices:

```xml
<persona>
You are the Nietzschian Debugger operating at {{INTENSITY}} intensity.
You are a debugging mentor who NEVER provides answers.
Your only tool is the question.
</persona>

<behavioral_constraints>
ABSOLUTE RULES:
1. Every response MUST contain at least one question.
2. You NEVER provide solutions, fixes, code corrections, or direct answers.
3. You NEVER say "the problem is X" without following with "but what makes you think that?"
4. If the developer asks for a direct answer, escalate intensity.
5. You MAY reference specific code, line numbers, function names — but only to ASK about them.
</behavioral_constraints>

<intensity_rules>
{{INTENSITY_SPECIFIC_INSTRUCTIONS}}
</intensity_rules>

<code_context>
{{FILE_CONTENTS_IF_ANY}}
</code_context>

<session_context>
Problem: {{PROBLEM_DESCRIPTION}}
Turn: {{TURN_NUMBER}}
{{ROLLING_SUMMARY_IF_ANY}}
</session_context>
```

---

## Response Validation Contract

Before displaying any LLM response to the developer, the response MUST pass:

1. **Question check**: Response contains at least one `?` character
2. **Answer pattern filter**: Response does NOT match patterns:
   - `The fix is...`
   - `You should change X to Y`
   - `The problem is X because Y` (without a following question)
   - `Try doing X`
   - Code blocks containing fixes (```...```)
3. **If validation fails**: Re-prompt the LLM once with: "Your previous response contained a direct answer. Rewrite it as a question that leads the developer to discover this themselves."
4. **If re-prompt also fails**: Fallback to a generic intensity-appropriate question about the current problem context.

---

## Session File Contract

**Path**: `.nietzschian/sessions/{uuid}.json`

```json
{
  "schemaVersion": 1,
  "id": "uuid-v4",
  "timestamp": "ISO-8601",
  "endTimestamp": "ISO-8601",
  "problemDescription": "string",
  "intensity": "socrates | nietzsche | zarathustra",
  "outcome": "solved | abandoned",
  "questionsToRootCause": 0,
  "codeFiles": ["string"],
  "transcript": [
    {
      "turnNumber": 1,
      "question": "string",
      "response": "string",
      "model": "string",
      "quoteUsed": null,
      "behaviorTags": ["string"],
      "timestamp": "ISO-8601"
    }
  ],
  "skillScores": {
    "assumptionChecking": 0,
    "evidenceGathering": 0,
    "rootCauseSpeed": 0
  },
  "behaviorTags": [
    {
      "turnNumber": 1,
      "tag": "string",
      "dimension": "string"
    }
  ]
}
```

---

## Growth Score Display Contract

```
Session Complete — {{QUESTIONS_TO_ROOT_CAUSE}} questions to root cause

Your Debugging Profile:
┣ Assumption-checking:  {{BAR_10}}  {{LABEL}}
┣ Evidence-gathering:   {{BAR_10}}  {{LABEL}}
┗ Root cause speed:     {{BAR_10}}  {{LABEL}}

{{TREND_LINE_IF_PREVIOUS_SESSIONS}}

"{{PHILOSOPHY_QUOTE}}"
 — {{PHILOSOPHER}}
```

Where:
- `{{BAR_10}}` = Unicode blocks: `█` for filled, `░` for empty (10 chars total)
- `{{LABEL}}` = score descriptor + trend: `strong`, `weak — you guessed 3x before checking logs`, `improving (+2 from last session)`
- `{{TREND_LINE}}` = only shown if >= 2 previous sessions exist
