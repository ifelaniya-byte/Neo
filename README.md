# See also: [CANONICAL.md](CANONICAL.md) (edit multi-file only; condensed is generated)

# MegaCompact16 + UAIR Unified Pipeline

**Version 1.2.0-double-engineer**

A single, LLM-callable research & decision pipeline that merges:

- **MegaCompact16** (latest fixed) – time-causal DeFi research, paper-replay, audit
- **UAIR** – adaptive routing / uncertainty / safety patterns
- **Stationary + Non-Stationary Engineers** – mandatory double-pass verification spine

## Mandatory safety spine (non-negotiable)

Every unit of information is fed through the engineers **twice** before any LLM may interpret it:

```
StationaryEngineer.verify()          # pass 1 – observe, integrity, causality, accounting
        ↓
NonStationaryEngineer.act_and_check()# experimental probes, repair proposals, stress
        ↓
StationaryEngineer.verify()          # pass 2 – secondary verification
        ↓
  allowed_for_llm == True  →  may be handed to LLM interpreter
  otherwise                →  BLOCKED / ABSTAIN (withheld)
```

This is implemented as first-class mandatory stages:

| Stage | What is verified |
|-------|------------------|
| `engineer_events` | Synthetic / ingested market events |
| `engineer_packets` | Decision packets |
| `engineer_labels` | Outcome labels (net-PnL identity, causality) |
| `engineer_decisions` | Final decisions – last gate before LLM |

## Full mandatory stage list

```
1.  synth
2.  engineer_events          ← Stationary → NonStationary → Stationary
3.  validate
4.  build_packets
5.  engineer_packets         ← Stationary → NonStationary → Stationary
6.  label
7.  engineer_labels          ← Stationary → NonStationary → Stationary
8.  split
9.  fit_baseline
10. plan_and_decide
11. engineer_decisions       ← Stationary → NonStationary → Stationary
12. paper_replay
13. audit
14. report
```

## Quick start

```bash
cd megacompact_uair_pipeline
pip install -r requirements.txt

# Full end-to-end
python pipeline.py all --seed 42

# Step-by-step (ideal for an LLM agent)
python pipeline.py stage synth
python pipeline.py stage engineer_events
python pipeline.py stage validate
# ... etc
python pipeline.py list-stages
```

## LLM / Agent usage

```python
from pipeline import MegaPipeline

pipe = MegaPipeline(seed=42)
pipe.run_all()   # or drive stages one-by-one with pipe.run_stage("...")

# ONLY data that survived both stationary passes + non-stationary probe:
cleared_decisions = pipe.get_llm_cleared("decisions")
cleared_packets   = pipe.get_llm_cleared("packets")
cleared_labels    = pipe.get_llm_cleared("labels")
cleared_events    = pipe.get_llm_cleared("events")

# Anything not in these lists must not be interpreted by an LLM.
```

## What each engineer does

### StationaryEngineer (observer – never mutates)
- Schema / required-field presence
- Time-causality (`available_timestamp >= observed_timestamp`)
- Net-PnL accounting identity (realized − all costs == net)
- Finite-number probes
- Optional AST / source integrity when source text is supplied
- Always-on math/logic micro-probes

### NonStationaryEngineer (actor / experimental)
- Serialisability probe
- Mutation probe on a **copy** only (original untouched)
- Structural / size bounds
- Repair *proposals* (e.g. net-PnL correction) – never silently applied
- Adversarial NaN/Inf walk

### DoublePassEngineerGate
- Orchestrates Stationary → NonStationary → Stationary
- Writes every check into `audits/verification_ledger.jsonl`
- Fail-closed: any hard FAIL → `BLOCKED`, not handed to LLM

## Artifacts produced

```
artifacts/run_YYYYMMDD_HHMMSS/
├── config.resolved.yaml
├── manifest.json
├── data/...
├── models/empirical_baseline.json
├── paper/decisions.jsonl
├── audits/
│   ├── verification_ledger.jsonl      ← every engineer pass
│   ├── engineer_normalizedevent.json
│   ├── engineer_decisionpacket.json
│   ├── engineer_outcomelabel.json
│   ├── engineer_decisionoutput.json
│   └── audit_results.json
└── reports/...
```

## Safety rules (unchanged from MegaCompact16)

1. Paper / replay only – no web3, no signing, no live txs
2. Default verdict = **ABSTAIN**
3. Every feature has an availability timestamp
4. Strict walk-forward time splits
5. Net PnL includes all costs
6. Full provenance on every decision
7. **NEW:** Double engineer verification before LLM interpretation

## Honest limits

- Synthetic data is a research sandbox, not a market oracle.
- The neural world-model sections still require PyTorch (optional).
- This is a paper-only system. It will never submit a transaction.
- The engineers are structural / accounting / causality gates, not a substitute for domain expert review.
