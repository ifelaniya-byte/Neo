"""Assured tests for Online → Offline → Online Karpathy loop."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from src.karpathy_loop import KarpathyLoop, muse_style_reward


def test_muse_reward():
    r = muse_style_reward("ANSWER: SOLUTION: 42", expected="42")
    assert r["answer_ok"] and r["reward"] >= 1.0
    r2 = muse_style_reward("I don't know — insufficient data")
    assert r2["abstained"] and r2["reward"] > 0
    r3 = muse_style_reward("blah")
    assert r3["reward"] < 0.5
    print("  PASS  muse_style_reward")


def test_full_loop():
    cfg = yaml.safe_load(open("config.yaml"))
    out = Path("artifacts/karpathy_test")
    loop = KarpathyLoop(cfg, out_dir=out)
    report = loop.run(cycles=5, collect_n=6)
    assert report["cycles"] == 5
    assert loop.stats.online1_collected > 0
    assert loop.stats.offline_kept >= 0
    assert (out / "karpathy_report.json").exists()
    # holdout scores recorded
    assert len(loop.stats.holdout_scores) == 5
    for s in loop.stats.holdout_scores:
        assert 0.0 <= s <= 1.0
    print("  PASS  full online-offline-online loop")
    print(f"  promotions={loop.stats.promotions} rollbacks={loop.stats.rollbacks}")
    print(f"  online1={loop.stats.online1_collected} kept={loop.stats.offline_kept}")
    return report


if __name__ == "__main__":
    print("KARPATHY LOOP TESTS")
    test_muse_reward()
    test_full_loop()
    print("ALL PASS")
