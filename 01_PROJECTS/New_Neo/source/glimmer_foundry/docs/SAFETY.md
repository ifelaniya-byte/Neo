# Safety Layer

## Why this exists

A single NaN loss or a reward-hacked adapter can permanently destroy a LoRA checkpoint.  
The safety module is the last gate before and after every weight write.

## Guards

1. **NaN / Inf gradient block** — inspected before `optimizer.step()`.
2. **Explosion block** — total gradient norm > 10 × max_grad_norm → reject step.
3. **Holdout evaluation** — score computed on data that never enters the training loss.
4. **Promote** — holdout improves → write `checkpoints/best` and `checkpoints/current`.
5. **Rollback** — relative drop > `holdout_drop_threshold` → restore `best` into `current`.

## Forbidden patterns

- `lr = base_lr * (2 ** (elapsed / 2))`
- Training on the holdout set
- LLM-as-judge as the sole promotion criterion
- Updating base model weights in continual mode

## Watchdog

`GET /heartbeat` writes `watchdog_heartbeat.json` with wall time, uptime, and pass rate.  
External process supervisors can restart the container if the heartbeat goes stale.
