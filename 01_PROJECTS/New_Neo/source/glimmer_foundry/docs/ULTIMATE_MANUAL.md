# Ultimate Manual — Weight Foundry / Universal Agent Lab
## Strongest-methods edition

This document is the single source of truth. Given only this file, the micro-agent must be able to **build** and **deconstruct** the system.

---

## 1. Purpose

A controlled continual-learning harness that absorbs the strongest open methods and keeps a stricter safety contract than most research repos:

- **Online-LoRA+** — task-free online CL, importance regularization, shift detection  
  (lineage: [Online-LoRA](https://github.com/Christina200/Online-LoRA-official), CL-LoRA)
- **GRPO-R1** — group-relative policy optimization without a critic  
  (lineage: DeepSeek-R1, [verl](https://github.com/volcengine/verl), [open-r1](https://github.com/huggingface/open-r1), [GRPO-Zero](https://github.com/policy-gradient/GRPO-Zero))
- **Tree-Filtered** — hierarchical adapter banks with interference isolation + hard filter  
  (lineage: [TreeLoRA](https://github.com/ZinYY/TreeLoRA), LibContinual CL-LoRA / InfLoRA)

Shared rules:

- One **deterministic verifier**
- Promotions require **holdout** improvement
- Failures **roll back**
- Learning rate is **never** multiplied by wall-clock time
- Base weights stay **frozen**

## 2. Why these three (and not weaker placeholders)

| Method | What we absorbed from SOTA | What we kept stricter |
|--------|----------------------------|------------------------|
| Online-LoRA+ | Loss-dynamics shift detection, importance-weighted adapter updates, anchor regularization | Still requires verifier / holdout for permanent promote |
| GRPO-R1 | Group relative advantage, no value network, optional KL-to-anchor, group size 8 | Fixed LR; deterministic reward only; holdout gate |
| Tree-Filtered | Multi-bank isolation, route-to-best, decay non-selected banks | Hard filter (score > threshold) before any bank update |

Simulation mode encodes the **update geometry** of each method in numpy so the closed loop runs on CPU. Real weight paths are in `src/trainer.py` (peft / trl / verl when installed).

## 3. Hard invariants (never violate)

1. Fixed or schedule-based LR only — never `lr * 2^(t/2)`.
2. Deterministic verifier for promotion decisions.
3. Holdout never used in the training loss or advantage that drives the update.
4. Rollback when holdout drops more than `holdout_drop_threshold`.
5. Base model frozen; only adapters / banks move.
6. Cadence is observational logging, not a gradient multiplier.

## 4. Architecture

```
[Task queue] → compress → generate (group for GRPO)
                ↓
         deterministic verifier
            /            \
         pass            fail → ledger loss
          ↓
    paradigm-specific update geometry
    (Online-LoRA+ | GRPO-R1 | Tree-Filtered)
          ↓
    safety: NaN / explosion / clip
          ↓
    holdout eval → promote or rollback
          ↓
    ledger + session + heartbeat
```

## 5. Real backends (when GPU packages exist)

| Backend | Detection | Use |
|---------|-----------|-----|
| verl | `import verl` | Production GRPO at scale |
| trl.GRPOTrainer | `from trl import GRPOTrainer` | open-r1 style GRPO |
| peft + transformers | always preferred over pure torch | Online-LoRA+ / Tree banks |
| simulation | always | CPU closed-loop comparison |

See `OnlineTrainerDaemon.grpo_step_hint()` for exact wiring notes.

## 6. File contract

| Path | Role |
|------|------|
| `src/paradigms.py` | OnlineLoRAPlus, GRPOR1, TreeFilteredAdapter |
| `src/lab.py` | Side-by-side closed loop + session.json |
| `src/trainer.py` | Real peft/trl/verl daemon |
| `src/safety.py` | NaN, explosion, holdout promote/rollback |
| `src/verifier.py` | Deterministic authority |
| `src/compressor.py` | Graphical + caveman token filters |
| `src/ledger.py` | Winnings / losses / profit |
| `src/micro_agent.py` | Build / deconstruct from this manual |
| `web/index.html` | Live dashboard |

## 7. Commands

```bash
python -m src.lab --mode simulation --cycles 30 --cadence 2.0
uvicorn src.server:app --host 0.0.0.0 --port 8000
python -m src.micro_agent "deconstruct GRPO-R1"
python -m src.micro_agent "build Online-LoRA+ with shift detection"
```

## 8. Advancement definition

A meaningful advancement is a **verified holdout gain** under the fixed-LR, filtered/relative/isolated update contract — not a larger context window and not an exponential LR trick.

End of Ultimate Manual.
