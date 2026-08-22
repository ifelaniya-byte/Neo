#!/usr/bin/env python3
"""Generate distribution monolith: embed module sources and exec into one namespace."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent

MODULES = [
    "check_registry.py",
    "constants_db.py",
    "known_settled_db.py",
    "atlas.py",
    "unit_tags.py",
    "smt_gate.py",
    "interval_arith.py",
    "merkle_artifacts.py",
    "sandbox.py",
    "typed_ir.py",
    "causal_graph.py",
    "chain_observer_ro.py",
    "bit_exact_replay.py",
    "formal_bridge.py",
    "ledger_index.py",
    "differential_audit.py",
    "rag_settled/__init__.py",
    "schema_registry/__init__.py",
    "knowledge_coverage.py",
    "knowledge_facade.py",
    "promotion.py",
    "adversarial_suite.py",
    "gate_fuzzer.py",
    "engineers.py",
]


def build() -> Path:
    files = {}
    for rel in MODULES:
        p = ROOT / rel
        if p.exists():
            files[rel] = p.read_text(encoding="utf-8", errors="replace")

    # Also embed small data
    data = {}
    for rel in [
        "policies/calibration_thresholds.json",
        "schema_registry/events_v1.json",
        "schema_registry/packets_v1.json",
        "schema_registry/labels_v1.json",
        "rag_settled/corpus.jsonl",
        "artifacts/known_settled_export.json",
    ]:
        p = ROOT / rel
        if p.exists():
            data[rel] = p.read_text(encoding="utf-8", errors="replace")

    out = ROOT / "megacompact_monolith.py"
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "modules": files,
        "data": data,
    }
    # Write loader + JSON payload as a separate companion to avoid huge escape issues
    blob_path = ROOT / "megacompact_monolith_blob.json"
    blob_path.write_text(json.dumps(payload), encoding="utf-8")

    loader = f'''#!/usr/bin/env python3
# AUTO-GENERATED MONOLITH LOADER — canonical source remains multi-file package.
# Generated: {payload["generated"]}
# Loads embedded modules from megacompact_monolith_blob.json into one namespace.

from __future__ import annotations
import json
import sys
from pathlib import Path

BLOB = Path(__file__).resolve().parent / "megacompact_monolith_blob.json"

def load_namespace():
    data = json.loads(BLOB.read_text(encoding="utf-8"))
    ns = {{"__name__": "megacompact_monolith", "__file__": str(Path(__file__).resolve())}}
    # seed package-ish markers
    import types
    for pkg in ["rag_settled", "schema_registry"]:
        if pkg not in sys.modules:
            sys.modules[pkg] = types.ModuleType(pkg)
    # exec modules in order
    for name, src in data["modules"].items():
        code = compile(src, name, "exec")
        exec(code, ns)
        # register as modules for imports inside later files
        mod_name = name.replace("/", ".").replace(".py", "").replace(".__init__", "")
        if mod_name.endswith("."):
            mod_name = mod_name[:-1]
        m = types.ModuleType(mod_name)
        m.__dict__.update({{k: v for k, v in ns.items() if not k.startswith("__")}})
        sys.modules[mod_name] = m
        # short names
        short = Path(name).stem if not name.endswith("__init__.py") else Path(name).parent.name
        sys.modules[short] = m
    return ns, data

def main():
    import argparse
    ns, data = load_namespace()
    p = argparse.ArgumentParser(description="MegaCompact monolith CLI")
    p.add_argument("cmd", choices=["adversarial", "facade-stats", "smt-demo", "help"], nargs="?", default="help")
    args = p.parse_args()
    if args.cmd == "adversarial":
        print(ns["run_suite"]())
    elif args.cmd == "facade-stats":
        print(ns["get_facade"]().stats())
    elif args.cmd == "smt-demo":
        print(ns["pre_trade_gate"](2.0, 0.01, 0.95, 0.2))
        print(ns["pre_trade_gate"](0.1, 0.01, 0.95, 0.2))
    else:
        print("cmds: adversarial | facade-stats | smt-demo")
        print("modules_embedded:", len(data["modules"]), "data_files:", len(data["data"]))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''
    out.write_text(loader, encoding="utf-8")
    print("wrote", out, "bytes", out.stat().st_size)
    print("wrote", blob_path, "bytes", blob_path.stat().st_size)
    return out


if __name__ == "__main__":
    build()
