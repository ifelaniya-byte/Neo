#!/usr/bin/env python3
"""
Fix A: generate condensed distribution scripts from the canonical multi-file package.

  python build_condense.py

Humans edit modules in this tree only. Output files are GENERATED — DO NOT EDIT.
See CANONICAL.md.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_SPINE = ROOT / "megacompact_condensed_spine.py"
OUT_ENGINE = ROOT / "megacompact_condensed_engine.py"

SPINE_MODULES = [
    "check_registry.py",
    "constants_db.py",
    "known_settled_db.py",
    "typed_ir.py",
    "interval_arith.py",
    "causal_graph.py",
    "chain_observer_ro.py",
    "sandbox.py",
    "merkle_artifacts.py",
    "smt_gate.py",
    "ledger_index.py",
    "bit_exact_replay.py",
    "differential_audit.py",
    "formal_bridge.py",
    "signed_ledger.py",
    "unit_tags.py",
    "atlas.py",
    "rag_settled/__init__.py",
    "schema_registry/__init__.py",
    "knowledge_coverage.py",
    "knowledge_facade.py",
    "engineers.py",
    "adversarial_suite.py",
    "gate_fuzzer.py",
    "promotion.py",
    "adapters/historical.py",
    "adapters/feed_format.py",
    "independent_audit.py",
    "llm_wrapper.py",
    "ci/lab_ci.py",
    "tools/artifacts.py",
    "tools/verifiers.py",
    "uair/contracts.py",
    "uair/layers.py",
    "uair/orchestrator.py",
]

LOCAL_MODS = {
    "engineers", "atlas", "known_settled_db", "constants_db", "rag_settled",
    "knowledge_coverage", "knowledge_facade", "signed_ledger", "formal_bridge",
    "adversarial_suite", "bit_exact_replay", "merkle_artifacts", "schema_registry",
    "unit_tags", "ledger_index", "smt_gate", "interval_arith", "causal_graph",
    "typed_ir", "sandbox", "promotion", "independent_audit", "gate_fuzzer",
    "tools", "adapters", "llm_wrapper", "ci", "uair", "historical", "contracts",
    "layers", "orchestrator", "check_registry", "chain_observer_ro",
}

NONE_CLOBBER_KEYS = [
    "load_schema", "validate_required", "pre_trade_gate", "run_suite",
    "Interval", "trade_allowed_by_interval", "net_edge_interval",
    "SignedLedger", "get_atlas", "get_settled_db", "get_constants_db",
    "full_mechanical_battery", "self_proof", "build_merkle",
    "submit_obligation", "kernel_available", "try_lean_check",
]


def strip_local_imports(src: str) -> str:
    lines = src.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("from __future__"):
            i += 1
            continue
        is_import = stripped.startswith("import ") or stripped.startswith("from ")
        if is_import:
            block = [line]
            paren = stripped.count("(") - stripped.count(")")
            j = i + 1
            while paren > 0 and j < len(lines):
                block.append(lines[j])
                paren += lines[j].count("(") - lines[j].count(")")
                j += 1
            block_text = "\n".join(block)
            local = False
            if stripped.startswith("from "):
                m = re.match(r"from\s+(\.?[\w\.]*)\s+import", stripped)
                if m:
                    mod = m.group(1)
                    if mod.startswith(".") or mod.split(".")[0] in LOCAL_MODS:
                        local = True
            elif stripped.startswith("import "):
                rest = stripped[len("import "):].split("#")[0]
                for part in rest.split(","):
                    name = part.strip().split(" as ")[0].strip().split(".")[0]
                    if name in LOCAL_MODS:
                        local = True
            if local:
                i = j
                continue
            out.extend(block)
            i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def fix_empty_tries(src: str) -> str:
    src = re.sub(
        r"try:\s*\nexcept Exception:\s*\n((?:[ \t]+.+\n)+)",
        lambda m: "\n".join(line.lstrip() for line in m.group(0).splitlines() if not line.strip().startswith("try:") and not line.strip().startswith("except")) + "\n",
        src,
    )
    # Remove lines that assign known callables to None
    for k in NONE_CLOBBER_KEYS:
        src = re.sub(rf"^.*\b{k}\b.*= None.*\n", "", src, flags=re.M)
    src = re.sub(r"^Interval = net_edge_interval = trade_allowed_by_interval = None.*\n", "", src, flags=re.M)
    return src


def section_rename(src: str, begin: str, end: str, old: str, new: str) -> str:
    marker_b = f"# ===== BEGIN {begin} ====="
    marker_e = f"# ===== END {begin} ====="
    if marker_b not in src:
        return src
    head, rest = src.split(marker_b, 1)
    mid, tail = rest.split(marker_e, 1)
    mid = mid.replace(old, new)
    return head + marker_b + mid + marker_e + tail


def embed_data() -> str:
    data = {}
    for rel in [
        "policies/calibration_thresholds.json",
        "schema_registry/events_v1.json",
        "schema_registry/packets_v1.json",
        "schema_registry/labels_v1.json",
        "rag_settled/corpus.jsonl",
        "artifacts/known_settled_export.json",
        "schemas/normalized_event_feed.v1.json",
    ]:
        p = ROOT / rel
        if p.exists():
            data[rel] = p.read_text(encoding="utf-8", errors="replace")
    return (
        "_EMBEDDED_DATA = " + repr(data) + "\n\n"
        "def _embedded(rel: str, default: str = '') -> str:\n"
        "    return _EMBEDDED_DATA.get(rel, default)\n\n"
    )


def build_spine() -> Path:
    ts = datetime.now(timezone.utc).isoformat()
    parts = [f'''#!/usr/bin/env python3
# GENERATED — DO NOT EDIT. Canonical source: multi-file package. See CANONICAL.md
# Built by build_condense.py at {ts}
"""MegaCompact condensed spine (distribution only). Stdlib. Regenerate via: python build_condense.py"""
from __future__ import annotations

import ast
import csv
import copy
import hashlib
import hmac
import json
import math
import os
import platform
import random
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time
import traceback
import concurrent.futures
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Protocol, Set, Tuple, Union

''']
    parts.append(embed_data())
    missing = []
    for rel in SPINE_MODULES:
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        src = p.read_text(encoding="utf-8", errors="replace")
        if rel == "differential_audit.py":
            src = src.replace("def compare_runs", "def differential_compare_runs")
        if rel == "ledger_index.py":
            src = src.replace("def search(", "def ledger_search(")
        src = strip_local_imports(src)
        if rel == "rag_settled/__init__.py":
            src = src.replace(
                "def load_corpus() -> List[Dict[str, Any]]:\n    _ensure_seed_corpus()",
                "def load_corpus() -> List[Dict[str, Any]]:\n"
                "    if not _CORPUS.exists():\n"
                "        t = _embedded('rag_settled/corpus.jsonl', '')\n"
                "        if t:\n"
                "            _CORPUS.parent.mkdir(parents=True, exist_ok=True)\n"
                "            _CORPUS.write_text(t, encoding='utf-8')\n"
                "    _ensure_seed_corpus()",
            )
        if rel == "schema_registry/__init__.py":
            src = re.sub(
                r"def load_schema\(name: str\) -> Dict\[str, Any\]:.*?(?=\ndef |\nclass |\Z)",
                '''def load_schema(name: str) -> Dict[str, Any]:
    mapping = {
        "events_v1": "schema_registry/events_v1.json",
        "packets_v1": "schema_registry/packets_v1.json",
        "labels_v1": "schema_registry/labels_v1.json",
        "NormalizedEvent": "schema_registry/events_v1.json",
        "DecisionPacket": "schema_registry/packets_v1.json",
        "OutcomeLabel": "schema_registry/labels_v1.json",
    }
    key = name[:-5] if name.endswith(".json") else name
    rel = mapping.get(key) or mapping.get(name) or f"schema_registry/{key}.json"
    raw = _embedded(rel, "")
    if raw:
        return json.loads(raw)
    path = Path("schema_registry") / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(name)

''',
                src,
                count=1,
                flags=re.S,
            )
        if rel == "differential_audit.py":
            src += "\ncompare_runs = differential_compare_runs\n"
        if rel == "ledger_index.py":
            src += "\nsearch = ledger_search\n"
        parts.append(f"\n# ===== BEGIN {rel} =====\n")
        parts.append(src)
        parts.append(f"\n# ===== END {rel} =====\n")

    text = "\n".join(parts)
    text = fix_empty_tries(text)
    # Neuter intermediate __main__ blocks so only spine CLI runs
    text = re.sub(
        r'\nif __name__ == ["\']__main__["\']:\n',
        '\nif __name__ == "__main__" and False:  # disabled in GENERATED spine\n',
        text,
    )

    # collision renames inside sections
    text = section_rename(text, "known_settled_db.py", "", "_DB", "_SETTLED_DB")
    text = section_rename(text, "constants_db.py", "", "_DB", "_CONSTANTS_DB")
    text = section_rename(text, "rag_settled/__init__.py", "", "_ROOT", "_RAG_ROOT")
    text = section_rename(text, "rag_settled/__init__.py", "", "_CORPUS", "_RAG_CORPUS")
    # fix embed inject still using _CORPUS if renamed mid-file — re-apply corpus exists check name
    text = text.replace("if not _CORPUS.exists()", "if not _RAG_CORPUS.exists()")
    text = text.replace("_CORPUS.parent", "_RAG_CORPUS.parent")
    text = text.replace("_CORPUS.write_text", "_RAG_CORPUS.write_text")
    text = section_rename(text, "schema_registry/__init__.py", "", "_ROOT", "_SCHEMA_ROOT")

    # disable intermediate __main__ adversarial auto-run
    text = text.replace(
        'if __name__ == "__main__":\n    print(json.dumps(run_suite(), indent=2))',
        'if __name__ == "__main__" and False:\n    print(json.dumps(run_suite(), indent=2))',
    )

    # soft-dep defaults before engineers if needed
    eng = "# ===== BEGIN engineers.py ====="
    if eng in text and "rag_search =" not in text[text.find(eng):text.find(eng)+800]:
        inject = '''
# Spine inlined soft-deps
ATLAS_AVAILABLE = True
SETTLED_DB_AVAILABLE = True
SCHEMA_REG_AVAILABLE = True
LEDGER_INDEX_AVAILABLE = True
RAG_AVAILABLE = True
CONSTANTS_AVAILABLE = True
SYMPY_AVAILABLE = False
sympy = None
UNIT_TAGS_AVAILABLE = True

def rag_search(query, limit=5):
    q = query.lower().split()
    hits = []
    for d in load_corpus():
        blob = (d.get("title", "") + " " + d.get("text", "") + " " + " ".join(d.get("tags", []))).lower()
        score = sum(1 for t in q if t in blob)
        if score:
            hits.append((score, d))
    hits.sort(key=lambda x: -x[0])
    return [h for _, h in hits[:limit]]

ledger_search = globals().get("ledger_search") or globals().get("search")
'''
        text = text.replace(eng, eng + inject)

    text += '''
def _spine_main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="GENERATED condensed spine — do not edit; rebuild with build_condense.py")
    p.add_argument("cmd", nargs="?", default="help",
                   choices=["help", "adversarial", "smt-demo", "evidence", "feed-demo"])
    args = p.parse_args(argv)
    if args.cmd == "adversarial":
        print(json.dumps(run_suite(), indent=2, default=str))
    elif args.cmd == "smt-demo":
        print("allow", pre_trade_gate(2.0, 0.01, 0.95, 0.1))
        print("block", pre_trade_gate(0.1, 0.5, 0.5, 0.9))
    elif args.cmd == "evidence":
        print(json.dumps(evidence_for_decision({"regime": "normal"}), indent=2, default=str))
    elif args.cmd == "feed-demo":
        path = write_example_feed("artifacts/spine_feed_demo.json", n=3)
        print(json.dumps(ingest_feed_file(path), indent=2, default=str)[:2000])
    else:
        print("GENERATED file. Edit canonical modules, then: python build_condense.py")
        print("cmds: adversarial | smt-demo | evidence | feed-demo")
    return 0

if __name__ == "__main__":
    raise SystemExit(_spine_main())
'''
    OUT_SPINE.write_text(text, encoding="utf-8")
    return OUT_SPINE, missing


def build_engine() -> Path:
    ts = datetime.now(timezone.utc).isoformat()
    core = (ROOT / "megacompact16" / "core.py").read_text(encoding="utf-8", errors="replace")
    pipe = (ROOT / "pipeline.py").read_text(encoding="utf-8", errors="replace")
    run = (ROOT / "run_all.py").read_text(encoding="utf-8", errors="replace")
    pipe = re.sub(
        r"sys\.path\.insert\(0, str\(Path\(__file__\)\.parent / \"megacompact16\"\)\s*\nimport core as mc.*\n",
        "import core as mc  # bootstrapped below\n",
        pipe,
        count=1,
    )
    run = re.sub(
        r"sys\.path\.insert\(0, str\(Path\(__file__\)\.parent / \"megacompact16\"\)\s*\nimport core as mc\s*\n",
        "import core as mc\n",
        run,
        count=1,
    )
    text = f'''#!/usr/bin/env python3
# GENERATED — DO NOT EDIT. Canonical: megacompact16/core.py, pipeline.py, run_all.py. See CANONICAL.md
# Built by build_condense.py at {ts}
"""Condensed engine (numpy/pandas/pydantic). Requires megacompact_condensed_spine.py beside this file."""
from __future__ import annotations
import sys
from pathlib import Path
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import megacompact_condensed_spine as spine
import types

def _mod(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m

_mod("smt_gate", pre_trade_gate=spine.pre_trade_gate, Constraint=getattr(spine, "Constraint", None), solve=getattr(spine, "solve", None))
_mod("interval_arith", Interval=spine.Interval, trade_allowed_by_interval=spine.trade_allowed_by_interval, net_edge_interval=getattr(spine, "net_edge_interval", None))
_mod("engineers", DoublePassEngineerGate=spine.DoublePassEngineerGate, EngineerVerdict=spine.EngineerVerdict,
     StationaryEngineer=getattr(spine, "StationaryEngineer", None), NonStationaryEngineer=getattr(spine, "NonStationaryEngineer", None),
     DoublePassResult=getattr(spine, "DoublePassResult", None))
_mod("adversarial_suite", run_suite=spine.run_suite)
_mod("knowledge_coverage", evidence_for_decision=spine.evidence_for_decision, coverage_report=spine.coverage_report, best_effort_answer=spine.best_effort_answer)
_mod("knowledge_facade", get_facade=getattr(spine, "get_facade", None))

# ===== BEGIN core.py =====
{core}
# ===== END core.py =====

_core_mod = types.ModuleType("core")
_core_mod.__dict__.update({{k: v for k, v in list(globals().items()) if not k.startswith("__")}})
sys.modules["core"] = _core_mod
sys.modules["megacompact16.core"] = _core_mod

# ===== BEGIN pipeline.py =====
{pipe}
# ===== BEGIN run_all.py =====
{run}

if __name__ == "__main__":
    raise SystemExit(main())
'''
    OUT_ENGINE.write_text(text, encoding="utf-8")
    return OUT_ENGINE


def main() -> int:
    spine_path, missing = build_spine()
    print("wrote", spine_path, "bytes", spine_path.stat().st_size)
    if missing:
        print("missing modules:", missing)
    eng = build_engine()
    print("wrote", eng, "bytes", eng.stat().st_size)
    # syntax check spine
    import ast
    try:
        ast.parse(spine_path.read_text(encoding="utf-8"))
        print("spine AST OK")
    except SyntaxError as e:
        print("spine SYNTAX", e)
        return 1
    print("CANONICAL: edit multi-file package only; regenerate with this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
