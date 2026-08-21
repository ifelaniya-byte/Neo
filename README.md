# Neo — State Resolutions Operation Solver

Neo is the engineering repository for the **State Resolutions Operation Solver (SROS)** and the systems, models, knowledge, experiments, and tooling that support it.

## Primary program

**SROS** resolves a defined problem state into a validated operation/resolution by explicitly engineering two regimes:

- **Stationary Engineer** — resolution against a sufficiently stable state.
- **Non-Stationary Engineer** — resolution while the relevant state/environment can change during the resolution cycle.

SROS owns the orchestration and acceptance contract. Existing Neo systems are integrated as dependencies only after their behavior is verified against that contract.

## Start here

1. [`01_PROJECTS/SROS/README.md`](01_PROJECTS/SROS/README.md) — primary program.
2. [`_INDEX_AND_METADATA/SROS_PASS.md`](_INDEX_AND_METADATA/SROS_PASS.md) — SROS architecture-pass record.
3. [`05_DOCUMENTATION/Architecture/REPOSITORY_ARCHITECTURE.md`](05_DOCUMENTATION/Architecture/REPOSITORY_ARCHITECTURE.md) — repository ownership rules.
4. [`_INDEX_AND_METADATA/REPOSITORY_AUDIT.md`](_INDEX_AND_METADATA/REPOSITORY_AUDIT.md) — prior repository audit.

## Repository contract

| Area | Purpose |
|---|---|
| `00_START_HERE/` | Orientation and entry points |
| `01_PROJECTS/SROS/` | Primary solver implementation |
| `01_PROJECTS/` | Other deployable/experimental projects |
| `02_SYSTEMS/` | Candidate reusable systems and dependencies |
| `03_MODELS_AND_WEIGHTS/` | Model artifacts and metadata |
| `04_KNOWLEDGE_AND_DATA/` | Data, training material, and world-model evidence |
| `05_DOCUMENTATION/` | Architecture, strategy, setup, and reference documentation |
| `06_CONFIGURATION/` | Non-secret configuration and templates |
| `07_UTILITIES_AND_TOOLS/` | Verification, automation, profiling, and maintenance |
| `08_ARCHIVES_AND_BACKUPS/` | Historical snapshots and provenance |
| `_INDEX_AND_METADATA/` | Repository indexes, manifests, and audit history |

## SROS integration rule

Do not assume that an existing component is part of SROS because its documentation says so. A component becomes an SROS dependency after its interfaces, imports, tests, and runtime behavior have been inspected and validated.

The existing Atlas Shadow Unified recursive optimizer is a particularly relevant candidate because it already contains guarded candidate evaluation and stationary verification logic. UAIR world-model material is a candidate dynamic-state dependency. New Neo's planning/memory/evaluation systems are candidates for additional SROS subsystems after duplicate snapshot analysis.

## Security

Do not commit API keys, cookies, access tokens, model credentials, or real `.env` files. Use templates and local environment injection.
