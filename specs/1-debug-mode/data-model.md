# Data Model: Debug Mode

**Branch**: `1-debug-mode` | **Date**: 2026-02-25

## Entities

### Session

A single debug interaction from start to finish. Stored as one JSON file per session in `.nietzschian/sessions/`.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `schemaVersion` | `number` | Schema version for forward compatibility. Current: `1` |
| `id` | `string` | UUID v4. Generated at session start |
| `timestamp` | `string` | ISO 8601 start time |
| `endTimestamp` | `string` | ISO 8601 end time |
| `problemDescription` | `string` | Verbatim problem text from CLI argument |
| `intensity` | `"socrates" \| "nietzsche" \| "zarathustra"` | Intensity level used |
| `outcome` | `"solved" \| "abandoned"` | How the session ended |
| `questionsToRootCause` | `number` | Total turns before solve/abandon |
| `codeFiles` | `string[]` | File paths read during session |
| `transcript` | `Turn[]` | Full Q&A exchange (see Turn below) |
| `skillScores` | `SkillScores` | Final normalized scores (see below) |
| `behaviorTags` | `BehaviorTag[]` | Per-turn behavior observations |

**Identity**: `id` (UUID v4, unique per session)
**Storage**: `.nietzschian/sessions/{id}.json`
**Lifecycle**: Created at session start → updated per turn → finalized at session end

---

### Turn

A single exchange within a session (one tool question + one developer response).

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `turnNumber` | `number` | 1-indexed position in session |
| `question` | `string` | The tool's question/challenge |
| `response` | `string` | The developer's answer |
| `model` | `string` | Model ID used for this turn |
| `quoteUsed` | `Quote \| null` | Philosophy quote embedded in this turn, if any |
| `behaviorTags` | `string[]` | Behaviors observed in developer's response |
| `timestamp` | `string` | ISO 8601 timestamp of the turn |

**Note**: `question` for turn 1 is the opening question. `response` may be empty if session was abandoned mid-turn.

---

### SkillScores

Normalized skill dimension ratings at session end.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `assumptionChecking` | `number` | 1-10 scale. Did the developer question their assumptions? |
| `evidenceGathering` | `number` | 1-10 scale. Did they check logs/data before hypothesizing? |
| `rootCauseSpeed` | `number` | 1-10 scale. How efficiently did they narrow down? |

**Scoring**: LLM evaluates each turn's `response`, tags behaviors, and at session end normalizes the tags into 1-10 scores. The LLM sees the full transcript and produces scores in a structured JSON call.

---

### BehaviorTag

An observable reasoning behavior tagged by the LLM during the session.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `turnNumber` | `number` | Which turn this was observed in |
| `tag` | `string` | Behavior identifier (see vocabulary below) |
| `dimension` | `string` | Which skill dimension this maps to |

**Behavior vocabulary** (extensible):
- `guessed-without-evidence` → evidenceGathering (negative)
- `checked-logs` → evidenceGathering (positive)
- `questioned-assumption` → assumptionChecking (positive)
- `assumed-without-checking` → assumptionChecking (negative)
- `narrowed-scope` → rootCauseSpeed (positive)
- `went-broad-unnecessarily` → rootCauseSpeed (negative)
- `asked-for-answer` → assumptionChecking (negative, triggers intensity escalation)

---

### Quote

A curated philosophy quote with context metadata.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `text` | `string` | The quote itself |
| `philosopher` | `string` | Attribution (Nietzsche, Seneca, Sun Tzu, etc.) |
| `context` | `string` | When to use: `avoidance`, `overwhelm`, `strategy`, `victory`, `defeat`, `perseverance` |
| `source` | `string` | Book/work the quote is from |

**Storage**: Bundled as a static JSON corpus in the npm package. Not fetched externally.

---

### GrowthProfile

Aggregated view computed from all sessions in `.nietzschian/sessions/`. Not stored separately — computed on demand from session files.

**Computed fields**:

| Field | Type | Description |
|-------|------|-------------|
| `totalSessions` | `number` | Count of all session files |
| `solvedCount` | `number` | Sessions with outcome "solved" |
| `abandonedCount` | `number` | Sessions with outcome "abandoned" |
| `averageScores` | `SkillScores` | Mean scores across all sessions |
| `recentTrend` | `TrendMap` | Per-dimension: "improving" / "declining" / "stable" |

**Trend calculation**: Compare average of last 5 sessions vs previous 5 sessions per dimension. Delta > +1 = improving, delta < -1 = declining, else stable.

## State Transitions

### Session Lifecycle

```
[not started] → session start → [active]
[active] → developer types "solved"/"found it" → [solved] → growth score → [complete]
[active] → developer types "exit"/"quit"/Ctrl+C → [abandoned] → growth score → [complete]
[active] → developer types "I give up" → [lifeline] → one more question → [active] or [abandoned]
[complete] → session JSON written to disk
```

## Schema Versioning

Session JSON files include `schemaVersion: 1`. On load, the tool checks the version:
- If `schemaVersion` matches current: load normally
- If `schemaVersion` is older: apply migration (add default values for new fields)
- If `schemaVersion` is newer: warn but attempt best-effort load (ignore unknown fields)
