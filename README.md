# Nietzschian Debugger

![Nietzschian Debugger: the debugger that hands the question back](assets/banner.png)

[![PyPI](https://img.shields.io/pypi/v/nietzschian-debugger)](https://pypi.org/project/nietzschian-debugger/)
[![Python](https://img.shields.io/pypi/pyversions/nietzschian-debugger)](https://pypi.org/project/nietzschian-debugger/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> "What doesn't kill your code makes it stronger."

**It won't fix your bug. It'll fix you.** Every other tool hands you the answer; Nietzschian Debugger hands the question back.

You paste your bug. It doesn't fix it. Instead, it:

- Challenges your assumptions about what's happening
- Forces you to confront the evidence you're avoiding
- Attacks the assumption you're proudest of — the one you stopped questioning
- Guides you to the fix yourself — your realization, not the AI's

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
- An Anthropic API key (BYOK) — *or* bring another model (OpenAI, Gemini, DeepSeek, …), or run a local **Ollama** model, which needs no key. See [Models — set one up, switch any time](#models--set-one-up-switch-any-time).

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
# Start a debugging session (adaptive by default — it reads your state and shifts lens)
nietzschian debug "My API returns 500 but only on Tuesdays"

# Force a single lens instead of adapting
nietzschian debug --lens socrates "My login endpoint fails randomly"
nietzschian debug --lens zarathustra "Memory leak in production"

# Point it at specific code
nietzschian debug "Auth fails in ./src/middleware/auth.ts"

# Interrogate your actual uncommitted changes (feeds the git diff as context)
nietzschian debug --diff "tests started failing after my last change"

# Use any model — Claude by default; or OpenAI, Gemini, DeepSeek, local Ollama…
nietzschian debug --model ollama:llama3.1 "my function returns null sometimes"
```

## Models — set one up, switch any time

**Claude is the default and the sharpest experience.** With `ANTHROPIC_API_KEY` set,
every command just works with no flags. But the tool is model-agnostic — it speaks
the OpenAI API, so almost any hosted or local model works too.

### Switching models

The model is chosen *per command* with `--model`. There's no config to edit and no
state to reset — you switch just by changing the flag, or **drop it to return to
Claude**:

```bash
nietzschian debug "my bug"                                # Claude (needs ANTHROPIC_API_KEY)
nietzschian debug "my bug" --model openai:gpt-4o-mini     # a hosted model
nietzschian debug "my bug" --model ollama:llama3.1        # a local model, no key
```

The flag isn't sticky — each run is independent. (There's no mid-session switch yet;
to change model, re-run the command with a different `--model`.)

### Hosted models (bring your own key)

Set the matching key, then select the model:

```bash
export OPENAI_API_KEY=...     # or GEMINI_API_KEY, DEEPSEEK_API_KEY, GROQ_API_KEY, …
nietzschian debug --model openai:gpt-4o-mini "..."
nietzschian debug --model deepseek:deepseek-chat "..."
nietzschian debug --model gemini:gemini-1.5-flash "..."
```

Supported: **openai, gemini, deepseek, groq, mistral, together, openrouter, xai** —
plus `custom:<model>` with `NIETZSCHIAN_BASE_URL` for any other OpenAI-compatible endpoint.

### Local models with Ollama (no key, no cost, offline)

```bash
# 1. Install Ollama (https://ollama.com) and make sure it's running
# 2. Pull a model once:
ollama pull llama3.1
# 3. Add the provider deps once, then point the tool at it:
pip install "nietzschian-debugger[providers]"
nietzschian roast ./messy.py --model ollama:llama3.1
```

(LM Studio works the same way: `--model lmstudio:<model>`.)

### Which local model should I use?

Different jobs reward different kinds of model — and the twist is that the *best*
model for `predict` is the *worst* for `roast`:

| Command | Best local model | Why |
|---|---|---|
| **`roast`**, **`debug`** | a **general chat** model — `llama3.1`, `qwen3` | built for prose and wit |
| **`predict`** | a **coding** model — `qwen2.5-coder` | it wants a precise function call — exactly the dare |

A coding model asked to *roast* reaches for JSON instead of a joke; a chat model asked
to *predict* is vaguer about the exact return value. Match the model to the job.

> Honest caveat: the "never give answers" discipline is sharpest on **Claude**.
> Smaller local models leak and over-ask more — the built-in validator and the
> roast/predict guards catch a lot of it, not all.

## Share a session

Your sessions are made to be shared. Turn the last one into clean markdown:

```bash
nietzschian share            # most recent session, to your terminal
nietzschian share -o run.md  # or save it to a file
```

## Three Lenses — it picks, not you

By default it **adapts**: each turn it reads where you are and shifts between three methods. You don't choose a difficulty — a confused developer can't diagnose their own state, so the tool reads you instead. Nietzsche is home; it shifts only on sustained signals, not twitchily, and the active lens shows in every turn header (`[Turn 3 · socrates]`).

| When you're… | Lens | What it does |
|---|---|---|
| **confused** — you don't know what you mean | `socrates` | Relentless clarification. Defines your vague terms until a testable claim appears. The stingray, not a gentle mentor. |
| **avoiding** — hiding in an assumption | `nietzsche` | The tuning fork. Taps the idol you're proudest of and listens for the hollow ring. |
| **defeated** — ready to quit | `zarathustra` | Affirmation. Reframes the bug as the weight that makes you stronger, and will not let you quit. |

None of them is soft — **adaptivity changes the angle of the blade, never sheathes it.** To pin one lens instead of adapting:

```bash
nietzschian debug --lens socrates "my bug"
nietzschian debug --lens zarathustra "my bug"
```

## How a Session Looks

```
$ nietzschian debug "login endpoint returns 403, but only for users who signed up before last week; new signups work; same code path; Node/Express"

Nietzschian Debugger [Adaptive mode]


[Turn 1 · nietzsche]
You said "same code path" — but the data is screaming that something
changed between last week and today.

What is different about the user record itself between those who signed
up before last week and those who signed up after?

> I assumed the records were identical. Let me actually compare one.

[Turn 2 · nietzsche]
"Assumed." There is the word you built a week of debugging on. Stop
assuming and read two rows side by side.

What field exists on an old account that a new signup was never given?

> ...the old ones carry a legacy role claim the new ones don't, and the
  auth middleware rejects any token without it.

[Turn 3 · nietzsche]
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

Nietzschian Debugger [Adaptive mode]


[Turn 1 · nietzsche]
"Flaky." The word you reach for when a test has found something true and
you'd rather it hadn't. A test that fails one run in three isn't random —
it's telling you something is ordered that you assumed was not.

What does CI have, or do in a different order, that your machine does not?

> idk, maybe the database isn't ready yet

[Turn 2 · nietzsche]
"Maybe" — you named a suspect and refused to question it in the same
breath. A database that wasn't ready would throw a connection error, not a
wrong answer. Unless your test is reading rows another test wrote.

Do your tests share a database, and are they guaranteed to run in order?

> ...they share one. locally they always run alphabetically

[Turn 3 · nietzsche]
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

## Prove You Understand It — `predict`

`debug` interrogates a bug. `predict` interrogates **you**: it dares you to say what
one of your functions returns, then **runs the code** for the truth — never a model
guessing (that can be confidently wrong). At the end it names the *pattern* in your
misses, not a score.

```bash
nietzschian predict ./parsers.py          # 3 dares by default
nietzschian predict ./parsers.py -n 5     # go five rounds
```

```
$ nietzschian predict ./parsers.py

Nietzschian Debugger [predict mode]

3 rounds — type 'quit' (or press Ctrl+C) to stop early.

── Round 1 of 3 ──

You named it truncate, and now you believe it truncates. Sweet certainty. But
look — you gave length a default of zero, and zero is a falsy little god that
answers "if not length". So tell me, prophet:
what does truncate("hello world") return?

your prophecy > "" — it truncates to zero, so nothing

Wrong, and gloriously so. "if not length" caught your zero and handed back the
text untouched, before a single character was cut. You read the name and never
the first line. The guard fired; your logic never ran.

The truth, once run — it returned 'hello world'.

── Round 2 of 3 ──

You wrote dedupe, and I can smell the doubt — most who write it reach for a set
and let the order rot. Did you keep the order, or did you betray it?
what does dedupe([3, 1, 2, 1, 3]) return?

your prophecy > [3, 1, 2]

Right — and not by luck. You kept the first sighting of each and dropped the
echoes. Clean. There was no trap here; some things you simply know.

The truth, once run — it returned [3, 1, 2].

── Round 3 of 3 ──

A tier function, a border drawn at one hundred. Borders are where confidence
goes to die. Stand on the line itself and tell me which side claims you:
what does shipping_tier(100) return?

your prophecy > "freight" — 100 is the heavy tier

Wrong. "weight > 100", and one hundred is not greater than one hundred. You
stood ON the boundary and assumed it pulled you across; it let you fall back to
'parcel'. The strict > you typed yourself is the thing you forgot.

The truth, once run — it returned 'parcel'.

Proof of Understanding

Two of three — and the two you missed were cut from the same cloth. You read
functions by their name and their happy middle, and walk straight past the lines
that quietly decide everything first: the falsy default that returns early, the
strict > that owns its edge. You trust what the code is *for* over what it
*says*. Read the guards before the gift — the boundary is not an afterthought,
it is the whole argument.
```

> It runs your code in a separate process with a timeout — your own functions, called
> the way you'd call them. It only picks functions it can invoke with simple literal
> arguments, and a function that raises is a legitimate answer (predict that too).

## Roast Your Code — `roast`

For when you don't want a question or a fix — you want the truth, fast and funny.
Point it at your worst file; it reads the code's cowardice and laughs. Fixes nothing.

```bash
nietzschian roast ./legacy/utils.py
```

```
$ nietzschian roast ./legacy/utils.py

🔥 Nietzschian Roast

A function named `helper` wrapping a bare `except: pass` — you built a room with
no windows and called it tidy. The bug you're hiding from in there is the only
honest thing you've written all week.
```

> "Not by wrath does one kill, but by laughter." — *Thus Spoke Zarathustra*

## Session Commands

| Command | Effect |
|---------|--------|
| `solved` or `found it` | End session — you found the root cause |
| `I give up` | Get one lifeline question, then exit |
| `exit` or `quit` | Abandon session immediately |
| `Ctrl+C` / `Ctrl+D` | Force quit |

## Features

- **Refuses to Hand You the Fix** — Every response is a question. It's built to withhold the answer, and a model-judge double-checks each reply to catch it when it slips.
- **Proof of Understanding** — `predict` dares you to say what your code returns, then *runs it* for the truth (never a model guessing) and names the pattern in your misses.
- **Nietzschian Roast** — `roast` reads your worst file and burns it down in one or two lines. Fixes nothing. Deeply shareable.
- **Real Code Reading** — Reference a file path and it reads YOUR actual code, not generic examples. `--diff` feeds it your uncommitted changes.
- **Any Model, Even Local** — Claude by default; or OpenAI, Gemini, DeepSeek, Groq, and more — or a local Ollama / LM Studio model with no key and no cost.
- **Try With No Key** — `nietzschian demo` runs a full scripted session so you can see it before committing a key.
- **Shareable Sessions** — `nietzschian share` exports a session as clean markdown you can post.
- **Adaptive Lenses** — it reads your state each turn and shifts between Socrates (when you're confused), Nietzsche (when you're avoiding), and Zarathustra (when you're defeated). You don't pick the difficulty; it reads you.
- **Growth Score** — Track your debugging skills across sessions with visual bar charts.
- **Session History** — All sessions saved locally in `.nietzschian/sessions/` for trend tracking.
- **Sliding Context** — Long sessions don't crash; older turns are transparently summarized.

## Development

```bash
# Clone and install
git clone https://github.com/DilawarShafiq/nietzschian-debugger.git
cd nietzschian-debugger
pip install -e ".[dev]"

# Run the test suite
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
