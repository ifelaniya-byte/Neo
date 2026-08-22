# MegaCompact16

**Time-causal, uncertainty-aware DeFi research, simulation, prediction, planning, paper-replay, and validation harness.**

## What This Is

One self-contained Python 3.11 script (`megacompact16.py`) that generates decision packets, simulates action outcomes, trains an uncertainty-aware world model, calibrates risk, plans conservatively, paper-replays decisions, stress-tests them, audits for leakage, and writes reproducible artifacts.

## What This Is NOT

- **Not a live trading bot** - No wallet access, private keys, signing, transaction submission, Flashbots, RPC broadcast, or contract calls
- **Not a promise of profit** - No claims about accuracy, returns, or "omniscience"
- **Not a notebook** - Not split into hundreds of cells
- **Not protocol-specific** - Uses generic, configurable AMM mechanics

## Safety Rules

1. **Paper/replay mode only** - No live execution code
2. **Default verdict is ABSTAIN** - Must pass all safety gates to trade
3. **Time-causal features** - Every feature has availability timestamp; no future data
4. **Time-split data** - train → validation → calibration → test (no random shuffling)
5. **Strict separation** - Model/scaler/calibration fitting restricted to assigned windows
6. **Net PnL only** - Gross spread never reported as strategy performance
7. **Full provenance** - Every decision logs data, model version, uncertainty, and outcome
8. **Fail closed** - Stale, malformed, or OOD inputs return ABSTAIN
9. **No online updates** - Retraining is explicit and versioned

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Five-minute smoke test with synthetic data:

```bash
python megacompact16.py all --mode synth --preset smoke --seed 7
```

Larger CPU research run:

```bash
python megacompact16.py all --mode synth --preset research --seed 7
```

Ingest historical data:

```bash
python megacompact16.py all --mode parquet --input data/events.parquet --config configs/ingest.yaml --seed 7
```

## Expected Artifacts

After a successful run:

```
artifacts/<run_id>/
  manifest.json
  config.resolved.yaml
  logs/
  hashes/
  data/
    raw/
    normalized/
    quarantine/
    packets/
    labels/
    splits/
    regimes/
  models/
    member_0.pt ... member_4.pt
    scaler.joblib
    feature_spec.json
    conformal_global.json
    ood_stats.joblib
    retrieval_index.joblib
  paper/
    decisions.jsonl
    outcomes.jsonl
    ledger.parquet
  backtests/
  stress/
  audits/
  reports/
    charts/
```

## CLI Commands

```bash
python megacompact16.py synth --config configs/smoke.yaml
python megacompact16.py ingest --input <file> --mode csv|parquet --config <file>
python megacompact16.py validate --run-dir <dir>
python megacompact16.py build-packets --run-dir <dir>
python megacompact16.py label --run-dir <dir>
python megacompact16.py split --run-dir <dir>
python megacompact16.py train --run-dir <dir>
python megacompact16.py calibrate --run-dir <dir>
python megacompact16.py replay --run-dir <dir>
python megacompact16.py backtest --run-dir <dir>
python megacompact16.py stress --run-dir <dir>
python megacompact16.py audit --run-dir <dir>
python megacompact16.py report --run-dir <dir>
python megacompact16.py all --mode synth --preset smoke --seed 7
python megacompact16.py serve --run-dir <dir>
```

## Data Requirements

For historical data ingestion, provide CSV/Parquet with these fields:

- `chain_id`: int
- `block_number`: int
- `block_hash`: str
- `event_timestamp_ms`: int
- `observed_timestamp_ms`: int
- `available_timestamp_ms`: int
- `event_type`: str (swap, pool_update, quote, gas, block, oracle, etc.)
- `entity_id`: str
- `payload`: dict with event-specific data

## Integration with Stationary/Non-Stationary Models

The system includes a `ForecastAdapter` protocol and `DualModelArbiter` for fusing your existing stationary and non-stationary models. Implement the adapter interface for each model:

```python
class ForecastAdapter(Protocol):
    name: str
    version: str
    
    def predict(self, packet: DecisionPacket, candidate: ActionCandidate) -> ModelForecast
    def fit(self, train_data, validation_data) -> None
    def calibrate(self, calibration_data) -> None
    def save(self, path: str) -> None
    def load(self, path: str) -> None
```

## Limitations

- **Unmodeled MEV** - No simulation of private order flow, front-running, or sandwich attacks
- **Hidden liquidity** - Only observes public pool state
- **Reorg mechanics** - No chain reorganization simulation
- **Delayed data** - Assumes fixed latency; real latency varies
- **Simulator mismatch** - AMM mechanics are approximations
- **Selection bias** - Logged data may not represent all decision opportunities
- **Distribution shift** - Calibration assumes exchangeability; markets are nonstationary

## Important Disclaimer

**Paper/simulated results are not evidence of future profit.** This is a research tool for evaluating decision strategies under uncertainty. Any real deployment requires additional safeguards, legal compliance, and risk management beyond this system.

## License

Research and educational use only.
