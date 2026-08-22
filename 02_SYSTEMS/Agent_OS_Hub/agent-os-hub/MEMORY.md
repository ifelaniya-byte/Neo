# Active Memory - Core Truths

## Project State
- **Primary active system:** Agent OS Hub (this folder) — shared filesystem memory for multiple agents
- **Previous major project:** Universal Substrate Singularity Entity (USSE) — bounded, paper-only, governor-sealed probe
- All USSE work remains paper-only with hard governors (no live trading, no world-oracle claims)

## Key Decisions
- Shared context between different LLMs is best achieved via a simple, transparent filesystem (this hub) rather than a heavy distributed platform
- MEMORY.md is the single most important file — every agent must read it first
- Full conversation history has been reconstructed and stored in `docs/projects/conversation-history-2026-08.md`

## Operating Rules
- Never make destructive changes without explicit human approval
- Always write durable facts here or into the appropriate docs/ file
- Prefer structured Markdown over long chat transcripts
- When a new agent joins, give it the prompt in AGENT-BOOTSTRAP-PROMPT.md

## Current Focus
- Keeping the Agent OS Hub as the living memory layer
- Optionally linking the existing USSE packages into this system
