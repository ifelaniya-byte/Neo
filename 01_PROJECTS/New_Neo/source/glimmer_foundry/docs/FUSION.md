# GlimmerFoundry — Fusion of both gaps

## Thesis

> Open weights in your hands + continual adaptation you control.

Zuckerberg’s Muse Glimmer puts a strong **local open model** on consumer hardware.  
Weight Foundry puts a **safe continual-learning harness** around whatever base you own.  
**GlimmerFoundry** is both.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Muse Glimmer 30B (Apache 2.0) — FROZEN base            │
│  4-bit on one consumer GPU / Mac · local agent ready    │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   Online-LoRA+     GRPO-R1    Tree-Filtered
   shift+importance group-rel   bank isolation
         │             │             │
         └─────────────┼─────────────┘
                       ▼
              Deterministic verifier
                       ▼
           Holdout promote / rollback
                       ▼
              Your local adapter deltas
```

## What each side contributes

| Gap | Filled by |
|-----|-----------|
| Downloadable open model for individuals | **Muse Glimmer** (`meta-models/Muse-Glimmer-30B`) |
| On-device / single-GPU agent runtime | Glimmer 4-bit + local-only agent config |
| Continual weight updates after deploy | **Online-LoRA+ / GRPO-R1 / Tree-Filtered** |
| Safe promote without reward hacking | Holdout gate + rollback |
| No time-scaled LR explosion | Fixed LR contract |

## Run paths

### A. Simulation (no GPU, tests the harness)

```bash
python -m src.lab --mode simulation --cycles 40 --cadence 0
```

### B. Local server (API + dashboard)

```bash
uvicorn src.server:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/fusion
```

### C. Real Glimmer + LoRA (one GPU, ~16–20GB at 4-bit)

```bash
pip install torch transformers peft bitsandbytes accelerate
# config.yaml already points at meta-models/Muse-Glimmer-30B
python -c "from src.trainer import OnlineTrainerDaemon; import yaml; c=yaml.safe_load(open('config.yaml')); d=OnlineTrainerDaemon(c); print(d.status())"
```

### D. Inference-only (Meta’s packaging)

- Ollama / LM Studio / vLLM with `meta-models/Muse-Glimmer-30B`
- Then point Foundry’s trainer at the same weights for adapter training

## Safety (unchanged)

1. Base Glimmer weights stay frozen  
2. Only LoRA / tree banks train  
3. Deterministic verifier decides pass  
4. Holdout never enters the training loss  
5. Rollback if holdout drops  
6. Learning rate never multiplied by wall-clock time  

## Fallback

If Glimmer cannot load (no GPU / no download), `model.fallback_id` (`Qwen/Qwen2.5-0.5B-Instruct`) is used automatically so the harness still runs.
