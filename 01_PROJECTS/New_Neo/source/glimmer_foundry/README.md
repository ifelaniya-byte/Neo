# GlimmerFoundry
## Muse Glimmer × Weight Foundry — both gaps filled

**Open weights in your hands + continual adaptation you control.**

| Layer | Source | Role |
|-------|--------|------|
| **Base model** | [Muse Glimmer 30B](https://huggingface.co/meta-models/Muse-Glimmer-30B) (Meta, Apache 2.0) | On-device open agent model, 4-bit on one GPU |
| **Harness** | Online-LoRA+ · GRPO-R1 · Tree-Filtered | Continual updates under one verifier |
| **Safety** | Holdout promote/rollback · fixed LR · NaN guards | No blind updates, no time-scaled LR |

This merges Zuckerberg’s “power of AI into people’s hands” (downloadable local model) with Foundry’s continual-learning contract (you keep improving it safely).

## Quick start

```bash
# Harness simulation (CPU)
python -m src.lab --mode simulation --cycles 40 --cadence 0

# API + fusion status
uvicorn src.server:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/fusion

# Accuracy suite
python -m tests.test_accuracy
```

## Real Glimmer path (single GPU)

```bash
pip install torch transformers peft bitsandbytes accelerate
# config.yaml defaults to meta-models/Muse-Glimmer-30B with load_in_4bit: true
```

Fallback small model is automatic if Glimmer cannot load.

## Docs

- `docs/FUSION.md` — architecture of the merge  
- `docs/ULTIMATE_MANUAL.md` — full contract  
- `docs/EFFICIENCY.md` — measured speedups  
- `docs/SAFETY.md` — promote/rollback rules  

## Karpathy loop (Online → Offline → Online)

```bash
python -m src.karpathy_loop --cycles 12 --collect 9
python -m tests.test_karpathy_loop
```

Muse tips included: tool/format/abstain rewards, LoRA-only, preference pairs, holdout gate.
See `docs/KARPATHY_LOOP.md`.

## Micro-agent

```bash
python -m src.micro_agent fusion
python -m src.micro_agent lineage
```
