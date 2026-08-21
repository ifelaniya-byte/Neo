#!/usr/bin/env python3
"""
ORCHESTRATOR EVOLVED
====================
Evolution of orchestrator_combined.py + orchestrator_complete.py

REVIEW SUMMARY
--------------
Both predecessor scripts are syntactically valid and runnable.
Strengths retained:
  • Knowledge pod with novelty filter + reflection
  • Full sympy math surface
  • Reactive planner + agent loop
  • Tiny learned net + ensemble + training demo
  • Tool registry + named pipelines + bounded combination generator
  • Experimental thought loops
  • Honest translation stub + gap reports

What this evolution adds
------------------------
  1. Expanded Mathematical Language Atlas with explicit SHADOW / UMBRAL layer
  2. Documentation of what "shadow alphabet" can mean in mathematics
  3. Additional formal language forms (umbral calculus, type theory, rewrite systems,
     combinatorial shadow notation, dual/opposite systems)
  4. A lightweight "language review" engine that can list, search, and contrast
     mathematical languages (including shadow/umbral) without claiming to have
     trained a model on them
  5. Clear statement that true training across all mathematical languages is
     still blocked by data + compute

WHAT "SHADOW ALPHABET" REFERS TO (honest inventory)
---------------------------------------------------
No single standard "shadow alphabet" exists that covers all of mathematics.
Closest documented concepts:

  A. Umbral / shadow letters (Whitehead, Universal Algebra)
     Greek letters used as "shadows" that assign properties to regional
     (Roman) letters; never separated from the letters they modify.

  B. Shadow theory (Akiba and others) in formal semantics
     Quantifiers and compound terms denote "shadows" (individual-like objects)
     rather than higher-type Montagovian entities.

  C. Combinatorial shadows (set-family combinatorics)
     The shadow ∂𝒜 of a set family is obtained by removing one element
     from each set; upper shadow ∂⁺ by adding one element.

  D. Alternative logical alphabets (e.g. Zellweger Logic Alphabet)
     Geometric letter-shapes for the 16 binary connectives, designed so
     shape reflects logical symmetry.

  E. Other niche uses: shadow numbers, shadows in Coxeter groups,
     programming-language "shadow" objects, etc.

This script records these as first-class language forms in the atlas and
lets you query/contrast them. It does NOT claim to have trained a neural
model on every mathematical language — that remains outside single-file scope.
"""

from __future__ import annotations
import re
import math
import json
import hashlib
import base64
import datetime
import statistics
import itertools
import random
import sqlite3
import time
from collections import defaultdict
from typing import List, Dict, Callable, Any, Tuple, Optional, Set

import torch
import torch.nn as nn

try:
    import sympy
    from sympy import (
        symbols, simplify, solve, diff, integrate, Matrix, limit, series,
        factorial, binomial, Eq, sin, cos, exp, log, sqrt, pi
    )
    from sympy.logic.inference import satisfiable
    from sympy.ntheory import isprime, factorint
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
DB_PATH = ":memory:"

# =============================================================================
# 1. KNOWLEDGE POD
# =============================================================================
class KnowledgePod:
    def __init__(self):
        self.docs: List[Dict[str, str]] = []
        self._df = defaultdict(int)
        self.growth_log: List[str] = []
        self._seen: Set[str] = set()
        self.reflection_log: List[str] = []

    def _tok(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9']+", text.lower())

    def _hash(self, text: str) -> str:
        return hashlib.md5(re.sub(r"\s+", " ", text.lower().strip()).encode()).hexdigest()

    def add(self, doc_id: str, text: str, force: bool = False) -> bool:
        h = self._hash(text)
        if not force and h in self._seen:
            return False
        self._seen.add(h)
        self.docs.append({"id": doc_id, "text": text, "added_at": NOW})
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
            score = 0.0
            for qt in qtok:
                if qt in tf:
                    idf = math.log((n + 1) / (self._df.get(qt, 0) + 1)) + 1
                    score += (tf[qt] / max(len(dtok), 1)) * idf
            if score > 0:
                scored.append({"id": doc["id"], "score": round(score, 4), "excerpt": doc["text"][:220]})
        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k]

    def ingest(self, text: str, source_id: str = None) -> Dict[str, Any]:
        if source_id is None:
            source_id = f"ingest_{len(self.docs)}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        added, skipped = 0, 0
        for i, s in enumerate(sentences):
            s = s.strip()
            if len(s) < 30:
                continue
            did = f"{source_id}_s{i}"
            if self.add(did, s):
                added += 1
                self.growth_log.append(
                    f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] +{did}: {s[:90]}..."
                )
            else:
                skipped += 1
        return {"source": source_id, "added": added, "skipped_dupes": skipped, "total": len(self.docs)}

    def reflect(self) -> Dict[str, Any]:
        stats = {
            "total_docs": len(self.docs),
            "unique_hashes": len(self._seen),
            "vocab_size": len(self._df),
            "growth_events": len(self.growth_log),
        }
        reflection = (
            f"KnowledgePod reflection: {stats['total_docs']} unique documents, "
            f"vocab {stats['vocab_size']}, {stats['growth_events']} growth events. "
            f"Additive storage + retrieval — not adaptive trained understanding."
        )
        self.reflection_log.append(reflection)
        stats["reflection"] = reflection
        return stats


# =============================================================================
# 2. MATH ENGINE
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
            table = {
                "det": m.det, "inverse": m.inv, "transpose": lambda: m.T,
                "eigenvals": m.eigenvals, "rank": m.rank, "rref": m.rref
            }
            if op not in table: return f"[unknown op: {op}]"
            return str(table[op]())
        except Exception as e: return f"[math error: {e}]"

    def number_theory(self, n: int, op: str = "is_prime") -> Any:
        try:
            if op == "is_prime":
                return bool(isprime(n)) if HAS_SYMPY else n > 1 and all(n % i for i in range(2, int(n**0.5)+1))
            if op == "factorize":
                return str(factorint(n)) if HAS_SYMPY else "[sympy unavailable]"
            if op == "factorial":
                return str(factorial(n)) if HAS_SYMPY else str(math.factorial(n))
            return f"[unknown: {op}]"
        except Exception as e: return f"[math error: {e}]"

    def gcd_lcm(self, a: int, b: int) -> Dict[str, int]:
        g = math.gcd(a, b)
        return {"gcd": g, "lcm": abs(a*b)//g if g else 0}


# =============================================================================
# 3. LOGIC
# =============================================================================
class LogicEngine:
    def is_satisfiable(self, expr: str) -> str:
        if not HAS_SYMPY: return "[sympy unavailable]"
        try:
            r = satisfiable(sympy.sympify(expr))
            return str(r) if r else "UNSATISFIABLE"
        except Exception as e: return f"[logic error: {e}]"

    def truth_table(self, expr: str, variables: List[str]) -> List[Dict[str, Any]]:
        if not HAS_SYMPY: return [{"error": "sympy unavailable"}]
        try:
            syms = symbols(" ".join(variables))
            if not isinstance(syms, (list, tuple)): syms = (syms,)
            parsed = sympy.sympify(expr)
            rows = []
            n = len(variables)
            for i in range(2**n):
                bits = [(i >> j) & 1 for j in range(n)][::-1]
                subs = {syms[j]: bool(bits[j]) for j in range(n)}
                val = parsed.subs(subs)
                row = {variables[j]: bool(bits[j]) for j in range(n)}
                row["result"] = bool(val)
                rows.append(row)
            return rows
        except Exception as e: return [{"error": str(e)}]


# =============================================================================
# 4. CODE DETECTOR (kept lean)
# =============================================================================
class CodeLangDetector:
    SIGNATURES = {
        "python": [r"def \w+\(", r"import \w+", r"elif "],
        "javascript": [r"function\s+\w+\(", r"const\s+\w+\s*=", r"=>"],
        "typescript": [r"interface \w+", r":\s*(string|number|boolean)\b"],
        "rust": [r"fn\s+\w+\(", r"let mut", r"println!"],
        "java": [r"public class", r"System\.out\.println"],
        "csharp": [r"using System", r"Console\.WriteLine"],
        "cpp": [r"#include\s*<iostream>", r"std::"],
        "c": [r"#include\s*<stdio\.h>", r"int main\("],
        "go": [r"package main", r"func \w+\("],
        "ruby": [r"puts ", r"require '"],
        "php": [r"<\?php", r"\$\w+\s*="],
        "swift": [r"func \w+\(", r"var \w+:\s*\w+"],
        "kotlin": [r"fun \w+\(", r"val \w+"],
        "sql": [r"SELECT .* FROM", r"INSERT INTO"],
        "html": [r"<html", r"<!DOCTYPE"],
        "css": [r"\{[^}]*:\s*[^;]+;"],
        "bash": [r"#!/bin/bash", r"\becho\b"],
        "r": [r"<-\s*function", r"library\("],
        "scala": [r"object \w+", r"def \w+\("],
        "haskell": [r"::\s*\w+", r"where\b"],
        "julia": [r"function\s+\w+", r"using\s+\w+"],
        "solidity": [r"pragma solidity", r"contract\s+\w+"],
        "prolog": [r":-", r"\?-"],
        "assembly": [r"mov\s+\w+", r"section\s+\.text"],
        "fortran": [r"PROGRAM\s+\w+", r"END PROGRAM"],
        "matlab": [r"function\s+.*=", r"%\s"],
        "lisp": [r"\(defun\s+", r"\(lambda\s+"],
        "scheme": [r"\(define\s+", r"\(lambda\s+"],
        "elixir": [r"defmodule\s+", r"IO\.puts"],
        "clojure": [r"\(defn\s+", r"\(ns\s+"],
    }
    MISSING = [
        "APL / J / K", "Ada", "Agda / Coq / Lean", "D", "Elm", "Forth",
        "Idris", "Nix", "Objective-C", "PureScript", "Smalltalk", "Tcl",
        "V (Vlang)", "WebAssembly (wat)", "Wolfram / Mathematica", "most DSLs"
    ]

    def detect(self, code: str) -> str:
        scores = defaultdict(int)
        for lang, pats in self.SIGNATURES.items():
            for p in pats:
                if re.search(p, code, re.I | re.M):
                    scores[lang] += 1
        return max(scores, key=scores.get) if scores else "unknown"

    def list_supported(self): return sorted(self.SIGNATURES.keys())
    def list_missing(self): return self.MISSING


# =============================================================================
# 5. PREDICTORS + TINY TRAINING
# =============================================================================
class TinyNet(nn.Module):
    def __init__(self, hidden=16):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(1, hidden), nn.Tanh(), nn.Linear(hidden, 1))
    def forward(self, x): return self.net(x)


class PredictiveEngine:
    def trend(self, series: List[float], window: int = 3) -> Dict[str, float]:
        if len(series) < 2:
            return {"forecast": series[-1] if series else 0.0, "confidence": 0.0}
        window = min(window, len(series))
        recent = series[-window:]
        deltas = [recent[i+1]-recent[i] for i in range(len(recent)-1)]
        avg = statistics.mean(deltas) if deltas else 0.0
        var = statistics.pvariance(recent) if len(recent)>1 else 0.0
        return {"forecast": round(series[-1]+avg, 4), "confidence": round(1/(1+var), 4)}

    def linear(self, series: List[float], steps: int = 1) -> Dict[str, float]:
        n = len(series)
        if n < 2: return {"forecast": series[-1] if series else 0.0, "slope": 0.0}
        xs = list(range(n))
        xm, ym = statistics.mean(xs), statistics.mean(series)
        num = sum((xs[i]-xm)*(series[i]-ym) for i in range(n))
        den = sum((xs[i]-xm)**2 for i in range(n))
        slope = num/den if den else 0.0
        intercept = ym - slope*xm
        return {"forecast": round(intercept + slope*(n-1+steps), 4), "slope": round(slope, 4)}

    def learned(self, series: List[float], steps: int = 1, epochs: int = 120) -> Dict[str, Any]:
        if len(series) < 4: return {"error": "need ≥4 points"}
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
            learned = model(nxt).item()
        lin = self.linear(series, steps)
        ensemble = 0.55*learned + 0.45*lin["forecast"]
        return {
            "learned_forecast": round(learned, 4),
            "linear_forecast": lin["forecast"],
            "ensemble_forecast": round(ensemble, 4),
            "final_mse": round(loss.item(), 6),
            "note": "2-layer net + linear ensemble (real gradients)"
        }

    def elo(self, a: float, b: float) -> float:
        return round(1/(1+10**((b-a)/400)), 4)

    def kelly(self, p: float, decimal_odds: float) -> float:
        b = decimal_odds - 1
        f = (b*p - (1-p))/b if b else 0.0
        return round(max(f, 0.0), 4)


# =============================================================================
# 6. TRANSLATION STUB
# =============================================================================
class TranslationLayer:
    def translate(self, text: str, target: str) -> str:
        return (
            f"[translation offline → '{target}'] "
            "No API key / offline model present. Wire DeepL, Google, LibreTranslate, or deep-translator."
        )


# =============================================================================
# 7. TOOLS
# =============================================================================
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._desc: Dict[str, str] = {}

    def register(self, name: str, description: str = ""):
        def deco(fn):
            self._tools[name] = fn
            self._desc[name] = description or (fn.__doc__ or "")
            return fn
        return deco

    def call(self, name: str, *args, **kwargs):
        if name not in self._tools: return f"[tool '{name}' not registered]"
        return self._tools[name](*args, **kwargs)

    def list_tools(self):
        return [{"name": n, "description": self._desc[n]} for n in sorted(self._tools)]

    def named_pipelines(self):
        return {
            "hash_then_encode": ["hash_sha256", "base64_encode"],
            "full_fingerprint": ["md5", "hash_sha256", "base64_encode"],
            "normalize_text": ["lower", "reverse_text"],
            "timestamped_hash": ["timestamp_now", "hash_sha256"],
        }

    def run_pipeline(self, name: str, initial):
        pipes = self.named_pipelines()
        if name not in pipes:
            return {"error": f"unknown '{name}'", "available": list(pipes.keys())}
        current, trace = initial, []
        for step in pipes[name]:
            try:
                current = self.call(step, current)
                trace.append({"tool": step, "ok": True, "preview": str(current)[:70]})
            except Exception as e:
                trace.append({"tool": step, "ok": False, "error": str(e)})
                break
        return {"pipeline": name, "steps": pipes[name], "trace": trace, "final": current}


def build_tools() -> ToolRegistry:
    t = ToolRegistry()
    @t.register("unit_convert", "km/mi kg/lb m/ft C/F")
    def unit_convert(payload):
        value, frm, to = payload
        table = {
            ("km","mi"): 0.621371, ("mi","km"): 1.60934,
            ("kg","lb"): 2.20462, ("lb","kg"): 0.453592,
            ("m","ft"): 3.28084, ("ft","m"): 0.3048,
            ("c","f"): lambda c: c*9/5+32, ("f","c"): lambda f: (f-32)*5/9,
        }
        key = (frm.lower(), to.lower())
        if key not in table: return f"[no conversion {frm}->{to}]"
        f = table[key]
        return round(f(value), 4) if callable(f) else round(value*f, 4)

    @t.register("text_stats", "chars/words")
    def text_stats(text):
        words = str(text).split()
        return {"chars": len(str(text)), "words": len(words)}

    @t.register("hash_sha256", "SHA-256")
    def hash_sha256(text): return hashlib.sha256(str(text).encode()).hexdigest()

    @t.register("md5", "MD5")
    def md5(text): return hashlib.md5(str(text).encode()).hexdigest()

    @t.register("base64_encode", "Base64")
    def b64e(text): return base64.b64encode(str(text).encode()).decode()

    @t.register("timestamp_now", "UTC ISO")
    def ts(_=None): return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @t.register("lower", "Lowercase")
    def lo(text): return str(text).lower()

    @t.register("reverse_text", "Reverse")
    def rev(text): return str(text)[::-1]

    return t


# =============================================================================
# 8. EXPERIMENTAL THOUGHT
# =============================================================================
class ExperimentalThoughtLoop:
    def __init__(self, pod: KnowledgePod):
        self.pod = pod

    def seed(self):
        seeds = {
            "ley_lines": "Ley lines are hypothetical alignments of ancient sites; treated by mainstream science as cultural patterns or coincidence.",
            "gravity": "Gravity is spacetime curvature (GR) or a long-range attractive force (Newtonian).",
            "magnetism": "Magnetism from moving charges and particle moments; Maxwell + QED.",
            "information": "Shannon entropy quantifies information; Landauer links erasure to thermodynamics.",
            "geometry": "Differential geometry underpins GR and gauge theories.",
            "umbral": "Umbral/shadow letters (Whitehead): Greek letters that assign properties to regional Roman letters and are never separated from them.",
            "shadow_combinatorics": "The shadow ∂𝒜 of a set family is all sets obtained by deleting one element from a member of 𝒜.",
        }
        for cid, text in seeds.items():
            self.pod.add(cid, text, force=True)
        return {"seeded": list(seeds.keys())}

    def mix(self, concepts: List[str] = None) -> Dict[str, Any]:
        if concepts is None:
            concepts = ["ley lines", "gravity", "magnetism", "umbral", "geometry", "shadow"]
        retrieved = []
        for c in concepts:
            retrieved.extend(self.pod.query(c, top_k=2))
        seen, unique = set(), []
        for r in retrieved:
            if r["id"] not in seen:
                seen.add(r["id"]); unique.append(r)
        analogies = []
        for a, b in itertools.combinations(unique, 2):
            text = (
                f"Experimental analogy [{a['id']} ↔ {b['id']}]: structure in "
                f"'{a['excerpt'][:50]}...' treated as analogous to '{b['excerpt'][:50]}...'. "
                f"Speculative knowledge-play only."
            )
            analogies.append(text)
            self.pod.ingest(text, source_id=f"analogy_{a['id']}_{b['id']}")
        return {
            "concepts": concepts,
            "unique_retrieved": len(unique),
            "analogies_generated": len(analogies),
            "sample": analogies[0] if analogies else None,
            "note": "Analogy generation only — not trained scientific insight."
        }


# =============================================================================
# 9. PLANNER
# =============================================================================
class Planner:
    def plan(self, goal: str) -> List[Dict[str, Any]]:
        g = goal.lower()
        if any(k in g for k in ["shadow", "umbral", "mathematical language", "notation", "atlas"]):
            return [
                {"task": "atlas summary", "payload": None},
                {"task": "atlas search", "payload": "shadow"},
                {"task": "atlas search", "payload": "umbral"},
                {"task": "list language forms", "payload": None},
                {"task": "language review", "payload": "shadow"},
            ]
        if any(k in g for k in ["ley", "gravity", "magnetism", "experimental", "mix"]):
            return [
                {"task": "seed concepts", "payload": None},
                {"task": "mix concepts", "payload": ["ley lines","gravity","magnetism","umbral","geometry","shadow"]},
                {"task": "search knowledge", "payload": "experimental analogy"},
                {"task": "pod reflect", "payload": None},
            ]
        if any(k in g for k in ["predict", "forecast", "learn"]):
            return [{"task": "learned forecast", "payload": [1.0,2.2,3.1,4.5,5.8,7.0,8.3]}]
        if any(k in g for k in ["math", "equation"]):
            return [
                {"task": "solve equation", "payload": ("x**2-5*x+6=0", "x")},
                {"task": "atlas search", "payload": "theorem"},
            ]
        return [
            {"task": "search knowledge", "payload": goal},
            {"task": "pod reflect", "payload": None},
        ]

    def react(self, last: Any) -> Optional[Dict[str, Any]]:
        if isinstance(last, dict) and last.get("analogies_generated", 0) > 2:
            return {"task": "pod reflect", "payload": None}
        return None


# =============================================================================
# 10. EXPANDED MATH LANGUAGE ATLAS (includes shadow / umbral)
# =============================================================================
class MathLanguageAtlas:
    """
    Expanded atlas of mathematical languages / notation systems.
    Explicitly includes shadow/umbral and related formal systems.
    This is a catalogue + search engine, NOT a trained model on all of mathematics.
    """

    LANGUAGE_FORMS = [
        # Classical
        {"name": "Natural-language mathematics", "family": "Expository",
         "description": "Mathematics expressed in ordinary language.",
         "example": "For every real number x, x squared is nonnegative."},
        {"name": "Symbolic algebra", "family": "Algebraic",
         "description": "Variables, operators, equations in conventional algebraic notation.",
         "example": "a² + b² = c²"},
        {"name": "First-order logic", "family": "Formal logic",
         "description": "Quantified logic with ∀ ∃ ∧ ∨ ¬ →.",
         "example": "∀x ((Prime(x) ∧ x > 2) → Odd(x))"},
        {"name": "Set theory (ZFC)", "family": "Foundational",
         "description": "Mathematics via sets and membership.",
         "example": "{x ∈ ℝ | x² ≥ 0} = ℝ"},
        {"name": "Category theory", "family": "Abstract structural",
         "description": "Objects, morphisms, functors, natural transformations.",
         "example": "F ∘ G : C → E"},
        {"name": "Tensor / index notation", "family": "Physics / multilinear",
         "description": "Indexed tensors, Einstein summation.",
         "example": "R_μν − ½ R g_μν = 8πG T_μν"},
        {"name": "Differential-form notation", "family": "Geometry / calculus",
         "description": "Forms and exterior derivatives.",
         "example": "dω = 0"},
        {"name": "Matrix / linear-algebra notation", "family": "Algebraic / numerical",
         "description": "Vectors, matrices, eigenvalues.",
         "example": "Ax = b"},
        {"name": "Probability notation", "family": "Statistical",
         "description": "Random variables, distributions, conditionals.",
         "example": "P(A|B) = P(B|A)P(A)/P(B)"},
        {"name": "Calculus notation (Leibniz/Newton)", "family": "Analysis",
         "description": "Limits, derivatives, integrals.",
         "example": "∫_a^b f'(x) dx = f(b) − f(a)"},
        {"name": "Modal logic", "family": "Philosophical / formal logic",
         "description": "Necessity and possibility (□ ◇).",
         "example": "□P → ◇P"},
        {"name": "Lambda calculus", "family": "Computational",
         "description": "Abstraction and application of functions.",
         "example": "λf.λx.f (f x)"},
        {"name": "Type theory", "family": "Foundational / CS",
         "description": "Types, terms, judgments.",
         "example": "Γ ⊢ t : T"},
        {"name": "Homotopy type theory", "family": "Foundational",
         "description": "Types as spaces; identity types as paths.",
         "example": "Identity type Id_A(a,b) as path space"},
        {"name": "Rewrite systems", "family": "Computational",
         "description": "Term rewriting rules.",
         "example": "t → t'"},
        # Shadow / umbral layer (the request focus)
        {"name": "Umbral / shadow letters (Whitehead)", "family": "Shadow / umbral",
         "description": (
             "Greek letters used as 'shadows' or umbral letters that assign properties "
             "to regional (Roman) letters. Shadows are never written alone and are not "
             "separated from the letters they modify. From Whitehead's Universal Algebra."
         ),
         "example": "α as shadow of a; xa means regions x and a overlap (umbral reading)"},
        {"name": "Umbral calculus", "family": "Shadow / umbral",
         "description": (
             "Formal manipulation of sequences and polynomial operators using umbral "
             "notation (Blissard, Bell, Rota et al.). 'Shadows' of numbers or operators "
             "are treated as if they were ordinary algebraic quantities."
         ),
         "example": "a^n  (umbral) standing for a sequence a_n under suitable evaluation"},
        {"name": "Combinatorial shadow notation", "family": "Shadow / umbral",
         "description": (
             "In extremal set theory the shadow ∂𝒜 of a family 𝒜 is the family of all "
             "sets obtained by deleting one element from a member of 𝒜. Upper shadow ∂⁺ "
             "is obtained by adding one element. Notation: ∂𝒜, ∂⁺𝒜, ∂^k 𝒜."
         ),
         "example": "∂𝒜 = { A \\ {x} | A ∈ 𝒜, x ∈ A }"},
        {"name": "Shadow theory (formal semantics)", "family": "Shadow / umbral",
         "description": (
             "In some formal-semantic frameworks (e.g. Akiba), quantifiers and compound "
             "terms denote 'shadows' — individual-like objects of type e — rather than "
             "higher-type Montagovian denotations. Quantification is treated as denotation "
             "of shadows."
         ),
         "example": "'every man' denotes a shadow of type e"},
        {"name": "Logic Alphabet (Zellweger-style)", "family": "Alternative logical alphabet",
         "description": (
             "Geometric letter-shapes for the sixteen binary truth-functional connectives, "
             "designed so that visual form reflects logical symmetry group structure. "
             "An alternative to the conventional {∧,∨,¬,→,…} alphabet."
         ),
         "example": "Sixteen distinct letter-forms corresponding to the 16 binary connectives"},
        {"name": "Dual / opposite systems", "family": "Shadow / dual",
         "description": (
             "Many mathematical languages have dual or opposite presentations "
             "(e.g. category-theoretic dual, order-theoretic dual, projective dual). "
             "These can be viewed as 'shadow' presentations of the same structure."
         ),
         "example": "C^op (opposite category); dual vector space V*"},
    ]

    FORMULAS = [
        {"name": "Fundamental theorem of calculus", "domain": "Analysis",
         "statement": "Integration and differentiation are inverse operations under suitable conditions.",
         "unicode": "∫_a^b f' = f(b)−f(a)", "status": "theorem", "proof_status": "proven"},
        {"name": "Bayes' theorem", "domain": "Probability",
         "statement": "Posterior proportional to likelihood times prior.",
         "unicode": "P(A|B)=P(B|A)P(A)/P(B)", "status": "theorem", "proof_status": "proven"},
        {"name": "Pythagorean theorem", "domain": "Geometry",
         "statement": "In a right triangle a²+b²=c².",
         "unicode": "a²+b²=c²", "status": "theorem", "proof_status": "proven"},
        {"name": "Shannon entropy", "domain": "Information theory",
         "statement": "Expected negative log probability.",
         "unicode": "H(X)=−Σ p log p", "status": "definition", "proof_status": "accepted"},
        {"name": "Stokes' theorem", "domain": "Differential geometry",
         "statement": "∫_∂Ω ω = ∫_Ω dω",
         "unicode": "∫_∂Ω ω = ∫_Ω dω", "status": "theorem", "proof_status": "proven"},
        {"name": "Riemann hypothesis", "domain": "Number theory",
         "statement": "Non-trivial zeros of ζ have real part 1/2.",
         "unicode": "ζ(s)=0 ⇒ Re(s)=½", "status": "conjecture", "proof_status": "unproven"},
        {"name": "Central limit theorem", "domain": "Probability",
         "statement": "Normalized sums of i.i.d. variables converge to normal.",
         "unicode": "(X̄−μ)/(σ/√n) → N(0,1)", "status": "theorem", "proof_status": "proven"},
        {"name": "Cantor's theorem", "domain": "Set theory",
         "statement": "|S| < |P(S)|",
         "unicode": "|S| < |P(S)|", "status": "theorem", "proof_status": "proven"},
        {"name": "Combinatorial shadow definition", "domain": "Combinatorics",
         "statement": "Shadow of a set family is obtained by deleting one element from each member.",
         "unicode": "∂𝒜 = {A\\{x} | A∈𝒜, x∈A}", "status": "definition", "proof_status": "accepted"},
        {"name": "Umbral evaluation principle", "domain": "Umbral calculus",
         "statement": "Umbral expressions are evaluated by replacing powers a^n with sequence terms a_n under a linear functional.",
         "unicode": "eval(a^n) = a_n", "status": "principle", "proof_status": "accepted"},
        {"name": "Noether's theorem", "domain": "Mathematical physics",
         "statement": "Continuous symmetries correspond to conservation laws.",
         "unicode": "symmetry ⇒ conserved current", "status": "theorem", "proof_status": "proven"},
        {"name": "Gödel incompleteness", "domain": "Logic",
         "statement": "Consistent sufficiently strong formal systems are incomplete.",
         "unicode": "consistency ⇏ completeness", "status": "theorem", "proof_status": "proven"},
    ]

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._build()

    def _build(self):
        self.conn.executescript("""
        CREATE TABLE language_forms (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE, family TEXT,
            description TEXT, example TEXT
        );
        CREATE TABLE formulas (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE, domain TEXT,
            statement TEXT, unicode TEXT, status TEXT, proof_status TEXT
        );
        """)
        cur = self.conn.cursor()
        for lf in self.LANGUAGE_FORMS:
            cur.execute(
                "INSERT OR IGNORE INTO language_forms (name,family,description,example) VALUES (?,?,?,?)",
                (lf["name"], lf["family"], lf["description"], lf["example"])
            )
        for f in self.FORMULAS:
            cur.execute(
                "INSERT OR IGNORE INTO formulas (name,domain,statement,unicode,status,proof_status) VALUES (?,?,?,?,?,?)",
                (f["name"], f["domain"], f["statement"], f["unicode"], f["status"], f["proof_status"])
            )
        self.conn.commit()

    def search(self, q: str, limit: int = 12) -> List[Dict]:
        cur = self.conn.cursor()
        like = f"%{q}%"
        # search both tables
        cur.execute(
            "SELECT 'formula' AS kind, name, domain AS family, statement AS detail, unicode AS example "
            "FROM formulas WHERE name LIKE ? OR statement LIKE ? OR domain LIKE ? OR unicode LIKE ? "
            "UNION ALL "
            "SELECT 'language_form' AS kind, name, family, description AS detail, example "
            "FROM language_forms WHERE name LIKE ? OR family LIKE ? OR description LIKE ? OR example LIKE ? "
            "LIMIT ?",
            (like, like, like, like, like, like, like, like, limit)
        )
        return [dict(r) for r in cur.fetchall()]

    def list_language_forms(self) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT name, family, description, example FROM language_forms ORDER BY family, name")
        return [dict(r) for r in cur.fetchall()]

    def list_shadow_related(self) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT name, family, description, example FROM language_forms "
            "WHERE family LIKE '%Shadow%' OR family LIKE '%umbral%' OR family LIKE '%dual%' "
            "OR name LIKE '%shadow%' OR name LIKE '%umbral%' OR name LIKE '%Logic Alphabet%'"
        )
        return [dict(r) for r in cur.fetchall()]

    def show_formula(self, name: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM formulas WHERE name = ?", (name,))
        row = cur.fetchone()
        return dict(row) if row else None

    def summary(self) -> Dict[str, Any]:
        cur = self.conn.cursor()
        return {
            "language_forms": cur.execute("SELECT COUNT(*) FROM language_forms").fetchone()[0],
            "formulas": cur.execute("SELECT COUNT(*) FROM formulas").fetchone()[0],
            "shadow_related_forms": len(self.list_shadow_related()),
        }

    def language_review(self, focus: str = "shadow") -> Dict[str, Any]:
        """Review mathematical languages, optionally focused on shadow/umbral concepts."""
        forms = self.list_language_forms()
        shadow = self.list_shadow_related()
        return {
            "focus": focus,
            "total_language_forms": len(forms),
            "shadow_umbral_related": shadow,
            "all_families": sorted({f["family"] for f in forms}),
            "note": (
                "This is a structured catalogue review, not a trained model that has "
                "'learned' every mathematical language. True training requires large "
                "corpora and external compute."
            )
        }

    def close(self):
        self.conn.close()


# =============================================================================
# 11. ROUTER
# =============================================================================
class Router:
    def __init__(self, pod, math_e, logic, code, pred, trans, tools, thought, planner, atlas):
        self.pod, self.math, self.logic = pod, math_e, logic
        self.code, self.pred, self.trans = code, pred, trans
        self.tools, self.thought, self.planner = tools, thought, planner
        self.atlas = atlas

    def route(self, task: str, payload: Any = None) -> Dict[str, Any]:
        t = task.lower().strip()

        if task.startswith("tool:"):
            return {"engine": "tool", "result": self.tools.call(task.split(":",1)[1].strip(), payload)}

        if t == "plan" or t.startswith("plan "):
            goal = payload if payload else task[5:].strip()
            return {"engine": "planner", "result": self.planner.plan(goal)}

        if "seed concepts" in t: return {"engine": "thought.seed", "result": self.thought.seed()}
        if "mix concepts" in t: return {"engine": "thought.mix", "result": self.thought.mix(payload)}

        if "ingest" in t: return {"engine": "pod.ingest", "result": self.pod.ingest(payload or "")}
        if "pod reflect" in t or t == "reflect": return {"engine": "pod.reflect", "result": self.pod.reflect()}
        if any(k in t for k in ["search knowledge", "lookup", "recall"]):
            return {"engine": "pod.query", "result": self.pod.query(payload or "")}

        if "atlas search" in t: return {"engine": "atlas.search", "result": self.atlas.search(payload or "")}
        if "atlas show" in t or "show formula" in t:
            return {"engine": "atlas.show", "result": self.atlas.show_formula(payload or "")}
        if "atlas summary" in t: return {"engine": "atlas.summary", "result": self.atlas.summary()}
        if "list language forms" in t: return {"engine": "atlas.forms", "result": self.atlas.list_language_forms()}
        if "list shadow" in t or "shadow forms" in t:
            return {"engine": "atlas.shadow", "result": self.atlas.list_shadow_related()}
        if "language review" in t:
            focus = payload if isinstance(payload, str) else "shadow"
            return {"engine": "atlas.review", "result": self.atlas.language_review(focus)}

        if "learned forecast" in t or "learned trend" in t:
            return {"engine": "pred.learned", "result": self.pred.learned(payload)}
        if "linear forecast" in t: return {"engine": "pred.linear", "result": self.pred.linear(payload)}
        if any(k in t for k in ["trend", "predict", "forecast"]):
            return {"engine": "pred.trend", "result": self.pred.trend(payload)}
        if "elo" in t: return {"engine": "pred.elo", "result": self.pred.elo(*payload)}
        if "kelly" in t: return {"engine": "pred.kelly", "result": self.pred.kelly(*payload)}

        if "derivative" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.deriv", "result": self.math.derivative(*args)}
        if "integral" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.int", "result": self.math.integral(*args)}
        if "limit" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.limit", "result": self.math.limit(*args)}
        if "series" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.series", "result": self.math.series_expand(*args)}
        if "equation" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.solve", "result": self.math.solve_equation(*args)}
        if "matrix" in t:
            op = "eigenvals" if "eigen" in t else "det"
            return {"engine": "math.matrix", "result": self.math.matrix_ops(payload, op)}
        if "prime" in t or "factorize" in t:
            op = "factorize" if "factor" in t else "is_prime"
            return {"engine": "math.nt", "result": self.math.number_theory(payload, op)}
        if "gcd" in t or "lcm" in t: return {"engine": "math.gcd", "result": self.math.gcd_lcm(*payload)}
        if any(k in t for k in ["simplify", "calculate", "solve"]) and payload:
            return {"engine": "math.simp", "result": self.math.simplify(payload)}

        if "satisfiable" in t: return {"engine": "logic.sat", "result": self.logic.is_satisfiable(payload)}
        if "truth table" in t: return {"engine": "logic.tt", "result": self.logic.truth_table(*payload)}

        if "code language" in t or "detect language" in t:
            return {"engine": "code", "result": self.code.detect(payload)}
        if "list languages" in t: return {"engine": "code.list", "result": self.code.list_supported()}
        if "missing languages" in t: return {"engine": "code.missing", "result": self.code.list_missing()}

        if "translate" in t: return {"engine": "trans", "result": self.trans.translate(*payload)}

        if "list tools" in t: return {"engine": "tools", "result": self.tools.list_tools()}
        if "list pipelines" in t: return {"engine": "pipelines", "result": self.tools.named_pipelines()}
        if "run pipeline" in t:
            name, init = payload
            return {"engine": "pipeline", "result": self.tools.run_pipeline(name, init)}

        return {"engine": "none", "result": f"[no handler for '{task}']"}


# =============================================================================
# 12. AGENT
# =============================================================================
class Agent:
    def __init__(self, router: Router, planner: Planner):
        self.router = router
        self.planner = planner
        self.history = []

    def run(self, tasks: List[Dict[str, Any]], react: bool = True) -> List[Dict[str, Any]]:
        results, prev, i = [], None, 0
        task_list = list(tasks)
        while i < len(task_list):
            task = task_list[i]
            payload = task.get("payload")
            if payload == "$PREV": payload = prev
            try:
                out = self.router.route(task["task"], payload)
            except Exception as e:
                out = {"engine": "error", "result": f"[agent error: {e}]"}
            rec = {"task": task["task"], "payload_preview": str(payload)[:60] if payload is not None else None, **out}
            self.history.append(rec)
            results.append(rec)
            prev = out.get("result")
            if react and i == len(task_list) - 1:
                extra = self.planner.react(prev)
                if extra: task_list.append(extra)
            i += 1
        return results

    def run_goal(self, goal: str) -> List[Dict[str, Any]]:
        plan = self.planner.plan(goal)
        print(f"[PLANNER] Goal: {goal}")
        print(f"[PLANNER] Plan ({len(plan)} steps):")
        for i, s in enumerate(plan, 1):
            print(f"  {i}. {s['task']}")
        return self.run(plan, react=True)


# =============================================================================
# REPORTS
# =============================================================================
EVOLUTION_NOTES = """
EVOLUTION NOTES (combined → complete → evolved)
===============================================
1. Reviewed both predecessor scripts: syntax OK, capabilities retained.
2. Added explicit SHADOW / UMBRAL mathematical language forms:
     - Umbral / shadow letters (Whitehead)
     - Umbral calculus
     - Combinatorial shadow notation (∂𝒜)
     - Shadow theory (formal semantics)
     - Logic Alphabet (Zellweger-style alternative)
     - Dual / opposite systems
3. Atlas now supports language-form listing, shadow-focused search, and
   a structured language_review() method.
4. Experimental thought loop seeds umbral + combinatorial-shadow concepts.
5. Planner recognizes goals about shadow/umbral/mathematical languages.

STILL NOT DONE (and why)
------------------------
• "Train in all the mathematical languages"
  → Requires large corpora of formal mathematics + substantial GPU hours.
    A catalogue + search engine is what a single script can honestly provide.
• A single universal "shadow alphabet" that covers all of mathematics
  → Does not exist as a standard system; the closest concepts are now
    recorded as first-class language forms.
• Neural mastery of every notation system
  → Outside single-file scope; the training-compute plan from earlier
    scripts still applies.
"""

CHECKLIST = [
    ("Review of combined + complete scripts", "YES", "Both syntax-valid; strengths retained"),
    ("Expanded math-language atlas", "YES", "21 language forms including shadow/umbral layer"),
    ("Shadow / umbral concepts recorded", "YES", "Whitehead, umbral calculus, combinatorial ∂, semantics, Logic Alphabet, duals"),
    ("Language review engine", "YES", "list / search / shadow-focused review (catalogue, not trained model)"),
    ("Knowledge pod + growth + reflection", "YES", "Novelty filter retained"),
    ("Reactive planner + agent", "PARTIAL", "Rule-based; recognizes math-language goals"),
    ("Tiny learned model", "PARTIAL", "Real gradients; not large-scale training"),
    ("Tools + pipelines", "YES", "Core set retained"),
    ("Experimental thought loops", "PARTIAL", "Now includes umbral/shadow seeds"),
    ("True training on all mathematical languages", "NO", "Needs external data + compute"),
]


def print_reports():
    print("\n=== CHECKLIST ===")
    for item, status, note in CHECKLIST:
        print(f"[{status:7}] {item}\n           → {note}")
    print(EVOLUTION_NOTES)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 74)
    print("ORCHESTRATOR EVOLVED")
    print("Evolution of orchestrator_combined.py + orchestrator_complete.py")
    print("Focus: mathematical languages + shadow/umbral layer")
    print("=" * 74)

    pod = KnowledgePod()
    math_e = MathEngine()
    logic = LogicEngine()
    code = CodeLangDetector()
    pred = PredictiveEngine()
    trans = TranslationLayer()
    tools = build_tools()
    thought = ExperimentalThoughtLoop(pod)
    planner = Planner()
    atlas = MathLanguageAtlas()

    print(f"[ATLAS] {atlas.summary()}")

    pod.add("note1", "TT Oracle uses ELO rankings and a cushion engine for table tennis betting.", force=True)

    router = Router(pod, math_e, logic, code, pred, trans, tools, thought, planner, atlas)
    agent = Agent(router, planner)

    # Core capability smoke test
    demo = [
        {"task": "solve equation", "payload": ("x**2 - 4 = 0", "x")},
        {"task": "derivative", "payload": ("x**3 + 2*x", "x")},
        {"task": "is prime", "payload": 97},
        {"task": "satisfiable", "payload": "A & ~A"},
        {"task": "learned forecast", "payload": [1.0, 2.2, 3.1, 4.5, 5.8, 7.0]},
        {"task": "atlas summary", "payload": None},
        {"task": "list language forms", "payload": None},
        {"task": "list shadow", "payload": None},
        {"task": "atlas search", "payload": "shadow"},
        {"task": "atlas search", "payload": "umbral"},
        {"task": "language review", "payload": "shadow"},
        {"task": "atlas show", "payload": "Combinatorial shadow definition"},
        {"task": "run pipeline", "payload": ("full_fingerprint", "evolved")},
        {"task": "tool:unit_convert", "payload": (100, "km", "mi")},
    ]

    print("\n=== CORE + ATLAS DEMO ===")
    for r in agent.run(demo, react=False):
        res = r["result"]
        if isinstance(res, (list, dict)) and len(str(res)) > 160:
            res = str(res)[:160] + " ..."
        print(f"  [{r['engine']:<14}] {r['task'][:34]:34s} → {res}")

    print("\n=== SHADOW / UMBRAL + EXPERIMENTAL GOAL ===")
    results = agent.run_goal(
        "review mathematical languages with the shadow alphabet and umbral notation; mix with geometry experimentally"
    )
    for r in results:
        res = r["result"]
        if isinstance(res, dict) and len(str(res)) > 140:
            res = {k: (str(v)[:70]+"..." if len(str(v))>70 else v) for k,v in list(res.items())[:6]}
        print(f"  [{r['engine']:<14}] {r['task'][:34]:34s} → {res}")

    print("\n=== FINAL POD STATE ===")
    print(f"  {pod.reflect()}")

    print_reports()
    atlas.close()
    print("=" * 74)
    print("ORCHESTRATOR EVOLVED — DEMO COMPLETE")
    print("Mathematical languages reviewed; shadow/umbral layer added.")
    print("True training on all mathematical languages remains external.")
    print("=" * 74)
