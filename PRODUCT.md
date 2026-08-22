# MegaCompact Simulation Assurance — Product

**Version:** 1.3.0-product  
**Category:** Paper-only research & simulation assurance infrastructure  
**Not:** a live trading bot, profit engine, or complete physics oracle

## What this product does

Turns market-like data into **audited, time-causal decision experiments** under a mandatory double-pass engineer spine (Stationary → NonStationary → Stationary). Cleared artifacts may be handed to an LLM; uncleared ones stay blocked.

Primary buyers / users: research labs, internal quant research, simulation QA, compliance-minded paper-trading studies.

## Value-driver features (finished)

| # | Feature | Module(s) | Status |
|---|---------|-----------|--------|
| 1 | Historical adapters + bit-exact replay proofs | `adapters/historical.py`, `bit_exact_replay.py`, `chain_observer_ro.py` | Product |
| 2 | Hardened promotion + signed ledgers | `promotion.py`, `signed_ledger.py` (HMAC + optional Ed25519) | Product |
| 3 | SMT + interval on every TRADE path | `megacompact16/core.py` AbstentionGate + `smt_gate.py` + `interval_arith.py` | Product (fail-closed) |
| 4 | Independent audit / formal subset | `independent_audit.py`, `formal_bridge.py` | Product |
| 5 | Non-trading product story | this file + README + engineer claim gates | Product |

## Safety contract (non-negotiable)

- Double-pass before LLM clearance
- Completeness / “world physics” claims → BLOCKED
- Live trading / signing of real transactions → OFF
- Promotion offline only, human_confirm by default
- Formal obligations are **unchecked** until an external kernel accepts them

## Quick start (operator)

```bash
# Mechanical battery
python -m tools.cli_tools battery

# Independent product audit
python -c "from independent_audit import run_independent_audit; import json; print(json.dumps(run_independent_audit(), indent=2, default=str)[:2000])"

# Historical adapter demo
python -c "
from adapters.historical import HistoricalAdapter, write_sample_jsonl
p = write_sample_jsonl('artifacts/sample_hist.jsonl')
ev = HistoricalAdapter().from_jsonl(p)
print(len(ev), ev[0].to_dict())
"

# Signed promotion ledger verify
python -c "
from signed_ledger import SignedLedger
sl = SignedLedger('artifacts/demo_signed.jsonl')
e = sl.append('demo', {'ok': True})
print(e.entry_id, e.algorithm, sl.verify_file())
"

# Bit-exact self-proof on a run dir
python -c "
from bit_exact_replay import self_proof
from pathlib import Path
Path('artifacts/run_proof_demo/reports').mkdir(parents=True, exist_ok=True)
Path('artifacts/run_proof_demo/reports/run_summary.json').write_text('{\"demo\":true}')
print(self_proof('artifacts/run_proof_demo'))
"
```

## Pipeline stages (high level)

synth → engineer_events → validate → build_packets → engineer_packets → label → engineer_labels → split → fit_baseline → plan_and_decide → engineer_decisions → adversarial_ci → independent_audit → report

## What success looks like for a lab

- Reproducible paper runs with pin matrix + merkle + signed ledgers
- Every TRADE candidate blocked unless SMT + interval allow
- Historical data ingested only with availability timestamps
- Formal obligations filed for external kernels (Lean/Coq) without false “proven” claims
- Clear abstention when unsafe

## Explicit non-claims

- Does not guarantee alpha, Sharpe, or PnL
- Does not finish physics or absorb all knowledge
- Does not replace human judgment or a real formal proof kernel without external tools
