# State Resolutions Operation Solver (SROS)

SROS is the primary program architecture for Neo.

Its purpose is to resolve a defined problem state into a validated operation/resolution while explicitly handling two different engineering regimes:

- **Stationary Engineer** — solves against a sufficiently stable state, constraints, objective, and evaluation function.
- **Non-Stationary Engineer** — solves while allowing the state, constraints, objective, or environment to change during the resolution cycle.

SROS is the coordinator. The engineers are specialized reasoning/engineering regimes, not merely two interchangeable model calls.

## Current status

**Architecture pass:** `sros/architecture-pass-v4`  
**Status:** `IMPLEMENTED` architecture and reference engine; integration with the existing Neo systems remains `UNVERIFIED`.

This pass is intentionally additive. Existing Atlas/UAIR/New Neo implementations are not deleted or renamed until dependency and behavior analysis establishes a safe canonical migration path.

## Resolution contract

Input:

1. initial state
2. objective
3. constraints
4. available actions/operations
5. evaluation criteria
6. optional state-transition model
7. optional evidence/knowledge sources

Output:

1. selected engineering regime
2. proposed resolution
3. assumptions
4. predicted state transition
5. validation results
6. confidence/fitness metrics
7. unresolved risks and failure conditions

## Architecture

```text
Problem State
     |
     v
State Normalizer / Resolver
     |
     v
Regime Classifier
     |---------------------------|
     v                           v
Stationary Engineer       Non-Stationary Engineer
     |                           |
     |---- candidate resolutions |
     |                           |
     +------------+--------------+
                  v
          Resolution Evaluator
                  |
                  v
        Transition / Stress Tests
                  |
          +-------+-------+
          |               |
        reject           pass
          |               |
          v               v
      re-engineer     Resolution
```

## Relationship to existing Neo systems

The repository already contains useful primitives that should be evaluated as SROS dependencies rather than automatically duplicated:

- Atlas Shadow Unified's recursive optimizer provides champion/challenger evaluation, telemetry, deterministic checks, and a stationary gate. Its own source explicitly describes stationary verification and guarded promotion. `02_SYSTEMS/Atlas_Shadow_Unified/Atlas_Shadow_Unified_Clean/recursive_optimizer.py` is therefore a strong candidate for the SROS optimization layer, subject to integration testing.
- UAIR world-model material is a candidate source for dynamic state representation and transition modeling.
- New Neo's memory, planning, evaluation, and orchestration components are candidate SROS subsystems, but their duplicated extracted snapshots must be classified before adoption.

No existing component is declared canonical merely because its documentation claims that status.

## Next engineering stages

1. Bind existing stationary verification into `StationaryEngineer`.
2. Implement the non-stationary transition evaluator.
3. Add a common candidate/resolution representation.
4. Connect the Atlas recursive optimizer as an optional optimizer backend.
5. Connect validated world-model/state-transition capabilities.
6. Build stationary/non-stationary paired benchmarks.
7. Only then migrate duplicate New Neo implementations into SROS-owned modules.
