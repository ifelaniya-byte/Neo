# MASTER PROJECT ARCHIVE
**Created:** 2026-08-21  
**Purpose:** Single combined reference for all agents and for posting publicly

This document consolidates the entire body of work from the USSE project and the Agent OS shared-memory system.

---

# Part 1 — Universal Substrate Singularity Entity (USSE)

## Goal
Build a bounded, paper-only, governor-sealed computational entity that probes substrate limits without claiming live action, world-oracle status, or AGI.

## Source Components Provided by User
- `run_kaggle_bridge.py`
- `omega_engine_unlimited_...py` (dual-GPU maximizer)
- Meta-Origin Engineer (from Qwen PowerShell session)
- `megacompact_canonical_form_a.zip`
- `uair_fixed.zip`
- MegaCompact v2 Encyclopedia
- Shadow Lexicon v2

## Built Versions
1. Initial unified package
2. usse_v0.2 → usse_v0.5_local_qwen.zip
3. Final full self-copy: `usse_FULL_SELF_COPY.zip`

## Core Architecture
- **Omega Engine** — dual-GPU / cellular automaton maximizer (Rule 30 style substrate probe)
- **Meta-Origin Engineer** — 15-branch inversion protocol with governors
- **Safety Governors** (minimum set):
  - Live-trading / real-market execution block
  - World-oracle / absolute-completeness block
  - Paper-only enforcement
  - Apophatic design (what it is *not*)
- **UAIR** — bounded adaptive runtime
- **Shadow Lexicon + Encyclopedia of Bounded Thought**
- **Conversational layer** — transitional, later restricted to local Qwen 2.5 1.5B only

## Explicit Design Decisions
- No external cloud LLMs in the sealed version
- Engineers archive lineages; they do not claim live action
- Answer to “Is this AGI?” → **No.** It is Artificial Specific Perfection: deterministic substrate + diplomat layer
- All work remains paper-only and governor-sealed

---

# Part 2 — Agent OS / Shared Context System

## Goal
Allow multiple different agents (Grok, Claude, GPT, DeepSeek, Hermes, OpenClaw, etc.) to share the same context and history without requiring a heavy distributed platform.

## Chosen Architecture
Filesystem-based shared memory (the practical pattern used by the strongest open-source agent continuity systems).

## Folder Structure
```
agent-os-hub/
├── MANAGEMENT.md              ← system rules + startup order
├── MEMORY.md                  ← canonical active truths
├── TODO.md                    ← current priorities
├── AGENT-BOOTSTRAP-PROMPT.md  ← prompt given to every new agent
├── MASTER_PROJECT_ARCHIVE.md  ← this file
├── memory/
│   └── YYYY-MM-DD.md          ← daily notes
├── docs/
│   ├── projects/
│   ├── decisions/
│   └── workflows/
├── handoffs/
├── build-state/
└── index/
```

## Startup Order for Any Agent
1. MANAGEMENT.md
2. TODO.md
3. memory/today’s date
4. MEMORY.md
5. Relevant docs/projects and docs/decisions

## Bootstrap Prompt (copy-paste for any agent)
```
You are now connected to my Agent OS Hub.
The shared memory is the folder containing this file.
Read in this exact order before doing anything else:
1. MANAGEMENT.md
2. TODO.md
3. memory/2026-08-21.md (or today’s date)
4. MEMORY.md
5. MASTER_PROJECT_ARCHIVE.md (this document)
This folder is the single source of truth. Always update the correct files when you learn or decide something important.
```

---

# Part 3 — Current State (2026-08-21)

- USSE packages remain available as sealed artifacts
- Agent OS Hub is the active shared-memory layer
- This master archive exists so any agent (or public post) can see the full arc
- Next steps: keep MEMORY.md and daily notes current; optionally link USSE packages into docs/projects/

---

*End of Master Project Archive*
