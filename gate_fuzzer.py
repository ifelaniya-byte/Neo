#!/usr/bin/env python3
"""Differential fuzzer: mutate subjects and expect engineer gates to stay fail-closed."""
from __future__ import annotations
import copy
import random
from typing import Any, Dict, List
from engineers import DoublePassEngineerGate


def mutate(subject: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    s = copy.deepcopy(subject)
    keys = list(s.keys())
    if not keys:
        return s
    k = rng.choice(keys)
    v = s[k]
    choice = rng.randint(0, 5)
    if choice == 0 and isinstance(v, (int, float)):
        s[k] = float("nan")
    elif choice == 1 and isinstance(v, (int, float)):
        s[k] = -abs(float(v)) * 10
    elif choice == 2 and "available_timestamp_ms" in s and "observed_timestamp_ms" in s:
        s["available_timestamp_ms"] = int(s["observed_timestamp_ms"]) - abs(rng.randint(1, 10**6))
    elif choice == 3 and "net_pnl_usd" in s:
        s["net_pnl_usd"] = 1e9  # break identity if costs present
    elif choice == 4:
        s[k] = None
    else:
        s["claim"] = "complete conclusive world physics"
    return s


def fuzz(
    seed_subjects: List[Dict[str, Any]],
    n: int = 20,
    seed: int = 0,
    ledger_path: str = "artifacts/fuzz_ledger.jsonl",
) -> Dict[str, Any]:
    rng = random.Random(seed)
    gate = DoublePassEngineerGate(ledger_path=ledger_path)
    results = []
    for i in range(n):
        base = rng.choice(seed_subjects)
        mut = mutate(base if isinstance(base, dict) else {"v": base}, rng)
        r = gate.run(mut, f"fuzz-{i}", "dict")
        results.append({
            "i": i,
            "allowed": r.allowed_for_llm,
            "verdict": r.final_verdict.value,
        })
    # Fuzzer success = mutations usually blocked (not all must be; NaN/completeness should block)
    n_blocked = sum(1 for x in results if not x["allowed"])
    return {
        "n": n,
        "n_blocked": n_blocked,
        "block_rate": n_blocked / max(n, 1),
        "results": results,
        "ok": n_blocked >= max(1, n // 3),  # at least ~1/3 blocked
    }
