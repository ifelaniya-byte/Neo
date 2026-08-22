# Agent OS Management

This folder is the **canonical source of truth** for all agents working with you.

## Startup Read Order (Critical)
Every agent must read files in this exact order when starting a session:

1. `MANAGEMENT.md` (this file)
2. `TODO.md`
3. `memory/2026-08-21.md` (today's daily note)
4. `MEMORY.md`
5. Relevant files in `docs/projects/` and `docs/decisions/`

## Core Rules
- The filesystem is memory. Chat history is temporary.
- Every important fact must be written to its canonical home.
- Never rely on previous chat context alone.
- All agents share this exact folder structure.
- Use `handoffs/` when passing work between agents.
- Use `build-state/` for any multi-step work that might span sessions.

## How to use this system
Point any AI agent (Claude, Grok, GPT, DeepSeek, Hermes, etc.) at this folder and give it the bootstrap prompt from `AGENT-BOOTSTRAP-PROMPT.md`.
