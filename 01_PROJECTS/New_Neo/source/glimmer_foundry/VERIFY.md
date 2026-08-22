# Verification sweep (2026-08-10 / 11)

## What is real

| Component | Status | Evidence |
|-----------|--------|----------|
| Syntax (all src + tests) | PASS | ast.parse clean |
| Accuracy suite | ALL PASS | tests/test_accuracy.py ~4s |
| Karpathy loop | ALL PASS | tests/test_karpathy_loop.py |
| Lab simulation | PASS | src.lab cycles complete |
| Fusion module | PASS | describe_fusion / banner |
| Micro-agent | PASS | fusion / lineage commands |
| Growing assistant | PASS | learns from reports, recommends |
| Safety promote/rollback | PASS | explicit test |
| Efficiency | PASS | >20k steps/sec class |
| Muse Glimmer weights | NOT downloaded here | config points at HF id; needs GPU host |
| Real torch LoRA on Glimmer | Path only | trainer.py; needs torch/peft/bitsandbytes |

## Simulation vs real

- **Real in this package:** harness geometry, verifier, safety, Karpathy loop, tests, assistant memory, fusion contract.
- **Requires your GPU machine:** actual Muse Glimmer weight download + LoRA training.

## Commands

```bash
python -m tests.test_accuracy
python -m tests.test_karpathy_loop
python -m src.lab --mode simulation --cycles 20 --cadence 0
python -m src.karpathy_loop --cycles 8
python -m src.growing_assistant learn
python -m src.micro_agent fusion
uvicorn src.server:app --host 0.0.0.0 --port 8000
```
