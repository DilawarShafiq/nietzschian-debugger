# Nietzschian Debugger

![Nietzschian Debugger: the debugger that only asks questions](assets/banner.png)

> "What doesn't kill your code makes it stronger."

**It won't fix your bug. It'll fix you.** Every other tool hands you the answer; Nietzschian Debugger hands the question back.

You paste your bug. It doesn't fix it. Instead, it:

- Challenges your assumptions about what's happening
- Forces you to confront the evidence you're avoiding
- Tears apart your weak reasoning until only truth remains
- Guides you to the "aha!" moment — YOUR moment, not the AI's

## Why?

AI is making developers weaker. Copy-paste from ChatGPT, ship, repeat. Nobody understands their own code anymore. **Nietzschian Debugger forges stronger developers** — through struggle, not shortcuts.

This isn't anti-AI — it runs on Claude, on purpose. It's anti-*outsourcing-your-thinking*. Every other tool uses the model to hand you the answer; this one uses it to hand the question back.

> "He who has a why to debug can bear almost any how."

## Installation

```bash
# Python 3.10+
pip install nietzschian-debugger
nietzschian debug "your bug"
```

**No API key yet? See it in action first — no key, no cost:**
```bash
nietzschian demo
```

> **Note:** the current tool is the Python package above. The old `npx nietzschian-debugger` serves a stale pre-rewrite build — it has been deprecated in favour of the pip install.

**Requirements:**
- Python >= 3.10
- An Anthropic API key (BYOK) — *or* bring another model (OpenAI, Gemini, DeepSeek, …), or run a local **Ollama** model, which needs no key. See [Use any model](#use-any-model).

## Setup

Set your Anthropic API key:

```bash
# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Windows (CMD)
set ANTHROPIC_API_KEY=sk-ant-...
```

## Quick Start

```bash
# Start a debugging session (default: nietzsche intensity)
nietzschian debug "My API returns 500 but only on Tuesdays"

# Gentle mode — for when you need guidance, not punishment
nietzschian debug --intensity socrates "My login endpoint fails randomly"

# Maximum intensity — for seniors who want pain
nietzschian debug --intensity zarathustra "Memory leak in production"

# Point it at specific code
nietzschian debug "Auth fails in ./src/middleware/auth.ts"

# Interrogate your actual uncommitted changes (feeds the git diff as context)
nietzschian debug --diff "tests started failing after my last change"

# Use any model — Claude by default; or OpenAI, Gemini, DeepSeek, local Ollama…
nietzschian debug --model ollama:llama3.1 "my function returns null sometimes"
```

## Use any model — API or local

Claude is the default and the sharpest experience, but you can bring any model —
most speak the OpenAI API, so they just work:

```bash
# Hosted (set the matching key: OPENAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY, …)
nietzschian debug --model openai:gpt-4o-mini "..."
nietzschian debug --model deepseek:deepseek-chat "..."
nietzschian debug --model gemini:gemini-1.5-flash "..."

# Local — no key, no cost, runs offline
nietzschian debug --model ollama:llama3.1 "..."
```

Install the provider deps once: `pip install "nietzschian-debugger[providers]"`.
Supported: **openai, gemini, deepseek, groq, mistral, together, openrouter, xai, ollama, lmstudio** — plus `custom:<model>` with `NIETZSCHIAN_BASE_URL` for any other OpenAI-compatible endpoint.

> Honest caveat: the "never give answers" discipline is sharpest on Claude. Smaller local models leak and over-ask more (the built-in validator catches some of it, not all).

## Share a session

Your sessions are made to be shared. Turn the last one into clean markdown:

```bash
nietzschian share            # most recent session, to your terminal
nietzschian share -o run.md  # or save it to a file
```

## Three Intensity Levels

| Level | Style | Best For |
|-------|-------|----------|
| `socrates` | Warm, guiding, scaffolded questions | Juniors, learning fundamentals |
| `nietzsche` | Direct, confrontational, no hand-holding | Daily debugging (default) |
| `zarathustra` | Brutal, adversarial, hostile to weak reasoning | Seniors who want real pain |

Pick a level with `--intensity` (or `-i`); the default is `nietzsche`:

```bash
nietzschian debug -i socrates "my bug"
nietzschian debug --intensity zarathustra "my bug"
```

## How a Session Looks

```
$ nietzschian debug "login endpoint returns 403, but only for users who signed up before last week; new signups work; same code path; Node/Express"

Nietzschian Debugger [Nietzsche mode]


[Turn 1]
You said "same code path" — but the data is screaming that something
changed between last week and today.

What is different about the user record itself between those who signed
up before last week and those who signed up after?

> I assumed the records were identical. Let me actually compare one.

[Turn 2]
"Assumed." There is the word you built a week of debugging on. Stop
assuming and read two rows side by side.

What field exists on an old account that a new signup was never given?

> ...the old ones carry a legacy role claim the new ones don't, and the
  auth middleware rejects any token without it.

[Turn 3]
There it is. The bug was never in the code — it was in your certainty
that "same code path" meant "same data." You stopped looking exactly
where the difference lived.

> found it

Session Complete -- 3 questions to root cause (Solved)

Your Debugging Profile:
┣ Assumption-checking    ████████░░  strong
┣ Evidence-gathering     ██████░░░░  moderate
┗ Root cause speed       ████████░░  strong

"Man is something that shall be overcome."
 -- Friedrich Nietzsche
```

**Or when you call a test "flaky":**

```
$ nietzschian debug "integration test passes locally but fails in CI — it's flaky, I just rerun until it's green"

Nietzschian Debugger [Nietzsche mode]


[Turn 1]
"Flaky." The word you reach for when a test has found something true and
you'd rather it hadn't. A test that fails one run in three isn't random —
it's telling you something is ordered that you assumed was not.

What does CI have, or do in a different order, that your machine does not?

> idk, maybe the database isn't ready yet

[Turn 2]
"Maybe" — you named a suspect and refused to question it in the same
breath. A database that wasn't ready would throw a connection error, not a
wrong answer. Unless your test is reading rows another test wrote.

Do your tests share a database, and are they guaranteed to run in order?

> ...they share one. locally they always run alphabetically

[Turn 3]
There it is. "Flaky" was the mask on a race you refused to see — two tests
fighting over the same rows, hidden on your machine by an accident of
alphabetical ordering that CI parallelizes away. The test was never flaky.
It was honest, and you were not.

Will you isolate the data, or keep rolling the dice until they fall green?

> oh. found it

Session Complete -- 3 questions to root cause (Solved)

Your Debugging Profile:
┣ Assumption-checking    ███████░░░  strong
┣ Evidence-gathering     █████░░░░░  moderate
┗ Root cause speed       ████████░░  strong

"No victor believes in chance."
 -- Friedrich Nietzsche
```

## Session Commands

| Command | Effect |
|---------|--------|
| `solved` or `found it` | End session — you found the root cause |
| `I give up` | Get one lifeline question, then exit |
| `exit` or `quit` | Abandon session immediately |
| `Ctrl+C` / `Ctrl+D` | Force quit |

## Features

- **Never Gives Answers** — Every response is a question. The tool will NEVER tell you the fix.
- **Real Code Reading** — Reference a file path and it reads YOUR actual code, not generic examples.
- **Contextual Philosophy** — Nietzsche when you're avoiding, Seneca when overwhelmed, Sun Tzu when you need strategy.
- **Growth Score** — Track your debugging skills across sessions with visual bar charts.
- **Session History** — All sessions saved locally in `.nietzschian/sessions/` for trend tracking.
- **Sliding Context** — Long sessions don't crash; older turns are transparently summarized.

## The Philosophy

| Traditional AI | Nietzschian Debugger |
|---------------|---------------------|
| "Here's the fix" | "What have you tried?" |
| Makes you dependent | Makes you dangerous |
| You learn nothing | You learn everything |
| Fast but shallow | Painful but permanent |
| AI gets smarter | YOU get smarter |

## Who Is This For?

- **Junior developers** who want to actually learn, not just copy-paste
- **Senior developers** who miss the struggle that made them good
- **Engineering managers** who want their team thinking, not just prompting
- **Bootcamp students** building real debugging intuition
- **Anyone** who believes the best developer is a self-reliant one

## Development

```bash
# Clone and install
git clone https://github.com/DilawarShafiq/nietzschian-debugger.git
cd nietzschian-debugger
pip install -e ".[dev]"

# Run tests (121 tests)
pytest

# Run the CLI locally
nietzschian debug "test problem"
```

## Tech Stack

- Python >= 3.10
- Claude API via the Anthropic SDK
- Click for the CLI, Rich for the terminal UI
- pytest for testing

## License

MIT
