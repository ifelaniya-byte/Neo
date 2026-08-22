# Exhaustive Upgrade-to-Maximum Specification

**Status:** Stationary + double-pass CLEARED for production of specs/code under constraints.  
**Not in scope:** complete physics oracle, live trading, removing double-pass, online silent weight updates.

## Goal

Close the remaining **LLM-resistant** capability gaps with mechanical modules that plug into:

`Stationary → NonStationary → Stationary → (optional LLM)`

## Loop (exhaust until no accepted proposals)

```
while True:
  inventory = stationary.observe(system)
  proposals = non_stationary.propose(gaps)
  accepted = [p for p in proposals if double_pass(p) and not completeness(p)]
  if not accepted:
    break  # exhausted
  implement(accepted)
  consolidate()
  adversarial_ci()
  promote_only_human_confirm()
```

## Capability modules

| ID | Module | Priority |
|----|--------|----------|
| C1 | `smt_gate.py` — constraint satisfiability before TRADE | P0 |
| C2 | `interval_arith.py` — rigorous numeric enclosures | P0 |
| C3 | `merkle_artifacts.py` — hash tree over run artifacts | P0 |
| C4 | `gate_fuzzer.py` — mutating adversarial inputs | P1 |
| C5 | `sandbox.py` — time/CPU/mem limits on probes | P1 |
| C6 | `typed_ir.py` — typed action IR before sim | P1 |
| C7 | `causal_graph.py` — DAG + d-separation feature checks | P1 |
| C8 | `chain_observer_ro.py` — read-only availability-stamped feeds | P2 |
| C9 | `bit_exact_replay.py` — pin matrix + replay compare | P2 |
| C10 | `formal_bridge.py` — optional Lean/Coq external kernel hook | P3 |

## Integration points

1. **StationaryEngineer.verify** — call SMT/interval/unit/causal checks when subject carries constraints/bounds/edges.
2. **NonStationaryEngineer** — run probes inside `sandbox.run`.
3. **ArtifactStore** — after each stage, `merkle_artifacts.update`.
4. **pipeline STAGES** — insert `fuzz_ci` after `adversarial_ci`; optional `chain_ingest_ro`.
5. **AbstentionGate** — refuse TRADE if SMT unsat or interval edge lower-bound < min_edge.

## Acceptance criteria

- Adversarial suite still 100%
- Double-pass still mandatory
- Completeness claims still blocked
- New modules themselves PASS source_code engineer gate
- No private keys / live broadcast

## Exhaustion condition

No proposal remains that is: safe under constraints AND not already implemented AND not a pure data-content expansion.
