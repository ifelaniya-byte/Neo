"""Micro-agent: given the Ultimate Manual, build or deconstruct any part of the Lab."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

MANUAL = Path(__file__).resolve().parents[1] / "docs" / "ULTIMATE_MANUAL.md"


def load_manual() -> str:
    if MANUAL.exists():
        return MANUAL.read_text()
    return "(Ultimate Manual not found.)"


ACTIONS = {
    "build": """
Scaffold / repair Weight Foundry (strongest-methods edition).

Methods locked in:
  01 Online-LoRA+  — shift detect + importance reg + anchor (Online-LoRA + CL-LoRA)
  02 GRPO-R1       — group relative advantages, no critic, KL anchor (verl/open-r1/GRPO-Zero)
  03 Tree-Filtered — multi-bank isolation + hard filter (TreeLoRA / CL-LoRA / InfLoRA)

Invariants enforced on every build:
  1. Fixed LR — never multiply by wall-clock time
  2. Deterministic verifier only for promotions
  3. Holdout never in training loss
  4. Rollback on holdout regression
  5. Base frozen; adapters/banks only

Run:
  python -m src.lab --mode simulation --cycles 20
  uvicorn src.server:app --host 0.0.0.0 --port 8000
""",
    "deconstruct": """
Deconstruction map (strongest edition):

Online-LoRA+ (paradigms.OnlineLoRAPlus)
  - Absorbs: task-free online CL, loss-dynamics shift detection, Fisher-like importance, anchor reg
  - NOT: full vision Online-LoRA paper training loop (we encode geometry for LLM harness)

GRPO-R1 (paradigms.GRPOR1)
  - Absorbs: group relative advantage, no value net, KL-to-anchor, group size 8
  - NOT: full verl multi-node trainer (use trainer.py backend=verl for that)

Tree-Filtered (paradigms.TreeFilteredAdapter)
  - Absorbs: hierarchical banks, route-to-best, interference decay, hard filter
  - NOT: full TreeLoRA gradient-similarity tree over real transformer layers

safety.py  — last gate; without it one NaN destroys the adapter
verifier.py — sole promotion authority
ledger.py — accounting only
trainer.py — real peft/trl/verl when installed; simulation otherwise
lab.py — closed loop that scores all three on the same holdout
""",
    "run": """
python -m src.lab --mode simulation --cycles 30 --cadence 2.0
uvicorn src.server:app --host 0.0.0.0 --port 8000
""",
    "safety": """
Safety contract:
- NaN/Inf block before optimizer.step
- Gradient explosion block
- Holdout never trained on
- Promote only on holdout improvement
- Rollback if relative drop > threshold
- LR never scaled by elapsed seconds
- Importance regularization (Online-LoRA+) protects critical dims
""",
    "fusion": """
GlimmerFoundry = Muse Glimmer (Meta open local model) × Weight Foundry (continual harness).

Fills both gaps:
  • Downloadable Apache 2.0 ~30B on-device agent weights
  • Continual Online-LoRA+ / GRPO-R1 / Tree-Filtered under holdout safety

Base: meta-models/Muse-Glimmer-30B (4-bit on one consumer GPU)
Harness: frozen base + adapters only; promote on holdout; never time-scale LR

See docs/FUSION.md and GET /fusion
""",
    "lineage": """
Lineage of the three methods:
  Online-LoRA+  ← https://github.com/Christina200/Online-LoRA-official
                 + LibContinual CL-LoRA / InfLoRA ideas
  GRPO-R1       ← https://github.com/volcengine/verl
                 + https://github.com/huggingface/open-r1
                 + https://github.com/policy-gradient/GRPO-Zero
  Tree-Filtered ← https://github.com/ZinYY/TreeLoRA
                 + LibContinual CL-LoRA family

Weight Foundry adds: unified verifier, holdout promote/rollback, fixed-LR contract,
live dashboard, micro-agent, CPU simulation of all three side-by-side.
""",
}


def respond(query: str) -> str:
    q = query.lower().strip()
    manual_excerpt = load_manual()[:1400]

    if any(w in q for w in ("build", "scaffold", "create", "make", "upgrade")):
        body = ACTIONS["build"]
    elif any(w in q for w in ("deconstruct", "explain", "what is", "map")):
        body = ACTIONS["deconstruct"]
    elif any(w in q for w in ("run", "start", "launch")):
        body = ACTIONS["run"]
    elif any(w in q for w in ("safety", "rollback", "nan")):
        body = ACTIONS["safety"]
    elif any(w in q for w in ("fusion", "glimmer", "merge", "zuckerberg", "meta")):
        body = ACTIONS["fusion"]
    elif any(w in q for w in ("lineage", "source", "github", "strongest")):
        body = ACTIONS["lineage"]
    else:
        body = (
            "Weight Foundry micro-agent (strongest edition).\n"
            "Commands: build | deconstruct | run | safety | lineage\n"
        )

    return textwrap.dedent(f"""
    === MICRO-AGENT (Weight Foundry · strongest edition) ===
    Query: {query}

    {body}

    --- Manual excerpt ---
    {manual_excerpt}
    ...
    """).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default="lineage")
    args = parser.parse_args()
    print(respond(args.query))


if __name__ == "__main__":
    main()
