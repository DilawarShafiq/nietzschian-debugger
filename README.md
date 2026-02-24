# Nietzschian Debugger

> "What doesn't kill your code makes it stronger."

The anti-AI. Every other tool gives you answers. Nietzschian Debugger **confronts you with questions**.

You paste your bug. It doesn't fix it. Instead, it:

- Challenges your assumptions about what's happening
- Forces you to confront the evidence you're avoiding
- Tears apart your weak reasoning until only truth remains
- Guides you to the "aha!" moment — YOUR moment, not the AI's

## Why?

AI is making developers weaker. Copy-paste from ChatGPT, ship, repeat. Nobody understands their own code anymore. **Nietzschian Debugger forges stronger developers** — through struggle, not shortcuts.

> "He who has a why to debug can bear almost any how."

## Installation

```bash
# Install globally
npm install -g nietzschian-debugger

# Or use directly with npx
npx nietzschian-debugger
```

**Requirements:**
- Node.js >= 20.0.0
- An Anthropic API key (BYOK — bring your own key)

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
```

## Three Intensity Levels

| Level | Style | Best For |
|-------|-------|----------|
| `socrates` | Warm, guiding, scaffolded questions | Juniors, learning fundamentals |
| `nietzsche` | Direct, confrontational, no hand-holding | Daily debugging (default) |
| `zarathustra` | Brutal, adversarial, hostile to weak reasoning | Seniors who want real pain |

## How a Session Looks

```
  Nietzschian Debugger v0.1.0 — intensity: nietzsche

You: My login endpoint returns 403 for some users

Nietzschian: You say "some users." That's vague. What separates
             the ones who fail from the ones who don't?

You: I'm not sure, it seems random

Nietzschian: "Random" is the word we use when we haven't looked
             hard enough. What do the server logs say for the 403
             responses? Go look. I'll wait.

You: Let me check... oh, they all have expired JWT tokens

Nietzschian: Now we're getting somewhere. Why would some users
             have expired tokens while others don't? What changed
             recently in your auth system?

You: ... oh. We changed the token TTL last week and didn't
     invalidate existing sessions.

Nietzschian: There it is. You didn't need me to tell you — you
             needed to be forced to look.

Session Complete — 4 questions to root cause (Solved)

Your Debugging Profile:
┣ Assumption-checking    ██████████  strong
┣ Evidence-gathering     ██████░░░░  moderate
┗ Root cause speed       ████████░░  strong

"Man is something that shall be overcome."
 — Friedrich Nietzsche
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
git clone https://github.com/your-username/nietzschian-debugger.git
cd nietzschian-debugger
npm install

# Build
npm run build

# Run tests (121 tests)
npm test

# Run CLI locally
node dist/cli.js debug "test problem"
```

## Tech Stack

- TypeScript (strict mode)
- Node.js >= 20
- Claude API (Haiku for conversation, Sonnet for code analysis)
- Commander.js for CLI
- Vitest for testing

## License

MIT
