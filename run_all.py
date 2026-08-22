#!/usr/bin/env python3
"""Run full pipeline + engineer double-pass on data and source code."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "megacompact16"))
import core as mc
from engineers import DoublePassEngineerGate
import pandas as pd
import numpy as np


def safe_save(store, df, filename):
    df = df.copy()
    for c in df.columns:
        if getattr(df[c], "dtype", None) is not None and str(df[c].dtype) == "object":
            df[c] = df[c].apply(
                lambda x: x if isinstance(x, (str, int, float, bool, type(None))) else str(x)
            )
    path = store.path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        df.to_parquet(f, index=False, engine="pyarrow")


def main():
    cfg = mc.Config(seed=42)
    # Scaled synthetic config
    cfg.synthetic = mc.SyntheticConfig(
        days=5,
        blocks_per_day=120,
        num_tokens=6,
        num_pools=10,
        num_venues=4,
        seed=42,
    )
    store = mc.ArtifactStore("artifacts", run_id="run_scaled")
    gate = DoublePassEngineerGate(ledger_path=str(store.path("audits/verification_ledger.jsonl")))

    print("1. SYNTH (scaled: 5d x 120 blocks)")
    events = mc.SyntheticMarketGenerator(cfg.synthetic).generate()
    safe_save(store, pd.DataFrame([e.model_dump() for e in events]), "data/normalized/events.parquet")
    print("   events=", len(events))

    print("2. ENGINEER EVENTS")
    eng_n = min(40, len(events))
    s_ev = gate.run_batch(
        [(e.model_dump(), e.event_id, "NormalizedEvent") for e in events[:eng_n]]
    )
    print("   allowed=", s_ev["n_allowed_for_llm"], "/", s_ev["n_total"])

    print("3. VALIDATE")
    valid = mc.DataValidator(cfg).validate_events(events)
    print("   valid=", len(valid))

    print("4. BUILD PACKETS")
    fs = mc.TimeCausalFeatureStore(valid, cfg.max_feature_age_ms)
    packets = mc.DecisionPacketBuilder(cfg, fs).build_packets(valid)
    safe_save(store, pd.DataFrame([p.model_dump() for p in packets]), "data/packets/packets.parquet")
    print("   packets=", len(packets))

    print("5. ENGINEER PACKETS")
    s_pk = gate.run_batch(
        [(p.model_dump(), p.decision_id, "DecisionPacket") for p in packets[:min(40, len(packets))]]
    )
    print("   allowed=", s_pk["n_allowed_for_llm"], "/", s_pk["n_total"])

    print("6. LABEL")
    lb = mc.LabelBuilder(
        mc.MarketReplay(valid),
        mc.QuoteEngine(mc.ConstantProductAMM()),
        mc.ExecutionEngine(cfg),
        mc.CostEngine(),
        mc.OutcomeEngine(),
    )
    labels = lb.build_labels(packets, np.random.default_rng(42))
    safe_save(store, pd.DataFrame([l.model_dump() for l in labels]), "data/labels/labels.parquet")
    print("   labels=", len(labels))

    print("7. ENGINEER LABELS")
    s_lb = gate.run_batch(
        [(l.model_dump(), l.decision_id, "OutcomeLabel") for l in labels[:min(40, len(labels))]]
    )
    print("   allowed=", s_lb["n_allowed_for_llm"], "/", s_lb["n_total"])

    print("8. SPLIT")
    splitter = mc.WalkForwardSplitter(cfg)
    ps = splitter.split_packets(packets)
    ls = splitter.split_labels(labels)
    for name, items in ps.items():
        safe_save(
            store,
            pd.DataFrame([p.model_dump() for p in items]),
            f"data/splits/{name}_packets.parquet",
        )
    for name, items in ls.items():
        safe_save(
            store,
            pd.DataFrame([l.model_dump() for l in items]),
            f"data/splits/{name}_labels.parquet",
        )
    print("   splits=", {k: len(v) for k, v in ps.items()})

    print("9. FIT BASELINE")
    baseline = mc.EmpiricalBaselinePredictor(n_buckets=3)
    if ps["train"] and ls["train"]:
        baseline.fit(ps["train"], ls["train"])
        print("   fitted on", len(ls["train"]))
    else:
        print("   skipped (empty train)")

    print("10. PLAN AND DECIDE")
    abs_gate = mc.AbstentionGate(cfg)
    decisions = []
    for packet in (ps.get("test") or packets)[:5]:
        forecasts = []
        for action in packet.action_candidates:
            try:
                forecasts.append((action, baseline.predict(packet, action)))
            except Exception:
                pass
        if forecasts:
            decisions.append(abs_gate.decide(packet, forecasts))
    print("   decisions=", len(decisions))

    print("11. ENGINEER DECISIONS")
    s_dec = {"n_allowed_for_llm": 0, "n_total": 0}
    if decisions:
        s_dec = gate.run_batch(
            [(d.model_dump(), d.decision_id, "DecisionOutput") for d in decisions]
        )
    print("   allowed=", s_dec["n_allowed_for_llm"], "/", s_dec.get("n_total", 0))

    print("12. AUDIT")
    audit_results = mc.AuditEngine(store).run_all_audits(packets, labels, cfg)
    store.save_json(audit_results, "audits/audit_results.json")
    passed = sum(1 for r in audit_results.values() if r.get("passed", False))
    print("   passed=", passed, "/", len(audit_results))

    print("13. REPORT")
    mc.ReportGenerator(store).generate_all_reports({}, {}, audit_results, cfg)
    print("   ok")

    print("14. SOURCE CODE THROUGH ENGINEERS")
    for path in ["engineers.py", "pipeline.py", "megacompact16/core.py"]:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        r = gate.run(
            {"path": path, "n_chars": len(text), "n_lines": text.count("\n") + 1},
            path,
            "source_code",
            context={"source_text": text[:80000]},
        )
        print("  ", path, "->", r.final_verdict.value, "allowed_for_llm=", r.allowed_for_llm)

    summary = {
        "run_dir": str(store.run_dir),
        "n_events": len(events),
        "n_packets": len(packets),
        "n_labels": len(labels),
        "n_decisions": len(decisions),
        "engineer": {
            "events": f"{s_ev['n_allowed_for_llm']}/{s_ev['n_total']}",
            "packets": f"{s_pk['n_allowed_for_llm']}/{s_pk['n_total']}",
            "labels": f"{s_lb['n_allowed_for_llm']}/{s_lb['n_total']}",
            "decisions": f"{s_dec['n_allowed_for_llm']}/{s_dec.get('n_total', 0)}",
        },
        "audits_passed": f"{passed}/{len(audit_results)}",
    }
    store.save_json(summary, "reports/run_summary.json")
    print("\n=== FINAL SUMMARY ===")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
