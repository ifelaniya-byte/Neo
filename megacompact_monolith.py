#!/usr/bin/env python3
# AUTO-GENERATED MONOLITH LOADER — canonical source remains multi-file package.
# Generated: 2026-08-19T21:44:01.090940+00:00
# Loads embedded modules from megacompact_monolith_blob.json into one namespace.

from __future__ import annotations
import json
import sys
from pathlib import Path

BLOB = Path(__file__).resolve().parent / "megacompact_monolith_blob.json"

def load_namespace():
    data = json.loads(BLOB.read_text(encoding="utf-8"))
    import types
    ns = {
        "__name__": "megacompact_monolith",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    sys.modules["megacompact_monolith"] = types.ModuleType("megacompact_monolith")
    sys.modules["megacompact_monolith"].__dict__.update(ns)
    for pkg in ["rag_settled", "schema_registry"]:
        if pkg not in sys.modules:
            sys.modules[pkg] = types.ModuleType(pkg)
    for name, src in data["modules"].items():
        mod_name = name.replace("/", ".").replace(".py", "")
        if mod_name.endswith(".__init__"):
            mod_name = mod_name[: -len(".__init__")]
        mod = types.ModuleType(mod_name)
        mod.__dict__.update({
            "__name__": mod_name,
            "__file__": name,
            "__package__": mod_name.rpartition(".")[0] or None,
        })
        mod.__dict__.update({k: v for k, v in ns.items() if not k.startswith("__")})
        sys.modules[mod_name] = mod
        short = Path(name).stem if not name.endswith("__init__.py") else Path(name).parent.name
        sys.modules[short] = mod
        # package root for rag_settled / schema_registry
        if "." not in mod_name:
            pass
        top = mod_name.split(".")[0]
        if top in ("rag_settled", "schema_registry"):
            sys.modules[top].__dict__.update({k: v for k, v in mod.__dict__.items() if not k.startswith("__")})
        code = compile(src, name, "exec")
        exec(code, mod.__dict__)
        for k, v in mod.__dict__.items():
            if not k.startswith("__"):
                ns[k] = v
        if top in ("rag_settled", "schema_registry"):
            sys.modules[top].__dict__.update({k: v for k, v in mod.__dict__.items() if not k.startswith("__")})
        sys.modules["megacompact_monolith"].__dict__.update(ns)
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
