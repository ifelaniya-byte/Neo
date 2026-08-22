#!/usr/bin/env python3
"""
Physics & Mathematical Language Atlas (honest, extensible, non-omniscient)
==========================================================================

WHAT THIS IS
  A structured catalogue the Stationary / Non-Stationary engineers can query:
  - Physics domains (classical → quantum → statistical → continuum → info)
  - Formula cards with symbols, assumptions, and validity regimes
  - Mathematical language registry (arithmetic, calculus, linear algebra,
    probability, information theory, category-ish labels, etc.)
  - Hooks for coding / computing / AI knowledge tags used in verification

WHAT THIS IS NOT
  - Not a "world conclusive complete" physics encyclopaedia
  - Not a substitute for textbooks, PDG, NIST, or living review articles
  - Not a claim that all of mathematics or physics is encoded here
  - Not a quantum computer, oracle, or AGI

DESIGN RULES
  1. Every entry carries assumptions and known limits.
  2. Open problems are listed as OPEN, not solved.
  3. Engineers may USE this atlas for checks; they may not invent physics.
  4. Fail-closed: unknown domain → ABSTAIN / note gap, do not hallucinate.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


ATLAS_VERSION = "0.1.0-honest"
ATLAS_DISCLAIMER = (
    "Incomplete by construction. Physics and mathematics are open-ended. "
    "This atlas is a research scaffold for engineer verification, not a conclusive world model."
)


class DomainStatus(str, Enum):
    CORE = "core"           # well-established, textbook-level
    EFFECTIVE = "effective" # effective theory / regime-limited
    OPEN = "open"           # active research / incomplete


@dataclass
class FormulaCard:
    id: str
    name: str
    domain: str
    expression: str
    symbols: Dict[str, str]
    assumptions: List[str]
    validity_regime: str
    status: DomainStatus = DomainStatus.CORE
    math_languages: List[str] = field(default_factory=list)
    references_note: str = "standard textbook form; verify against primary sources"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class PhysicsDomain:
    id: str
    name: str
    status: DomainStatus
    summary: str
    key_ideas: List[str]
    open_problems: List[str]
    formula_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class MathLanguage:
    id: str
    name: str
    purpose: str
    typical_ops: List[str]
    used_by_domains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PhysicsMathAtlas:
    """
    Queryable atlas for engineers. Contents are curated CORE/EFFECTIVE entries
    plus explicitly marked OPEN problems — never presented as complete.
    """

    def __init__(self):
        self.version = ATLAS_VERSION
        self.disclaimer = ATLAS_DISCLAIMER
        self.languages: Dict[str, MathLanguage] = {}
        self.domains: Dict[str, PhysicsDomain] = {}
        self.formulas: Dict[str, FormulaCard] = {}
        self.computing_tags: Dict[str, str] = {}
        self.ai_tags: Dict[str, str] = {}
        self._build()

    # ------------------------------------------------------------------
    # Build catalogue
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._register_math_languages()
        self._register_physics_domains()
        self._register_formulas()
        self._register_computing_ai()

    def _register_math_languages(self) -> None:
        specs = [
            ("arithmetic", "Arithmetic", "Counting, rings of integers/rationals", ["+", "-", "*", "/", "mod"]),
            ("algebra", "Elementary & Abstract Algebra", "Equations, groups, rings, fields", ["solve", "factor", "homomorphism"]),
            ("linear_algebra", "Linear Algebra", "Vector spaces, operators, spectra", ["matmul", "eigen", "svd", "inner_product"]),
            ("calculus", "Calculus", "Limits, derivatives, integrals", ["d/dx", "∫", "∂", "∇"]),
            ("vector_calculus", "Vector Calculus", "Fields in R^n", ["grad", "div", "curl", "Stokes"]),
            ("differential_equations", "Differential Equations", "Dynamical laws", ["ODE", "PDE", "boundary_value"]),
            ("complex_analysis", "Complex Analysis", "Holomorphic structure", ["contour_integral", "residue"]),
            ("probability", "Probability", "Uncertainty, measures", ["E", "Var", "P", "conditional"]),
            ("statistics", "Statistics", "Inference from data", ["likelihood", "estimator", "hypothesis_test"]),
            ("information_theory", "Information Theory", "Entropy, coding, channels", ["H", "D_KL", "I(X;Y)", "rate"]),
            ("optimization", "Optimization", "Extrema under constraints", ["argmin", "Lagrange", "convex"]),
            ("geometry", "Geometry / Manifolds", "Space, metrics, curvature (intro)", ["metric", "geodesic", "curvature"]),
            ("group_theory", "Group Theory", "Symmetry", ["representation", "generator", "invariant"]),
            ("functional_analysis", "Functional Analysis", "Infinite-dim spaces (intro)", ["Hilbert", "operator", "spectrum"]),
            ("category_lite", "Category-lite labels", "Compositional structure tags only", ["morphism", "functor_tag"]),
            ("numerical", "Numerical Analysis", "Stable computation", ["discretize", "error_bound", "condition_number"]),
            ("logic", "Logic", "Proof and consistency checks", ["entailment", "satisfiable", "contradiction"]),
        ]
        for id_, name, purpose, ops in specs:
            self.languages[id_] = MathLanguage(id=id_, name=name, purpose=purpose, typical_ops=ops)

    def _register_physics_domains(self) -> None:
        self.domains["classical_mechanics"] = PhysicsDomain(
            id="classical_mechanics",
            name="Classical Mechanics",
            status=DomainStatus.CORE,
            summary="Newtonian / Lagrangian / Hamiltonian dynamics for macroscopic systems.",
            key_ideas=["Newton laws", "energy conservation", "symplectic structure"],
            open_problems=["n-body chaos detail in specific regimes"],
            formula_ids=["newton_second", "kinetic_energy", "hamilton_eq"],
        )
        self.domains["classical_em"] = PhysicsDomain(
            id="classical_em",
            name="Classical Electromagnetism",
            status=DomainStatus.CORE,
            summary="Maxwell fields, Lorentz force; classical continuum EM.",
            key_ideas=["Maxwell equations", "gauge freedom", "Poynting"],
            open_problems=[],
            formula_ids=["maxwell_div_e", "lorentz_force", "coulomb"],
        )
        self.domains["special_relativity"] = PhysicsDomain(
            id="special_relativity",
            name="Special Relativity",
            status=DomainStatus.CORE,
            summary="Minkowski spacetime; Lorentz transformations.",
            key_ideas=["c invariant", "time dilation", "E=mc^2"],
            open_problems=[],
            formula_ids=["einstein_mass_energy", "lorentz_gamma"],
        )
        self.domains["general_relativity"] = PhysicsDomain(
            id="general_relativity",
            name="General Relativity",
            status=DomainStatus.EFFECTIVE,
            summary="Gravity as spacetime curvature; classical continuum gravity.",
            key_ideas=["Einstein field equations", "geodesics", "equivalence principle"],
            open_problems=["singularities", "quantum gravity interface", "dark sector phenomenology"],
            formula_ids=["einstein_field_eq"],
        )
        self.domains["quantum_mechanics"] = PhysicsDomain(
            id="quantum_mechanics",
            name="Quantum Mechanics",
            status=DomainStatus.CORE,
            summary="Hilbert-space kinematics; unitary evolution; measurement postulates.",
            key_ideas=["state vector", "observables", "Born rule", "uncertainty"],
            open_problems=["measurement problem interpretations", "quantum → classical limit details"],
            formula_ids=["schrodinger", "born_rule", "heisenberg_uncertainty", "commutator"],
        )
        self.domains["quantum_stats"] = PhysicsDomain(
            id="quantum_stats",
            name="Quantum & Classical Statistical Mechanics",
            status=DomainStatus.CORE,
            summary="Ensembles, entropy, partition functions.",
            key_ideas=["Boltzmann", "partition function", "free energy"],
            open_problems=["non-equilibrium steady states in complex systems"],
            formula_ids=["boltzmann_entropy", "partition_function"],
        )
        self.domains["thermo"] = PhysicsDomain(
            id="thermo",
            name="Thermodynamics",
            status=DomainStatus.CORE,
            summary="Laws of thermo; macroscopic energy and entropy.",
            key_ideas=["1st/2nd law", "temperature", "irreversibility"],
            open_problems=[],
            formula_ids=["first_law_thermo"],
        )
        self.domains["waves_optics"] = PhysicsDomain(
            id="waves_optics",
            name="Waves & Optics",
            status=DomainStatus.CORE,
            summary="Wave equation, interference, geometric optics limit.",
            key_ideas=["superposition", "dispersion", "Fourier"],
            open_problems=[],
            formula_ids=["wave_eq_1d"],
        )
        self.domains["info_physics"] = PhysicsDomain(
            id="info_physics",
            name="Information & Physics interface",
            status=DomainStatus.EFFECTIVE,
            summary="Entropy links between information theory and statistical physics.",
            key_ideas=["Shannon entropy", "Landauer bound (regime-limited)", "channel capacity"],
            open_problems=["precise resource theories in all regimes"],
            formula_ids=["shannon_entropy", "kl_divergence"],
        )
        self.domains["open_fundamental"] = PhysicsDomain(
            id="open_fundamental",
            name="Open Fundamental Questions",
            status=DomainStatus.OPEN,
            summary="Areas without a conclusive complete theory.",
            key_ideas=["quantum gravity", "dark matter/energy phenomenology", "measurement problem"],
            open_problems=[
                "UV-complete quantum gravity",
                "nature of dark matter",
                "cosmological constant / dark energy",
                "hard problem of measurement / interpretations",
            ],
            formula_ids=[],
        )

        # Link languages to domains (light touch)
        for lang_id, domains in {
            "calculus": ["classical_mechanics", "classical_em", "quantum_mechanics"],
            "linear_algebra": ["quantum_mechanics", "classical_em"],
            "probability": ["quantum_mechanics", "quantum_stats", "info_physics"],
            "information_theory": ["info_physics", "quantum_stats"],
            "differential_equations": ["classical_mechanics", "classical_em", "waves_optics"],
            "geometry": ["special_relativity", "general_relativity"],
            "group_theory": ["quantum_mechanics", "classical_em"],
            "optimization": ["info_physics"],
            "logic": ["open_fundamental"],
        }.items():
            if lang_id in self.languages:
                self.languages[lang_id].used_by_domains = domains

    def _register_formulas(self) -> None:
        cards = [
            FormulaCard(
                id="newton_second",
                name="Newton's second law",
                domain="classical_mechanics",
                expression="F = m a",
                symbols={"F": "force", "m": "mass", "a": "acceleration"},
                assumptions=["inertial frame", "classical speeds << c", "point mass or CM motion"],
                validity_regime="non-relativistic classical mechanics",
                math_languages=["algebra", "calculus"],
            ),
            FormulaCard(
                id="kinetic_energy",
                name="Kinetic energy (classical)",
                domain="classical_mechanics",
                expression="T = (1/2) m v^2",
                symbols={"T": "kinetic energy", "m": "mass", "v": "speed"},
                assumptions=["non-relativistic"],
                validity_regime="v << c",
                math_languages=["algebra"],
            ),
            FormulaCard(
                id="hamilton_eq",
                name="Hamilton's equations",
                domain="classical_mechanics",
                expression="dq/dt = ∂H/∂p ,  dp/dt = -∂H/∂q",
                symbols={"H": "Hamiltonian", "q": "coordinate", "p": "momentum"},
                assumptions=["standard symplectic phase space"],
                validity_regime="classical Hamiltonian systems",
                math_languages=["calculus", "geometry"],
            ),
            FormulaCard(
                id="coulomb",
                name="Coulomb force",
                domain="classical_em",
                expression="F = k q1 q2 / r^2",
                symbols={"k": "Coulomb constant", "q": "charge", "r": "separation"},
                assumptions=["static point charges", "classical"],
                validity_regime="electrostatics",
                math_languages=["algebra"],
            ),
            FormulaCard(
                id="maxwell_div_e",
                name="Gauss's law (Maxwell)",
                domain="classical_em",
                expression="∇ · E = ρ / ε0",
                symbols={"E": "electric field", "ρ": "charge density", "ε0": "vacuum permittivity"},
                assumptions=["SI units", "classical fields"],
                validity_regime="classical EM",
                math_languages=["vector_calculus"],
            ),
            FormulaCard(
                id="lorentz_force",
                name="Lorentz force",
                domain="classical_em",
                expression="F = q (E + v × B)",
                symbols={"q": "charge", "E": "electric field", "B": "magnetic field", "v": "velocity"},
                assumptions=["classical point charge"],
                validity_regime="classical EM",
                math_languages=["vector_calculus", "algebra"],
            ),
            FormulaCard(
                id="lorentz_gamma",
                name="Lorentz factor",
                domain="special_relativity",
                expression="γ = 1 / sqrt(1 - v^2/c^2)",
                symbols={"γ": "Lorentz factor", "v": "speed", "c": "speed of light"},
                assumptions=["inertial frames", "SR"],
                validity_regime="special relativity",
                math_languages=["algebra", "calculus"],
            ),
            FormulaCard(
                id="einstein_mass_energy",
                name="Mass–energy equivalence",
                domain="special_relativity",
                expression="E = m c^2",
                symbols={"E": "rest energy", "m": "rest mass", "c": "speed of light"},
                assumptions=["rest frame for rest energy form"],
                validity_regime="SR / relativistic mechanics",
                math_languages=["algebra"],
            ),
            FormulaCard(
                id="einstein_field_eq",
                name="Einstein field equations (schematic)",
                domain="general_relativity",
                expression="G_{μν} + Λ g_{μν} = (8πG/c^4) T_{μν}",
                symbols={"G_{μν}": "Einstein tensor", "T_{μν}": "stress-energy", "Λ": "cosmological constant"},
                assumptions=["classical continuum spacetime", "GR"],
                validity_regime="classical gravity; not UV-complete quantum gravity",
                status=DomainStatus.EFFECTIVE,
                math_languages=["geometry", "differential_equations", "tensor_calc_tag"],
            ),
            FormulaCard(
                id="schrodinger",
                name="Time-dependent Schrödinger equation",
                domain="quantum_mechanics",
                expression="i ℏ ∂ψ/∂t = H ψ",
                symbols={"ψ": "state", "H": "Hamiltonian", "ℏ": "reduced Planck constant"},
                assumptions=["closed system unitary evolution between measurements"],
                validity_regime="non-relativistic QM",
                math_languages=["linear_algebra", "calculus", "complex_analysis"],
            ),
            FormulaCard(
                id="born_rule",
                name="Born rule",
                domain="quantum_mechanics",
                expression="P(a) = |⟨a|ψ⟩|^2",
                symbols={"P": "probability", "ψ": "state", "a": "eigenstate"},
                assumptions=["standard measurement postulate"],
                validity_regime="textbook QM",
                math_languages=["linear_algebra", "probability"],
            ),
            FormulaCard(
                id="heisenberg_uncertainty",
                name="Heisenberg uncertainty (canonical)",
                domain="quantum_mechanics",
                expression="σ_x σ_p ≥ ℏ/2",
                symbols={"σ": "std dev", "ℏ": "reduced Planck"},
                assumptions=["canonical x,p"],
                validity_regime="QM",
                math_languages=["probability", "linear_algebra"],
            ),
            FormulaCard(
                id="commutator",
                name="Canonical commutator",
                domain="quantum_mechanics",
                expression="[x, p] = i ℏ",
                symbols={"x": "position op", "p": "momentum op"},
                assumptions=["standard QM"],
                validity_regime="QM",
                math_languages=["linear_algebra"],
            ),
            FormulaCard(
                id="boltzmann_entropy",
                name="Boltzmann entropy",
                domain="quantum_stats",
                expression="S = k_B ln Ω",
                symbols={"S": "entropy", "Ω": "multiplicity", "k_B": "Boltzmann constant"},
                assumptions=["microcanonical counting"],
                validity_regime="equilibrium stat mech",
                math_languages=["probability", "algebra"],
            ),
            FormulaCard(
                id="partition_function",
                name="Canonical partition function",
                domain="quantum_stats",
                expression="Z = Σ_i e^{-β E_i}",
                symbols={"Z": "partition function", "β": "1/kT", "E_i": "energy level"},
                assumptions=["canonical ensemble"],
                validity_regime="equilibrium",
                math_languages=["probability", "calculus"],
            ),
            FormulaCard(
                id="first_law_thermo",
                name="First law of thermodynamics",
                domain="thermo",
                expression="dU = đQ - đW",
                symbols={"U": "internal energy", "Q": "heat", "W": "work"},
                assumptions=["sign convention as stated"],
                validity_regime="macroscopic thermo",
                math_languages=["calculus"],
            ),
            FormulaCard(
                id="wave_eq_1d",
                name="1D wave equation",
                domain="waves_optics",
                expression="∂²u/∂t² = c² ∂²u/∂x²",
                symbols={"u": "field", "c": "wave speed"},
                assumptions=["linear non-dispersive medium"],
                validity_regime="classical waves",
                math_languages=["differential_equations"],
            ),
            FormulaCard(
                id="shannon_entropy",
                name="Shannon entropy",
                domain="info_physics",
                expression="H(X) = -Σ p(x) log p(x)",
                symbols={"H": "entropy", "p": "probability mass"},
                assumptions=["discrete distribution"],
                validity_regime="information theory",
                math_languages=["probability", "information_theory"],
            ),
            FormulaCard(
                id="kl_divergence",
                name="Kullback–Leibler divergence",
                domain="info_physics",
                expression="D_KL(P||Q) = Σ p log(p/q)",
                symbols={"P": "true dist", "Q": "approx dist"},
                assumptions=["same support conditions as required"],
                validity_regime="information theory / stats",
                math_languages=["probability", "information_theory", "statistics"],
            ),
        ]
        for c in cards:
            self.formulas[c.id] = c

    def _register_computing_ai(self) -> None:
        self.computing_tags = {
            "complexity": "Time/space class tags (P, NP-hard as labels only)",
            "numerical_stability": "Conditioning, roundoff, discretization error",
            "reproducibility": "Seeds, version pins, artifact hashes",
            "parallelism": "Data/model parallel patterns as engineering tags",
            "memory_hierarchy": "Cache/locality awareness in implementations",
            "verification": "Tests, types, audits, ledgers",
        }
        self.ai_tags = {
            "supervised_learning": "Fit maps from labeled data",
            "uncertainty_quantification": "Epistemic/aleatoric separation",
            "calibration": "Probability reliability",
            "ood_detection": "Out-of-distribution flags",
            "abstention": "Refuse when unsafe/uncertain",
            "causality_time": "No future feature leakage",
            "alignment_process": "Process constraints, not claimed value lock-in",
        }

    # ------------------------------------------------------------------
    # Queries (engineer-facing API)
    # ------------------------------------------------------------------

    def list_languages(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.languages.values()]

    def list_domains(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.domains.values()]

    def list_formulas(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for f in self.formulas.values():
            if domain is None or f.domain == domain:
                out.append(f.to_dict())
        return out

    def get_formula(self, formula_id: str) -> Optional[Dict[str, Any]]:
        f = self.formulas.get(formula_id)
        return f.to_dict() if f else None

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        hits: List[Tuple[int, Dict[str, Any]]] = []
        for f in self.formulas.values():
            blob = " ".join([f.id, f.name, f.expression, f.domain, " ".join(f.assumptions)]).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, {"type": "formula", **f.to_dict()}))
        for d in self.domains.values():
            blob = " ".join([d.id, d.name, d.summary] + d.key_ideas + d.open_problems).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, {"type": "domain", **d.to_dict()}))
        for lang in self.languages.values():
            blob = " ".join([lang.id, lang.name, lang.purpose] + lang.typical_ops).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, {"type": "math_language", **lang.to_dict()}))
        hits.sort(key=lambda x: -x[0])
        return [h for _, h in hits[:limit]]

    def open_problems(self) -> List[Dict[str, Any]]:
        out = []
        for d in self.domains.values():
            for p in d.open_problems:
                out.append({"domain": d.id, "problem": p, "status": "OPEN"})
        return out

    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Lightweight claim gate for engineers.
        Does NOT prove physics — only checks whether the claim language
        matches catalogue entries or overreaches into OPEN/complete-world territory.
        """
        c = claim.lower()
        overreach = []
        if any(w in c for w in ["complete physics", "theory of everything", "conclusive world", "all of physics", "solved quantum gravity"]):
            overreach.append("claims completeness or solved open fundamental problems")
        if "faster than light" in c or "ftl" in c:
            overreach.append("conflicts with SR core regime unless clearly speculative fiction")
        hits = self.search(claim, limit=5)
        return {
            "claim": claim,
            "overreach": overreach,
            "ok_for_atlas_support": len(overreach) == 0,
            "related_hits": hits,
            "note": "Atlas support ≠ empirical truth. Use primary literature.",
        }

    def export(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "disclaimer": self.disclaimer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_languages": len(self.languages),
            "n_domains": len(self.domains),
            "n_formulas": len(self.formulas),
            "languages": self.list_languages(),
            "domains": self.list_domains(),
            "formulas": self.list_formulas(),
            "open_problems": self.open_problems(),
            "computing_tags": self.computing_tags,
            "ai_tags": self.ai_tags,
        }

    def checksum(self) -> str:
        blob = json.dumps(self.export(), sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()


# Singleton-style helper for engineers
_ATLAS: Optional[PhysicsMathAtlas] = None


def get_atlas() -> PhysicsMathAtlas:
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = PhysicsMathAtlas()
    return _ATLAS
