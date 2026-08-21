# SROS Architecture Pass

**Date:** 2026-08-21  
**Branch:** `sros/architecture-pass-v4`

## Decision

The **State Resolutions Operation Solver (SROS)** is now the primary program being built in Neo. Other systems are dependencies, research inputs, candidate optimizers, world models, or separate projects unless proven to be part of SROS.

## Evidence used

Repository inspection found existing material related to stationary/non-stationary engineering and several relevant systems. In particular, `02_SYSTEMS/Atlas_Shadow_Unified/Atlas_Shadow_Unified_Clean/recursive_optimizer.py` describes champion/challenger evaluation with deterministic checks, stationary verification, non-regression, and guarded promotion.

The repository also contains world-model material in both the UAIR system and knowledge/data areas. This makes dynamic state modeling a candidate dependency, but duplication across system/data layers means provenance and integration must be established before migration.

Search also surfaced a stationary planning artifact and engineer-related training artifacts. These are treated as knowledge/evidence, not executable engineer implementations, until code-level integration is established.

## What was created

```text
01_PROJECTS/SROS/
├── README.md
├── pyproject.toml
├── src/sros/
│   ├── __init__.py
│   ├── models.py
│   ├── engineers.py
│   └── solver.py
└── tests/
    └── test_solver.py
```

## Engineering interpretation

### SROS
Owns:

- problem/state normalization contract
- regime selection
- engineer orchestration
- resolution acceptance
- confidence/status contract
- future candidate comparison and transition evaluation

### Stationary Engineer
Owns resolution under an explicit stable-state assumption.

Required future bindings:

- real stationary verification suite
- deterministic benchmark suite
- domain constraint evaluator
- existing Atlas stationary gate where appropriate

### Non-Stationary Engineer
Owns resolution where the relevant state can change during the resolution cycle.

Required future bindings:

- transition model
- state observation/update loop
- re-planning policy
- dynamic constraint evaluation
- stress/adversarial transition tests

## Important non-claim

The reference SROS implementation is **not yet the full intelligent solver**. It is the stable orchestration contract that allows existing Neo engineering systems to be integrated without making undocumented assumptions. In particular, the default non-stationary engineer intentionally refuses to mark a dynamic solution resolved until a transition probe is bound.

## Migration rule

Do not move or delete the existing Atlas, UAIR, or New Neo implementations in this pass. First establish tests proving that a candidate component implements an SROS contract. Then migrate the canonical implementation and retain older copies as historical snapshots where provenance matters.

## Next pass

1. Extract the actual stationary engineering logic from existing artifacts/code.
2. Extract the actual non-stationary engineering logic from existing artifacts/code.
3. Bind both into the SROS interfaces.
4. Build a common candidate representation.
5. Bind Atlas recursive optimization to candidate evaluation.
6. Bind the world model to dynamic state transitions.
7. Create paired stationary/non-stationary benchmarks.
8. Add adversarial and regression gates.
9. Only then perform large-scale repository moves.
