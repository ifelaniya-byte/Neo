#!/usr/bin/env python3
"""
Known-Settled Knowledge Database (KSKB)
======================================

WHAT THIS IS
  A finite database of results that are treated as SETTLED within explicitly
  stated assumptions and regimes (standard textbook / empirically confirmed
  core science and math identities used by the engineer pipeline).

WHAT "CONCLUSIVE" MEANS HERE
  - Conclusive *among the included entries*, given their assumptions.
  - NOT conclusive about all of nature, all of mathematics, or all human knowledge.
  - Open research problems are EXCLUDED from this database (see atlas open list).

WHAT THIS IS NOT
  - Not a complete encyclopaedia of science
  - Not a substitute for primary literature, PDG, NIST, CODATA, textbooks
  - Not a claim of finished physics
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


KSKB_VERSION = "1.0.0-settled"
KSKB_SCOPE = (
    "Settled knowledge only: entries are standard identities / laws that hold "
    "under the listed assumptions. Scope is finite and curated. "
    "Absence from this DB does not mean false; presence means 'accepted within regime'."
)


class Confidence(str, Enum):
    SETTLED = "SETTLED"  # textbook + regime-confirmed


@dataclass
class SettledEntry:
    id: str
    field: str          # math | physics | computing | information
    statement: str
    formal: str
    assumptions: List[str]
    regime: str
    confidence: Confidence = Confidence.SETTLED
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["confidence"] = self.confidence.value
        return d


class KnownSettledDB:
    """Queryable database of settled entries only."""

    def __init__(self):
        self.version = KSKB_VERSION
        self.scope = KSKB_SCOPE
        self.entries: Dict[str, SettledEntry] = {}
        self._build()
        self._load_export()

    def _add(self, e: SettledEntry) -> None:
        self.entries[e.id] = e

    def _build(self) -> None:
        # ----- Mathematics (identities / definitions that are settled) -----
        self._add(SettledEntry(
            id="math.arithmetic.2p2",
            field="math",
            statement="Two plus two equals four in standard integer arithmetic.",
            formal="2 + 2 = 4",
            assumptions=["Peano/integer arithmetic", "standard base-10 numerals"],
            regime="elementary arithmetic",
            tags=["arithmetic", "identity"],
        ))
        self._add(SettledEntry(
            id="math.logic.noncontradiction",
            field="math",
            statement="A statement and its negation are not both true (classical logic).",
            formal="¬(A ∧ ¬A)",
            assumptions=["classical bivalent logic"],
            regime="classical logic",
            tags=["logic"],
        ))
        self._add(SettledEntry(
            id="math.prob.unit_measure",
            field="math",
            statement="Probabilities of a discrete partition sum to 1.",
            formal="Σ_i P(i) = 1 for a complete discrete partition",
            assumptions=["probability measure axioms (Kolmogorov)"],
            regime="probability theory",
            tags=["probability"],
        ))
        self._add(SettledEntry(
            id="math.prob.bayes",
            field="math",
            statement="Bayes' rule relating conditional probabilities.",
            formal="P(A|B) = P(B|A) P(A) / P(B)  when P(B) > 0",
            assumptions=["Kolmogorov probability", "P(B)>0"],
            regime="probability theory",
            tags=["probability", "inference"],
        ))
        self._add(SettledEntry(
            id="math.linalg.matmul_assoc",
            field="math",
            statement="Matrix multiplication is associative where defined.",
            formal="(AB)C = A(BC)",
            assumptions=["compatible dimensions over a ring/field"],
            regime="linear algebra",
            tags=["linear_algebra"],
        ))
        self._add(SettledEntry(
            id="math.calc.ftc",
            field="math",
            statement="Fundamental theorem of calculus (standard form).",
            formal="d/dx ∫_a^x f(t) dt = f(x) for continuous f",
            assumptions=["f continuous on interval"],
            regime="real calculus",
            tags=["calculus"],
        ))
        self._add(SettledEntry(
            id="math.info.shannon_nonneg",
            field="math",
            statement="Shannon entropy is nonnegative.",
            formal="H(X) ≥ 0",
            assumptions=["discrete distribution", "Shannon definition"],
            regime="information theory",
            tags=["information_theory"],
        ))
        self._add(SettledEntry(
            id="math.info.kl_nonneg",
            field="math",
            statement="KL divergence is nonnegative.",
            formal="D_KL(P||Q) ≥ 0",
            assumptions=["P absolutely continuous w.r.t. Q as required"],
            regime="information theory",
            tags=["information_theory", "statistics"],
        ))

        # ----- Physics (settled within regime) -----
        self._add(SettledEntry(
            id="phys.newton.second",
            field="physics",
            statement="Net force equals mass times acceleration (Newtonian).",
            formal="F = m a",
            assumptions=["inertial frame", "non-relativistic", "classical"],
            regime="classical mechanics v ≪ c",
            tags=["classical_mechanics"],
        ))
        self._add(SettledEntry(
            id="phys.em.maxwell_div_b",
            field="physics",
            statement="No magnetic monopoles in classical Maxwell theory (div B = 0).",
            formal="∇ · B = 0",
            assumptions=["classical Maxwell electrodynamics"],
            regime="classical EM",
            tags=["classical_em"],
        ))
        self._add(SettledEntry(
            id="phys.sr.c_invariant",
            field="physics",
            statement="Speed of light in vacuum is invariant across inertial frames (SR).",
            formal="c invariant under Lorentz transformations",
            assumptions=["special relativity", "inertial frames", "vacuum"],
            regime="special relativity",
            tags=["special_relativity"],
        ))
        self._add(SettledEntry(
            id="phys.sr.mass_energy",
            field="physics",
            statement="Rest energy equals rest mass times c squared.",
            formal="E₀ = m c²",
            assumptions=["SR", "rest frame for rest energy"],
            regime="relativistic mechanics",
            tags=["special_relativity"],
        ))
        self._add(SettledEntry(
            id="phys.qm.born",
            field="physics",
            statement="Born rule: outcome probabilities from |amplitude|².",
            formal="P(a) = |⟨a|ψ⟩|²",
            assumptions=["standard quantum measurement postulate"],
            regime="textbook quantum mechanics",
            tags=["quantum_mechanics"],
        ))
        self._add(SettledEntry(
            id="phys.qm.uncertainty",
            field="physics",
            statement="Canonical Heisenberg uncertainty relation.",
            formal="σ_x σ_p ≥ ℏ/2",
            assumptions=["canonical x,p operators", "standard QM"],
            regime="quantum mechanics",
            tags=["quantum_mechanics"],
        ))
        self._add(SettledEntry(
            id="phys.thermo.second_isolated",
            field="physics",
            statement="Entropy of an isolated system does not decrease (2nd law, Clausius form summary).",
            formal="ΔS ≥ 0 for isolated system",
            assumptions=["thermodynamic limit / macroscopic", "isolated"],
            regime="classical thermodynamics",
            tags=["thermo"],
        ))
        self._add(SettledEntry(
            id="phys.stat.boltzmann",
            field="physics",
            statement="Boltzmann entropy relates entropy to multiplicity.",
            formal="S = k_B ln Ω",
            assumptions=["microcanonical ensemble counting"],
            regime="equilibrium statistical mechanics",
            tags=["stat_mech"],
        ))

        # ----- Computing / information engineering (settled engineering facts) -----
        self._add(SettledEntry(
            id="comp.hash.sha256_length",
            field="computing",
            statement="SHA-256 digest is 256 bits (64 hex characters).",
            formal="|SHA256(m)| = 256 bits",
            assumptions=["FIPS 180-4 SHA-256"],
            regime="cryptographic hash standards",
            tags=["hashing", "standards"],
        ))
        self._add(SettledEntry(
            id="comp.ieee754.note",
            field="computing",
            statement="IEEE-754 binary floating point has finite precision and rounding modes.",
            formal="float arithmetic ≠ real arithmetic",
            assumptions=["IEEE-754 binary formats"],
            regime="numerical computing",
            tags=["numerical"],
        ))
        self._add(SettledEntry(
            id="comp.causality.no_future_read",
            field="computing",
            statement="In a time-causal feature system, features with availability time > decision time must not be used.",
            formal="∀ features f: available_time(f) ≤ decision_time",
            assumptions=["defined timestamps", "enforced access layer"],
            regime="time-causal ML / trading research systems",
            tags=["causality", "ml_systems"],
        ))
        self._add(SettledEntry(
            id="ai.abstain.safety",
            field="computing",
            statement="When uncertainty or constraint checks fail, refusing to act (abstain) is a valid control decision.",
            formal="verdict = ABSTAIN if ¬constraints_ok ∨ uncertainty_high",
            assumptions=["explicit constraint and uncertainty thresholds"],
            regime="safety-aware decision systems",
            tags=["abstention", "safety"],
        ))

        # Explicit exclusions note (not entries): quantum gravity TOE, dark matter identity, etc.


    def _load_export(self) -> None:
        """Merge persisted promotions from artifacts/known_settled_export.json if present."""
        try:
            from pathlib import Path
            import json
            path = Path("artifacts/known_settled_export.json")
            if not path.exists():
                path = Path(__file__).resolve().parent / "artifacts" / "known_settled_export.json"
            if not path.exists():
                return
            data = json.loads(path.read_text(encoding="utf-8"))
            for e in data.get("entries") or []:
                eid = e.get("id")
                if not eid or eid in self.entries:
                    continue
                self.entries[eid] = SettledEntry(
                    id=eid,
                    field=e.get("field", "math"),
                    statement=e.get("statement", ""),
                    formal=e.get("formal", ""),
                    assumptions=list(e.get("assumptions") or []),
                    regime=e.get("regime", ""),
                    confidence=Confidence.SETTLED,
                    tags=list(e.get("tags") or []),
                )
        except Exception:
            pass

    def get(self, entry_id: str) -> Optional[Dict[str, Any]]:
        e = self.entries.get(entry_id)
        return e.to_dict() if e else None

    def list_entries(self, field: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for e in self.entries.values():
            if field is None or e.field == field:
                out.append(e.to_dict())
        return out

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        hits = []
        for e in self.entries.values():
            blob = " ".join([e.id, e.field, e.statement, e.formal, e.regime] + e.assumptions + e.tags).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, e.to_dict()))
        hits.sort(key=lambda x: -x[0])
        return [h for _, h in hits[:limit]]

    def lookup_formal(self, formal_substr: str) -> List[Dict[str, Any]]:
        s = formal_substr.lower()
        return [e.to_dict() for e in self.entries.values() if s in e.formal.lower()]

    def assert_settled(self, entry_id: str) -> Dict[str, Any]:
        """Engineer-facing: confirm id is in the settled DB."""
        e = self.entries.get(entry_id)
        if not e:
            return {"ok": False, "entry_id": entry_id, "reason": "not_in_settled_db"}
        return {"ok": True, "entry": e.to_dict()}

    def reject_completeness_claim(self, text: str) -> Dict[str, Any]:
        t = text.lower()
        bad = []
        for phrase in [
            "complete physics", "theory of everything", "all knowledge",
            "conclusive world", "finished physics", "everything that is known",
            "fully conclusive universe",
        ]:
            if phrase in t:
                bad.append(phrase)
        return {
            "ok": len(bad) == 0,
            "rejected_phrases": bad,
            "note": "KSKB is finite settled entries only; completeness claims are out of scope",
        }

    def export(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "scope": self.scope,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_entries": len(self.entries),
            "fields": sorted({e.field for e in self.entries.values()}),
            "entries": self.list_entries(),
            "explicitly_excluded": [
                "UV-complete quantum gravity",
                "identity of dark matter",
                "final measurement interpretation",
                "any claim of complete human knowledge",
            ],
        }

    def checksum(self) -> str:
        return hashlib.sha256(
            json.dumps(self.export(), sort_keys=True, default=str).encode()
        ).hexdigest()


_DB: Optional[KnownSettledDB] = None


def get_settled_db() -> KnownSettledDB:
    global _DB
    if _DB is None:
        _DB = KnownSettledDB()
    return _DB
