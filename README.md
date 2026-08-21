# Neo — State Resolutions Operation Solver

Neo is the engineering repository for the **State Resolutions Operation Solver (SROS)** and the larger engineering/model system that supports it.

> **READING CONTRACT — IMPORTANT**
>
> Neo must be read as **one connected program and evidence corpus**, not as a collection of independent folders. Before designing, modifying, or evaluating SROS, a reader/agent must establish the context in the order below and retain the meaning of later records in the context of everything already read.
>
> **Do not jump directly into `01_PROJECTS/SROS/` and assume the engineers are standalone agents.** The Stationary Engineer and Non-Stationary Engineer are parts of the larger engineering system. The AI-model records document prior model analyses, critiques, proposals, experiments, and assumptions that may affect how those engineers and SROS are intended to operate.

## 0. The context rule

Every implementation decision must be interpreted against four layers simultaneously:

1. **The whole Neo program** — what the repository is trying to build.
2. **The engineering system** — how state resolution, verification, experimentation, planning, memory, models, and engineers interact.
3. **The model record** — what GPT/ChatGPT, Claude, Grok, Devin, LM Arena and other recorded systems previously analyzed, proposed, rejected, or warned about.
4. **The current executable implementation** — what the code actually proves today.

These layers are not interchangeable. Documentation is not proof of implementation; a model's proposal is not an accepted design; a benchmark is not a runtime guarantee; and a historical snapshot is not automatically current code.

---

# Required reading order

## 1. Repository orientation — read first

Start with:

1. `README.md` — this document.
2. `00_START_HERE/` — repository entry points and orientation.
3. `_INDEX_AND_METADATA/REPOSITORY_AUDIT.md` — current repository structure and known conditions.
4. `05_DOCUMENTATION/Architecture/REPOSITORY_ARCHITECTURE.md` — ownership, canonical-source, snapshot, and integration rules.

**Goal:** understand what Neo contains before treating any individual project as the whole system.

---

## 2. Primary program — SROS

Then read the complete SROS documentation and implementation in this order:

1. `01_PROJECTS/SROS/README.md`
2. `01_PROJECTS/SROS/ENGINEER_VERIFIED_PASS.md`
3. `_INDEX_AND_METADATA/SROS_ENGINEER_VERIFICATION.md`
4. `_INDEX_AND_METADATA/SROS_FINAL_REVIEW_2026-08-21.md`
5. `01_PROJECTS/SROS/pyproject.toml`
6. `01_PROJECTS/SROS/src/sros/models.py`
7. `01_PROJECTS/SROS/src/sros/engineers.py`
8. `01_PROJECTS/SROS/src/sros/solver.py`
9. `01_PROJECTS/SROS/src/sros/__init__.py`
10. **all** SROS tests.

**Goal:** understand the actual current state/resolution contracts before using older design material to interpret them.

SROS has two primary engineering regimes:

- **Stationary Engineer:** resolution against a sufficiently stable state.
- **Non-Stationary Engineer:** resolution while state, environment, constraints, or objectives can change.

The engineers must be understood as members of the larger engineering system, not merely as two independent Python classes.

---

## 3. Engineering-system records — read before integrating anything

Next read the engineering-system documentation throughout:

- `05_DOCUMENTATION/Architecture/`
- `05_DOCUMENTATION/Engineering/`
- `05_DOCUMENTATION/Systems/`
- relevant files under `02_SYSTEMS/`
- relevant New Neo / Atlas / UAIR design records
- engineering ledgers, evaluation records, verification records, and promotion records under `_INDEX_AND_METADATA/`

Then inspect the corresponding source implementations.

**Rule:** whenever a document describes a subsystem, locate its actual implementation and tests before treating the description as authoritative.

---

# 4. AI model record corpus — read ALL model records

This is a mandatory context layer.

Read the complete `05_DOCUMENTATION/AI_Models/` corpus before asking the engineers, changing SROS architecture, or deciding what an AI/model subsystem is supposed to do.

At minimum this includes the records for:

- **Grok**
- **GPT / ChatGPT**
- **Claude**
- **Devin**
- **LM Arena / LMArena**
- **Qwen**
- **Perplexity**
- **OmniRoute**
- and **every additional file currently present in `05_DOCUMENTATION/AI_Models/`**.

Do not read only the obvious `*_Info.txt` files. Read assessments, reviews, benchmark records, transcripts, analyses, and related model documents as well.

### Model-record interpretation rules

Each model record is evidence from a particular model/system at a particular point in time. Preserve:

- the model identity;
- the date/context when known;
- what question it was answering;
- its assumptions;
- its proposed architecture;
- its objections;
- its rejected ideas;
- its uncertainty;
- what was subsequently verified;
- what was subsequently disproven or superseded.

**Never collapse all model records into one undifferentiated "AI says" source.** Disagreement is valuable data.

A model proposal becomes an engineering candidate only after the engineering verification process accepts it.

A model warning remains relevant until it is explicitly resolved by evidence.

A benchmark record is historical evidence unless its methodology and current runtime conditions establish otherwise.

---

## 5. Model/world-model implementations

After reading the model records, inspect the executable systems they refer to:

- model clients and adapters;
- model councils;
- world-model implementations;
- UAIR;
- Atlas Shadow Unified;
- New Neo model/planning/memory/evaluation components;
- training and inference systems;
- model metadata and weights;
- any other system referenced by the model corpus.

For each candidate component determine:

```text
DOCUMENTED
    ↓
IMPLEMENTED?
    ↓
TESTED?
    ↓
RUNTIME VERIFIED?
    ↓
INTERFACE VERIFIED AGAINST SROS?
    ↓
SROS DEPENDENCY?
```

Only the last state means it has actually become an SROS dependency.

---

# 6. Engineers — only after the full corpus is understood

Only after steps 1–5 should an engineering agent be asked to analyze or modify the system.

The **Stationary Engineer** and **Non-Stationary Engineer** must receive the relevant full-context record, including:

- SROS contracts;
- repository architecture;
- existing engineering records;
- model records;
- world-model assumptions;
- previous experiment results;
- known failures;
- competing proposals;
- current implementation state.

They should then work independently before their conclusions are synthesized.

### Stationary Engineer asks

- Is the state sufficiently stable for this reasoning?
- Are assumptions explicit?
- Is the result reproducible?
- Are constraints satisfied?
- Can the proposed resolution be independently verified?
- What evidence would falsify it?

### Non-Stationary Engineer asks

- What changes while the resolution is being generated or executed?
- Can the state transition invalidate the solution?
- Can the solver detect model/state drift?
- What happens when objectives or constraints change?
- What transition evidence is required before accepting the result?
- When should the system abstain?

### The engineers must be allowed to disagree

Do not force consensus. Preserve conflicting analyses, identify their assumptions, and let the verification layer determine which claims survive.

---

# 7. Collect → brainstorm → plan → verify → implement → re-review

All substantial changes follow this loop:

```text
COLLECT
   ↓
READ FULL CONTEXT
   ↓
STATIONARY ANALYSIS ─────┐
                         ├──► BRAINSTORM
NON-STATIONARY ANALYSIS ─┘
                         ↓
                    CONFLICT ANALYSIS
                         ↓
                       PLAN
                         ↓
                  ENGINEER VERIFICATION
                         ↓
                 IMPLEMENT ACCEPTED ONLY
                         ↓
                       TEST
                         ↓
                  FULL REPOSITORY REVIEW
                         ↓
                REWORK IF EVIDENCE REQUIRES
                         ↓
                     FINAL REVIEW
```

**The previous architecture pass is a filter, not authority.** Earlier decisions may be challenged by later evidence.

No implementation change should be justified merely by saying that an earlier pass recommended it.

---

# 8. Primary-program relationship

The intended conceptual relationship is:

```text
                         NEO ENGINEERING SYSTEM
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
     MODEL RECORDS           WORLD MODELS             ENGINEERS
          │                       │                        │
   GPT / Claude /           UAIR / simulations     Stationary
   Grok / Devin /            / state models        Non-Stationary
   LM Arena / etc.                                  + other roles
          │                       │                        │
          └───────────────────────┼────────────────────────┘
                                  │
                                  ▼
                    STATE RESOLUTIONS OPERATION SOLVER
                                  │
                         validated resolution
```

This diagram is a **conceptual architecture**, not a claim that every component is currently integrated.

---

# 9. Evidence hierarchy

When sources disagree, use this order for implementation decisions:

1. **Current reproducible runtime/test evidence**
2. **Current source-code contracts and verified behavior**
3. **Fresh engineer verification against the current code**
4. **Recorded experiments with reproducible methodology**
5. **Model records and expert analyses**
6. **Architecture/design documents**
7. **Historical plans, transcripts, and snapshots**

Lower-ranked evidence remains useful. It must not silently override stronger current evidence.

---

# 10. Current integration rule

Do not assume that an existing component is part of SROS because its documentation says so, because a model recommended it, or because it appears architecturally useful.

A component becomes an SROS dependency only after its:

- interfaces;
- imports;
- assumptions;
- tests;
- runtime behavior;
- failure behavior;
- security properties;
- stationary behavior;
- non-stationary behavior;

have been inspected and verified against the current SROS contract.

---

# Security

Do not commit API keys, cookies, access tokens, model credentials, or real `.env` files. Use templates and local environment injection.

# Final rule

**Read the whole program before interpreting a part of the program.**

**Read all model records before asking the engineers to make architectural judgments.**

**Preserve disagreements and provenance.**

**Implement verified conclusions, not attractive speculation.**
