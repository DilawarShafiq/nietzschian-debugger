# Socratic Debugger

> I won't fix your bugs. I'll teach you to.

The anti-AI. Every other tool gives you answers. Socratic Debugger **asks you questions**.

You paste your bug. It doesn't fix it. Instead, it:

- Asks what you've already tried
- Challenges your assumptions about what's happening
- Points you to the exact evidence you're missing
- Guides you to the "aha!" moment — YOUR moment, not the AI's

## Why?

AI is making developers worse. Copy-paste from ChatGPT, ship, repeat. Nobody understands their own code anymore. **Socratic Debugger makes you a better developer**, not a more dependent one.

## Quick Start

```bash
# Start a debugging session
npx socratic debug "My API returns 500 but only on Tuesdays"

# Analyze a specific file
npx socratic investigate ./src/api/handler.ts

# Review your reasoning journey
npx socratic reflect --session latest
```

## How a Session Looks

```
  Socratic Debugger v0.1.0

You: My login endpoint returns 403 for some users

Socratic: Interesting. Before we dive in — what's different about
          the users who get 403 vs those who don't?

You: I'm not sure, it seems random

Socratic: "Seems random" is a hypothesis. Have you checked the
          server logs for the 403 responses? What do they say?

You: Let me check... oh, they all have expired JWT tokens

Socratic: Good finding. Now — why would some users have expired
          tokens while others don't? What controls token expiry
          in your system?

You: ... oh. We changed the token TTL last week and didn't
     invalidate existing sessions.

Socratic: You just found your bug. And more importantly — what
          did you learn about deploying auth changes?
```

## Features

- **Debug Mode** — Guided Socratic questioning for any bug
- **Investigate Mode** — Point it at code, it asks you what you think it does (and challenges you)
- **Reflect Mode** — Reviews your past debugging sessions, shows patterns in your thinking
- **Skill Adaptation** — Adjusts question depth to your experience level
- **Evidence-First** — Always points to code, logs, data. Never hand-waves.
- **Session Memory** — Tracks your debugging journey and growth over time

## The Philosophy

| Traditional AI | Socratic Debugger |
|---------------|-------------------|
| "Here's the fix" | "What have you tried?" |
| Makes you dependent | Makes you independent |
| You learn nothing | You learn everything |
| Fast but shallow | Slower but lasting |
| AI gets smarter | YOU get smarter |

## Who Is This For?

- **Junior developers** who want to actually learn, not just copy-paste
- **Senior developers** who miss the "aha!" moments
- **Engineering managers** who want their team thinking, not just prompting
- **Bootcamp students** building real debugging intuition
- **Anyone** tired of AI making them lazier

## Status

🚧 **Under active development** — Star this repo to follow progress!

## License

MIT
