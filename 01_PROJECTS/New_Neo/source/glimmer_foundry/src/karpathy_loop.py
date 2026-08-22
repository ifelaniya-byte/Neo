"""
Karpathy-style Online → Offline → Online loop for GlimmerFoundry.

Pattern (tested in simulation; real path uses Muse + LoRA):
  ONLINE  1  Generate / collect trajectories against live verifier
  OFFLINE    Curate, compress, build preference pairs, hard-example set
  ONLINE  2  Apply filtered / GRPO / Tree update on curated batch only
  GATE       Holdout promote or rollback
  REPEAT

Incorporates Muse evolution tips:
  - LoRA-only (base frozen)
  - Tool-success + format + abstain rewards
  - Reasoning preservation (mix think + answer)
  - Fixed LR (never time-scaled)
  - Hard-example focus offline
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .compressor import compress_prompt
from .ledger import Ledger
from .paradigms import build_paradigms, hard_mask
from .safety import SafetyGuard
from .verifier import verify_output_text


@dataclass
class Trajectory:
    prompt: str
    output: str
    reward: float
    tool_ok: bool
    format_ok: bool
    abstained: bool
    phase: str  # online1 | offline | online2
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LoopStats:
    cycle: int = 0
    online1_collected: int = 0
    offline_kept: int = 0
    offline_dropped: int = 0
    online2_updates: int = 0
    promotions: int = 0
    rollbacks: int = 0
    holdout_scores: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def muse_style_reward(text: str, expected: Optional[str] = None) -> dict[str, Any]:
    """
    Muse / A1B-inspired reward components (deterministic).
    """
    format_ok = bool(
        ("SOLUTION:" in text or "ANSWER:" in text or "TOOL:" in text)
        and 8 <= len(text.strip()) <= 2000
    )
    tool_ok = "TOOL:" in text and ("{" in text or "(" in text)
    abstained = any(
        x in text.lower()
        for x in ("i don't know", "i do not know", "cannot determine", "insufficient")
    )
    answer_ok = verify_output_text(text, expected) if expected else format_ok

    # Composite: prefer correct answers; credit abstain over confident wrong
    reward = 0.0
    if answer_ok:
        reward += 1.0
    if format_ok:
        reward += 0.25
    if tool_ok:
        reward += 0.5
    if abstained and not answer_ok:
        reward += 0.35  # better than hallucinating
    if not format_ok and not abstained:
        reward -= 0.2

    return {
        "reward": float(reward),
        "format_ok": format_ok,
        "tool_ok": tool_ok,
        "abstained": abstained,
        "answer_ok": answer_ok,
    }


class KarpathyLoop:
    """
    Online → Offline → Online continual loop.

    Simulation mode uses numpy paradigms.
    Real mode hooks: collect text trajectories → offline filter → LoRA/GRPO step.
    """

    def __init__(self, cfg: dict, out_dir: str | Path = "./artifacts/karpathy"):
        self.cfg = cfg
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.paradigms = build_paradigms(cfg)
        self.ledger = Ledger()
        self.stats = LoopStats()
        self.buffer: list[Trajectory] = []
        self.safety = SafetyGuard(
            checkpoint_dir=str(self.out_dir / "ckpts"),
            drop_threshold=cfg.get("training", {}).get("holdout_drop_threshold", 0.15),
        )
        rng = np.random.default_rng(42)
        dim = cfg.get("simulation", {}).get("input_dim", 8)
        self.train_data = rng.standard_normal((24, dim))
        self.holdout_data = rng.standard_normal((12, dim))

    # ----- ONLINE 1: collect -----
    def online_collect(self, n: int = 8) -> list[Trajectory]:
        """Live generation against verifier (simulated as paradigm probes)."""
        collected = []
        for p in self.paradigms:
            for i in range(max(1, n // len(self.paradigms))):
                # Simulate an online rollout
                r = p.step(self.train_data)
                text = (
                    f"THOUGHT: probe {p.short} step {p.step_count}\n"
                    f"{'TOOL: search()' if r.get('accepted') else 'ANSWER: '}"
                    f"{'SOLUTION: ok' if r.get('score', 0) > 0.5 else 'uncertain'}"
                )
                if r.get("score", 0) < 0.35:
                    text = "I don't know — insufficient signal."
                m = muse_style_reward(text)
                traj = Trajectory(
                    prompt=f"task:{p.short}:{i}",
                    output=text,
                    reward=m["reward"],
                    tool_ok=m["tool_ok"],
                    format_ok=m["format_ok"],
                    abstained=m["abstained"],
                    phase="online1",
                )
                collected.append(traj)
                self.stats.online1_collected += 1
        self.buffer.extend(collected)
        return collected

    # ----- OFFLINE: curate -----
    def offline_curate(self, min_reward: float = 0.5) -> list[Trajectory]:
        """
        Karpathy offline phase:
          - drop low-reward / malformed
          - keep hard successes + good abstains
          - compress prompts
          - build preference-ready set
        """
        kept, dropped = [], []
        for t in self.buffer:
            if t.phase != "online1":
                continue
            compressed = compress_prompt(t.prompt)
            t.prompt = compressed
            # Keep: high reward OR useful abstain
            if t.reward >= min_reward or (t.abstained and t.reward >= 0.3):
                t.phase = "offline"
                kept.append(t)
            else:
                dropped.append(t)
        self.stats.offline_kept += len(kept)
        self.stats.offline_dropped += len(dropped)
        # Preference pairs: high vs low within buffer
        pairs_path = self.out_dir / "preference_pairs.jsonl"
        try:
            with open(pairs_path, "a") as f:
                highs = [t for t in kept if t.reward >= 0.8]
                lows = [t for t in self.buffer if t.reward < 0.3]
                for h in highs[:20]:
                    for low in lows[:2]:
                        f.write(
                            json.dumps(
                                {
                                    "prompt": h.prompt,
                                    "chosen": h.output,
                                    "rejected": low.output,
                                }
                            )
                            + "\n"
                        )
        except OSError as e:
            print(f"  [warn] preference pair write skipped: {e}")
        # Replace buffer with curated only
        self.buffer = [t for t in self.buffer if t.phase == "offline"] + kept
        # dedupe by object id roughly
        self.buffer = kept
        return kept

    # ----- ONLINE 2: train on curated only -----
    def online_update(self) -> dict[str, Any]:
        """Apply paradigm updates using only offline-curated signal density."""
        if not self.buffer:
            return {"status": "empty_buffer"}

        # Hard-example focus on train_data
        reports = []
        for p in self.paradigms:
            # Extra steps proportional to curated quality
            n_steps = max(1, min(5, self.stats.offline_kept // 3))
            for _ in range(n_steps):
                r = p.step(self.train_data)
                if r.get("accepted"):
                    self.ledger.record_accept(0.1)
                    self.stats.online2_updates += 1
                elif not r.get("skipped"):
                    self.ledger.record_reject(0.05)
                reports.append(r)

        # Holdout gate
        holdouts = {p.name: p.score(self.holdout_data) for p in self.paradigms}
        mean_h = float(np.mean(list(holdouts.values())))
        self.stats.holdout_scores.append(mean_h)

        def eval_fn():
            return mean_h

        self.safety.eval_fn = eval_fn

        def save_fn(path: Path):
            path = Path(path)
            try:
                path.mkdir(parents=True, exist_ok=True)
                (path / "meta.json").write_text(
                    json.dumps({"holdouts": holdouts, "cycle": self.stats.cycle})
                )
            except OSError as e:
                # non-fatal in constrained environments
                print(f"  [warn] checkpoint write skipped: {e}")

        gate = self.safety.after_update(save_fn)
        if gate.get("action") == "promote":
            self.stats.promotions += 1
        elif gate.get("action") == "rollback":
            self.stats.rollbacks += 1

        return {
            "status": "updated",
            "holdouts": holdouts,
            "gate": gate,
            "reports_n": len(reports),
        }

    # ----- full cycle -----
    def run_cycle(self, collect_n: int = 8) -> dict[str, Any]:
        self.stats.cycle += 1
        c1 = self.online_collect(n=collect_n)
        curated = self.offline_curate()
        upd = self.online_update()
        # clear soft buffer after update (keep ledger/stats)
        self.buffer = []
        summary = {
            "cycle": self.stats.cycle,
            "online1": len(c1),
            "offline_kept": len(curated),
            "update": upd,
            "stats": self.stats.to_dict(),
            "ledger_profit": self.ledger.profit,
        }
        try:
            (self.out_dir / "last_cycle.json").write_text(json.dumps(summary, indent=2, default=str))
        except OSError as e:
            print(f"  [warn] last_cycle write skipped: {e}")
        return summary

    def run(self, cycles: int = 10, collect_n: int = 8) -> dict[str, Any]:
        print("=" * 64)
        print("  KARPATHY LOOP  ·  Online → Offline → Online")
        print("  Muse tips: tool/format/abstain rewards · LoRA-only · fixed LR")
        print("=" * 64)
        t0 = time.perf_counter()
        history = []
        for i in range(cycles):
            s = self.run_cycle(collect_n=collect_n)
            history.append(s)
            h = s["update"].get("holdouts", {})
            hstr = "  ".join(f"{k[:12]}={v:.2f}" for k, v in h.items())
            print(
                f"[{s['cycle']:03d}] online1={s['online1']}  "
                f"kept={s['offline_kept']}  "
                f"gate={s['update'].get('gate', {}).get('action')}  "
                f"{hstr}"
            )
        wall = time.perf_counter() - t0
        report = {
            "cycles": cycles,
            "wall_seconds": round(wall, 4),
            "final_stats": self.stats.to_dict(),
            "ledger": self.ledger.to_dict(),
            "history_tail": history[-3:],
        }
        try:
            (self.out_dir / "karpathy_report.json").write_text(json.dumps(report, indent=2, default=str))
        except OSError as e:
            print(f"  [warn] report write skipped: {e}")
        print("-" * 64)
        print(
            f"  done  promotions={self.stats.promotions}  "
            f"rollbacks={self.stats.rollbacks}  "
            f"updates={self.stats.online2_updates}  "
            f"wall={wall:.3f}s"
        )
        print(f"  report → {self.out_dir / 'karpathy_report.json'}")
        print("=" * 64)
        return report


def main():
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Karpathy online-offline-online loop")
    parser.add_argument("--cycles", type=int, default=12)
    parser.add_argument("--collect", type=int, default=9)
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    cfg = yaml.safe_load(open(args.config))
    loop = KarpathyLoop(cfg)
    loop.run(cycles=args.cycles, collect_n=args.collect)


if __name__ == "__main__":
    main()
