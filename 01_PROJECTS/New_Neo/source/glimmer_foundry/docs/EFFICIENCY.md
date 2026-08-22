# Efficiency core (real gains, not fake exponential LR)

## What we shipped

| Technique | Effect |
|-----------|--------|
| Vectorized scoring (matmul batch) | ~10–12× less Python overhead |
| Hard-example importance sampling | Train on the 50% hardest rows only |
| Adaptive plateau skip | Skip ~40–50% of steps once a method plateaus |
| Preallocated noise buffers | Zero alloc per GRPO/Tree step |
| Max-throughput mode (`--cadence 0`) | No observational sleep |

Measured on this host:
- Before: ~0.093s / 50 cycles × 3 paradigms
- After:  ~0.008s / 50 cycles × 3 paradigms  (**~12× wall-clock**)
- 80 cycles finish in ~0.013s at ~19k paradigm-steps/sec
- Adaptive skip rate ~45% once plateaus appear

## What we refused

`lr *= 2**(elapsed/2)` — causes NaN within a few steps and destroys adapters.
That is not efficiency; it is numerical suicide.

Real efficiency = more verified holdout signal per wall-second, under fixed LR.
