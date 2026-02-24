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

## Quick Start

```bash
# Start a debugging session
npx nietzschian debug "My API returns 500 but only on Tuesdays"

# Analyze a specific file
npx nietzschian investigate ./src/api/handler.ts

# Review your reasoning journey
npx nietzschian reflect --session latest
```

## How a Session Looks

```
  Nietzschian Debugger v0.1.0

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
             needed to be forced to look. What will you check
             BEFORE deploying auth changes next time?
```

## Features

- **Debug Mode** — Relentless questioning that strips away assumptions
- **Investigate Mode** — Point it at code, it challenges everything you think you know
- **Reflect Mode** — Reviews your past sessions, exposes patterns in your thinking
- **Skill Adaptation** — Adjusts intensity to your experience level
- **Evidence-First** — Always points to code, logs, data. Never hand-waves.
- **Session Memory** — Tracks your debugging journey and growth over time

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

## Status

Under active development — Star this repo to follow progress!

## License

MIT
