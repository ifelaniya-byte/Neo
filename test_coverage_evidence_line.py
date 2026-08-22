#!/usr/bin/env python3
"""Line-for-line verification of coverage-as-evidence expansion (not world oracle)."""
from __future__ import annotations
import json
import sys
import traceback
from pathlib import Path

RESULTS = []

def check(name: str, cond: bool, detail: str = ""):
    RESULTS.append({"name": name, "ok": bool(cond), "detail": detail})
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))

def main():
    # L01 knowledge_coverage.evidence_for_decision exists and flags
    from knowledge_coverage import evidence_for_decision, best_effort_answer, coverage_report
    ev = evidence_for_decision({"regime": "normal", "chain_id": 42161})
    check("L01_evidence_role", ev.get("role") == "evidence_only")
    check("L02_not_authority", ev.get("not_authority") is True)
    check("L03_not_oracle", ev.get("not_a_complete_oracle") is True)
    check("L04_completeness_false", ev.get("completeness_claim_allowed") is False)
    check("L05_has_recommendation", bool(ev.get("recommendation")))

    # L06 coverage report completeness still false
    cov = coverage_report("causality abstain")
    check("L06_coverage_completeness_false", cov.get("completeness_claim_allowed") is False)
    check("L07_open_problems_tracked", (cov.get("n_open_problems") or 0) > 0)

    # L08 best_effort mode
    be = best_effort_answer("net pnl accounting")
    check("L08_best_effort_mode", be.get("mode") == "best_effort_coverage")
    check("L09_best_effort_not_oracle", be.get("not_a_complete_oracle") is True)

    # L10 RAG expanded
    from rag_settled import load_corpus, search
    corpus = load_corpus()
    ids = {d.get("doc_id") for d in corpus}
    check("L10_rag_size_ge_17", len(corpus) >= 17, f"n={len(corpus)}")
    check("L11_rag_evidence_digest", "digest-evidence-not-authority" in ids)
    check("L12_rag_smt_digest", "digest-smt-interval" in ids)
    hits = search("evidence authority abstain")
    check("L13_rag_search_hits", len(hits) >= 1)

    # L14 settled promotions
    from known_settled_db import get_settled_db
    db = get_settled_db()
    check("L14_settled_ge_26", len(db.entries) >= 26, f"n={len(db.entries)}")
    check("L15_settled_evidence_fact", "comp.evidence.not_authority" in db.entries)
    check("L16_settled_smt_fact", "comp.smt_interval.required_before_trade" in db.entries)

    # L17 claim gate still blocks completeness
    rej = db.reject_completeness_claim("complete conclusive world physics oracle")
    check("L17_completeness_blocked", rej.get("ok") is False)

    # L18 pipeline source contains evidence wire
    pipe = Path("pipeline.py").read_text()
    check("L18_pipeline_imports_evidence", "evidence_for_decision" in pipe)
    check("L19_pipeline_saves_evidence_json", "decision_knowledge_evidence.json" in pipe)
    check("L20_pipeline_not_override_gate", "does NOT change verdict" in pipe or "sole authority" in pipe)

    # L21 SMT/interval still wired in core
    core = Path("megacompact16/core.py").read_text()
    check("L21_core_smt_wired", "pre_trade_gate(" in core and "_SMT_TRADE_AVAILABLE = True" in core)
    check("L22_core_interval_wired", "trade_allowed_by_interval(" in core)

    # L23 signed ledger still works
    from signed_ledger import SignedLedger
    sl = SignedLedger("artifacts/line_test_signed.jsonl")
    e = sl.append("line_test", {"n": 1})
    ver = sl.verify_file()
    check("L23_signed_append", bool(e.entry_id))
    check("L24_signed_verify", ver.get("ok") is True)

    # L25 independent audit still ok
    from independent_audit import run_independent_audit
    audit = run_independent_audit("artifacts/run_line_test_audit")
    check("L25_independent_audit_ok", audit.get("ok") is True, str(audit.get("failed")))

    # L26 adversarial 5/5
    from adversarial_suite import run_suite
    adv = run_suite()
    check("L26_adversarial_5_5", adv.get("all_ok") is True, f"{adv.get('n_suite_pass')}/{adv.get('n_cases')}")

    # L27 historical adapter
    from adapters.historical import HistoricalAdapter, write_sample_jsonl
    p = write_sample_jsonl("artifacts/line_hist.jsonl", n=3)
    evs = HistoricalAdapter().from_jsonl(p)
    check("L27_historical_events", len(evs) == 3)
    check("L28_historical_causality", all(e.available_timestamp_ms >= e.event_timestamp_ms for e in evs))

    # L29 bit-exact self proof
    from bit_exact_replay import self_proof
    demo = Path("artifacts/run_line_proof")
    (demo / "reports").mkdir(parents=True, exist_ok=True)
    (demo / "reports" / "run_summary.json").write_text(json.dumps({"line": True}))
    proof = self_proof(str(demo))
    check("L29_bit_exact", proof.get("ok") is True, proof.get("proof"))

    # L30 overclaim still blocked by engineers
    from engineers import DoublePassEngineerGate
    gate = DoublePassEngineerGate(ledger_path="artifacts/line_test_engineer.jsonl")
    r = gate.run(
        {"claim": "complete conclusive world physics catalogue as oracle stage"},
        subject_type="claim",
        subject_id="line_overclaim",
    )
    check("L30_overclaim_blocked", r.to_dict().get("final_verdict") == "BLOCKED")

    # L31 product claim safe language passes
    r2 = gate.run(
        {"claim": "Paper-only simulation assurance under double-pass engineers. No live trading."},
        subject_type="claim",
        subject_id="line_product_claim",
    )
    check("L31_product_claim_pass", r2.to_dict().get("final_verdict") == "PASS")

    # L32 modules pass engineer as source
    for mod in ["knowledge_coverage.py", "pipeline.py", "promotion.py"]:
        rr = gate.run(Path(mod).read_text(), subject_type="source", subject_id=mod)
        check(f"L32_source_{mod}", rr.to_dict().get("final_verdict") == "PASS")

    # summary
    n_ok = sum(1 for r in RESULTS if r["ok"])
    n = len(RESULTS)
    summary = {"n": n, "n_ok": n_ok, "n_fail": n - n_ok, "all_ok": n_ok == n, "results": RESULTS}
    Path("artifacts/line_test_results.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== SUMMARY {n_ok}/{n} all_ok={summary['all_ok']} ===")
    if not summary["all_ok"]:
        for r in RESULTS:
            if not r["ok"]:
                print(" FAIL:", r["name"], r["detail"])
        sys.exit(1)
    return 0

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
