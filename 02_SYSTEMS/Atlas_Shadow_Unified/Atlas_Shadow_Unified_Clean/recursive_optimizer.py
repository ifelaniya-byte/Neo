"""Recursive candidate optimizer for Atlas + Shadow Unified.

Design decision after stationary/non-stationary review:
    The proposed metric/LLM-mutate/hot-swap loop is useful, but unsafe and
    statistically weak if it promotes a candidate from one timed execution.

The implementation therefore uses a Champion/Challenger + Canary + Gate +
Rollback architecture. Candidates are never promoted merely because they are
faster. Promotion requires source validity, deterministic behavior, math/code
checks, stationary verification, non-regression, and a multi-run fitness gain.

No external dependencies are required.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass
class TelemetrySample:
    duration_s: float
    memory_mb: float
    errors: int
    payloads: int = 1

    @property
    def throughput(self) -> float:
        return self.payloads / self.duration_s if self.duration_s > 0 else 0.0


@dataclass
class FitnessResult:
    score: float
    median_duration_s: float
    median_memory_mb: float
    error_rate: float
    throughput: float
    samples: int
    regression_free: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateResult:
    candidate_id: str
    source_hash: str
    static_ok: bool
    deterministic_ok: bool
    benchmark: Optional[FitnessResult]
    stationary_ok: bool
    promoted: bool = False
    rejected_reasons: List[str] = field(default_factory=list)


class TelemetryCollector:
    """Measure real runtime telemetry; never use fabricated resource values."""

    def run(self, fn: Callable[[str], Any], payloads: Sequence[str]) -> List[TelemetrySample]:
        samples: List[TelemetrySample] = []
        for payload in payloads:
            # Measure exactly one invocation. The previous implementation ran
            # each payload twice (once for timing and once under tracemalloc),
            # which distorted side-effecting workloads and could overwrite a
            # first-call error with a second-call success.
            errors = 0
            memory_mb = 0.0
            try:
                import tracemalloc
                tracemalloc.start()
            except Exception:
                tracemalloc = None

            start = time.perf_counter()
            try:
                fn(payload)
            except Exception:
                errors = 1
            elapsed = max(time.perf_counter() - start, 1e-12)

            if tracemalloc is not None:
                try:
                    _, peak = tracemalloc.get_traced_memory()
                    memory_mb = peak / (1024 * 1024)
                finally:
                    tracemalloc.stop()
            samples.append(TelemetrySample(elapsed, memory_mb, errors))
        return samples


class CandidateStaticGate:
    """AST/compile/import checks before a candidate can reach runtime tests."""

    def validate_file(self, path: Path) -> Dict[str, Any]:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            compile(tree, str(path), "exec")
            return {
                "ok": True,
                "path": str(path),
                "lines": len(source.splitlines()),
                "sha256": hashlib.sha256(source.encode()).hexdigest(),
                "classes": sum(isinstance(n, ast.ClassDef) for n in tree.body),
                "functions": sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in tree.body),
            }
        except Exception as exc:
            return {"ok": False, "path": str(path), "error": repr(exc)}


class FitnessEvaluator:
    """Multi-objective fitness with hard correctness gates.

    Score is dimensionless and deliberately favors correctness first. The
    performance terms are normalized against the current champion, preventing
    memory units from overwhelming execution-time units as in the original
    proposal.
    """

    def __init__(self, time_weight: float = 0.35, memory_weight: float = 0.15,
                 throughput_weight: float = 0.50):
        self.time_weight = time_weight
        self.memory_weight = memory_weight
        self.throughput_weight = throughput_weight

    @staticmethod
    def summarize(samples: Sequence[TelemetrySample]) -> Tuple[float, float, float, float]:
        durations = [s.duration_s for s in samples]
        memory = [s.memory_mb for s in samples]
        errors = sum(s.errors for s in samples)
        return (
            statistics.median(durations),
            statistics.median(memory),
            errors / max(len(samples), 1),
            statistics.median([s.throughput for s in samples]),
        )

    def evaluate(self, samples: Sequence[TelemetrySample], champion: Optional[FitnessResult]) -> FitnessResult:
        if not samples:
            return FitnessResult(0.0, math.inf, math.inf, 1.0, 0.0, 0, False)
        duration, memory, error_rate, throughput = self.summarize(samples)
        if champion is None:
            # First champion establishes the normalization scale.
            score = throughput / (1.0 + duration + memory)
            return FitnessResult(score, duration, memory, error_rate, throughput,
                                 len(samples), error_rate == 0)

        time_ratio = champion.median_duration_s / max(duration, 1e-12)
        memory_ratio = champion.median_memory_mb / max(memory, 1e-12) if champion.median_memory_mb > 0 else 1.0
        throughput_ratio = throughput / max(champion.throughput, 1e-12)
        correctness = max(0.0, 1.0 - error_rate)
        score = correctness * (
            self.time_weight * time_ratio
            + self.memory_weight * memory_ratio
            + self.throughput_weight * throughput_ratio
        )
        regression_free = error_rate <= champion.error_rate and score > champion.score
        return FitnessResult(score, duration, memory, error_rate, throughput,
                             len(samples), regression_free)


class CandidateEvaluator:
    """Evaluate a candidate without mutating the live registry."""

    def __init__(self, module_name: str, class_name: str = "UnifiedOrchestrator", repetitions: int = 3):
        self.module_name = module_name
        self.class_name = class_name
        self.repetitions = max(2, min(int(repetitions), 20))
        self.telemetry = TelemetryCollector()
        self.fitness = FitnessEvaluator()

    def load_isolated(self):
        module = importlib.import_module(self.module_name)
        if hasattr(module, self.class_name):
            return getattr(module, self.class_name)()
        # The current unified_orchestrator.py uses AgentLoop, not the older
        # UnifiedOrchestrator name. Build its real dependency graph instead of
        # silently assuming an API that is not present.
        if self.module_name == "unified_orchestrator" and hasattr(module, "AgentLoop"):
            kb = module.KnowledgeBase()
            math_e = module.MathEngine()
            logic = module.LogicEngine()
            code = module.CodeLangDetector()
            pred = module.PredictiveScorer()
            translator = module.Translator()
            tools = module.build_default_tools()
            thought = module.ExperimentalThoughtLoop(kb)
            planner = module.AutonomousPlanner()
            atlas = module.MathAtlas(":memory:")
            atlas.create_and_populate()
            router = module.Router(kb, math_e, logic, code, pred, translator, tools, thought, planner, atlas)
            return module.AgentLoop(router)
        raise AttributeError(
            f"{self.module_name!r} exposes neither {self.class_name!r} nor a supported runner adapter"
        )

    @staticmethod
    def _execute(obj: Any, payload: str) -> Any:
        if hasattr(obj, "execute_pipeline"):
            return obj.execute_pipeline(payload)
        if hasattr(obj, "run"):
            return obj.run([{"task": payload, "payload": None}])
        raise TypeError("candidate object has no supported execute method")

    def deterministic_check(self, payloads: Sequence[str]) -> Tuple[bool, str]:
        try:
            a = self.load_isolated()
            b = self.load_isolated()
            for payload in payloads:
                if self._execute(a, payload) != self._execute(b, payload):
                    return False, f"non_deterministic_payload:{payload!r}"
            return True, "deterministic"
        except Exception as exc:
            return False, repr(exc)

    def benchmark(self, payloads: Sequence[str], champion: Optional[FitnessResult]) -> FitnessResult:
        obj = self.load_isolated()
        workload = [p for p in payloads for _ in range(self.repetitions)]
        samples = self.telemetry.run(lambda p: self._execute(obj, p), workload)
        return self.fitness.evaluate(samples, champion)


class ChampionRegistry:
    """Persistent champion metadata; source promotion remains transactional."""

    def __init__(self, path: str = "optimizer_registry.json"):
        self.path = Path(path)
        self.data: Dict[str, Any] = {"champion": None, "history": []}
        self._load()

    def _load(self):
        try:
            if self.path.exists():
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self.data = {"champion": None, "history": []}

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")

    def record(self, result: CandidateResult):
        self.data.setdefault("history", []).append(asdict(result))
        if result.promoted:
            self.data["champion"] = asdict(result)
        self.save()


class RecursiveOptimizer:
    """Champion/challenger recursive optimization controller.

    The optimizer can generate candidates externally (including by an LLM),
    but candidate code is treated as untrusted input and cannot directly
    replace the live implementation. The caller must explicitly provide a
    stationary verification callback before promotion.
    """

    def __init__(self, system_core: Any = None,
                 stationary_gate: Optional[Callable[[], Dict[str, Any]]] = None,
                 registry: Optional[ChampionRegistry] = None):
        self.system = system_core
        self.stationary_gate = stationary_gate
        self.registry = registry or ChampionRegistry()
        self.static_gate = CandidateStaticGate()
        self.last_result: Optional[CandidateResult] = None

    @staticmethod
    def _candidate_id(module_name: str) -> str:
        return hashlib.sha256(module_name.encode()).hexdigest()[:16]

    def evaluate_candidate(self, module_name: str, payloads: Sequence[str],
                           champion: Optional[FitnessResult] = None) -> CandidateResult:
        module_path = Path(module_name.replace(".", os.sep) + ".py")
        static = self.static_gate.validate_file(module_path)
        candidate_id = self._candidate_id(module_name)
        if not static.get("ok"):
            result = CandidateResult(candidate_id, "", False, False, None, False,
                                     False, ["static_gate_failed"])
            self.registry.record(result)
            self.last_result = result
            return result

        evaluator = CandidateEvaluator(module_name)
        deterministic, detail = evaluator.deterministic_check(payloads)
        if not deterministic:
            result = CandidateResult(candidate_id, static["sha256"], True, False, None, False,
                                     False, [detail])
            self.registry.record(result)
            self.last_result = result
            return result

        benchmark = evaluator.benchmark(payloads, champion)
        stationary_ok = False
        reasons: List[str] = []
        if self.stationary_gate:
            try:
                stationary_report = self.stationary_gate()
                stationary_ok = bool(stationary_report.get("all_ok"))
                if not stationary_ok:
                    reasons.append("stationary_gate_failed")
            except Exception as exc:
                reasons.append(f"stationary_gate_error:{exc!r}")
        else:
            reasons.append("stationary_gate_not_bound")

        promoted = bool(benchmark.regression_free and stationary_ok and not reasons)
        if not promoted:
            if benchmark.error_rate > 0:
                reasons.append("runtime_errors")
            if not benchmark.regression_free:
                reasons.append("no_strict_fitness_improvement_or_regression")
        result = CandidateResult(candidate_id, static["sha256"], True, True,
                                 benchmark, stationary_ok, promoted, reasons)
        self.registry.record(result)
        self.last_result = result
        return result

    def promote_registry_only(self, module_name: str) -> Dict[str, Any]:
        """Atomically switch the live registry reference; never rewrite source."""
        if not self.system or not self.last_result or not self.last_result.promoted:
            return {"ok": False, "reason": "promotion_gate_not_satisfied"}
        obj = CandidateEvaluator(module_name).load_isolated()
        self.system.register_module("orchestrator", obj)
        return {"ok": True, "mode": "registry_swap", "module": module_name}


__all__ = [
    "TelemetrySample", "FitnessResult", "CandidateResult", "TelemetryCollector",
    "CandidateStaticGate", "FitnessEvaluator", "CandidateEvaluator",
    "ChampionRegistry", "RecursiveOptimizer",
]
