#!/usr/bin/env python3
"""CLI for local artifact + mechanical verifier tool-set (Simulation Assurance product)."""
from __future__ import annotations
import argparse
import json
from tools import artifacts, verifiers


def main(argv=None):
    p = argparse.ArgumentParser(description="MegaCompact Simulation Assurance: artifacts + mechanical verifiers")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-runs")
    pr = sub.add_parser("run-summary")
    pr.add_argument("run_dir")
    pm = sub.add_parser("merkle")
    pm.add_argument("run_dir")
    pm.add_argument("--write", action="store_true")
    pc = sub.add_parser("compare")
    pc.add_argument("run_a")
    pc.add_argument("run_b")
    sub.add_parser("ledgers")
    pq = sub.add_parser("ledger-search")
    pq.add_argument("query")
    sub.add_parser("battery")
    sub.add_parser("adversarial")
    sub.add_parser("knowledge")
    ps = sub.add_parser("smt")
    ps.add_argument("--edge", type=float, default=2.0)
    ps.add_argument("--revert", type=float, default=0.01)
    ps.add_argument("--inclusion", type=float, default=0.95)
    ps.add_argument("--ood", type=float, default=0.2)
    pd = sub.add_parser("double-pass")
    pd.add_argument("--json", default='{"ping": true}')
    # Product features
    sub.add_parser("independent-audit")
    sub.add_parser("formal-subset")
    prp = sub.add_parser("replay-proof")
    prp.add_argument("run_dir")
    sub.add_parser("verify-promotion-ledger")
    sub.add_parser("product-report")

    args = p.parse_args(argv)
    out = None
    if args.cmd == "list-runs":
        out = artifacts.list_runs()
    elif args.cmd == "run-summary":
        out = artifacts.run_summary(args.run_dir)
    elif args.cmd == "merkle":
        out = artifacts.merkle(args.run_dir, write=getattr(args, "write", False))
    elif args.cmd == "compare":
        out = artifacts.compare_runs(args.run_a, args.run_b)
    elif args.cmd == "ledgers":
        out = artifacts.ledgers()
    elif args.cmd == "ledger-search":
        out = artifacts.ledger_search(args.query)
    elif args.cmd == "battery":
        out = verifiers.full_mechanical_battery()
    elif args.cmd == "adversarial":
        out = verifiers.adversarial()
    elif args.cmd == "knowledge":
        out = verifiers.knowledge_stats()
    elif args.cmd == "smt":
        out = verifiers.smt_trade(args.edge, args.revert, args.inclusion, args.ood)
    elif args.cmd == "double-pass":
        subject = json.loads(args.json)
        out = verifiers.double_pass(subject)
    elif args.cmd == "independent-audit":
        from independent_audit import run_independent_audit
        out = run_independent_audit()
    elif args.cmd == "formal-subset":
        from formal_subset import export_formal_subset
        out = export_formal_subset()
    elif args.cmd == "replay-proof":
        from bit_exact_replay import write_replay_proof
        out = write_replay_proof(args.run_dir)
    elif args.cmd == "verify-promotion-ledger":
        from promotion import PromotionService
        out = PromotionService().verify_promotion_ledger()
    elif args.cmd == "product-report":
        from independent_audit import run_independent_audit
        from formal_subset import export_formal_subset
        from tools.verifiers import knowledge_stats, adversarial
        out = {
            "product": "MegaCompact Simulation Assurance",
            "positioning": "paper-only simulation assurance for labs — not live trading",
            "knowledge": knowledge_stats(),
            "adversarial": adversarial(),
            "formal": export_formal_subset(),
            "independent_audit": run_independent_audit(),
        }
    else:
        p.error(f"unknown cmd {args.cmd}")

    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
