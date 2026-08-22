# MegaCompact — Two-Script Condensed Distribution

## Script 1: `megacompact_condensed_spine.py` (pure stdlib)

**~6k lines.** Safety / knowledge / verification spine. No numpy/pandas/pydantic required.

Includes: engineers (double-pass), KSKB, atlas, RAG, SMT, interval, signed ledgers,
promotion, adversarial suite, independent audit, historical + feed adapters, LLM gateway,
lab CI, UAIR contracts/layers/orchestrator, tools.

```bash
python megacompact_condensed_spine.py smt-demo
python megacompact_condensed_spine.py adversarial
python megacompact_condensed_spine.py battery
python megacompact_condensed_spine.py lab-ci
python megacompact_condensed_spine.py evidence
python megacompact_condensed_spine.py feed-demo
```

## Script 2: `megacompact_condensed_engine.py` (third-party deps)

**~4.5k lines.** `megacompact16/core.py` + `pipeline.py` + `run_all.py`.

Requires: `numpy`, `pandas`, `pydantic` (optional: `typer`, `rich`, `pyarrow`).

Must sit next to Script 1 so `import megacompact_condensed_spine` works (wires `smt_gate` /
`interval_arith` / `engineers` into `sys.modules` for core).

```bash
pip install numpy pandas pydantic
python megacompact_condensed_engine.py run-all
```

## Why two scripts?

| Piece | Why not one file |
|--------|------------------|
| Spine | Pure stdlib — portable verification OS |
| Engine | Hard dependency on numpy/pandas/pydantic for market sim, packets, labels |

Canonical multi-file package remains the maintainable source of truth.
These two files are a **distribution / lean-muscle** form.

## Safety (unchanged)

- Double-pass before LLM
- Completeness / world-oracle claims BLOCKED
- Paper-only — no live trading
- Evidence ≠ authority for TRADE
