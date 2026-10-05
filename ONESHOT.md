# One-Shot AI

Run Pi as a single-shot command — no interactive session, no persistence.

## Basic

```bash
pi --print "your question here"
```

## Common Patterns

```bash
# Pipe input
cat file.txt | pi --print "Summarize this"

# Specific model
pi --print --model sonnet "What's in this repo?"

# Ephemeral (no session stored)
pi --print --no-session "Quick question"

# JSON output (for scripting)
pi --mode json "Inspect this repo" > events.jsonl
```

## Key Flags

| Flag | Purpose |
|---|---|
| `--print` | Run once, print answer, exit |
| `--no-session` | Don't persist the session |
| `--mode json` | Output JSONL events instead of text |
| `--model <id>` | Pick a specific model |
