# Karpathy Loop — Online → Offline → Online

## Pattern

```
ONLINE 1   collect trajectories (live verifier / tool rewards)
    ↓
OFFLINE    curate: drop junk, keep hard wins + good abstains,
           compress prompts, write preference pairs
    ↓
ONLINE 2   train adapters ONLY on curated batch
           (Online-LoRA+ / GRPO-R1 / Tree-Filtered)
    ↓
GATE       holdout promote or rollback
    ↓
REPEAT
```

This matches the “mandatory offline between online tests” design and Karpathy-style data flywheels: generate → filter → train → deploy → generate.

## Muse evolution tips baked in

- LoRA-only (base Muse frozen)
- Tool / format / abstain composite rewards
- Reasoning-friendly outputs (`THOUGHT` + `ANSWER` / `TOOL`)
- Hard-example emphasis offline
- Fixed learning rate
- Preference pairs for optional DPO later

## Run

```bash
# Simulation (CPU, tested)
python -m src.karpathy_loop --cycles 12 --collect 9

# Tests
python -m tests.test_karpathy_loop
```

## Real Muse path

1. ONLINE 1: roll out Glimmer (vLLM/Ollama) on tasks → log traces  
2. OFFLINE: filter with `muse_style_reward` + compress  
3. ONLINE 2: Unsloth/TRL LoRA or Foundry trainer on kept set  
4. GATE: holdout eval → promote adapter or rollback  

## Files

- `src/karpathy_loop.py` — loop implementation  
- `artifacts/karpathy/` — reports, preference pairs, checkpoints  
