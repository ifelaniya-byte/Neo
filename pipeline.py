#!/usr/bin/env python3
"""
MegaCompact16 + UAIR Unified Pipeline
=====================================

A single, LLM-callable research & decision pipeline that combines:

- MegaCompact16 (time-causal DeFi research / paper-replay / audit harness)
- UAIR (adaptive routing, uncertainty, safety, cost-aware execution)

Design goals
------------
1. Explicit staged pipeline an LLM or agent can drive step-by-step or end-to-end.
2. Paper/replay only – no wallet, signing, or live transaction submission.
3. ABSTAIN by default; every constraint and time-causality check is enforced.
4. Full provenance, net-PnL accounting, and auditability.
5. EmpiricalBaselinePredictor is wired so ConservativePlanner / AbstentionGate
   actually have real forecasts to evaluate (the critical missing piece in earlier versions).

Pipeline stages (LLM-callable)
------------------------------
  1. synth / ingest      → generate or load events
  2. validate            → time-causality & schema checks
  3. build_packets       → DecisionPackets with feature availability times
  4. label               → OutcomeLabels via market replay + cost engine
  5. split               → walk-forward train/val/cal/test
  6. fit_baseline        → EmpiricalBaselinePredictor (no PyTorch required)
  7. plan_and_decide     → ConservativePlanner + AbstentionGate
  8. paper_replay        → deterministic paper outcomes
  9. audit               → leakage, split integrity, net-PnL accounting
 10. report              → dataset card, assumptions, final summary

Usage (CLI)
-----------
  python pipeline.py all --mode synth --seed 42
  python pipeline.py stage fit_baseline --run-dir artifacts/run_XXXX

Usage (from an LLM / agent)
---------------------------
  from pipeline import MegaPipeline
  pipe = MegaPipeline(seed=42)
  pipe.run_stage("synth")
  pipe.run_stage("build_packets")
  ...
  # or
  result = pipe.run_all()
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import typer
from rich.console import Console
from rich.table import Table

# ---------------------------------------------------------------------------
# Import the MegaCompact16 core (the latest fixed version)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent / "megacompact16"))
import core as mc  # type: ignore

# Robust parquet writer – some environments silently write 0-byte files when
# DataFrames contain nested dict / None object columns. Coerce those columns
# to strings so pyarrow always produces a valid file.
def _safe_save_parquet(self, df, filename):
    # Coerce nested/object columns and always write via binary file handle
    # (pathlib.Path + to_parquet can produce 0-byte files in this environment).
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].apply(
                lambda x: x if isinstance(x, (str, int, float, bool, type(None))) else str(x)
            )
    path = self.path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        df.to_parquet(f, index=False, engine="pyarrow")

mc.ArtifactStore.save_parquet = _safe_save_parquet

# Optional UAIR layers (for general request routing if desired)
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from uair.orchestrator import UAIRRuntime
    from uair.contracts import Request, Sensitivity
    UAIR_AVAILABLE = True
except Exception:
    UAIR_AVAILABLE = False

console = Console()
logger = logging.getLogger("MegaPipeline")
logging.basicConfig(level=logging.INFO)

VERSION = "1.2.0-double-engineer"

# Mandatory stationary / non-stationary engineers
from engineers import (
    DoublePassEngineerGate,
    EngineerVerdict,
    DoublePassResult,
)


# =============================================================================
# PIPELINE FACADE – the piece an LLM actually talks to
# =============================================================================

class MegaPipeline:
    """
    Explicit staged pipeline. Every public method is a stage that can be
    invoked independently by an LLM / agent or by the CLI.

    MANDATORY SAFETY SPINE
    ----------------------
    All information produced by data stages is fed through the double-pass
    engineer gate BEFORE it may be handed to an LLM interpreter:

        StationaryEngineer (pass 1)
     →  NonStationaryEngineer
     →  StationaryEngineer (pass 2 – secondary verification)

    Only subjects that receive final_verdict=PASS and allowed_for_llm=True
    may proceed to LLM interpretation. Everything else is BLOCKED or ABSTAIN.

    State is persisted under self.artifact_store.run_dir so stages can be
    resumed or inspected later.
    """

    # All stages are mandatory. Engineer double-passes are first-class stages.
    STAGES = [
        "synth",
        "engineer_events",          # double-pass over generated events
        "validate",
        "build_packets",
        "engineer_packets",         # double-pass over decision packets
        "label",
        "engineer_labels",          # double-pass over outcome labels
        "split",
        "fit_baseline",
        "plan_and_decide",
        "engineer_decisions",       # double-pass over decisions before LLM
        "paper_replay",
        "adversarial_ci",
        "knowledge_report",
        "audit",
        "report",
    ]

    def __init__(
        self,
        mode: str = "synth",
        seed: int = 42,
        output_root: str = "artifacts",
        run_id: Optional[str] = None,
        config: Optional[mc.Config] = None,
    ):
        self.mode = mode
        self.seed = seed
        mc.set_seed(seed)

        if config is None:
            # Sensible defaults – no YAML file required for a smoke run
            self.config = mc.Config(
                mode=mode,
                seed=seed,
                synthetic=mc.SyntheticConfig(
                    days=3,          # keep smoke runs fast
                    blocks_per_day=200,
                    num_tokens=6,
                    num_pools=8,
                    seed=seed,
                ),
                output=mc.OutputConfig(root=output_root, run_id=run_id),
            )
        else:
            self.config = config
            self.config.seed = seed

        self.artifact_store = mc.ArtifactStore(
            self.config.output.root,
            run_id=run_id or self.config.output.run_id,
        )
        self.manifest = mc.RunManifest(self.config, self.artifact_store)

        # Persist resolved config
        self.config.to_yaml(str(self.artifact_store.path("config.resolved.yaml")))

        # Runtime state (populated by stages)
        self.events: List[mc.NormalizedEvent] = []
        self.packets: List[mc.DecisionPacket] = []
        self.labels: List[mc.OutcomeLabel] = []
        self.baseline: Optional[mc.EmpiricalBaselinePredictor] = None
        self.decisions: List[mc.DecisionOutput] = []
        self.audit_results: Dict[str, Any] = {}

        # Mandatory double-pass engineer gate
        ledger_path = self.artifact_store.path("audits/verification_ledger.jsonl")
        self.engineer_gate = DoublePassEngineerGate(ledger_path=ledger_path)
        self.engineer_results: Dict[str, Any] = {}

        # Subjects cleared for LLM interpretation (only PASS + allowed_for_llm)
        self.llm_cleared_events: List[Any] = []
        self.llm_cleared_packets: List[Any] = []
        self.llm_cleared_labels: List[Any] = []
        self.llm_cleared_decisions: List[Any] = []

        console.print(f"[bold green]MegaPipeline v{VERSION}[/bold green]")
        console.print(f"Run ID : {self.artifact_store.run_id}")
        console.print(f"Root   : {self.artifact_store.run_dir}")
        console.print("[bold yellow]Mandatory spine: Stationary → NonStationary → Stationary (×2) before LLM[/bold yellow]")

    # ------------------------------------------------------------------
    # Stage helpers
    # ------------------------------------------------------------------

    def _load_events(self) -> List[mc.NormalizedEvent]:
        path = self.artifact_store.path("data/normalized/events.parquet")
        if not path.exists():
            raise FileNotFoundError("No events.parquet – run 'synth' or 'ingest' first")
        df = self.artifact_store.load_parquet("data/normalized/events.parquet")
        return [mc.NormalizedEvent(**row) for _, row in df.iterrows()]

    def _load_packets(self) -> List[mc.DecisionPacket]:
        path = self.artifact_store.path("data/packets/packets.parquet")
        if not path.exists():
            raise FileNotFoundError("No packets.parquet – run 'build_packets' first")
        df = self.artifact_store.load_parquet("data/packets/packets.parquet")
        return [mc.DecisionPacket(**row) for _, row in df.iterrows()]

    def _load_labels(self) -> List[mc.OutcomeLabel]:
        path = self.artifact_store.path("data/labels/labels.parquet")
        if not path.exists():
            raise FileNotFoundError("No labels.parquet – run 'label' first")
        df = self.artifact_store.load_parquet("data/labels/labels.parquet")
        return [mc.OutcomeLabel(**row) for _, row in df.iterrows()]

    # ------------------------------------------------------------------
    # Individual stages
    # ------------------------------------------------------------------

    def stage_synth(self) -> Dict[str, Any]:
        """Stage 1 – Generate synthetic market events."""
        console.print("[bold blue]Stage: synth[/bold blue]")
        generator = mc.SyntheticMarketGenerator(self.config.synthetic)
        self.events = generator.generate()
        df = __import__("pandas").DataFrame([e.model_dump() for e in self.events])
        self.artifact_store.save_parquet(df, "data/normalized/events.parquet")
        self.manifest.update_stage("synth")
        console.print(f"[green]Generated {len(self.events)} events[/green]")
        return {"n_events": len(self.events)}

    def stage_validate(self) -> Dict[str, Any]:
        """Stage 2 – Validate events for time-causality and schema."""
        console.print("[bold blue]Stage: validate[/bold blue]")
        if not self.events:
            self.events = self._load_events()
        validator = mc.DataValidator(self.config)
        valid = validator.validate_events(self.events)
        self.events = valid
        self.manifest.update_stage("validate")
        console.print(f"[green]Validated {len(valid)} events[/green]")
        return {"n_valid": len(valid)}

    def stage_build_packets(self) -> Dict[str, Any]:
        """Stage 3 – Build DecisionPackets with causal feature store."""
        console.print("[bold blue]Stage: build_packets[/bold blue]")
        if not self.events:
            self.events = self._load_events()
        feature_store = mc.TimeCausalFeatureStore(self.events, self.config.max_feature_age_ms)
        builder = mc.DecisionPacketBuilder(self.config, feature_store)
        self.packets = builder.build_packets(self.events)
        df = __import__("pandas").DataFrame([p.model_dump() for p in self.packets])
        self.artifact_store.save_parquet(df, "data/packets/packets.parquet")
        self.manifest.update_stage("build_packets")
        console.print(f"[green]Built {len(self.packets)} packets[/green]")
        return {"n_packets": len(self.packets)}

    def stage_label(self) -> Dict[str, Any]:
        """Stage 4 – Simulate outcomes and produce OutcomeLabels."""
        console.print("[bold blue]Stage: label[/bold blue]")
        if not self.packets:
            self.packets = self._load_packets()
        if not self.events:
            self.events = self._load_events()

        market_replay = mc.MarketReplay(self.events)
        amm = mc.ConstantProductAMM()
        quote_engine = mc.QuoteEngine(amm)
        execution_engine = mc.ExecutionEngine(self.config)
        cost_engine = mc.CostEngine()
        outcome_engine = mc.OutcomeEngine()
        label_builder = mc.LabelBuilder(
            market_replay, quote_engine, execution_engine, cost_engine, outcome_engine
        )
        rng = np.random.default_rng(self.seed)
        self.labels = label_builder.build_labels(self.packets, rng)
        df = __import__("pandas").DataFrame([l.model_dump() for l in self.labels])
        self.artifact_store.save_parquet(df, "data/labels/labels.parquet")
        self.manifest.update_stage("label")
        console.print(f"[green]Built {len(self.labels)} labels[/green]")
        return {"n_labels": len(self.labels)}

    def stage_split(self) -> Dict[str, Any]:
        """Stage 5 – Walk-forward time splits (no random shuffle)."""
        console.print("[bold blue]Stage: split[/bold blue]")
        if not self.packets:
            self.packets = self._load_packets()
        if not self.labels:
            self.labels = self._load_labels()

        splitter = mc.WalkForwardSplitter(self.config)
        packet_splits = splitter.split_packets(self.packets)
        label_splits = splitter.split_labels(self.labels)

        for name, items in packet_splits.items():
            df = __import__("pandas").DataFrame([p.model_dump() for p in items])
            self.artifact_store.save_parquet(df, f"data/splits/{name}_packets.parquet")
        for name, items in label_splits.items():
            df = __import__("pandas").DataFrame([l.model_dump() for l in items])
            self.artifact_store.save_parquet(df, f"data/splits/{name}_labels.parquet")

        self.manifest.update_stage("split")
        console.print("[green]Created walk-forward splits[/green]")
        return {k: len(v) for k, v in packet_splits.items()}

    def stage_fit_baseline(self) -> Dict[str, Any]:
        """Stage 6 – Fit EmpiricalBaselinePredictor on train split.

        This is the critical missing piece that was added in the fixed version:
        without a real predictor, AbstentionGate and ConservativePlanner had
        nothing honest to evaluate.
        """
        console.print("[bold blue]Stage: fit_baseline[/bold blue]")
        train_packets_df = self.artifact_store.load_parquet("data/splits/train_packets.parquet")
        train_labels_df = self.artifact_store.load_parquet("data/splits/train_labels.parquet")
        train_packets = [mc.DecisionPacket(**row) for _, row in train_packets_df.iterrows()]
        train_labels = [mc.OutcomeLabel(**row) for _, row in train_labels_df.iterrows()]

        self.baseline = mc.EmpiricalBaselinePredictor(n_buckets=5)
        self.baseline.fit(train_packets, train_labels)

        # Persist a simple JSON snapshot of the fitted stats
        snapshot = {
            "n_buckets": self.baseline.n_buckets,
            "min_observed": getattr(self.baseline, "min_observed", None),
            "max_observed": getattr(self.baseline, "max_observed", None),
            "global_stats": self.baseline.global_stats,
            "bucket_stats": self.baseline.bucket_stats,
        }
        self.artifact_store.save_json(snapshot, "models/empirical_baseline.json")
        self.manifest.update_stage("fit_baseline")
        console.print(f"[green]Fitted EmpiricalBaselinePredictor on {len(train_labels)} train labels[/green]")
        return {"n_train": len(train_labels), "n_buckets": self.baseline.n_buckets}

    def stage_plan_and_decide(self) -> Dict[str, Any]:
        """Stage 7 – Run ConservativePlanner + AbstentionGate on test packets."""
        console.print("[bold blue]Stage: plan_and_decide[/bold blue]")
        if self.baseline is None:
            # try to reload
            train_packets_df = self.artifact_store.load_parquet("data/splits/train_packets.parquet")
            train_labels_df = self.artifact_store.load_parquet("data/splits/train_labels.parquet")
            train_packets = [mc.DecisionPacket(**row) for _, row in train_packets_df.iterrows()]
            train_labels = [mc.OutcomeLabel(**row) for _, row in train_labels_df.iterrows()]
            self.baseline = mc.EmpiricalBaselinePredictor(n_buckets=5)
            self.baseline.fit(train_packets, train_labels)

        test_packets_df = self.artifact_store.load_parquet("data/splits/test_packets.parquet")
        test_packets = [mc.DecisionPacket(**row) for _, row in test_packets_df.iterrows()]

        gate = mc.AbstentionGate(self.config)
        decisions = []
        evidence_log = []
        try:
            from knowledge_coverage import evidence_for_decision
            _ev_fn = evidence_for_decision
        except Exception:
            _ev_fn = None  # type: ignore

        for packet in test_packets:
            # Produce a forecast for every action candidate
            forecasts = []
            for action in packet.action_candidates:
                fc = self.baseline.predict(packet, action)
                forecasts.append((action, fc))

            decision = gate.decide(packet, forecasts)
            # Evidence attach only — does NOT change verdict (gate is sole authority)
            if _ev_fn is not None:
                try:
                    summary = {
                        "regime": getattr(packet, "regime", None),
                        "chain_id": getattr(packet, "chain_id", None),
                    }
                    ev = _ev_fn(packet_summary=summary)
                    evidence_log.append({
                        "decision_id": getattr(decision, "decision_id", None),
                        "verdict": str(getattr(decision, "verdict", None)),
                        "evidence": ev,
                    })
                    # attach to decision metadata if model allows extra fields
                    meta = getattr(decision, "metadata", None)
                    if meta is None and hasattr(decision, "__dict__"):
                        try:
                            decision.metadata = {"knowledge_evidence": ev}  # type: ignore
                        except Exception:
                            pass
                    elif isinstance(meta, dict):
                        meta["knowledge_evidence"] = ev
                except Exception as _e:
                    evidence_log.append({"error": str(_e)})
            decisions.append(decision)

        self.decisions = decisions
        self.artifact_store.save_jsonl(
            [d.model_dump() if hasattr(d, "model_dump") else d for d in decisions],
            "paper/decisions.jsonl",
        )
        if evidence_log:
            self.artifact_store.save_json(
                {
                    "role": "evidence_only",
                    "not_a_complete_oracle": True,
                    "n": len(evidence_log),
                    "entries": evidence_log[:50],
                },
                "paper/decision_knowledge_evidence.json",
            )
        self.manifest.update_stage("plan_and_decide")

        n_trade = sum(1 for d in decisions if d.verdict == mc.Verdict.TRADE)
        n_abstain = len(decisions) - n_trade
        console.print(f"[green]Decisions: {n_trade} TRADE / {n_abstain} ABSTAIN[/green]")
        return {"n_trade": n_trade, "n_abstain": n_abstain}

    def stage_paper_replay(self) -> Dict[str, Any]:
        """Stage 8 – Placeholder for full paper-replay (labels already contain outcomes)."""
        console.print("[bold blue]Stage: paper_replay[/bold blue]")
        # In this unified version the labels already contain the simulated paper outcomes.
        # A fuller replay would re-execute only the TRADE decisions against the market replay.
        self.manifest.update_stage("paper_replay")
        console.print("[green]Paper outcomes already present in labels[/green]")
        return {"status": "labels_contain_outcomes"}

    def stage_audit(self) -> Dict[str, Any]:
        """Stage 9 – Run all leakage / accounting / split-integrity audits."""
        console.print("[bold blue]Stage: audit[/bold blue]")
        if not self.packets:
            self.packets = self._load_packets()
        if not self.labels:
            self.labels = self._load_labels()

        audit_engine = mc.AuditEngine(self.artifact_store)
        self.audit_results = audit_engine.run_all_audits(self.packets, self.labels, self.config)
        self.artifact_store.save_json(self.audit_results, "audits/audit_results.json")
        self.manifest.update_audit_result("all_audits", self.audit_results)
        self.manifest.update_stage("audit")

        passed = sum(1 for r in self.audit_results.values() if r.get("passed", False))
        total = len(self.audit_results)
        console.print(f"[green]Audits: {passed}/{total} passed[/green]")
        return {"passed": passed, "total": total, "details": self.audit_results}



    def stage_knowledge_report(self) -> Dict[str, Any]:
        """Emit knowledge coverage facade stats (not a complete oracle)."""
        console.print("[bold blue]Stage: knowledge_report[/bold blue]")
        try:
            from knowledge_facade import get_facade
            fac = get_facade()
            stats = fac.stats()
            cov = fac.coverage("causality accounting abstain")
            out = {"stats": stats, "coverage_excerpt": {"n_open": cov.get("n_open_problems"), "disclaimer": cov.get("disclaimer")}}
        except Exception as e:
            out = {"error": str(e)}
        self.artifact_store.save_json(out, "reports/knowledge_report.json")
        self.manifest.update_stage("knowledge_report")
        return out

    def stage_adversarial_ci(self) -> Dict[str, Any]:
        """Mandatory adversarial suite — engineers must catch planted failures."""
        console.print("[bold blue]Stage: adversarial_ci[/bold blue]")
        from adversarial_suite import run_suite
        result = run_suite(ledger_path=str(self.artifact_store.path("audits/adversarial_ledger.jsonl")))
        self.artifact_store.save_json(result, "audits/adversarial_results.json")
        self.manifest.update_stage("adversarial_ci")
        if not result.get("all_ok"):
            console.print(f"[red]Adversarial suite FAILED: {result.get('n_suite_fail')} cases[/red]")
        else:
            console.print(f"[green]Adversarial suite OK: {result.get('n_suite_pass')}/{result.get('n_cases')}[/green]")
        return result

    def stage_report(self) -> Dict[str, Any]:
        """Generate dataset card, assumptions, and final summary."""
        console.print("[bold blue]Stage: report[/bold blue]")
        reporter = mc.ReportGenerator(self.artifact_store)
        reporter.generate_all_reports(
            backtest_results={},
            stress_results={},
            audit_results=self.audit_results or {},
            config=self.config,
        )
        self.manifest.update_stage("report")
        console.print("[green]Reports written under reports/[/green]")
        return {"status": "ok"}

    # ------------------------------------------------------------------
    # MANDATORY ENGINEER DOUBLE-PASS STAGES
    # Stationary → NonStationary → Stationary (secondary verification)
    # before any information is cleared for LLM interpretation.
    # ------------------------------------------------------------------

    def _run_double_pass_batch(
        self,
        items: List[Any],
        id_fn,
        subject_type: str,
        cleared_attr: str,
        max_items: int = 50,
    ) -> Dict[str, Any]:
        """
        Feed a batch through Stationary → NonStationary → Stationary.
        Only PASS + allowed_for_llm subjects are appended to the cleared list.
        Caps at max_items for smoke-run speed; full runs can raise the cap.
        """
        batch = items[:max_items]
        triples = []
        for obj in batch:
            sid = id_fn(obj)
            triples.append((obj, sid, subject_type))

        summary = self.engineer_gate.run_batch(triples)
        cleared = []
        for r_dict, obj in zip(summary["results"], batch):
            if r_dict.get("allowed_for_llm"):
                cleared.append(obj)

        setattr(self, cleared_attr, cleared)
        self.engineer_results[subject_type] = summary

        # Persist engineer results
        self.artifact_store.save_json(
            summary,
            f"audits/engineer_{subject_type.lower()}.json",
        )
        return {
            "n_total": summary["n_total"],
            "n_allowed_for_llm": summary["n_allowed_for_llm"],
            "n_blocked": summary["n_blocked"],
            "subject_type": subject_type,
        }

    def stage_engineer_events(self) -> Dict[str, Any]:
        """Mandatory double-pass over events before downstream use."""
        console.print("[bold blue]Stage: engineer_events (Stationary→NonStationary→Stationary)[/bold blue]")
        if not self.events:
            self.events = self._load_events()

        def _eid(e):
            return getattr(e, "event_id", None) or (e.get("event_id") if isinstance(e, dict) else str(id(e)))

        result = self._run_double_pass_batch(
            self.events, _eid, "NormalizedEvent", "llm_cleared_events", max_items=40
        )
        self.manifest.update_stage("engineer_events")
        console.print(
            f"[green]Events engineer: {result['n_allowed_for_llm']}/{result['n_total']} "
            f"cleared for LLM[/green]"
        )
        return result

    def stage_engineer_packets(self) -> Dict[str, Any]:
        """Mandatory double-pass over decision packets before labelling / planning."""
        console.print("[bold blue]Stage: engineer_packets (Stationary→NonStationary→Stationary)[/bold blue]")
        if not self.packets:
            self.packets = self._load_packets()

        def _pid(p):
            return getattr(p, "decision_id", None) or (p.get("decision_id") if isinstance(p, dict) else str(id(p)))

        result = self._run_double_pass_batch(
            self.packets, _pid, "DecisionPacket", "llm_cleared_packets", max_items=40
        )
        self.manifest.update_stage("engineer_packets")
        console.print(
            f"[green]Packets engineer: {result['n_allowed_for_llm']}/{result['n_total']} "
            f"cleared for LLM[/green]"
        )
        return result

    def stage_engineer_labels(self) -> Dict[str, Any]:
        """Mandatory double-pass over outcome labels before model fit / audit."""
        console.print("[bold blue]Stage: engineer_labels (Stationary→NonStationary→Stationary)[/bold blue]")
        if not self.labels:
            self.labels = self._load_labels()

        def _lid(l):
            return getattr(l, "decision_id", None) or (l.get("decision_id") if isinstance(l, dict) else str(id(l)))

        result = self._run_double_pass_batch(
            self.labels, _lid, "OutcomeLabel", "llm_cleared_labels", max_items=40
        )
        self.manifest.update_stage("engineer_labels")
        console.print(
            f"[green]Labels engineer: {result['n_allowed_for_llm']}/{result['n_total']} "
            f"cleared for LLM[/green]"
        )
        return result

    def stage_engineer_decisions(self) -> Dict[str, Any]:
        """Mandatory double-pass over decisions – final gate before LLM interpretation."""
        console.print("[bold blue]Stage: engineer_decisions (Stationary→NonStationary→Stationary)[/bold blue]")
        if not self.decisions:
            # decisions may live only in JSONL
            path = self.artifact_store.path("paper/decisions.jsonl")
            if path.exists():
                self.decisions = [
                    mc.DecisionOutput(**rec)
                    for rec in self.artifact_store.load_jsonl("paper/decisions.jsonl")
                ]

        def _did(d):
            return getattr(d, "decision_id", None) or (d.get("decision_id") if isinstance(d, dict) else str(id(d)))

        result = self._run_double_pass_batch(
            self.decisions, _did, "DecisionOutput", "llm_cleared_decisions", max_items=40
        )
        self.manifest.update_stage("engineer_decisions")
        console.print(
            f"[green]Decisions engineer: {result['n_allowed_for_llm']}/{result['n_total']} "
            f"cleared for LLM[/green]"
        )
        return result

    def get_llm_cleared(self, kind: str = "decisions") -> List[Any]:
        """
        Return only the subjects that survived both stationary passes and the
        non-stationary probe. This is the ONLY data an LLM interpreter may see.
        """
        mapping = {
            "events": self.llm_cleared_events,
            "packets": self.llm_cleared_packets,
            "labels": self.llm_cleared_labels,
            "decisions": self.llm_cleared_decisions,
        }
        if kind not in mapping:
            raise ValueError(f"kind must be one of {list(mapping)}")
        return mapping[kind]

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_stage(self, name: str) -> Dict[str, Any]:
        """Run a single named stage. Intended for LLM / agent control."""
        mapping = {
            "synth": self.stage_synth,
            "engineer_events": self.stage_engineer_events,
            "validate": self.stage_validate,
            "build_packets": self.stage_build_packets,
            "engineer_packets": self.stage_engineer_packets,
            "label": self.stage_label,
            "engineer_labels": self.stage_engineer_labels,
            "split": self.stage_split,
            "fit_baseline": self.stage_fit_baseline,
            "plan_and_decide": self.stage_plan_and_decide,
            "engineer_decisions": self.stage_engineer_decisions,
            "paper_replay": self.stage_paper_replay,
            "adversarial_ci": self.stage_adversarial_ci,
            "knowledge_report": self.stage_knowledge_report,
            "audit": self.stage_audit,
            "report": self.stage_report,
        }
        if name not in mapping:
            raise ValueError(f"Unknown stage '{name}'. Valid: {list(mapping)}")
        return mapping[name]()

    def run_all(self) -> Dict[str, Any]:
        """Run the complete pipeline end-to-end."""
        results = {}
        for stage in self.STAGES:
            try:
                results[stage] = self.run_stage(stage)
            except Exception as e:
                console.print(f"[red]Stage {stage} failed: {e}[/red]")
                results[stage] = {"error": str(e)}
                # Continue so later diagnostic stages still run where possible
        console.print(f"[bold green]Pipeline finished. Artifacts → {self.artifact_store.run_dir}[/bold green]")
        return results

    def status(self) -> Dict[str, Any]:
        """Return a quick status snapshot an LLM can inspect."""
        return {
            "version": VERSION,
            "run_id": self.artifact_store.run_id,
            "run_dir": str(self.artifact_store.run_dir),
            "stages_completed": self.manifest.manifest.get("stages_completed", []),
            "n_events": len(self.events) or None,
            "n_packets": len(self.packets) or None,
            "n_labels": len(self.labels) or None,
            "baseline_fitted": self.baseline is not None,
            "n_decisions": len(self.decisions),
            "llm_cleared": {
                "events": len(self.llm_cleared_events),
                "packets": len(self.llm_cleared_packets),
                "labels": len(self.llm_cleared_labels),
                "decisions": len(self.llm_cleared_decisions),
            },
            "engineer_summary": {
                k: {
                    "n_total": v.get("n_total"),
                    "n_allowed_for_llm": v.get("n_allowed_for_llm"),
                    "n_blocked": v.get("n_blocked"),
                }
                for k, v in self.engineer_results.items()
            },
        }


# =============================================================================
# CLI
# =============================================================================

cli = typer.Typer(help="MegaCompact16 + UAIR Unified Pipeline")


@cli.command()
def all(
    mode: str = typer.Option("synth", help="synth | historical"),
    seed: int = typer.Option(42, help="RNG seed"),
    output_root: str = typer.Option("artifacts", help="Artifact root"),
):
    """Run the complete pipeline."""
    pipe = MegaPipeline(mode=mode, seed=seed, output_root=output_root)
    results = pipe.run_all()
    console.print_json(json.dumps(results, default=str, indent=2))


@cli.command()
def stage(
    name: str = typer.Argument(..., help="Stage name"),
    run_dir: Optional[str] = typer.Option(None, help="Existing run directory to resume"),
    seed: int = typer.Option(42),
):
    """Run a single pipeline stage (useful for LLM step-by-step control)."""
    if run_dir:
        # Resume from existing artifact store
        store = mc.ArtifactStore(run_dir)
        config = mc.Config(**store.load_json("config.resolved.yaml"))
        pipe = MegaPipeline(seed=seed, config=config, run_id=store.run_id)
        # Point the store at the existing directory
        pipe.artifact_store = store
    else:
        pipe = MegaPipeline(seed=seed)

    result = pipe.run_stage(name)
    console.print_json(json.dumps(result, default=str, indent=2))


@cli.command()
def status(run_dir: str = typer.Argument(..., help="Run directory")):
    """Show pipeline status for a run."""
    store = mc.ArtifactStore(run_dir)
    try:
        manifest = store.load_json("manifest.json")
    except Exception:
        manifest = {}
    table = Table(title=f"Run {store.run_id}")
    table.add_column("Key")
    table.add_column("Value")
    table.add_row("stages_completed", str(manifest.get("stages_completed", [])))
    table.add_row("status", str(manifest.get("status", "unknown")))
    console.print(table)


@cli.command()
def list_stages():
    """List available pipeline stages."""
    for s in MegaPipeline.STAGES:
        console.print(f"  • {s}")


if __name__ == "__main__":
    cli()
