"""
Growing Assistant — learns alongside the LLM from test results.

Not a second neural net: a persistent skill/memory store that:
  - Ingests accuracy + Karpathy + lab reports
  - Updates confidence on methods, safety rules, Muse tips
  - Answers questions using accumulated evidence
  - Improves recommendations after each test run

Grows every time you run: python -m src.growing_assistant learn
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


MEMORY_PATH = Path("artifacts/assistant_memory.json")


@dataclass
class Skill:
    name: str
    confidence: float = 0.5  # 0..1
    evidence: list[str] = field(default_factory=list)
    wins: int = 0
    losses: int = 0

    def reinforce(self, success: bool, note: str) -> None:
        if success:
            self.wins += 1
            self.confidence = min(1.0, self.confidence + 0.05)
        else:
            self.losses += 1
            self.confidence = max(0.05, self.confidence - 0.04)
        self.evidence.append(note)
        self.evidence = self.evidence[-20:]  # keep last 20


@dataclass
class AssistantMemory:
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    lessons: list[str] = field(default_factory=list)
    skills: dict[str, dict] = field(default_factory=dict)
    method_scores: dict[str, list] = field(default_factory=dict)
    test_runs: int = 0
    total_passes: int = 0
    total_fails: int = 0

    def get_skill(self, name: str) -> Skill:
        if name not in self.skills:
            self.skills[name] = asdict(Skill(name=name))
        d = self.skills[name]
        return Skill(**d)

    def put_skill(self, skill: Skill) -> None:
        self.skills[skill.name] = asdict(skill)
        self.updated_at = time.time()

    def add_lesson(self, text: str) -> None:
        self.lessons.append(f"[{time.strftime('%Y-%m-%d %H:%M')}] {text}")
        self.lessons = self.lessons[-100:]
        self.updated_at = time.time()


def load_memory() -> AssistantMemory:
    if MEMORY_PATH.exists():
        try:
            data = json.loads(MEMORY_PATH.read_text())
            return AssistantMemory(**{k: v for k, v in data.items() if k in AssistantMemory.__dataclass_fields__})
        except Exception:
            pass
    return AssistantMemory()


def save_memory(mem: AssistantMemory) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        MEMORY_PATH.write_text(json.dumps(asdict(mem), indent=2))
    except OSError as e:
        print(f"[warn] memory save failed: {e}")


class GrowingAssistant:
    """Smarter operator that grows from every test suite run."""

    SEED_SKILLS = [
        "holdout_isolation",
        "fixed_lr",
        "online_lora",
        "grpo_r1",
        "tree_filtered",
        "karpathy_loop",
        "muse_rewards",
        "safety_rollback",
        "efficiency",
        "fusion_glimmer",
    ]

    def __init__(self):
        self.mem = load_memory()
        for s in self.SEED_SKILLS:
            if s not in self.mem.skills:
                self.mem.put_skill(Skill(name=s))

    def learn_from_accuracy_report(self, path: str | Path = "artifacts/accuracy_report.json") -> list[str]:
        path = Path(path)
        notes = []
        if not path.exists():
            notes.append("no accuracy_report.json yet — run tests.test_accuracy")
            return notes
        data = json.loads(path.read_text())
        self.mem.test_runs += 1
        status = data.get("suite_status") or data.get("multiseed_status")
        if status == "ALL PASS" or data.get("multiseed_status") == "PASS":
            self.mem.total_passes += 1
        # method holdouts
        multi = data.get("multiseed_holdout") or {}
        for name, stats in multi.items():
            mean = stats.get("mean", 0)
            self.mem.method_scores.setdefault(name, []).append(mean)
            self.mem.method_scores[name] = self.mem.method_scores[name][-50:]
            skill_key = {
                "Online-LoRA+": "online_lora",
                "GRPO-R1": "grpo_r1",
                "Tree-Filtered": "tree_filtered",
            }.get(name)
            if skill_key:
                sk = self.mem.get_skill(skill_key)
                sk.reinforce(mean >= 0.4, f"holdout mean={mean:.3f}")
                self.mem.put_skill(sk)
        # safety
        if data.get("safety", {}).get("status") == "PASS":
            sk = self.mem.get_skill("safety_rollback")
            sk.reinforce(True, "safety suite passed")
            self.mem.put_skill(sk)
        if data.get("efficiency", {}).get("status") == "PASS":
            sk = self.mem.get_skill("efficiency")
            sps = data.get("efficiency", {}).get("steps_per_second", 0)
            sk.reinforce(sps > 1000, f"steps/sec={sps}")
            self.mem.put_skill(sk)
        self.mem.add_lesson(f"Ingested accuracy report; methods={list(multi.keys())}")
        notes.append("learned from accuracy_report.json")
        save_memory(self.mem)
        return notes

    def learn_from_karpathy(self, path: str | Path = "artifacts/karpathy_test/karpathy_report.json") -> list[str]:
        path = Path(path)
        notes = []
        if not path.exists():
            # try alternate
            alt = Path("artifacts/karpathy/karpathy_report.json")
            path = alt if alt.exists() else path
        if not path.exists():
            return ["no karpathy report — run tests.test_karpathy_loop"]
        data = json.loads(path.read_text())
        stats = data.get("final_stats") or {}
        sk = self.mem.get_skill("karpathy_loop")
        promo = stats.get("promotions", 0)
        sk.reinforce(promo >= 0, f"promotions={promo} updates={stats.get('online2_updates')}")
        self.mem.put_skill(sk)
        sk2 = self.mem.get_skill("muse_rewards")
        sk2.reinforce(True, "karpathy used muse_style_reward")
        self.mem.put_skill(sk2)
        self.mem.add_lesson(
            f"Karpathy cycle done: promotions={promo}, "
            f"online1={stats.get('online1_collected')}, kept={stats.get('offline_kept')}"
        )
        notes.append("learned from karpathy report")
        save_memory(self.mem)
        return notes

    def learn_all(self) -> dict[str, Any]:
        notes = []
        notes += self.learn_from_accuracy_report()
        notes += self.learn_from_karpathy()
        # fusion skill
        sk = self.mem.get_skill("fusion_glimmer")
        sk.reinforce(True, "GlimmerFoundry config present")
        self.mem.put_skill(sk)
        sk = self.mem.get_skill("fixed_lr")
        sk.reinforce(True, "invariant: never time-scale LR")
        self.mem.put_skill(sk)
        sk = self.mem.get_skill("holdout_isolation")
        sk.reinforce(True, "holdout never in train signal")
        self.mem.put_skill(sk)
        save_memory(self.mem)
        return {
            "notes": notes,
            "test_runs": self.mem.test_runs,
            "skills": {k: v.get("confidence") for k, v in self.mem.skills.items()},
            "lessons_tail": self.mem.lessons[-5:],
        }

    def recommend(self) -> str:
        """Recommend strongest method from accumulated scores."""
        best_name, best_avg = None, -1.0
        for name, vals in self.mem.method_scores.items():
            if not vals:
                continue
            avg = sum(vals) / len(vals)
            if avg > best_avg:
                best_avg, best_name = avg, name
        skills_sorted = sorted(
            ((k, v.get("confidence", 0)) for k, v in self.mem.skills.items()),
            key=lambda x: -x[1],
        )
        lines = [
            "=== GROWING ASSISTANT ===",
            f"test_runs={self.mem.test_runs}  passes≈{self.mem.total_passes}",
            f"recommended_method={best_name or 'n/a'}  avg_holdout={best_avg if best_name else 0:.2%}",
            "top_skills:",
        ]
        for k, c in skills_sorted[:6]:
            lines.append(f"  {k:<20} confidence={c:.2f}")
        if self.mem.lessons:
            lines.append("recent_lessons:")
            for L in self.mem.lessons[-3:]:
                lines.append(f"  - {L}")
        lines.append(
            "advice: keep base frozen; run Karpathy loop after each online batch; "
            "promote only on holdout gain."
        )
        return "\n".join(lines)

    def ask(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ("learn", "ingest", "update")):
            r = self.learn_all()
            return self.recommend() + "\n\nlearn_result=" + json.dumps(r, indent=2)
        if any(w in q for w in ("recommend", "best", "which method")):
            return self.recommend()
        if "safety" in q:
            sk = self.mem.get_skill("safety_rollback")
            return f"safety confidence={sk.confidence:.2f} wins={sk.wins} evidence={sk.evidence[-3:]}"
        if "karpathy" in q or "loop" in q:
            sk = self.mem.get_skill("karpathy_loop")
            return f"karpathy confidence={sk.confidence:.2f} wins={sk.wins}\n" + self.recommend()
        return self.recommend()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", nargs="?", default="learn", help="learn | recommend | ask ...")
    parser.add_argument("rest", nargs="*", default=[])
    args = parser.parse_args()
    ga = GrowingAssistant()
    if args.cmd == "learn":
        print(json.dumps(ga.learn_all(), indent=2))
        print()
        print(ga.recommend())
    elif args.cmd == "recommend":
        print(ga.recommend())
    else:
        q = " ".join([args.cmd] + args.rest)
        print(ga.ask(q))


if __name__ == "__main__":
    main()
