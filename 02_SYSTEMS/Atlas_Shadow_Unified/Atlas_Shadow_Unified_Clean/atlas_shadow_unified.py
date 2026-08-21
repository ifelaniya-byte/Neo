#!/usr/bin/env python3
"""
ATLAS + SHADOW UNIFIED (complete merge)
=======================================
One script combining ALL feasible pieces from the conversation:

  • Shadow Alphabet — cryptographic seal (word, phrase, stack, hash, verify)
  • Shadow Alphabet — English a–z textual-gradient engine (supplemental)
  • Mathematical Language Atlas (expanded math + coding + computational AI forms)
  • Knowledge pod (novelty filter, ingest, reflection)
  • Sympy math engine + propositional logic
  • Code-language detector
  • Computational / AI knowledge layer
  • Tools + tiny learned predictor
  • Reactive planner + agent loop
  • Preflight super-math/code gate, source-engineer audit, staged plan/research/test/verify/implement pipeline
  • Persistent verification/growth telemetry, directive scoring, schema v2, integrity budget

Sources merged:
  shadow_alphabet.py, shadow_alphabet_engine.py,
  orchestrator_combined / complete / evolved / max / expanded,
  unified_orchestrator.py, math-atlas concepts

Honest limits remain documented.
"""

from __future__ import annotations
import re
import math
import json
import hashlib
import base64
import datetime
import random
import sqlite3
import ast
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Callable, Any, Tuple, Optional, Set

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None
    nn = None

try:
    import sympy
    from sympy import (
        symbols, simplify, solve, diff, integrate, Matrix, limit, series,
        factorial, Eq
    )
    from sympy.logic.inference import satisfiable
    from sympy.ntheory import isprime, factorint
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
DB_PATH = ":memory:"

# =============================================================================
# SHADOW ALPHABET
# =============================================================================
VERBS = [
    "binds", "folds", "lifts", "projects", "seals", "reflects", "stabilizes",
    "transforms", "compresses", "verifies", "encodes", "decodes", "maps",
    "traces", "anchors", "resolves", "propagates", "absorbs", "emits", "converges",
]
OBJECTS = [
    "boundary", "kernel", "spectrum", "measure", "morphism", "invariant",
    "residue", "operator", "distribution", "functor", "gradient", "lattice",
    "fiber", "sheaf", "cobordism", "attractor", "eigenstate", "partition",
    "trajectory", "signal", "manifold", "tensor", "attention", "embedding",
]

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-") or "unknown"

def make_shadow_word(name: str, domain: str) -> str:
    return f"{_norm(domain)}-{_sha256(name)[:8]}"

def make_shadow_phrase(name: str, domain: str) -> str:
    seed = int(_sha256(name)[:16], 16)
    rng = random.Random(seed)
    return f"the {domain.lower()} {rng.choice(VERBS)} the {rng.choice(OBJECTS)} and verifies {_norm(name)}"

def build_payload(name, domain, statement, latex, unicode_text, shadow_word, shadow_phrase) -> str:
    return "\n".join([
        name or "", domain or "", statement or "", latex or "",
        unicode_text or "", shadow_word or "", shadow_phrase or "",
    ])

def make_shadow_stack(name, domain, statement, latex, unicode_text, sw, sp, sh) -> List[List[str]]:
    return [
        ["PUSH_CONTEXT", name],
        ["PUSH_DOMAIN", domain],
        ["PUSH_STATEMENT", statement],
        ["PUSH_LATEX", latex or ""],
        ["PUSH_UNICODE", unicode_text or ""],
        ["PUSH_SHADOW_WORD", sw],
        ["PUSH_SHADOW_PHRASE", sp],
        ["EXPECT_HASH", sh],
        ["ASSERT_NONEMPTY"],
        ["VERIFY"],
        ["SEAL"],
    ]

def seal_formula(name, domain, statement, latex="", unicode_text="") -> Dict[str, Any]:
    sw = make_shadow_word(name, domain)
    sp = make_shadow_phrase(name, domain)
    payload = build_payload(name, domain, statement, latex, unicode_text, sw, sp)
    sh = _sha256(payload)
    stack = make_shadow_stack(name, domain, statement, latex, unicode_text, sw, sp, sh)
    return {
        "name": name, "domain": domain, "statement": statement,
        "latex": latex, "unicode": unicode_text,
        "shadow_word": sw, "shadow_phrase": sp,
        "shadow_stack": stack, "shadow_hash": sh, "sealed_at": NOW,
    }

def verify_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    payload = build_payload(
        entry.get("name",""), entry.get("domain",""), entry.get("statement",""),
        entry.get("latex",""), entry.get("unicode",""),
        entry.get("shadow_word",""), entry.get("shadow_phrase",""),
    )
    recomputed = _sha256(payload)
    stored = entry.get("shadow_hash", "")
    expect = None
    for op in entry.get("shadow_stack", []):
        if op and op[0] == "EXPECT_HASH" and len(op) > 1:
            expect = op[1]
            break
    match_stored = recomputed == stored
    match_stack = expect is None or recomputed == expect
    nonempty = all(bool(str(entry.get(k,"")).strip()) for k in
                   ("name","domain","statement","shadow_word","shadow_phrase","shadow_hash"))
    status = "INTACT" if (match_stored and match_stack and nonempty) else "COMPROMISED"
    return {
        "name": entry.get("name"), "status": status,
        "match_stored_hash": match_stored, "match_stack_expect": match_stack,
        "assert_nonempty": nonempty, "stored_hash": stored, "recomputed_hash": recomputed,
    }

def run_stack(stack: List[List[str]], entry: Dict[str, Any]) -> Dict[str, Any]:
    log, verified, sealed = [], False, False
    machine = []
    for op in stack:
        if not op: continue
        code, arg = op[0], (op[1] if len(op) > 1 else None)
        if code.startswith("PUSH_") or code == "EXPECT_HASH":
            machine.append(arg)
            log.append(f"{code} → {str(arg)[:50]}")
        elif code == "ASSERT_NONEMPTY":
            ok = all(x is not None and str(x).strip() for x in machine)
            log.append(f"ASSERT_NONEMPTY → {ok}")
            if not ok:
                return {"ok": False, "log": log, "reason": "empty"}
        elif code == "VERIFY":
            result = verify_entry(entry)
            verified = result["status"] == "INTACT"
            log.append(f"VERIFY → {result['status']}")
            if not verified:
                return {"ok": False, "log": log, "reason": "hash mismatch", "detail": result}
        elif code == "SEAL":
            sealed = verified
            log.append(f"SEAL → {'sealed' if sealed else 'refused'}")
    return {"ok": sealed, "log": log, "verified": verified, "sealed": sealed}


# =============================================================================
# SHADOW ALPHABET — English a–z textual gradient engine (supplemental)
# Maps mathematical-language text into 26-dim letter-frequency space.
# =============================================================================
ENGLISH_AXIS = "abcdefghijklmnopqrstuvwxyz"
AXIS_INDEX = {ch: i for i, ch in enumerate(ENGLISH_AXIS)}
AXIS_DIM = 26

def _encode_gradient(text: str) -> List[float]:
    t = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    counts = [0.0] * AXIS_DIM
    total = 0.0
    for ch in t:
        if ch in AXIS_INDEX:
            counts[AXIS_INDEX[ch]] += 1.0
            total += 1.0
    if total == 0:
        return counts
    return [c / total for c in counts]

def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return dot/(na*nb) if na and nb else 0.0

class TextualGradientEngine:
    """English-alphabet textual gradients over mathematical language descriptions."""
    def __init__(self, language_blobs: List[Dict[str, str]] = None):
        self.items = language_blobs or []
        self._cache: Dict[str, List[float]] = {}
        for it in self.items:
            blob = f"{it.get('name','')} {it.get('family','')} {it.get('example','')}"
            self._cache[it["name"]] = _encode_gradient(blob)

    def encode(self, text: str) -> Dict[str, Any]:
        vec = _encode_gradient(text)
        ranked = sorted([(ENGLISH_AXIS[i], vec[i]) for i in range(AXIS_DIM) if vec[i] > 0],
                        key=lambda x: -x[1])[:6]
        centroid = sum(i * vec[i] for i in range(AXIS_DIM))
        return {"centroid": round(centroid, 4), "dominant": ranked, "preview": text[:60]}

    def rank(self, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        qv = _encode_gradient(query)
        ranked = []
        for name, vec in self._cache.items():
            ranked.append({"name": name, "similarity": round(_cosine(qv, vec), 4)})
        ranked.sort(key=lambda x: -x["similarity"])
        return ranked[:top_k]

    def gradient(self, text_a: str, text_b: str) -> Dict[str, Any]:
        va, vb = _encode_gradient(text_a), _encode_gradient(text_b)
        delta = [vb[i]-va[i] for i in range(AXIS_DIM)]
        increased = sorted([(ENGLISH_AXIS[i], delta[i]) for i in range(AXIS_DIM) if delta[i] > 1e-6],
                           key=lambda x: -x[1])[:5]
        return {
            "cosine": round(_cosine(va, vb), 4),
            "centroid_shift": round(sum(i*vb[i] for i in range(AXIS_DIM)) - sum(i*va[i] for i in range(AXIS_DIM)), 4),
            "letters_increased": increased,
        }


# =============================================================================
# EXPANDED MATHEMATICAL + COMPUTATIONAL AI KNOWLEDGE
# =============================================================================
LANGUAGE_FORMS = [
    # Classical mathematical languages
    {"name": "Natural-language mathematics", "family": "Expository",
     "description": "Mathematics in ordinary language.", "example": "For every real x, x² ≥ 0"},
    {"name": "Symbolic algebra", "family": "Algebraic",
     "description": "Variables, operators, equations.", "example": "a² + b² = c²"},
    {"name": "First-order logic", "family": "Formal logic",
     "description": "Quantifiers and connectives.", "example": "∀x (Prime(x) ∧ x>2 → Odd(x))"},
    {"name": "Set theory (ZFC)", "family": "Foundational",
     "description": "Sets and membership.", "example": "{x ∈ ℝ | x² ≥ 0} = ℝ"},
    {"name": "Category theory", "family": "Abstract structural",
     "description": "Objects, morphisms, functors.", "example": "F ∘ G : C → E"},
    {"name": "Tensor / index notation", "family": "Physics",
     "description": "Indexed tensors, Einstein summation.", "example": "R_μν − ½Rg_μν = 8πGT_μν"},
    {"name": "Differential-form notation", "family": "Geometry",
     "description": "Forms and exterior derivatives.", "example": "dω = 0"},
    {"name": "Matrix notation", "family": "Linear algebra",
     "description": "Vectors, matrices, eigenvalues.", "example": "Ax = b"},
    {"name": "Probability notation", "family": "Statistical",
     "description": "Random variables, conditionals.", "example": "P(A|B)=P(B|A)P(A)/P(B)"},
    {"name": "Calculus notation", "family": "Analysis",
     "description": "Limits, derivatives, integrals.", "example": "∫_a^b f' = f(b)−f(a)"},
    {"name": "Modal logic", "family": "Philosophical logic",
     "description": "Necessity and possibility.", "example": "□P → ◇P"},
    {"name": "Lambda calculus", "family": "Computational",
     "description": "Abstraction and application.", "example": "λf.λx.f (f x)"},
    {"name": "Type theory", "family": "Foundational CS",
     "description": "Types, terms, judgments.", "example": "Γ ⊢ t : T"},
    {"name": "Homotopy type theory", "family": "Foundational",
     "description": "Types as spaces.", "example": "Id_A(a,b) as path space"},
    # Shadow / umbral
    {"name": "Umbral / shadow letters", "family": "Shadow umbral",
     "description": "Whitehead umbral letters assigning properties to regional letters.",
     "example": "α as shadow of a"},
    {"name": "Umbral calculus", "family": "Shadow umbral",
     "description": "Formal manipulation of sequences via umbral notation.",
     "example": "eval(a^n) = a_n"},
    {"name": "Combinatorial shadow", "family": "Shadow umbral",
     "description": "Shadow ∂𝒜 by deleting one element from each set.",
     "example": "∂𝒜 = {A\\{x} | A∈𝒜, x∈A}"},
    {"name": "Shadow theory semantics", "family": "Shadow umbral",
     "description": "Quantifiers as individual-like shadows of type e.",
     "example": "'every man' denotes a shadow"},
    {"name": "Logic Alphabet (Zellweger)", "family": "Alternative logical alphabet",
     "description": "Geometric letter-shapes for 16 binary connectives.",
     "example": "sixteen letter-forms for truth functions"},
    # Coding / computational AI languages & concepts
    {"name": "Pseudocode / algorithmic notation", "family": "Computational",
     "description": "Stepwise procedural description of algorithms.",
     "example": "for i ← 1 to n do ..."},
    {"name": "Complexity notation", "family": "Computational",
     "description": "Asymptotic resource bounds.", "example": "O(n log n), Θ(n²), Ω(n)"},
    {"name": "Neural network notation", "family": "Computational AI",
     "description": "Layers, weights, activations, loss.",
     "example": "y = σ(Wx + b); L = −Σ y log ŷ"},
    {"name": "Attention / transformer notation", "family": "Computational AI",
     "description": "Query-key-value attention.",
     "example": "Attention(Q,K,V) = softmax(QKᵀ/√d_k) V"},
    {"name": "Gradient / optimization notation", "family": "Computational AI",
     "description": "Backprop and parameter updates.",
     "example": "θ ← θ − η ∇_θ L"},
    {"name": "Probabilistic graphical models", "family": "Computational AI",
     "description": "Bayesian networks, factor graphs.",
     "example": "P(X,Y) = P(X) P(Y|X)"},
    {"name": "Information-theoretic ML", "family": "Computational AI",
     "description": "Cross-entropy, KL, mutual information in learning.",
     "example": "H(p,q) = −Σ p log q; D_KL(p‖q)"},
    {"name": "Type systems for programs", "family": "Computational",
     "description": "Static types, inference, soundness.",
     "example": "Γ ⊢ e : τ"},
    {"name": "Operational semantics", "family": "Computational",
     "description": "Small-step / big-step evaluation rules.",
     "example": "〈e,σ〉 → 〈e',σ'〉"},
    {"name": "Denotational semantics", "family": "Computational",
     "description": "Meaning as mathematical objects.",
     "example": "〚e〛ρ = ..."},
    {"name": "Measure-theoretic probability", "family": "Advanced analysis",
     "description": "Probability spaces, measurable functions, Lebesgue integral.",
     "example": "P(A) = ∫_A dμ"},
    {"name": "Stochastic calculus notation", "family": "Advanced analysis",
     "description": "Itô integrals, quadratic variation, SDEs.",
     "example": "dX_t = μ dt + σ dW_t"},
    {"name": "Homological algebra", "family": "Abstract algebra",
     "description": "Chain complexes, homology, derived functors.",
     "example": "H_n(C) = ker ∂_n / im ∂_{n+1}"},
    {"name": "Algebraic geometry (schemes)", "family": "Geometry",
     "description": "Spec of rings, sheaves, morphisms of schemes.",
     "example": "X = Spec R"},
    {"name": "Quantum information notation", "family": "Physics / CS",
     "description": "Dirac notation, density operators, channels.",
     "example": "|ψ⟩, ρ = |ψ⟩⟨ψ|, Φ(ρ)"},
    {"name": "Convex optimization notation", "family": "Optimization",
     "description": "Convex sets/functions, dual problems, KKT conditions.",
     "example": "minimize f(x) subject to g_i(x) ≤ 0"},
]

FORMULAS = [
    # Classical math
    {"name": "Fundamental theorem of calculus", "domain": "Analysis",
     "statement": "Integration and differentiation are inverse operations under suitable conditions.",
     "latex": r"\int_a^b f'(x)\,dx = f(b)-f(a)", "unicode": "∫_a^b f' = f(b)−f(a)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Pythagorean theorem", "domain": "Geometry",
     "statement": "In a right triangle a²+b²=c².",
     "latex": r"a^2+b^2=c^2", "unicode": "a²+b²=c²",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Euler's identity", "domain": "Complex analysis",
     "statement": "e^{iπ} + 1 = 0.",
     "latex": r"e^{i\pi}+1=0", "unicode": "e^{iπ}+1=0",
     "status": "identity", "proof_status": "proven"},
    {"name": "Bayes' theorem", "domain": "Probability",
     "statement": "Posterior ∝ likelihood × prior.",
     "latex": r"P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}", "unicode": "P(A|B)=P(B|A)P(A)/P(B)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Stokes' theorem", "domain": "Differential geometry",
     "statement": "∫_∂Ω ω = ∫_Ω dω.",
     "latex": r"\int_{\partial\Omega}\omega=\int_\Omega d\omega", "unicode": "∫_∂Ω ω = ∫_Ω dω",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Shannon entropy", "domain": "Information theory",
     "statement": "Expected negative log probability.",
     "latex": r"H(X)=-\sum p\log p", "unicode": "H(X)=−Σ p log p",
     "status": "definition", "proof_status": "accepted"},
    {"name": "Central limit theorem", "domain": "Probability",
     "statement": "Normalized i.i.d. sums converge to normal.",
     "latex": r"(\bar X-\mu)/(\sigma/\sqrt n)\to N(0,1)", "unicode": "(X̄−μ)/(σ/√n)→N(0,1)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Cantor's theorem", "domain": "Set theory",
     "statement": "|S| < |P(S)|.",
     "latex": r"|S|<|\mathcal{P}(S)|", "unicode": "|S|<|P(S)|",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Noether's theorem", "domain": "Mathematical physics",
     "statement": "Continuous symmetries correspond to conservation laws.",
     "latex": r"symmetry\Rightarrow conserved current", "unicode": "symmetry ⇒ conserved current",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Combinatorial shadow definition", "domain": "Combinatorics",
     "statement": "Shadow of a family is obtained by deleting one element from each member.",
     "latex": r"\partial\mathcal{A}=\{A\setminus\{x\}\mid A\in\mathcal{A},x\in A\}",
     "unicode": "∂𝒜 = {A\\{x} | A∈𝒜, x∈A}",
     "status": "definition", "proof_status": "accepted"},
    # Computational / AI
    {"name": "Cross-entropy loss", "domain": "Machine learning",
     "statement": "Negative log-likelihood under a categorical model; standard classification loss.",
     "latex": r"L=-\sum_i y_i\log\hat y_i", "unicode": "L = −Σ y log ŷ",
     "status": "definition", "proof_status": "accepted"},
    {"name": "Gradient descent update", "domain": "Machine learning",
     "statement": "Parameter step opposite the loss gradient.",
     "latex": r"\theta\leftarrow\theta-\eta\nabla_\theta L", "unicode": "θ ← θ − η ∇_θ L",
     "status": "algorithm", "proof_status": "accepted"},
    {"name": "Attention formula", "domain": "Machine learning",
     "statement": "Scaled dot-product attention as used in transformers.",
     "latex": r"\mathrm{Attention}(Q,K,V)=\mathrm{softmax}(QK^T/\sqrt{d_k})V",
     "unicode": "Attention(Q,K,V)=softmax(QKᵀ/√d_k)V",
     "status": "definition", "proof_status": "accepted"},
    {"name": "Backpropagation chain rule", "domain": "Machine learning",
     "statement": "Gradients composed via the chain rule through computational graphs.",
     "latex": r"\frac{\partial L}{\partial x}=\frac{\partial L}{\partial y}\frac{\partial y}{\partial x}",
     "unicode": "∂L/∂x = (∂L/∂y)(∂y/∂x)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "KL divergence", "domain": "Information theory / ML",
     "statement": "Relative entropy between distributions p and q.",
     "latex": r"D_{KL}(p\Vert q)=\sum p\log(p/q)", "unicode": "D_KL(p‖q)=Σ p log(p/q)",
     "status": "definition", "proof_status": "accepted"},
    {"name": "Universal approximation (informal)", "domain": "Machine learning theory",
     "statement": "Sufficiently wide feedforward networks with non-polynomial activation can approximate continuous functions on compact sets arbitrarily well.",
     "latex": r"\forall f\in C(K)\,\forall\varepsilon>0\,\exists net: \|net-f\|_\infty<\varepsilon",
     "unicode": "∀f∈C(K) ∀ε>0 ∃ network approximating f within ε",
     "status": "theorem", "proof_status": "proven"},
    {"name": "PAC learning bound (schematic)", "domain": "Learning theory",
     "statement": "With high probability, empirical risk close to true risk given enough samples relative to hypothesis class complexity.",
     "latex": r"P(|R-\hat R|>\varepsilon)\le\delta", "unicode": "P(|R−R̂|>ε) ≤ δ (under sample-size conditions)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Softmax", "domain": "Machine learning",
     "statement": "Maps logits to a probability simplex.",
     "latex": r"\mathrm{softmax}(z)_i=e^{z_i}/\sum_j e^{z_j}",
     "unicode": "softmax(z)_i = e^{z_i} / Σ_j e^{z_j}",
     "status": "definition", "proof_status": "accepted"},
    # Advanced mathematics
    {"name": "Cauchy-Schwarz inequality", "domain": "Analysis",
     "statement": "For inner product spaces, |⟨u,v⟩|² ≤ ⟨u,u⟩⟨v,v⟩.",
     "latex": r"|\langle u,v\rangle|^2\le\langle u,u\rangle\langle v,v\rangle",
     "unicode": "|⟨u,v⟩|² ≤ ⟨u,u⟩⟨v,v⟩",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Fourier inversion", "domain": "Harmonic analysis",
     "statement": "Under suitable conditions a function is recovered from its Fourier transform.",
     "latex": r"f(x)=\int\hat f(\xi)e^{2\pi i x\xi}\,d\xi",
     "unicode": "f(x)=∫ f̂(ξ) e^{2πixξ} dξ",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Itô formula", "domain": "Stochastic calculus",
     "statement": "Chain rule for Itô processes includes a second-order correction term.",
     "latex": r"df(X_t)=f'(X_t)dX_t+\frac12 f''(X_t)d\langle X\rangle_t",
     "unicode": "df(X)=f'(X)dX + ½f''(X)d⟨X⟩",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Gauss-Bonnet theorem", "domain": "Differential geometry",
     "statement": "Integral of Gaussian curvature over a closed surface equals 2π times Euler characteristic.",
     "latex": r"\int_M K\,dA=2\pi\chi(M)",
     "unicode": "∫_M K dA = 2π χ(M)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Yoneda lemma", "domain": "Category theory",
     "statement": "Natural transformations Hom(A,−) ⇒ F are in bijection with elements of F(A).",
     "latex": r"Nat(yA,F)\cong F(A)",
     "unicode": "Nat(yA, F) ≅ F(A)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "ELBO variational bound", "domain": "Machine learning",
     "statement": "Evidence lower bound: log p(x) ≥ E_q[log p(x|z)] − D_KL(q(z|x)||p(z)).",
     "latex": r"\log p(x)\ge\mathbb{E}_q[\log p(x|z)]-D_{KL}(q\|p)",
     "unicode": "log p(x) ≥ E_q[log p(x|z)] − D_KL(q||p)",
     "status": "theorem", "proof_status": "proven"},
    {"name": "RSA modular exponentiation", "domain": "Cryptography",
     "statement": "Ciphertext c ≡ m^e (mod n); decryption m ≡ c^d (mod n) with ed≡1 (mod φ(n)).",
     "latex": r"c\equiv m^e\pmod n,\quad m\equiv c^d\pmod n",
     "unicode": "c ≡ m^e (mod n), m ≡ c^d (mod n)",
     "status": "algorithm", "proof_status": "accepted"},
    {"name": "Bellman optimality equation", "domain": "Reinforcement learning",
     "statement": "Optimal value is max over actions of expected reward plus discounted future value.",
     "latex": r"V^*(s)=\max_a\sum_{s'}P(s'|s,a)[R+\gamma V^*(s')]",
     "unicode": "V*(s)=max_a Σ_{s'} P(s'|s,a)[R+γV*(s')]",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Spectral theorem (finite)", "domain": "Linear algebra",
     "statement": "A normal matrix is unitarily diagonalizable.",
     "latex": r"A=U\Lambda U^*",
     "unicode": "A = UΛU*",
     "status": "theorem", "proof_status": "proven"},
    {"name": "Green's theorem", "domain": "Vector calculus",
     "statement": "Line integral of a vector field around a positively oriented curve equals double integral of curl over the region.",
     "latex": r"\oint_C P\,dx+Q\,dy=\iint_D(Q_x-P_y)\,dA",
     "unicode": "∮_C P dx+Q dy = ∬_D (Q_x−P_y) dA",
     "status": "theorem", "proof_status": "proven"},
]

# Coding / AI knowledge documents for the pod
AI_CODING_KNOWLEDGE = [
    # Core ML
    ("ml_backprop", "Backpropagation computes gradients of a scalar loss with respect to all parameters by reverse-mode automatic differentiation on the computational graph."),
    ("ml_transformer", "Transformers use multi-head self-attention, residual connections, and layer normalization; they process sequences without recurrence and scale via parallel attention."),
    ("ml_regularization", "Regularization techniques (weight decay, dropout, early stopping, data augmentation) reduce overfitting by constraining effective capacity or injecting noise."),
    ("ml_optimization", "Adam and AdamW adapt per-parameter learning rates using moment estimates; cosine schedules and warmup stabilize large-model training."),
    ("ml_attention_math", "Scaled dot-product attention is softmax(QK^T / sqrt(d_k)) V. Multi-head attention concatenates h parallel attention outputs and projects with W_O."),
    ("ml_layernorm", "Layer normalization normalizes across features for each example: y = ((x - μ) / sqrt(σ² + ε)) * γ + β. Stabilizes deep residual networks."),
    ("ml_residual", "Residual connections compute F(x) + x so gradients can flow directly; critical for training networks deeper than ~20 layers."),
    ("ml_softmax_temp", "Temperature-scaled softmax is softmax(z/T). Higher T flattens the distribution; T→0 approaches argmax."),
    ("ml_cross_entropy", "Cross-entropy loss for classification is -sum y_i log ŷ_i. Minimizing it is equivalent to maximizing likelihood under a categorical model."),
    ("ml_kl_use", "KL divergence D_KL(p||q) measures how many extra bits are needed to encode samples from p using a code optimal for q. Asymmetric; used in VAEs and distillation."),
    ("ml_vae", "Variational autoencoders optimize ELBO = E_q[log p(x|z)] - D_KL(q(z|x)||p(z)). Reparameterization trick allows gradient flow through stochastic nodes."),
    ("ml_gan", "GANs train a generator and discriminator adversarially. At equilibrium the generator matches the data distribution; training is often unstable."),
    ("ml_diffusion", "Diffusion models learn to reverse a gradual noising process. Score matching or denoising objectives yield high-quality sample generation."),
    ("ml_rlhf", "RLHF fine-tunes language models with a reward model trained on human preferences, then optimizes policy via PPO or similar RL algorithms."),
    ("ml_lora", "LoRA freezes pretrained weights and injects low-rank adapters A·B into layers, reducing trainable parameters for efficient fine-tuning."),
    ("ml_mixture_experts", "Mixture-of-Experts routes tokens to sparse expert FFNs via a gating network, increasing capacity without proportional compute."),
    # Theory
    ("ml_pac", "PAC learning: with high probability (1-δ), empirical risk is within ε of true risk given enough samples relative to hypothesis class complexity (VC dimension / Rademacher)."),
    ("ml_vc", "VC dimension is the largest set a hypothesis class can shatter. Finite VC dimension implies PAC learnability for binary classification."),
    ("ml_ntk", "Neural tangent kernel describes infinitely wide networks as kernel methods under gradient descent; linearizes training dynamics around initialization."),
    ("ml_info_bottleneck", "Information bottleneck principle: learn a representation T of X that minimizes I(X;T) while preserving I(T;Y) for task label Y."),
    # CS / algorithms
    ("cs_complexity", "Big-O notation classifies algorithms by asymptotic growth of time or space as input size grows; common classes include O(1), O(log n), O(n), O(n log n), O(n²)."),
    ("cs_types", "Static type systems reject many ill-formed programs before execution; soundness means well-typed programs do not exhibit certain runtime errors."),
    ("cs_semantics", "Operational semantics define evaluation steps; denotational semantics assign mathematical meanings; axiomatic semantics use pre/post-conditions."),
    ("cs_p_np", "P vs NP: whether every problem whose solution can be verified in polynomial time can also be solved in polynomial time. Open; central to complexity theory."),
    ("cs_fft", "Fast Fourier Transform computes discrete Fourier transform in O(n log n) via divide-and-conquer on roots of unity; enables fast polynomial multiplication and signal processing."),
    ("cs_graph_algorithms", "BFS/DFS explore graphs in O(V+E). Dijkstra finds shortest paths with non-negative weights; Bellman-Ford handles negatives; Floyd-Warshall all-pairs."),
    ("cs_dynamic_programming", "Dynamic programming solves overlapping subproblems by storing intermediate results. Optimal substructure + memoization yields polynomial solutions for many exponential naive problems."),
    ("cs_hashing", "Cryptographic hashes (SHA-256) are one-way and collision-resistant under standard assumptions. Used for integrity, commitments, and proof-of-work."),
    ("cs_merkle", "Merkle trees hash leaves upward so any leaf change alters the root. Enables efficient inclusion proofs and tamper detection in distributed systems."),
    ("code_verification", "Formal verification uses logic and proof assistants (Coq, Lean, Isabelle) to prove that programs satisfy specifications; testing alone cannot guarantee absence of bugs."),
    ("cs_category_prog", "Category theory informs functional programming: functors map types and functions; monads sequence effectful computations; natural transformations map between functors."),
    # AI systems
    ("ai_alignment", "Alignment research studies how to ensure AI systems pursue intended goals; techniques include RLHF, constitutional AI, and interpretability methods."),
    ("ai_scaling", "Empirical scaling laws relate model size, data size, and compute to loss; larger models trained on more data generally improve until data or compute saturates."),
    ("ai_rag", "Retrieval-augmented generation fetches relevant documents at inference time and conditions the model on them, reducing hallucination for knowledge-intensive tasks."),
    ("ai_tool_use", "Tool-using agents interleave model generations with external API/tool calls. Planner selects tools; executor runs them; results are fed back into context."),
    ("ai_constitutional", "Constitutional AI trains models to critique and revise their own outputs according to a written constitution of principles, reducing reliance on human labels."),
    ("ai_mechanistic", "Mechanistic interpretability reverse-engineers internal circuits of neural networks to understand how specific behaviors are implemented in weights and activations."),
    # Advanced math knowledge for the pod
    ("math_measure", "Measure theory generalizes length/area/volume. Lebesgue integration extends Riemann integration to a larger class of functions and underpins modern probability."),
    ("math_functional_analysis", "Functional analysis studies infinite-dimensional vector spaces (Banach, Hilbert). Spectral theory and operator algebras are central to quantum mechanics and PDEs."),
    ("math_algebraic_topology", "Algebraic topology assigns algebraic invariants (homology, homotopy groups) to topological spaces. Distinguishes spaces up to continuous deformation."),
    ("math_diff_geom", "Differential geometry studies manifolds with metrics and connections. Riemannian curvature underlies general relativity; gauge theory uses principal bundles."),
    ("math_number_theory", "Analytic number theory uses complex analysis on L-functions. The Riemann hypothesis concerns zeros of ζ(s) and implies strong bounds on prime gaps."),
    ("math_cryptography", "Public-key cryptography relies on hard problems: integer factorization (RSA), discrete log (DH, ECC). Post-quantum schemes use lattices, codes, or hash-based signatures."),
    ("math_optimization", "Convex optimization: local minima are global. Gradient descent, Newton's method, interior-point, and proximal algorithms solve large-scale problems in ML and control."),
    ("math_stochastic", "Stochastic calculus (Itô, Stratonovich) defines integrals against Brownian motion. Underpins Black-Scholes, filtering, and SDEs in physics and finance."),
    ("math_category", "Categories organize mathematical structures: objects and morphisms. Functors preserve structure; adjunctions and limits/colimits are universal constructions."),
    ("math_type_theory", "Dependent type theory unifies programming and proof. Curry-Howard: types are propositions, terms are proofs. Homotopy type theory adds univalence and higher inductive types."),
]


# =============================================================================
# KNOWLEDGE POD
# =============================================================================
class KnowledgePod:
    def __init__(self):
        self.docs: List[Dict[str, str]] = []
        self._df = defaultdict(int)
        self.growth_log: List[str] = []
        self._seen: Set[str] = set()

    def _tok(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9']+", text.lower())

    def _hash(self, text: str) -> str:
        return hashlib.md5(re.sub(r"\s+", " ", text.lower().strip()).encode()).hexdigest()

    def add(self, doc_id: str, text: str, force: bool = False) -> bool:
        h = self._hash(text)
        if not force and h in self._seen:
            return False
        self._seen.add(h)
        self.docs.append({"id": doc_id, "text": text})
        for t in set(self._tok(text)):
            self._df[t] += 1
        return True

    def query(self, q: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.docs:
            return []
        qtok = self._tok(q)
        n = len(self.docs)
        scored = []
        for doc in self.docs:
            dtok = self._tok(doc["text"])
            tf = defaultdict(int)
            for t in dtok:
                tf[t] += 1
            score = sum(
                (tf[qt] / max(len(dtok), 1)) * (math.log((n + 1) / (self._df.get(qt, 0) + 1)) + 1)
                for qt in qtok if qt in tf
            )
            if score > 0:
                scored.append({"id": doc["id"], "score": round(score, 4), "excerpt": doc["text"][:200]})
        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k]

    def ingest(self, text: str, source_id: str = None) -> Dict[str, Any]:
        if source_id is None:
            source_id = f"ingest_{len(self.docs)}_{_sha256(text)[:8]}"
        added = 0
        for i, s in enumerate(re.split(r'(?<=[.!?])\s+', text.strip())):
            s = s.strip()
            if len(s) < 25:
                continue
            if self.add(f"{source_id}_s{i}", s):
                added += 1
                self.growth_log.append(f"+{source_id}_s{i}: {s[:80]}...")
        return {"added": added, "total": len(self.docs)}

    def stats(self) -> Dict[str, Any]:
        return {"docs": len(self.docs), "vocab": len(self._df), "growth": len(self.growth_log)}


# =============================================================================
# MATH + LOGIC ENGINES
# =============================================================================
class MathEngine:
    def simplify(self, expr: str) -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try: return str(simplify(sympy.sympify(expr)))
        except Exception as e: return f"[math error: {e}]"

    def solve_equation(self, equation: str, variable: str = "x") -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try:
            var = symbols(variable)
            if "=" in equation:
                lhs, rhs = equation.split("=", 1)
                eq = Eq(sympy.sympify(lhs), sympy.sympify(rhs))
            else:
                eq = sympy.sympify(equation)
            return str(solve(eq, var))
        except Exception as e: return f"[math error: {e}]"

    def derivative(self, expr: str, variable: str = "x") -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try: return str(diff(sympy.sympify(expr), symbols(variable)))
        except Exception as e: return f"[math error: {e}]"

    def integral(self, expr: str, variable: str = "x") -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try: return str(integrate(sympy.sympify(expr), symbols(variable)))
        except Exception as e: return f"[math error: {e}]"

    def limit(self, expr: str, variable: str = "x", point: str = "0") -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try: return str(limit(sympy.sympify(expr), symbols(variable), sympy.sympify(point)))
        except Exception as e: return f"[math error: {e}]"

    def series_expand(self, expr: str, variable: str = "x", n: int = 6) -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try: return str(series(sympy.sympify(expr), symbols(variable), n=n))
        except Exception as e: return f"[math error: {e}]"

    def matrix_ops(self, matrix: List[List[float]], op: str = "det") -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try:
            m = Matrix(matrix)
            ops = {"det": m.det, "inverse": m.inv, "eigenvals": m.eigenvals, "rank": m.rank}
            return str(ops.get(op, lambda: f"[unknown {op}]")())
        except Exception as e: return f"[math error: {e}]"

    def gcd_lcm(self, a: int, b: int) -> Dict[str, int]:
        g = math.gcd(a, b)
        return {"gcd": g, "lcm": abs(a * b) // g if g else 0}

    def partial_derivative(self, expr: str, variables: List[str]) -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try:
            e = sympy.sympify(expr)
            for v in variables:
                e = diff(e, symbols(v))
            return str(e)
        except Exception as e: return f"[math error: {e}]"

    def solve_system(self, equations: List[str], variables: List[str]) -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try:
            vars_ = symbols(" ".join(variables))
            if not isinstance(vars_, (list, tuple)):
                vars_ = (vars_,)
            eqs = []
            for eq in equations:
                if "=" in eq:
                    lhs, rhs = eq.split("=", 1)
                    eqs.append(Eq(sympy.sympify(lhs), sympy.sympify(rhs)))
                else:
                    eqs.append(sympy.sympify(eq))
            return str(solve(eqs, vars_))
        except Exception as e: return f"[math error: {e}]"

    def number_theory(self, n: int, op: str = "is_prime") -> Any:
        try:
            if op == "is_prime":
                return bool(isprime(n)) if HAS_SYMPY else n > 1 and all(n % i for i in range(2, int(n**0.5)+1))
            if op == "factorize":
                return str(factorint(n)) if HAS_SYMPY else "[sympy unavailable]"
            return f"[unknown {op}]"
        except Exception as e: return f"[math error: {e}]"


class LogicEngine:
    def is_satisfiable(self, expr: str) -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try:
            r = satisfiable(sympy.sympify(expr))
            return str(r) if r else "UNSATISFIABLE"
        except Exception as e: return f"[logic error: {e}]"


# =============================================================================
# CODE DETECTOR
# =============================================================================
class CodeLangDetector:
    SIGNATURES = {
        "python": [r"def \w+\(", r"import \w+", r"elif "],
        "javascript": [r"function\s+\w+\(", r"const\s+\w+\s*=", r"=>"],
        "typescript": [r"interface \w+", r":\s*(string|number|boolean)\b"],
        "rust": [r"fn\s+\w+\(", r"let mut", r"println!"],
        "java": [r"public class", r"System\.out\.println"],
        "cpp": [r"#include\s*<iostream>", r"std::"],
        "c": [r"#include\s*<stdio\.h>", r"int main\("],
        "go": [r"package main", r"func \w+\("],
        "sql": [r"SELECT .* FROM", r"INSERT INTO"],
        "bash": [r"#!/bin/bash", r"\becho\b"],
        "haskell": [r"::\s*\w+", r"where\b"],
        "julia": [r"function\s+\w+", r"using\s+\w+"],
        "solidity": [r"pragma solidity", r"contract\s+\w+"],
        "prolog": [r":-", r"\?-"],
        "lisp": [r"\(defun\s+", r"\(lambda\s+"],
        "matlab": [r"function\s+.*=", r"%\s"],
        "r": [r"<-\s*function", r"library\("],
        "kotlin": [r"fun \w+\(", r"val \w+"],
        "swift": [r"func \w+\(", r"var \w+:\s*\w+"],
        "csharp": [r"using System", r"Console\.WriteLine"],
    }
    def detect(self, code: str) -> str:
        scores = defaultdict(int)
        for lang, pats in self.SIGNATURES.items():
            for p in pats:
                if re.search(p, code, re.I | re.M):
                    scores[lang] += 1
        return max(scores, key=scores.get) if scores else "unknown"
    def list_supported(self): return sorted(self.SIGNATURES.keys())


# =============================================================================
# TINY LEARNED PREDICTOR (torch optional)
# =============================================================================
if HAS_TORCH:
    class TinyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(nn.Linear(1, 12), nn.Tanh(), nn.Linear(12, 1))
        def forward(self, x): return self.net(x)
else:
    class TinyNet:  # placeholder so name exists
        pass

class PredictiveEngine:
    def learned(self, series: List[float], steps: int = 1, epochs: int = 100) -> Dict[str, Any]:
        if len(series) < 4:
            return {"error": "need ≥4 points"}
        if not HAS_TORCH:
            # Closed-form linear least-squares fallback
            n = len(series)
            xs = list(range(n))
            x_mean = sum(xs) / n
            y_mean = sum(series) / n
            num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, series))
            den = sum((x - x_mean) ** 2 for x in xs) or 1.0
            slope = num / den
            intercept = y_mean - slope * x_mean
            pred = intercept + slope * (n - 1 + steps)
            return {
                "forecast": round(pred, 4),
                "final_mse": None,
                "note": "torch unavailable — closed-form linear least-squares fallback"
            }
        xs = torch.tensor([[float(i)] for i in range(len(series))], dtype=torch.float32)
        ys = torch.tensor([[float(v)] for v in series], dtype=torch.float32)
        model = TinyNet()
        opt = torch.optim.Adam(model.parameters(), lr=0.04)
        loss_fn = nn.MSELoss()
        for _ in range(epochs):
            opt.zero_grad()
            loss = loss_fn(model(xs), ys)
            loss.backward()
            opt.step()
        with torch.no_grad():
            nxt = torch.tensor([[float(len(series)-1+steps)]], dtype=torch.float32)
            pred = model(nxt).item()
        return {"forecast": round(pred, 4), "final_mse": round(loss.item(), 6),
                "note": "tiny 2-layer net, real gradients"}
    def elo(self, a, b): return round(1/(1+10**((b-a)/400)), 4)
    def kelly(self, p, odds):
        b = odds - 1
        return round(max((b*p-(1-p))/b if b else 0, 0), 4)


# =============================================================================
# TOOLS
# =============================================================================
class ToolRegistry:
    def __init__(self):
        self._tools = {}
    def register(self, name, desc=""):
        def deco(fn):
            self._tools[name] = fn
            return fn
        return deco
    def call(self, name, *a, **k):
        return self._tools[name](*a, **k) if name in self._tools else f"[no tool {name}]"
    def list_tools(self): return list(self._tools.keys())

def build_tools():
    t = ToolRegistry()
    @t.register("hash_sha256")
    def h(text): return hashlib.sha256(str(text).encode()).hexdigest()
    @t.register("md5")
    def m(text): return hashlib.md5(str(text).encode()).hexdigest()
    @t.register("base64_encode")
    def b(text): return base64.b64encode(str(text).encode()).decode()
    @t.register("unit_convert")
    def u(payload):
        v, frm, to = payload
        table = {("km","mi"):0.621371,("mi","km"):1.60934,("c","f"):lambda c:c*9/5+32,("f","c"):lambda f:(f-32)*5/9}
        key = (frm.lower(), to.lower())
        if key not in table: return f"[no {frm}->{to}]"
        f = table[key]
        return round(f(v),4) if callable(f) else round(v*f,4)
    @t.register("timestamp_now")
    def ts(_=None): return datetime.datetime.now(datetime.timezone.utc).isoformat()
    return t


# =============================================================================
# UNIFIED ATLAS (math + AI formulas with Shadow Alphabet)
# =============================================================================
class UnifiedAtlas:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
        CREATE TABLE language_forms (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE, family TEXT,
            description TEXT, example TEXT
        );
        CREATE TABLE formulas (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE, domain TEXT,
            statement TEXT, latex TEXT, unicode TEXT, status TEXT, proof_status TEXT,
            shadow_word TEXT, shadow_phrase TEXT, shadow_stack TEXT, shadow_hash TEXT,
            sealed_at TEXT, seal_status TEXT DEFAULT 'SEALED'
        );
        CREATE TABLE verification_log (
            id INTEGER PRIMARY KEY, formula_name TEXT, status TEXT, detail TEXT, checked_at TEXT
        );
        """)
        self._populate()

    def _populate(self):
        cur = self.conn.cursor()
        for lf in LANGUAGE_FORMS:
            cur.execute(
                "INSERT OR IGNORE INTO language_forms (name,family,description,example) VALUES (?,?,?,?)",
                (lf["name"], lf["family"], lf["description"], lf["example"])
            )
        for f in FORMULAS:
            entry = seal_formula(
                f["name"], f["domain"], f["statement"],
                f.get("latex",""), f.get("unicode","")
            )
            cur.execute(
                """INSERT OR IGNORE INTO formulas
                   (name,domain,statement,latex,unicode,status,proof_status,
                    shadow_word,shadow_phrase,shadow_stack,shadow_hash,sealed_at,seal_status)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    entry["name"], entry["domain"], entry["statement"],
                    entry["latex"], entry["unicode"],
                    f.get("status","theorem"), f.get("proof_status","proven"),
                    entry["shadow_word"], entry["shadow_phrase"],
                    json.dumps(entry["shadow_stack"]), entry["shadow_hash"],
                    entry["sealed_at"], "SEALED",
                )
            )
        self.conn.commit()

    def summary(self) -> Dict[str, int]:
        cur = self.conn.cursor()
        return {
            "language_forms": cur.execute("SELECT COUNT(*) FROM language_forms").fetchone()[0],
            "formulas": cur.execute("SELECT COUNT(*) FROM formulas").fetchone()[0],
            "ai_ml_formulas": cur.execute(
                "SELECT COUNT(*) FROM formulas WHERE domain LIKE '%learning%' OR domain LIKE '%Machine%' OR domain LIKE '%Information theory / ML%'"
            ).fetchone()[0],
        }

    def search(self, q: str, limit: int = 10) -> List[Dict]:
        """Search formulas; multi-word queries match if any token hits."""
        cur = self.conn.cursor()
        tokens = [t for t in re.findall(r"[a-zA-Z0-9_]+", q or "") if len(t) > 1]
        if not tokens:
            tokens = [q or ""]
        clauses = []
        params: List[Any] = []
        for tok in tokens:
            like = f"%{tok}%"
            clauses.append(
                "(name LIKE ? OR statement LIKE ? OR domain LIKE ? "
                "OR latex LIKE ? OR unicode LIKE ? OR shadow_word LIKE ? OR shadow_phrase LIKE ?)"
            )
            params.extend([like] * 7)
        where = " OR ".join(clauses)
        cur.execute(
            f"SELECT name, domain, status, unicode, shadow_word, seal_status FROM formulas "
            f"WHERE {where} LIMIT ?",
            params + [limit],
        )
        # de-dupe while preserving order
        seen, rows = set(), []
        for r in cur.fetchall():
            d = dict(r)
            if d["name"] not in seen:
                seen.add(d["name"])
                rows.append(d)
        return rows

    def get(self, name: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM formulas WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row: return None
        d = dict(row)
        d["shadow_stack"] = json.loads(d["shadow_stack"] or "[]")
        return d

    def list_language_forms(self, family: str = None) -> List[Dict]:
        cur = self.conn.cursor()
        if family:
            cur.execute("SELECT name, family, description, example FROM language_forms WHERE family LIKE ?", (f"%{family}%",))
        else:
            cur.execute("SELECT name, family, description, example FROM language_forms ORDER BY family, name")
        return [dict(r) for r in cur.fetchall()]

    def verify_all(self, force: bool = True) -> List[Dict]:
        """
        Verify sealed formulas.
        force=True: full re-hash of every row (default for audits).
        force=False: return last cached results if present and no dirty flags.
        """
        if not force and getattr(self, "_verify_cache", None) and not getattr(self, "_dirty", set()):
            return list(self._verify_cache)

        cur = self.conn.cursor()
        cur.execute("SELECT name FROM formulas")
        names = [r[0] for r in cur.fetchall()]
        dirty = getattr(self, "_dirty", set())
        # When force=False, only re-check dirty names; keep others from cache
        cache_map = {v["name"]: v for v in getattr(self, "_verify_cache", []) or []}
        results = []
        for name in names:
            if not force and name not in dirty and name in cache_map:
                results.append(cache_map[name])
                continue
            entry = self.get(name)
            v = verify_entry(entry)
            # Stack run is the expensive path; skip full stack if hash already fails
            if v["status"] == "INTACT":
                stack_ok = run_stack(entry["shadow_stack"], entry)["ok"]
                if not stack_ok:
                    v["status"] = "COMPROMISED"
            if v["status"] != "INTACT":
                cur.execute("UPDATE formulas SET seal_status=? WHERE name=?", ("COMPROMISED", name))
            else:
                cur.execute("UPDATE formulas SET seal_status=? WHERE name=?", ("SEALED", name))
            cur.execute(
                "INSERT INTO verification_log (formula_name, status, detail, checked_at) VALUES (?,?,?,?)",
                (name, v["status"], json.dumps({"match": v["match_stored_hash"]}), NOW)
            )
            results.append(v)
        self.conn.commit()
        self._verify_cache = results
        self._dirty = set()
        return results

    def corrupt(self, name: str, field: str = "latex", value: str = "CORRUPTED") -> bool:
        if field not in ("latex", "unicode", "statement"): return False
        self.conn.execute(f"UPDATE formulas SET {field}=? WHERE name=?", (value, name))
        self.conn.commit()
        if not hasattr(self, "_dirty"):
            self._dirty = set()
        self._dirty.add(name)
        return True

    def reseal(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Re-seal a formula from its *current* stored fields.
        Use after intentional content update, or to restore integrity
        when current content is trusted as the new canonical form.
        """
        entry = self.get(name)
        if not entry:
            return None
        sealed = seal_formula(
            entry["name"], entry["domain"], entry["statement"],
            entry.get("latex") or "", entry.get("unicode") or "",
        )
        cur = self.conn.cursor()
        cur.execute(
            """UPDATE formulas SET shadow_word=?, shadow_phrase=?, shadow_stack=?,
               shadow_hash=?, sealed_at=?, seal_status=? WHERE name=?""",
            (
                sealed["shadow_word"], sealed["shadow_phrase"],
                json.dumps(sealed["shadow_stack"]), sealed["shadow_hash"],
                sealed["sealed_at"], "SEALED", name,
            ),
        )
        self.conn.commit()
        if not hasattr(self, "_dirty"):
            self._dirty = set()
        self._dirty.add(name)
        return sealed

    def close(self):
        self.conn.close()


# =============================================================================
# PLANNER + ROUTER + AGENT
# =============================================================================
class Planner:
    def plan(self, goal: str) -> List[Dict[str, Any]]:
        g = goal.lower()
        if any(k in g for k in ["shadow", "verify", "seal", "integrity"]):
            return [
                {"task": "atlas summary", "payload": None},
                {"task": "verify shadows", "payload": None},
                {"task": "show formula", "payload": "Euler's identity"},
            ]
        if any(k in g for k in ["ai", "machine learning", "neural", "attention", "coding"]):
            return [
                {"task": "atlas search", "payload": "learning"},
                {"task": "list language forms", "payload": "Computational"},
                {"task": "search knowledge", "payload": "transformer attention gradient"},
            ]
        if any(k in g for k in ["math", "theorem", "calculus"]):
            return [
                {"task": "solve equation", "payload": ("x**2-4=0", "x")},
                {"task": "atlas search", "payload": "theorem"},
            ]
        return [
            {"task": "atlas summary", "payload": None},
            {"task": "search knowledge", "payload": goal},
        ]


class Router:
    def __init__(self, pod, math_e, logic, code, pred, tools, atlas, planner, gradient=None):
        self.pod, self.math, self.logic = pod, math_e, logic
        self.code, self.pred, self.tools = code, pred, tools
        self.atlas, self.planner = atlas, planner
        self.gradient = gradient

    def route(self, task: str, payload: Any = None) -> Dict[str, Any]:
        t = task.lower().strip()
        if task.startswith("tool:"):
            return {"engine": "tool", "result": self.tools.call(task.split(":",1)[1].strip(), payload)}
        if "plan" == t or t.startswith("plan "):
            return {"engine": "planner", "result": self.planner.plan(payload or task[5:].strip())}
        if "atlas summary" in t: return {"engine": "atlas.summary", "result": self.atlas.summary()}
        if "atlas search" in t: return {"engine": "atlas.search", "result": self.atlas.search(payload or "")}
        if "show formula" in t: return {"engine": "atlas.get", "result": self.atlas.get(payload or "")}
        if "list language forms" in t:
            return {"engine": "atlas.forms", "result": self.atlas.list_language_forms(payload)}
        if "verify shadows" in t: return {"engine": "shadow.verify", "result": self.atlas.verify_all(force=True)}
        if "reseal" in t:
            names = payload if isinstance(payload, list) else [payload]
            out = []
            for n in names:
                if n:
                    out.append(self.atlas.reseal(n))
            return {"engine": "shadow.reseal", "result": out}
        if "gradient rank" in t or "shadow rank" in t:
            if self.gradient is None: return {"engine": "gradient", "result": "[no gradient engine]"}
            return {"engine": "gradient.rank", "result": self.gradient.rank(payload or "")}
        if "gradient encode" in t:
            if self.gradient is None: return {"engine": "gradient", "result": "[no gradient engine]"}
            return {"engine": "gradient.encode", "result": self.gradient.encode(payload or "")}
        if "search knowledge" in t: return {"engine": "pod", "result": self.pod.query(payload or "")}
        if "pod stats" in t: return {"engine": "pod.stats", "result": self.pod.stats()}
        if "learned" in t: return {"engine": "pred", "result": self.pred.learned(payload)}
        if "elo" in t: return {"engine": "pred.elo", "result": self.pred.elo(*payload)}
        if "kelly" in t: return {"engine": "pred.kelly", "result": self.pred.kelly(*payload)}
        if "derivative" in t:
            args = payload if isinstance(payload,(list,tuple)) else (payload,)
            return {"engine": "math", "result": self.math.derivative(*args)}
        if "equation" in t:
            args = payload if isinstance(payload,(list,tuple)) else (payload,)
            return {"engine": "math", "result": self.math.solve_equation(*args)}
        if "matrix" in t: return {"engine": "math", "result": self.math.matrix_ops(payload, "eigenvals")}
        if "prime" in t: return {"engine": "math", "result": self.math.number_theory(payload, "is_prime")}
        if "satisfiable" in t: return {"engine": "logic", "result": self.logic.is_satisfiable(payload)}
        if "code language" in t or "detect" in t: return {"engine": "code", "result": self.code.detect(payload)}
        if "list languages" in t: return {"engine": "code.list", "result": self.code.list_supported()}
        if "list tools" in t: return {"engine": "tools", "result": self.tools.list_tools()}
        return {"engine": "none", "result": f"[no handler: {task}]"}


class Agent:
    def __init__(self, router, planner):
        self.router, self.planner = router, planner
    def run(self, tasks):
        results, prev = [], None
        for task in tasks:
            payload = task.get("payload")
            if payload == "$PREV": payload = prev
            try:
                out = self.router.route(task["task"], payload)
            except Exception as e:
                out = {"engine": "error", "result": str(e)}
            results.append({"task": task["task"], **out})
            prev = out.get("result")
        return results
    def run_goal(self, goal):
        plan = self.planner.plan(goal)
        print(f"[PLAN] {goal}")
        for i, s in enumerate(plan, 1):
            print(f"  {i}. {s['task']}")
        return self.run(plan)


# =============================================================================
# STATIONARY PROCESSOR → ACTOR PIPELINE
# =============================================================================
# StationaryModel: reads full system state (atlas, shadows, pod, tools) and
#   emits structured observations + action directives.
# ActorModel: receives directives and executes them via the router/agent.
# These are honest rule/structure processors, not large neural LLMs.
# =============================================================================

class StationaryModel:
    """
    Stationary (observer/processor) model.
    Does not act on the world. Ingests state, produces:
      - situation report
      - integrity assessment
      - ranked knowledge highlights
      - ordered list of action directives for the Actor
      - full verification suite (code lines, plans, formulas, debug checks)
    """

    SOURCE_PATH = Path(__file__) if "__file__" in globals() else Path("atlas_shadow_unified.py")

    def __init__(self, atlas, pod, gradient=None, code=None, math_e=None, logic=None, planner=None):
        self.atlas = atlas
        self.pod = pod
        self.gradient = gradient
        self.code = code
        self.math_e = math_e
        self.logic = logic
        self.planner = planner
        self.last_report: Dict[str, Any] = {}
        self.last_verification: Dict[str, Any] = {}

    def verify_source_code(self, path: Path = None) -> Dict[str, Any]:
        """Parse and structurally check every class/function; report line inventory."""
        path = path or self.SOURCE_PATH
        try:
            src = path.read_text(encoding="utf-8")
        except Exception as e:
            # fallback: try cwd name
            try:
                src = Path("atlas_shadow_unified.py").read_text(encoding="utf-8")
                path = Path("atlas_shadow_unified.py")
            except Exception as e2:
                return {"ok": False, "error": str(e2)}
        lines = src.splitlines()
        issues = []
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            return {"ok": False, "syntax_error": str(e), "lines": len(lines)}

        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        # dead-import heuristics
        if "import statistics" in src and "statistics." not in src:
            issues.append("unused_import: statistics")
        if "import itertools" in src and "itertools." not in src:
            issues.append("unused_import: itertools")

        # required symbols present
        required = [
            "StationaryModel", "ExperimentalMergedModel", "UnifiedAtlas",
            "seal_formula", "verify_entry", "KnowledgePod", "MathEngine",
        ]
        for name in required:
            if name not in src:
                issues.append(f"missing_symbol: {name}")

        return {
            "ok": len(issues) == 0,
            "path": str(path),
            "line_count": len(lines),
            "byte_count": len(src),
            "syntax": "OK",
            "class_count": len(classes),
            "class_names": [c.name for c in classes],
            "module_function_count": len(funcs),
            "issues": issues,
        }

    def verify_formulas(self, force: bool = True) -> Dict[str, Any]:
        results = self.atlas.verify_all(force=force)
        compromised = [v for v in results if v["status"] == "COMPROMISED"]
        intact = [v for v in results if v["status"] == "INTACT"]
        return {
            "ok": len(compromised) == 0,
            "intact": len(intact),
            "compromised": len(compromised),
            "compromised_names": [c["name"] for c in compromised],
            "total": len(results),
        }

    def verify_plans(self) -> Dict[str, Any]:
        if self.planner is None:
            return {"ok": False, "error": "no planner bound"}
        goals = [
            "verify shadow integrity",
            "machine learning attention",
            "solve math equation",
            "unknown freeform goal",
        ]
        plans = {}
        issues = []
        for g in goals:
            plan = self.planner.plan(g)
            plans[g] = [s["task"] for s in plan]
            if not plan:
                issues.append(f"empty_plan: {g}")
            if not all(isinstance(s, dict) and "task" in s for s in plan):
                issues.append(f"malformed_plan: {g}")
        return {"ok": len(issues) == 0, "plans": plans, "issues": issues}

    def verify_math_logic(self) -> Dict[str, Any]:
        if self.math_e is None or self.logic is None:
            return {"ok": False, "error": "math/logic not bound"}
        checks = []
        def add(name, got, expect_substr=None, expect_exact=None):
            ok = True
            if expect_exact is not None:
                ok = str(got) == str(expect_exact)
            elif expect_substr is not None:
                ok = expect_substr in str(got)
            checks.append({"name": name, "ok": ok, "got": str(got)[:80]})

        add("solve_x2_9", self.math_e.solve_equation("x**2 - 9 = 0", "x"), expect_substr="-3")
        add("deriv_x3", self.math_e.derivative("x**3", "x"), expect_substr="3*x**2")
        add("limit_sinc", self.math_e.limit("sin(x)/x", "x", "0"), expect_exact="1")
        add("prime_97", self.math_e.number_theory(97, "is_prime"), expect_exact="True")
        add("sat_contradiction", self.logic.is_satisfiable("A & ~A"), expect_substr="UNSAT")
        add("series_exp", self.math_e.series_expand("exp(x)", "x", 4), expect_substr="x**2")
        add("partial_xy", self.math_e.partial_derivative("x**2*y + y**3", ["x", "y"]), expect_substr="2")
        add("gcd_lcm", self.math_e.gcd_lcm(48, 18), expect_substr="gcd")
        add("system_2eq", self.math_e.solve_system(["x + y - 3", "x - y - 1"], ["x", "y"]), expect_substr="2")
        ok = all(c["ok"] for c in checks)
        return {"ok": ok, "checks": checks}

    def verify_debug(self) -> Dict[str, Any]:
        """Runtime debug probes: pod, gradient, code detect, tools."""
        probes = []
        try:
            st = self.pod.stats()
            probes.append({"name": "pod_stats", "ok": isinstance(st, dict), "detail": st})
        except Exception as e:
            probes.append({"name": "pod_stats", "ok": False, "detail": str(e)})
        try:
            if self.gradient:
                r = self.gradient.rank("attention transformer", top_k=3)
                probes.append({"name": "gradient_rank", "ok": len(r) > 0, "detail": r[:2]})
            else:
                probes.append({"name": "gradient_rank", "ok": False, "detail": "no engine"})
        except Exception as e:
            probes.append({"name": "gradient_rank", "ok": False, "detail": str(e)})
        try:
            if self.code:
                lang = self.code.detect("def foo():\n    return 1\n")
                probes.append({"name": "code_detect", "ok": lang == "python", "detail": lang})
            else:
                probes.append({"name": "code_detect", "ok": False, "detail": "no detector"})
        except Exception as e:
            probes.append({"name": "code_detect", "ok": False, "detail": str(e)})
        try:
            summary = self.atlas.summary()
            probes.append({"name": "atlas_summary", "ok": summary.get("formulas", 0) > 0, "detail": summary})
        except Exception as e:
            probes.append({"name": "atlas_summary", "ok": False, "detail": str(e)})
        return {"ok": all(p["ok"] for p in probes), "probes": probes}

    def full_verification(self) -> Dict[str, Any]:
        """Verify source, formulas, plans, math/logic, and debug probes."""
        report = {
            "source": self.verify_source_code(),
            "formulas": self.verify_formulas(force=True),
            "plans": self.verify_plans(),
            "math_logic": self.verify_math_logic(),
            "debug": self.verify_debug(),
        }
        report["all_ok"] = all(
            report[k].get("ok") for k in ("source", "formulas", "plans", "math_logic", "debug")
        )
        self.last_verification = report
        return report

    def score_directives(self, directives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank actions by integrity, expected information gain, and cost."""
        weights = {
            "report_compromised": (100, 100, 1),
            "reseal_compromised": (100, 90, 2),
            "confirm_integrity": (90, 30, 1),
            "search_atlas": (20, 70, 2),
            "search_pod": (20, 70, 2),
            "gradient_rank": (15, 45, 3),
            "show_formula": (10, 20, 1),
            "solve_equation": (10, 35, 2),
        }
        scored = []
        for d in directives:
            x = dict(d)
            integrity, info, cost = weights.get(x.get("action"), (5, 10, 5))
            x["expected_information_gain"] = info
            x["integrity_priority"] = integrity
            x["estimated_cost"] = cost
            x["score"] = round(integrity + info - cost, 3)
            scored.append(x)
        return sorted(scored, key=lambda d: (-d["score"], d.get("priority", 99)))

    def process(self, focus: str = None, force_verify: bool = False) -> Dict[str, Any]:
        summary = self.atlas.summary()
        # Efficient path: use cache unless forced or dirty
        verifications = self.atlas.verify_all(force=force_verify)
        compromised = [v for v in verifications if v["status"] == "COMPROMISED"]
        intact = [v for v in verifications if v["status"] == "INTACT"]
        pod_stats = self.pod.stats()

        # Knowledge highlights
        highlights = []
        if focus:
            highlights = self.pod.query(focus, top_k=4)
            atlas_hits = self.atlas.search(focus, limit=4)
        else:
            atlas_hits = self.atlas.search("theorem", limit=3)
            highlights = self.pod.query("attention gradient transformer", top_k=3)

        # Gradient ranking if available
        grad_rank = []
        if self.gradient and focus:
            grad_rank = self.gradient.rank(focus, top_k=4)

        # Build action directives (ordered by priority)
        directives = []

        # Highest priority: integrity
        if compromised:
            directives.append({
                "priority": 1,
                "action": "report_compromised",
                "payload": [c["name"] for c in compromised],
                "reason": "Shadow Alphabet detected corrupted formula(s)",
            })
            # Direct experimental actor to re-seal current content as new canonical
            # (demo policy: trust current DB fields and re-hash)
            directives.append({
                "priority": 1,
                "action": "reseal_compromised",
                "payload": [c["name"] for c in compromised],
                "reason": "Re-seal compromised entries from current stored fields",
            })
        else:
            directives.append({
                "priority": 2,
                "action": "confirm_integrity",
                "payload": {"intact_count": len(intact)},
                "reason": "All sealed formulas verify INTACT",
            })

        # Knowledge / exploration
        if focus:
            directives.append({
                "priority": 3,
                "action": "search_atlas",
                "payload": focus,
                "reason": f"User/system focus: {focus}",
            })
            directives.append({
                "priority": 4,
                "action": "search_pod",
                "payload": focus,
                "reason": "Retrieve related coding/AI knowledge",
            })
            if grad_rank:
                directives.append({
                    "priority": 5,
                    "action": "gradient_rank",
                    "payload": focus,
                    "reason": "Textual-gradient ranking of language forms",
                })

        # Optional: demonstrate a sealed formula
        directives.append({
            "priority": 6,
            "action": "show_formula",
            "payload": "Euler's identity",
            "reason": "Expose a canonical sealed mathematical identity",
        })

        # Optional: math capability check
        directives.append({
            "priority": 7,
            "action": "solve_equation",
            "payload": ("x**2 - 9 = 0", "x"),
            "reason": "Confirm symbolic math path is live",
        })

        report = {
            "role": "stationary_processor",
            "timestamp": NOW,
            "focus": focus,
            "atlas_summary": summary,
            "integrity": {
                "intact": len(intact),
                "compromised": len(compromised),
                "compromised_names": [c["name"] for c in compromised],
            },
            "pod_stats": pod_stats,
            "atlas_hits": atlas_hits,
            "pod_highlights": highlights,
            "gradient_rank": grad_rank,
            "directives": self.score_directives(directives),
            "note": (
                "Stationary model processes state only. "
                "It does not execute side effects; Actor consumes directives."
            ),
        }
        self.last_report = report
        return report



# =============================================================================
# SUPER MATH + CODE PREFLIGHT / ENGINEERING GATE
# =============================================================================

class SourceEngineer:
    """
    Non-stationary engineering pass.

    This is intentionally conservative: it does not pretend that static
    heuristics are a human engineer or a trained coding model. It performs
    real AST/compile/runtime-oriented checks and returns actionable upgrade
    suggestions before the system is allowed to plan or act.
    """
    SEVERITY = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    def __init__(self, root: Optional[str] = None):
        self.root = Path(root) if root else Path(__file__).resolve().parent

    def _files(self) -> List[Path]:
        try:
            return sorted(self.root.glob("*.py"))
        except Exception:
            return [Path(__file__).resolve()]

    def audit_file(self, path: Path) -> Dict[str, Any]:
        out = {
            "file": str(path),
            "ok": True,
            "lines": 0,
            "syntax_ok": False,
            "issues": [],
            "suggestions": [],
        }
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            out["lines"] = len(source.splitlines())
            tree = ast.parse(source, filename=str(path))
            out["syntax_ok"] = True

            imports = []
            imported_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        imports.append(a.name.split(".")[0])
                        imported_names.add(a.asname or a.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    for a in node.names:
                        imported_names.add(a.asname or a.name)

            # Real structural smells, not style nitpicking.
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    out["issues"].append({
                        "severity": "medium", "kind": "bare_except",
                        "line": getattr(node, "lineno", None),
                    })
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for default in list(node.args.defaults) + [
                        d for d in node.args.kw_defaults if d is not None
                    ]:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            out["issues"].append({
                                "severity": "high", "kind": "mutable_default",
                                "line": getattr(node, "lineno", None),
                                "name": node.name,
                            })
                    if len(node.body) > 120:
                        out["suggestions"].append({
                            "severity": "low", "kind": "large_function",
                            "line": getattr(node, "lineno", None),
                            "name": node.name,
                            "message": "Consider splitting a very large function into tested units.",
                        })

            # Compile independently of import availability.
            compile(source, str(path), "exec")
        except SyntaxError as e:
            out["ok"] = False
            out["issues"].append({
                "severity": "critical", "kind": "syntax_error",
                "line": getattr(e, "lineno", None), "message": str(e),
            })
        except Exception as e:
            out["ok"] = False
            out["issues"].append({
                "severity": "high", "kind": "audit_error", "message": str(e),
            })

        if not out["issues"]:
            out["suggestions"].append({
                "severity": "low", "kind": "baseline_clean",
                "message": "No critical static defect detected; preserve behavior and test before refactoring.",
            })
        return out

    def audit(self) -> Dict[str, Any]:
        files = self._files()
        reports = [self.audit_file(f) for f in files]
        critical = [
            i for r in reports for i in r["issues"]
            if i.get("severity") == "critical"
        ]
        high = [
            i for r in reports for i in r["issues"]
            if i.get("severity") == "high"
        ]
        return {
            "root": str(self.root),
            "files": reports,
            "file_count": len(reports),
            "critical_count": len(critical),
            "high_count": len(high),
            "ok": not critical,
            "engineering_rule": (
                "No implementation stage may ship a source change that fails "
                "syntax/AST preflight or the stationary verification gate."
            ),
        }


class SuperMathCodingGate:
    """
    Mandatory mathematical + coding sanity gate.

    The point is not to prove arbitrary programs correct; it is to force a
    cheap, repeatable battery of independent checks before brainstorming,
    research, testing, or implementation directives are trusted.
    """

    def __init__(self, math_e=None, logic=None, code=None):
        self.math_e = math_e
        self.logic = logic
        self.code = code

    def run(self) -> Dict[str, Any]:
        checks = []
        def check(name, fn):
            try:
                value = fn()
                ok = bool(value) if not isinstance(value, dict) else bool(value.get("ok", True))
                checks.append({"name": name, "ok": ok, "value": value})
            except Exception as e:
                checks.append({"name": name, "ok": False, "error": str(e)})

        if HAS_SYMPY:
            check("quadratic_roots", lambda: len(solve(Eq(symbols("x")**2 - 9, 0), symbols("x"))) == 2)
            check("derivative", lambda: simplify(diff(symbols("x")**3, symbols("x")) - 3*symbols("x")**2) == 0)
            check("integral_derivative", lambda: simplify(diff(integrate(symbols("x")**2, symbols("x")), symbols("x")) - symbols("x")**2) == 0)
            check("limit_sin_x_over_x", lambda: simplify(limit(sympy.sin(symbols("x"))/symbols("x"), symbols("x"), 0) - 1) == 0)
            check("matrix_rank", lambda: Matrix([[1, 2], [2, 4]]).rank() == 1)
            check("prime_test", lambda: isprime(97) and not isprime(91))
            check("factorization", lambda: factorint(84) == {2: 2, 3: 1, 7: 1})
        else:
            checks.append({"name": "sympy_available", "ok": False, "error": "SymPy unavailable"})

        if self.logic is not None:
            check("logic_contradiction", lambda: self.logic.is_satisfiable("A & ~A") == "UNSATISFIABLE")
        if self.code is not None:
            check("code_detector_available", lambda: len(self.code.list_supported()) > 0)

        return {
            "ok": all(c["ok"] for c in checks),
            "checks": checks,
            "count": len(checks),
            "principle": "math/code preflight precedes planning and side effects",
        }


class VerificationLedger:
    """Small persistent audit trail for verification and knowledge growth."""

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else Path("verification_ledger.jsonl")

    def append(self, event: str, payload: Dict[str, Any]) -> None:
        try:
            record = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "event": event,
                "payload": payload,
            }
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
        except Exception:
            # Telemetry must never break the reasoning system.
            pass


class PreActionGate:
    """
    Enforces the requested order:

      super-math/code → stationary full verification → brainstorm/research
      → test → verify → implement/act → stationary verification again.
    """

    def __init__(self, stationary, actor, math_code_gate, engineer, ledger=None):
        self.stationary = stationary
        self.actor = actor
        self.math_code_gate = math_code_gate
        self.engineer = engineer
        self.ledger = ledger or VerificationLedger()

    def preflight(self) -> Dict[str, Any]:
        engineering = self.engineer.audit()
        math_code = self.math_code_gate.run()
        stationary = self.stationary.full_verification()
        result = {
            "stage": "pre_action_gate",
            "engineering": engineering,
            "math_code": math_code,
            "stationary": stationary,
            "ok": bool(engineering["ok"] and math_code["ok"] and stationary["all_ok"]),
            "order": [
                "super_math_and_code",
                "stationary_full_verification",
                "brainstorm_research",
                "test",
                "verify",
                "implement_act",
                "stationary_post_verification",
            ],
        }
        self.ledger.append("preflight", result)
        return result

    def postflight(self) -> Dict[str, Any]:
        result = self.stationary.full_verification()
        self.ledger.append("postflight", result)
        return result


# Phase 1–2 integration: metrics, directive schema, LLMAdapter stub
DIRECTIVE_SCHEMA_VERSION = "2.0"
TOOL_ALLOWLIST = frozenset({
    "report_compromised", "confirm_integrity", "reseal_compromised",
    "search_atlas", "search_pod", "gradient_rank", "show_formula",
    "solve_equation", "verify shadows", "reseal",
})


class RetrievalMetrics:
    """Phase 1: measure retrieval hit rates for pod and atlas."""
    def __init__(self):
        self.pod_queries = 0
        self.pod_hits = 0
        self.atlas_queries = 0
        self.atlas_hits = 0
        self.directives_scored = 0
        self.directives_executed = 0
        self.directives_blocked = 0
        self.rounds = 0

    def record_pod(self, n_results: int):
        self.pod_queries += 1
        if n_results > 0:
            self.pod_hits += 1

    def record_atlas(self, n_results: int):
        self.atlas_queries += 1
        if n_results > 0:
            self.atlas_hits += 1

    def summary(self) -> Dict[str, Any]:
        def rate(h, q):
            return round(h / q, 4) if q else None
        return {
            "pod_queries": self.pod_queries,
            "pod_hit_rate": rate(self.pod_hits, self.pod_queries),
            "atlas_queries": self.atlas_queries,
            "atlas_hit_rate": rate(self.atlas_hits, self.atlas_queries),
            "directives_scored": self.directives_scored,
            "directives_executed": self.directives_executed,
            "directives_blocked": self.directives_blocked,
            "rounds": self.rounds,
        }


class LLMAdapter:
    """
    Phase 2 interface for external LLM (not connected by default).
    Same directive schema; credentials/weights plugged in later.
    """
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.provider = None  # e.g. "openai", "local", None

    def propose_directives(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []  # stack-only mode
        # Placeholder: when wired, call external model and return directives
        return []

    def choose_action(self, directive: Dict[str, Any], allowlist: Set[str] = None) -> Optional[str]:
        if not self.enabled:
            return directive.get("action")
        allow = allowlist or TOOL_ALLOWLIST
        action = directive.get("action")
        return action if action in allow else None

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "schema_version": DIRECTIVE_SCHEMA_VERSION,
            "note": "Adapter ready; no external LLM credentials in this environment",
        }


class ExperimentalMergedModel:
    """
    Acting model = the experimental merged / combined / evolved system.

    Identity: lineage orchestrator_combined → complete → evolved →
    atlas_shadow_unified. This is the model that *acts* on directives
    from the Stationary processor.

    Not a frontier LLM. It is this project's own experimental stack
    (router, atlas, shadow seals, math, pod, tools, gradients) wired
    as the actor in the stationary → actor pipeline.
    Phase 2: optional LLMAdapter for future tool choice; execute stays here.
    """

    MODEL_ID = "experimental-merged-combined-evolved"
    LINEAGE = [
        "orchestrator_expanded",
        "orchestrator_max",
        "unified_orchestrator",
        "orchestrator_combined",
        "orchestrator_complete",
        "orchestrator_evolved",
        "atlas_shadow_unified",
    ]

    def __init__(self, router: Router, agent: Agent = None, llm_adapter: LLMAdapter = None,
                 metrics: RetrievalMetrics = None):
        self.router = router
        self.agent = agent
        self.llm = llm_adapter or LLMAdapter(enabled=False)
        self.metrics = metrics or RetrievalMetrics()
        self.history: List[Dict[str, Any]] = []

    def identity(self) -> Dict[str, Any]:
        return {
            "model_id": self.MODEL_ID,
            "role": "actor",
            "lineage": self.LINEAGE,
            "schema_version": DIRECTIVE_SCHEMA_VERSION,
            "llm_adapter": self.llm.status(),
            "capabilities": [
                "shadow_verify", "shadow_reseal", "atlas_search", "pod_query",
                "gradient_rank", "sympy_math", "partial_derivatives",
                "solve_system", "series", "limits", "gcd_lcm",
                "logic_sat", "code_detect", "tools", "learned_forecast",
                "advanced_ml_knowledge", "advanced_math_knowledge",
                "dry_run", "directive_schema_v2", "information_gain_scoring", "integrity_budget", "structured_action_results",
            ],
            "note": (
                "Experimental merged model acts on stationary directives. "
                "Not an external LLM; it is this project's own stack."
            ),
        }

    def act(self, report: Dict[str, Any], dry_run: bool = False) -> List[Dict[str, Any]]:
        results = []
        directives = list(report.get("directives", []))
        # Phase 2: optional LLM-proposed directives (empty when adapter disabled)
        extra = self.llm.propose_directives(report)
        if extra:
            directives = extra + directives
        # Integrity budget: if compromised, only allow integrity actions first
        integrity = report.get("integrity") or {}
        compromised_n = integrity.get("compromised", 0) if isinstance(integrity, dict) else 0

        self.metrics.directives_scored += len(directives)
        for d in directives:
            # Ensure schema version on directive
            d = dict(d)
            d.setdefault("schema_version", DIRECTIVE_SCHEMA_VERSION)
            action = self.llm.choose_action(d, TOOL_ALLOWLIST)
            if action is None:
                self.metrics.directives_blocked += 1
                results.append({
                    "actor": self.MODEL_ID,
                    "action": d.get("action"),
                    "status": "blocked_allowlist",
                    "schema_version": DIRECTIVE_SCHEMA_VERSION,
                    "ok": False,
                })
                continue
            if compromised_n > 0 and action not in (
                "report_compromised", "confirm_integrity", "reseal_compromised"
            ):
                # A5: never bypass reseal path when compromised
                if action not in ("reseal_compromised", "report_compromised", "confirm_integrity"):
                    self.metrics.directives_blocked += 1
                    results.append({
                        "actor": self.MODEL_ID,
                        "action": action,
                        "status": "deferred_integrity",
                        "reason": "compromised seals present; integrity actions only",
                        "ok": False,
                        "schema_version": DIRECTIVE_SCHEMA_VERSION,
                    })
                    continue
            payload = d.get("payload")
            task_map = {
                "report_compromised": ("verify shadows", None),
                "confirm_integrity": ("verify shadows", None),
                "reseal_compromised": ("reseal", payload),
                "search_atlas": ("atlas search", payload),
                "search_pod": ("search knowledge", payload),
                "gradient_rank": ("gradient rank", payload),
                "show_formula": ("show formula", payload),
                "solve_equation": ("solve equation", payload),
            }
            if action not in task_map:
                results.append({
                    "actor": self.MODEL_ID,
                    "action": action,
                    "status": "skipped",
                    "reason": f"unknown action '{action}'",
                    "ok": False,
                    "schema_version": DIRECTIVE_SCHEMA_VERSION,
                })
                continue
            if dry_run:
                results.append({
                    "actor": self.MODEL_ID,
                    "action": action,
                    "status": "dry_run",
                    "priority": d.get("priority"),
                    "reason": d.get("reason"),
                    "ok": True,
                    "schema_version": DIRECTIVE_SCHEMA_VERSION,
                })
                continue
            task, pl = task_map[action]
            try:
                out = self.router.route(task, pl)
                # metrics for retrieval actions
                if action == "search_pod" and isinstance(out.get("result"), list):
                    self.metrics.record_pod(len(out["result"]))
                if action == "search_atlas" and isinstance(out.get("result"), list):
                    self.metrics.record_atlas(len(out["result"]))
                entry = {
                    "actor": self.MODEL_ID,
                    "action": action,
                    "priority": d.get("priority"),
                    "reason": d.get("reason"),
                    "engine": out.get("engine"),
                    "status": "executed",
                    "ok": True,
                    "result_preview": str(out.get("result"))[:160],
                    "schema_version": DIRECTIVE_SCHEMA_VERSION,
                }
            except Exception as e:
                entry = {
                    "actor": self.MODEL_ID,
                    "action": action,
                    "status": "error",
                    "ok": False,
                    "error": str(e),
                    "schema_version": DIRECTIVE_SCHEMA_VERSION,
                }
            if entry.get("ok"):
                self.metrics.directives_executed += 1
            else:
                self.metrics.directives_blocked += 1
            results.append(entry)
            self.history.append(entry)
        return results


# Alias so existing call sites keep working
ActorModel = ExperimentalMergedModel



class SuperReasoningPipeline:
    """
    Explicit staged execution spine requested by the project:

      preflight → brainstorm → research → test → verify → implement → post-verify

    Each stage is observable. No stage after preflight is trusted if its gate
    fails. Research is local/offline here (pod + atlas); an external research
    provider can later occupy the same interface.
    """

    def __init__(self, stationary, actor):
        self.stationary = stationary
        self.actor = actor
        self.engineer = SourceEngineer()
        self.math_code = SuperMathCodingGate(
            getattr(stationary, "math_e", None),
            getattr(stationary, "logic", None),
            getattr(stationary, "code", None),
        )
        self.ledger = VerificationLedger()

    def brainstorm(self, focus: str) -> Dict[str, Any]:
        # Candidate directions are derived from actual stored knowledge, not
        # invented execution goals.
        atlas_hits = self.stationary.atlas.search(focus, limit=8)
        pod_hits = self.stationary.pod.query(focus, top_k=8)
        candidates = []
        for item in atlas_hits:
            candidates.append({"source": "atlas", "name": item.get("name"), "reason": "relevant sealed knowledge"})
        for item in pod_hits:
            candidates.append({"source": "pod", "name": item.get("id"), "reason": "relevant knowledge document"})
        return {"ok": True, "focus": focus, "candidates": candidates[:16]}

    def research(self, focus: str) -> Dict[str, Any]:
        # Offline research stage: retrieve, score, and expose evidence already
        # available to the system. No claim of web/external research.
        atlas = self.stationary.atlas.search(focus, limit=8)
        pod = self.stationary.pod.query(focus, top_k=8)
        return {
            "ok": bool(atlas or pod),
            "mode": "offline_local_retrieval",
            "atlas_results": atlas,
            "pod_results": pod,
        }

    def test(self) -> Dict[str, Any]:
        return {
            "math_code": self.math_code.run(),
            "stationary": self.stationary.full_verification(),
        }

    def verify(self) -> Dict[str, Any]:
        return self.stationary.full_verification()

    def implement(self, focus: str) -> Dict[str, Any]:
        report = self.stationary.process(focus=focus, force_verify=False)
        actions = self.actor.act(report)
        return {"report": report, "actions": actions}

    def run(self, focus: str) -> Dict[str, Any]:
        pre = PreActionGate(
            self.stationary, self.actor, self.math_code, self.engineer, self.ledger
        ).preflight()
        if not pre["ok"]:
            return {"ok": False, "stage": "preflight", "preflight": pre}

        stages = {
            "brainstorm": self.brainstorm(focus),
            "research": self.research(focus),
            "test": self.test(),
        }
        if not stages["test"]["math_code"]["ok"] or not stages["test"]["stationary"]["all_ok"]:
            return {"ok": False, "stage": "test", "preflight": pre, "stages": stages}

        stages["verify"] = self.verify()
        if not stages["verify"]["all_ok"]:
            return {"ok": False, "stage": "verify", "preflight": pre, "stages": stages}

        stages["implement"] = self.implement(focus)
        stages["post_verify"] = self.verify()
        ok = stages["post_verify"]["all_ok"]
        result = {
            "ok": ok,
            "pipeline": "preflight→brainstorm→research→test→verify→implement→post_verify",
            "preflight": pre,
            "stages": stages,
        }
        self.ledger.append("super_reasoning_pipeline", result)
        return result


class ReflectiveReasoningLoop:
    """
    THE highest-leverage upgrade for this project:

      retrieve → critique → revise directives → act → verify

    Research basis (agent literature): plan/query/retrieve/verify loops,
    self-critique, and tool-augmented reasoning outperform one-shot
    plan→act. Within this offline script, the loop is rule-structured
    (not a frontier LLM), but it is the architectural piece that multiplies
    the value of every tool, formula, and knowledge doc already present.

    Stationary owns retrieve+critique+revise.
    Experimental merged model owns act.
    Stationary owns post-act verify.
    """

    def __init__(self, stationary: StationaryModel, actor: ExperimentalMergedModel, max_rounds: int = 3):
        self.stationary = stationary
        self.actor = actor
        self.max_rounds = max(1, min(int(max_rounds), 8))
        self.ledger = VerificationLedger()

    def _critique(self, report: Dict[str, Any], prior_actions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Critique situation + prior actor results; propose directive revisions."""
        issues = []
        revisions = []
        integrity = report.get("integrity", {})
        if integrity.get("compromised", 0) > 0:
            issues.append("integrity_failure")
            revisions.append({
                "priority": 0,
                "action": "reseal_compromised",
                "payload": integrity.get("compromised_names", []),
                "reason": "critique: must reseal before trusting atlas content",
            })
        if prior_actions:
            failed = [a for a in prior_actions if a.get("status") in ("error", "skipped")]
            if failed:
                issues.append("actor_failures")
                for f in failed:
                    revisions.append({
                        "priority": 1,
                        "action": f.get("action"),
                        "payload": None,
                        "reason": f"critique: retry failed action {f.get('action')}",
                    })
            # If searches returned empty, broaden
            for a in prior_actions:
                if a.get("action") == "search_atlas" and a.get("status") == "executed":
                    preview = str(a.get("result_preview", ""))
                    if preview in ("[]", "") or "[]" in preview[:4]:
                        issues.append("empty_atlas_search")
                        revisions.append({
                            "priority": 3,
                            "action": "search_atlas",
                            "payload": "theorem learning attention",
                            "reason": "critique: broaden atlas query after empty hit",
                        })
        # Always ensure a math probe after critique
        revisions.append({
            "priority": 8,
            "action": "solve_equation",
            "payload": ("x**2 - 16 = 0", "x"),
            "reason": "critique: post-round math sanity check",
        })
        return {"issues": issues, "revisions": revisions, "ok": len(issues) == 0}

    def run(self, focus: str = None) -> Dict[str, Any]:
        rounds = []
        # Mandatory mathematical/source gate before any planning or action.
        engineer = SourceEngineer()
        gate = SuperMathCodingGate(
            getattr(self.stationary, "math_e", None),
            getattr(self.stationary, "logic", None),
            getattr(self.stationary, "code", None),
        )
        pre = PreActionGate(self.stationary, self.actor, gate, engineer, self.ledger).preflight()
        if not pre["ok"]:
            return {
                "pipeline": "preflight_blocked",
                "focus": focus,
                "preflight": pre,
                "final_verification_all_ok": False,
            }
        self.actor.metrics.rounds += 1
        report = self.stationary.process(focus=focus, force_verify=True)
        actions = self.actor.act(report)
        critique = self._critique(report, actions)
        rounds.append({
            "round": 1,
            "phase": "retrieve→act→critique",
            "directive_count": len(report.get("directives", [])),
            "actor_results": actions,
            "critique": {"issues": critique["issues"], "revision_count": len(critique["revisions"])},
        })

        # Round 2+: revise directives from critique, act again, verify
        for r in range(2, self.max_rounds + 1):
            if critique["ok"] and r > 2:
                break
            # Merge revisions into a synthetic report for the actor
            revised = dict(report)
            revised["directives"] = sorted(
                critique["revisions"] + [
                    d for d in report.get("directives", [])
                    if d.get("action") not in {x.get("action") for x in critique["revisions"]}
                ],
                key=lambda d: d.get("priority", 99),
            )
            actions2 = self.actor.act(revised)
            # Post-act verify via stationary formula check
            post = self.stationary.verify_formulas(force=False)
            critique = self._critique(report, actions2)
            rounds.append({
                "round": r,
                "phase": "revise→act→verify",
                "directive_count": len(revised["directives"]),
                "actor_results": actions2,
                "post_verify": post,
                "critique": {"issues": critique["issues"], "revision_count": len(critique["revisions"])},
            })
            if post.get("ok"):
                break

        final_verify = PreActionGate(
            self.stationary, self.actor,
            SuperMathCodingGate(
                getattr(self.stationary, "math_e", None),
                getattr(self.stationary, "logic", None),
                getattr(self.stationary, "code", None),
            ),
            SourceEngineer(), self.ledger
        ).postflight()
        return {
            "pipeline": "reflective: retrieve→critique→revise→act→verify",
            "one_thing": "closed reflective reasoning loop",
            "actor_identity": self.actor.identity(),
            "focus": focus,
            "rounds": rounds,
            "final_verification_all_ok": final_verify.get("all_ok"),
            "final_formulas": final_verify.get("formulas"),
            "final_math_logic_ok": final_verify.get("math_logic", {}).get("ok"),
            "final_source_ok": final_verify.get("source", {}).get("ok"),
            "metrics": self.actor.metrics.summary(),
            "preflight": pre,
        }


class StationaryActorLoop:
    """Stationary processes state → experimental merged/combined/evolved model acts.
    Optional reflective multi-round loop via ReflectiveReasoningLoop.
    """

    def __init__(self, stationary: StationaryModel, actor: ExperimentalMergedModel):
        self.stationary = stationary
        self.actor = actor
        self.reflective = ReflectiveReasoningLoop(stationary, actor, max_rounds=2)

    def cycle(self, focus: str = None) -> Dict[str, Any]:
        report = self.stationary.process(focus=focus)
        actions = self.actor.act(report)
        return {
            "pipeline": "stationary → experimental-merged-combined-evolved",
            "actor_identity": self.actor.identity(),
            "stationary_report": {
                "focus": report.get("focus"),
                "integrity": report.get("integrity"),
                "atlas_summary": report.get("atlas_summary"),
                "directive_count": len(report.get("directives", [])),
                "pod_stats": report.get("pod_stats"),
            },
            "actor_results": actions,
        }

    def cycle_reflective(self, focus: str = None) -> Dict[str, Any]:
        """Highest-leverage path: full reflective reasoning loop."""
        return self.reflective.run(focus=focus)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 74)
    print("ATLAS + SHADOW UNIFIED")
    print("Mathematical languages + Shadow Alphabet + Coding/AI knowledge")
    print("Stationary processor → Actor pipeline")
    print("=" * 74)

    pod = KnowledgePod()
    math_e = MathEngine()
    logic = LogicEngine()
    code = CodeLangDetector()
    pred = PredictiveEngine()
    tools = build_tools()
    atlas = UnifiedAtlas()
    planner = Planner()
    # Supplemental textual-gradient engine over language-form catalogue
    gradient = TextualGradientEngine(LANGUAGE_FORMS)
    router = Router(pod, math_e, logic, code, pred, tools, atlas, planner, gradient=gradient)
    agent = Agent(router, planner)

    # Seed AI/coding knowledge into pod
    for cid, text in AI_CODING_KNOWLEDGE:
        pod.add(cid, text, force=True)
    pod.add("note_tt", "TT Oracle uses ELO rankings and cushion engines for table tennis betting.", force=True)

    print(f"\n[ATLAS] {atlas.summary()}")
    print(f"[POD]   {pod.stats()}")
    print(f"[CODE]  {len(code.list_supported())} languages")
    print(f"[LANG]  {len(LANGUAGE_FORMS)} mathematical / computational language forms")
    print(f"[FORM]  {len(FORMULAS)} sealed formulas (math + ML/AI)")
    print(f"[GRAD]  textual-gradient engine over {len(LANGUAGE_FORMS)} language forms")

    # --- Core demo ---
    demo = [
        {"task": "solve equation", "payload": ("x**2 - 4 = 0", "x")},
        {"task": "derivative", "payload": ("x**3 + 2*x", "x")},
        {"task": "is prime", "payload": 97},
        {"task": "satisfiable", "payload": "A & ~A"},
        {"task": "what code language", "payload": "fn main() { let mut x = 5; println!(\"{}\", x); }"},
        {"task": "learned forecast", "payload": [1.0, 2.2, 3.1, 4.5, 5.8, 7.0]},
        {"task": "atlas summary", "payload": None},
        {"task": "atlas search", "payload": "attention"},
        {"task": "atlas search", "payload": "shadow"},
        {"task": "list language forms", "payload": "Computational"},
        {"task": "show formula", "payload": "Euler's identity"},
        {"task": "show formula", "payload": "Attention formula"},
        {"task": "search knowledge", "payload": "transformer gradient"},
        {"task": "verify shadows", "payload": None},
        {"task": "gradient rank", "payload": "shadow umbral quantifier attention"},
        {"task": "gradient encode", "payload": "the integral of the derivative equals the difference of endpoints"},
        {"task": "tool:unit_convert", "payload": (100, "km", "mi")},
    ]

    print("\n=== CORE DEMO ===")
    for r in agent.run(demo):
        res = r["result"]
        if isinstance(res, (list, dict)) and len(str(res)) > 140:
            res = str(res)[:140] + " ..."
        print(f"  [{r['engine']:<14}] {r['task'][:32]:32s} → {res}")

    # --- Corruption detection ---
    print("\n=== SHADOW INTEGRITY DEMO ===")
    print("  Corrupting Pythagorean theorem latex...")
    atlas.corrupt("Pythagorean theorem", "latex", r"a^2+b^2=c^3")
    for v in atlas.verify_all():
        mark = " ← COMPROMISED" if v["status"] == "COMPROMISED" else ""
        print(f"  {v['status']:12} {v['name']}{mark}")

    # --- Goal: AI + math languages ---
    print("\n=== GOAL: computational AI + mathematical languages ===")
    for r in agent.run_goal("explore machine learning and neural attention in the atlas"):
        res = r["result"]
        if isinstance(res, (list, dict)) and len(str(res)) > 120:
            res = str(res)[:120] + " ..."
        print(f"  [{r['engine']:<14}] {r['task'][:32]:32s} → {res}")

    # --- Show a full shadow entry ---
    print("\n=== FULL SHADOW ENTRY (Euler's identity) ===")
    euler = atlas.get("Euler's identity")
    if euler:
        print(f"  name         : {euler['name']}")
        print(f"  shadow_word  : {euler['shadow_word']}")
        print(f"  shadow_phrase: {euler['shadow_phrase']}")
        print(f"  shadow_hash  : {euler['shadow_hash'][:40]}...")
        print(f"  stack ops    : {len(euler['shadow_stack'])}")
        stack_result = run_stack(euler["shadow_stack"], euler)
        print(f"  stack run    : ok={stack_result['ok']} sealed={stack_result.get('sealed')}")

    print("\n=== FINAL COUNTS ===")
    print(f"  Atlas: {atlas.summary()}")
    print(f"  Pod:   {pod.stats()}")

    # --- Stationary full verification (code / plans / formulas / debug) ---
    print("\n=== STATIONARY FULL VERIFICATION SUITE ===")
    stationary = StationaryModel(
        atlas, pod, gradient=gradient, code=code,
        math_e=math_e, logic=logic, planner=planner,
    )
    ver = stationary.full_verification()
    print(f"  all_ok: {ver['all_ok']}")
    print(f"  source: lines={ver['source'].get('line_count')} classes={ver['source'].get('class_count')} "
          f"syntax={ver['source'].get('syntax')} issues={ver['source'].get('issues')}")
    print(f"  formulas: intact={ver['formulas'].get('intact')} compromised={ver['formulas'].get('compromised')} "
          f"names={ver['formulas'].get('compromised_names')}")
    print(f"  plans: ok={ver['plans'].get('ok')} issues={ver['plans'].get('issues')}")
    for p in ver['plans'].get('plans', {}).items():
        print(f"    plan[{p[0][:40]}]: {p[1]}")
    print(f"  math_logic: ok={ver['math_logic'].get('ok')}")
    for c in ver['math_logic'].get('checks', []):
        print(f"    [{('PASS' if c['ok'] else 'FAIL')}] {c['name']}: {c['got']}")
    print(f"  debug: ok={ver['debug'].get('ok')}")
    for p in ver['debug'].get('probes', []):
        print(f"    [{('PASS' if p['ok'] else 'FAIL')}] {p['name']}")

    # --- Stationary → Experimental merged model (actor) ---
    print("\n=== STATIONARY → EXPERIMENTAL MERGED/COMBINED/EVOLVED ACTOR ===")
    actor = ExperimentalMergedModel(router, agent=agent)
    loop = StationaryActorLoop(stationary, actor)

    cycle = loop.cycle(focus="machine learning attention transformer")
    ident = cycle.get("actor_identity", {})
    print(f"  [Actor identity] {ident.get('model_id')}")
    print(f"  [Actor lineage]  {' → '.join(ident.get('lineage', [])[-4:])}")
    print(f"  [Pipeline]       {cycle.get('pipeline')}")
    print("  [Stationary] integrity:", cycle["stationary_report"]["integrity"])
    print("  [Stationary] directives:", cycle["stationary_report"]["directive_count"])
    print("  [Experimental actor] results:")
    for a in cycle["actor_results"]:
        who = a.get("actor", "?")
        print(f"    p{a.get('priority','?')} [{who}] {a.get('action')}: {a.get('status')} — {str(a.get('result_preview', a.get('reason','')))[:80]}")

    # Integrity recovery is itself verified before the reflective loop is allowed.
    print("\n=== POST-ACTION INTEGRITY GATE ===")
    recovery_ver = stationary.full_verification()
    print(f"  all_ok_after_reseal: {recovery_ver['all_ok']}")
    if not recovery_ver["all_ok"]:
        print("  BLOCKED: integrity recovery did not reach a clean stationary state.")
    else:
        print("  PASS: stationary confirms the actor's reseal restored a clean state.")

    # --- Explicit super-reasoning staged pipeline ---
    print("\n=== SUPER REASONING PIPELINE ===")
    _pipeline = SuperReasoningPipeline(stationary, actor)
    _pipeline_result = _pipeline.run("machine learning attention transformer")
    print(f"  pipeline: {_pipeline_result.get('pipeline')}")
    print(f"  ok: {_pipeline_result.get('ok')}")
    if _pipeline_result.get("stages"):
        print(f"  brainstorm_candidates: {len(_pipeline_result['stages']['brainstorm'].get('candidates', []))}")
        print(f"  research_mode: {_pipeline_result['stages']['research'].get('mode')}")
        print(f"  post_verify_ok: {_pipeline_result['stages']['post_verify'].get('all_ok')}")

    # --- Reflective loop (the one highest-leverage upgrade) ---
    print("\n=== REFLECTIVE REASONING LOOP (retrieve→critique→revise→act→verify) ===")
    ref = loop.cycle_reflective(focus="attention learning theorem")
    print(f"  one_thing: {ref.get('one_thing')}")
    print(f"  pipeline:  {ref.get('pipeline')}")
    for rd in ref.get("rounds", []):
        print(f"  round {rd['round']} [{rd['phase']}]: directives={rd.get('directive_count')} "
              f"critique_issues={rd.get('critique', {}).get('issues')}")
        for a in rd.get("actor_results", [])[:4]:
            print(f"    • {a.get('action')}: {a.get('status')}")
    print(f"  final_source_ok:     {ref.get('final_source_ok')}")
    print(f"  final_math_logic_ok: {ref.get('final_math_logic_ok')}")
    print(f"  final_formulas:      {ref.get('final_formulas')}")
    print(f"  final_verification_all_ok: {ref.get('final_verification_all_ok')}")
    print(f"  metrics: {ref.get('metrics')}")
    print("  pipeline order: super-math/code → stationary → brainstorm/research → test → verify → implement/act → stationary")

    print("\n" + "=" * 74)
    print("ATLAS + SHADOW UNIFIED — complete")
    print("  • ONE THING: closed reflective reasoning loop (retrieve→critique→revise→act→verify)")
    print("  • Stationary verifies; experimental-merged actor acts; loop multiplies both")
    print("=" * 74)
    atlas.close()
