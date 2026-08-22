#!/usr/bin/env python3
"""Thin CLI over canonical multi-file package (hybrid alternative entrypoint)."""
from __future__ import annotations
import argparse
import json


def main():
    p = argparse.ArgumentParser(description="MegaCompact thin CLI")
    p.add_argument("cmd", choices=["adversarial", "facade-stats", "smt-demo", "coverage", "plan-status"])
    args = p.parse_args()
    if args.cmd == "adversarial":
        from adversarial_suite import run_suite
        print(json.dumps(run_suite(), indent=2))
    elif args.cmd == "facade-stats":
        from knowledge_facade import get_facade
        print(json.dumps(get_facade().stats(), indent=2))
    elif args.cmd == "smt-demo":
        from smt_gate import pre_trade_gate
        print(json.dumps({"allow": pre_trade_gate(2.0, 0.01, 0.95, 0.2), "block": pre_trade_gate(0.1, 0.01, 0.95, 0.2)}, indent=2))
    elif args.cmd == "coverage":
        from knowledge_coverage import coverage_report
        print(json.dumps(coverage_report("causality"), indent=2, default=str)[:3000])
    else:
        print(json.dumps({"canonical": "multi-file package", "monolith": "megacompact_monolith.py", "double_pass": "mandatory"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
