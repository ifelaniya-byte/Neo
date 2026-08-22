"""Closed-loop harness — strongest methods + efficiency metrics."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .ledger import Ledger
from .paradigms import build_paradigms
from .safety import SafetyGuard
from .fusion import fusion_banner


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_simulation(cfg: dict, cycles: int = 30, cadence: float = 0.0) -> dict:
    """
    cadence=0 means max throughput (no observational sleep).
    Efficiency metrics logged: steps/sec, skip rate, holdout gain per second.
    """
    sim = cfg.get("simulation", {})
    dim = sim.get("input_dim", 8)
    n_test = sim.get("n_test", 20)
    n_holdout = sim.get("n_holdout", 10)

    rng = np.random.default_rng(42)
    train_data = rng.standard_normal((n_test, dim))
    holdout_data = rng.standard_normal((n_holdout, dim))

    paradigms = build_paradigms(cfg)
    ledger = Ledger()

    session: dict[str, Any] = {
        "started_at": time.time(),
        "mode": "simulation",
        "methods": [p.name for p in paradigms],
        "efficiency": {},
        "cycles": [],
        "paradigm_scores": {p.name: [] for p in paradigms},
        "leader": None,
    }

    t0 = time.perf_counter()
    print(fusion_banner(cfg))
    print("  vectorized · hard-example sampling · adaptive skip · fixed LR")
    print("=" * 72)
    print(f"  Cycles: {cycles} | Cadence sleep: {cadence}s (0 = max throughput)")
    print()

    for cycle in range(1, cycles + 1):
        results = []
        for p in paradigms:
            r = p.step(train_data)
            r["holdout"] = p.score(holdout_data)
            results.append(r)
            if r.get("accepted"):
                ledger.record_accept(max(0.05, abs(r.get("delta", 0.1))))
            elif not r.get("skipped"):
                ledger.record_reject()
            session["paradigm_scores"][p.name].append(r["score"])

        best = max(results, key=lambda x: x["score"])
        session["leader"] = best["method"]
        elapsed = time.perf_counter() - t0

        if cycle <= 5 or cycle % 10 == 0 or cycle == cycles:
            scores_str = "  ".join(
                f"{r['method'][:14]:<14} {r['score']:.2%}" for r in results
            )
            skips = sum(1 for r in results if r.get("skipped"))
            print(f"[{cycle:04d}] t={elapsed:6.3f}s  {scores_str}  skips={skips}")

        session["cycles"].append({
            "cycle": cycle,
            "wall_time": round(elapsed, 4),
            "leader": best["method"],
            "scores": {r["method"]: r["score"] for r in results},
        })

        if cadence > 0:
            time.sleep(cadence)

    wall = time.perf_counter() - t0
    final = {p.name: p.score(holdout_data) for p in paradigms}
    leader_name = max(final, key=final.get)
    total_steps = sum(p.step_count for p in paradigms)
    total_skips = sum(p.skipped for p in paradigms)

    efficiency = {
        "wall_seconds": round(wall, 4),
        "cycles": cycles,
        "total_paradigm_steps": total_steps,
        "steps_per_second": round(total_steps / max(wall, 1e-9), 1),
        "skip_count": total_skips,
        "skip_rate": round(total_skips / max(total_steps, 1), 3),
        "holdout_per_second": {
            name: round(sc / max(wall, 1e-9), 4) for name, sc in final.items()
        },
    }
    session["efficiency"] = efficiency
    session["final_holdout"] = final
    session["final_leader"] = leader_name
    session["elapsed"] = wall

    Path(cfg["paths"]["session_file"]).parent.mkdir(parents=True, exist_ok=True)
    with open(cfg["paths"]["session_file"], "w") as f:
        json.dump(session, f, indent=2, default=str)
    ledger.save(cfg["paths"]["ledger_file"])

    print()
    print("-" * 72)
    print("  FINAL HOLDOUT")
    for name, sc in final.items():
        mark = "  ← LEADER" if name == leader_name else ""
        print(f"    {name:<28} {sc:.2%}{mark}")
    print()
    print("  EFFICIENCY")
    print(f"    wall time          {wall:.4f}s")
    print(f"    steps/sec          {efficiency['steps_per_second']}")
    print(f"    adaptive skips     {total_skips}/{total_steps} ({efficiency['skip_rate']:.0%})")
    print(f"    Ledger profit      {ledger.profit:.2f}")
    print("=" * 72)
    return session


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["simulation", "lora"], default="simulation")
    parser.add_argument("--cycles", type=int, default=50)
    parser.add_argument("--cadence", type=float, default=0.0,
                        help="Observational sleep; 0 = max throughput")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.mode == "simulation":
        run_simulation(cfg, cycles=args.cycles, cadence=args.cadence)
    else:
        print("Use uvicorn src.server:app for live API")


if __name__ == "__main__":
    main()
