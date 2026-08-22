#!/usr/bin/env python3
"""
ORCHESTRATOR COMBINED — single definitive script
================================================
Merges the strongest real pieces from:
  • unified_orchestrator.py
  • orchestrator_max.py

What you get in one file:
  • Knowledge base with novelty (hash) filter + growth log
  • Full sympy math engine (solve, diff, integrate, limit, series, matrix, number theory)
  • Propositional logic (SAT + truth tables)
  • Code-language detector (~40 languages) + explicit missing list
  • Tiny 2-layer learned net + linear ensemble (real gradients)
  • Closed-form predictors (Elo, Kelly, exponential smoothing, trend, linear)
  • Tool registry (12 tools) + 8 named multi-tool pipelines that actually run
  • Reactive heuristic planner + sequential agent loop
  • Experimental thought loop (multi-concept mixing + interest score)
  • Mathematical Language Atlas (SQLite in-memory: language forms + formulas + search/show)
  • Honest translation stub
  • Remaining-gap report + checklist

Still blocked (documented, not faked):
  real translation, large trained models, true world-model / self-awakening,
  exhaustive 20-tool combination tables, genuine scientific discovery.
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
from collections import defaultdict
from typing import List, Dict, Callable, Any, Tuple, Optional, Set

import torch
import torch.nn as nn

try:
    import sympy
    from sympy import (
        symbols, simplify, solve, diff, integrate, Matrix, limit, series,
        factorial, binomial, Eq
    )
    from sympy.logic.inference import satisfiable
    from sympy.ntheory import isprime, factorint
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
DB_PATH = ":memory:"

# =============================================================================
# 1. KNOWLEDGE BASE (novelty filter)
# =============================================================================
class KnowledgeBase:
    def __init__(self):
        self.docs: List[Dict[str, str]] = []
        self._df = defaultdict(int)
        self.growth_log: List[str] = []
        self._seen: Set[str] = set()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9']+", text.lower())

    def _hash(self, text: str) -> str:
        return hashlib.md5(re.sub(r"\s+", " ", text.lower().strip()).encode()).hexdigest()

    def add(self, doc_id: str, text: str, force: bool = False) -> bool:
        h = self._hash(text)
        if not force and h in self._seen:
            return False
        self._seen.add(h)
        self.docs.append({"id": doc_id, "text": text})
        for tok in set(self._tokenize(text)):
            self._df[tok] += 1
        return True

    def query(self, q: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.docs:
            return []
        q_tokens = self._tokenize(q)
        n = len(self.docs)
        scored = []
        for doc in self.docs:
            d_tokens = self._tokenize(doc["text"])
            tf = defaultdict(int)
            for t in d_tokens:
                tf[t] += 1
            score = 0.0
            for qt in q_tokens:
                if qt in tf:
                    idf = math.log((n + 1) / (self._df.get(qt, 0) + 1)) + 1
                    score += (tf[qt] / max(len(d_tokens), 1)) * idf
            if score > 0:
                scored.append({"id": doc["id"], "score": round(score, 4), "excerpt": doc["text"][:220]})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def ingest_and_grow(self, source_text: str, source_id: str = None) -> Dict[str, Any]:
        if source_id is None:
            source_id = f"ingest_{len(self.docs)}_{hashlib.md5(source_text.encode()).hexdigest()[:8]}"
        sentences = re.split(r'(?<=[.!?])\s+', source_text.strip())
        added, skipped = [], 0
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if len(sent) < 30:
                continue
            doc_id = f"{source_id}_s{i}"
            if self.add(doc_id, sent):
                added.append(doc_id)
                self.growth_log.append(
                    f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] + {doc_id}: {sent[:90]}..."
                )
            else:
                skipped += 1
        return {"source_id": source_id, "added": len(added), "skipped_dupes": skipped, "total_docs": len(self.docs)}

    def stats(self) -> Dict[str, Any]:
        return {
            "total_docs": len(self.docs),
            "unique_hashes": len(self._seen),
            "growth_log": len(self.growth_log),
            "vocab_size": len(self._df)
        }


# =============================================================================
# 2. MATH ENGINE
# =============================================================================
class MathEngine:
    def simplify(self, expr: str) -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            return str(simplify(sympy.sympify(expr)))
        except Exception as e:
            return f"[math error: {e}]"

    def solve_equation(self, equation: str, variable: str = "x") -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            var = symbols(variable)
            if "=" in equation:
                lhs, rhs = equation.split("=", 1)
                eq = Eq(sympy.sympify(lhs), sympy.sympify(rhs))
            else:
                eq = sympy.sympify(equation)
            return str(solve(eq, var))
        except Exception as e:
            return f"[math error: {e}]"

    def derivative(self, expr: str, variable: str = "x") -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            return str(diff(sympy.sympify(expr), symbols(variable)))
        except Exception as e:
            return f"[math error: {e}]"

    def integral(self, expr: str, variable: str = "x") -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            return str(integrate(sympy.sympify(expr), symbols(variable)))
        except Exception as e:
            return f"[math error: {e}]"

    def limit(self, expr: str, variable: str = "x", point: str = "0") -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            return str(limit(sympy.sympify(expr), symbols(variable), sympy.sympify(point)))
        except Exception as e:
            return f"[math error: {e}]"

    def series_expand(self, expr: str, variable: str = "x", n: int = 6) -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            return str(series(sympy.sympify(expr), symbols(variable), n=n))
        except Exception as e:
            return f"[math error: {e}]"

    def matrix_ops(self, matrix: List[List[float]], op: str = "det") -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            m = Matrix(matrix)
            ops = {
                "det": m.det, "inverse": m.inv, "transpose": lambda: m.T,
                "eigenvals": m.eigenvals, "rank": m.rank, "rref": m.rref
            }
            if op not in ops:
                return f"[unknown matrix op: {op}]"
            return str(ops[op]())
        except Exception as e:
            return f"[math error: {e}]"

    def number_theory(self, n: int, op: str = "is_prime") -> Any:
        try:
            if op == "is_prime":
                return bool(isprime(n)) if HAS_SYMPY else n > 1 and all(n % i for i in range(2, int(n**0.5)+1))
            if op == "factorize":
                return str(factorint(n)) if HAS_SYMPY else "[sympy unavailable]"
            if op == "factorial":
                return str(factorial(n)) if HAS_SYMPY else str(math.factorial(n))
            return f"[unknown: {op}]"
        except Exception as e:
            return f"[math error: {e}]"

    def gcd_lcm(self, a: int, b: int) -> Dict[str, int]:
        g = math.gcd(a, b)
        return {"gcd": g, "lcm": abs(a * b) // g if g else 0}


# =============================================================================
# 3. LOGIC
# =============================================================================
class LogicEngine:
    def is_satisfiable(self, expr: str) -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            result = satisfiable(sympy.sympify(expr))
            return str(result) if result else "UNSATISFIABLE"
        except Exception as e:
            return f"[logic error: {e}]"

    def truth_table(self, expr: str, variables: List[str]) -> List[Dict[str, Any]]:
        if not HAS_SYMPY:
            return [{"error": "sympy unavailable"}]
        try:
            syms = symbols(" ".join(variables))
            if not isinstance(syms, (list, tuple)):
                syms = (syms,)
            parsed = sympy.sympify(expr)
            rows = []
            n = len(variables)
            for i in range(2 ** n):
                bits = [(i >> j) & 1 for j in range(n)][::-1]
                subs = {syms[j]: bool(bits[j]) for j in range(n)}
                val = parsed.subs(subs)
                row = {variables[j]: bool(bits[j]) for j in range(n)}
                row["result"] = bool(val)
                rows.append(row)
            return rows
        except Exception as e:
            return [{"error": str(e)}]


# =============================================================================
# 4. CODE LANGUAGE DETECTOR
# =============================================================================
class CodeLangDetector:
    SIGNATURES = {
        "python": [r"def \w+\(", r"import \w+", r"elif ", r":\s*$"],
        "javascript": [r"function\s+\w+\(", r"const\s+\w+\s*=", r"=>", r"console\.log"],
        "typescript": [r"interface \w+", r":\s*(string|number|boolean)\b"],
        "rust": [r"fn\s+\w+\(", r"let mut", r"println!", r"impl "],
        "java": [r"public class", r"System\.out\.println"],
        "csharp": [r"using System", r"Console\.WriteLine"],
        "cpp": [r"#include\s*<iostream>", r"std::", r"cout\s*<<"],
        "c": [r"#include\s*<stdio\.h>", r"int main\("],
        "go": [r"package main", r"func \w+\(", r"fmt\.Println"],
        "ruby": [r"puts ", r"require '", r"\bend\b"],
        "php": [r"<\?php", r"\$\w+\s*="],
        "swift": [r"func \w+\(", r"var \w+:\s*\w+"],
        "kotlin": [r"fun \w+\(", r"val \w+", r"println\("],
        "sql": [r"SELECT .* FROM", r"INSERT INTO", r"CREATE TABLE"],
        "html": [r"<html", r"<div", r"<!DOCTYPE"],
        "css": [r"\{[^}]*:\s*[^;]+;[^}]*\}", r"@media"],
        "bash": [r"#!/bin/bash", r"\becho\b", r"\$\{.*\}"],
        "r": [r"<-\s*function", r"library\("],
        "scala": [r"object \w+", r"def \w+\("],
        "haskell": [r"::\s*\w+", r"where\b", r"data \w+"],
        "lua": [r"function\s+\w+", r"local\s+\w+"],
        "perl": [r"use strict", r"\$\w+\s*="],
        "julia": [r"function\s+\w+", r"using\s+\w+"],
        "elixir": [r"defmodule\s+", r"IO\.puts"],
        "clojure": [r"\(defn\s+", r"\(ns\s+"],
        "solidity": [r"pragma solidity", r"contract\s+\w+"],
        "zig": [r"pub fn\s+", r"@import"],
        "nim": [r"proc\s+\w+", r"echo\s+"],
        "assembly": [r"mov\s+\w+", r"section\s+\.text"],
        "prolog": [r":-", r"\?-", r"\w+\(.*\)\."],
        "fortran": [r"PROGRAM\s+\w+", r"END PROGRAM"],
        "cobol": [r"IDENTIFICATION DIVISION"],
        "powershell": [r"Write-Host", r"Get-\w+"],
        "matlab": [r"function\s+.*=", r"%\s"],
        "dart": [r"void\s+main", r"import 'package:"],
        "fsharp": [r"let\s+\w+\s*=", r"printfn"],
        "ocaml": [r"let\s+\w+\s*=", r"module\s+\w+"],
        "groovy": [r"def\s+\w+\s*=", r"println\s+"],
        "vba": [r"Sub\s+\w+", r"End Sub"],
        "scheme": [r"\(define\s+", r"\(lambda\s+"],
        "lisp": [r"\(defun\s+", r"\(setq\s+"],
        "crystal": [r"def\s+\w+", r"puts\s+"],
        "erlang": [r"-module\(", r"io:format"],
    }
    MISSING = [
        "APL / J / K", "Ada", "Agda / Coq / Lean", "Ballerina", "Chapel", "Clean",
        "D", "Elm", "Forth", "Gleam", "Hack", "Idris", "Io", "Mercury", "Nix",
        "Objective-C", "Pony", "PureScript", "Racket", "ReasonML / ReScript",
        "Smalltalk", "Tcl", "V (Vlang)", "WebAssembly (wat)", "Wolfram / Mathematica",
        "most DSLs and obscure academic languages"
    ]

    def detect(self, code: str) -> str:
        scores = defaultdict(int)
        for lang, pats in self.SIGNATURES.items():
            for p in pats:
                if re.search(p, code, re.I | re.M):
                    scores[lang] += 1
        return max(scores, key=scores.get) if scores else "unknown"

    def list_supported(self):
        return sorted(self.SIGNATURES.keys())

    def list_missing(self):
        return self.MISSING


# =============================================================================
# 5. PREDICTORS (2-layer net + ensemble)
# =============================================================================
class TinyNet(nn.Module):
    def __init__(self, hidden=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(1, hidden), nn.Tanh(), nn.Linear(hidden, 1))

    def forward(self, x):
        return self.net(x)


class PredictiveScorer:
    def trend_forecast(self, series: List[float], window: int = 3) -> Dict[str, float]:
        if len(series) < 2:
            return {"forecast": series[-1] if series else 0.0, "confidence": 0.0}
        window = min(window, len(series))
        recent = series[-window:]
        deltas = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        avg = statistics.mean(deltas) if deltas else 0.0
        var = statistics.pvariance(recent) if len(recent) > 1 else 0.0
        return {"forecast": round(series[-1] + avg, 4), "confidence": round(1/(1+var), 4)}

    def linear_regression_forecast(self, series: List[float], steps: int = 1) -> Dict[str, float]:
        n = len(series)
        if n < 2:
            return {"forecast": series[-1] if series else 0.0, "slope": 0.0}
        xs = list(range(n))
        xm, ym = statistics.mean(xs), statistics.mean(series)
        num = sum((xs[i]-xm)*(series[i]-ym) for i in range(n))
        den = sum((xs[i]-xm)**2 for i in range(n))
        slope = num/den if den else 0.0
        intercept = ym - slope*xm
        return {"forecast": round(intercept + slope*(n-1+steps), 4), "slope": round(slope, 4)}

    def learned_forecast(self, series: List[float], steps: int = 1, epochs: int = 120) -> Dict[str, Any]:
        if len(series) < 4:
            return {"error": "need ≥4 points", "forecast": series[-1] if series else 0.0}
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
        lin = self.linear_regression_forecast(series, steps)
        ensemble = 0.6 * learned + 0.4 * lin["forecast"]
        return {
            "learned_forecast": round(learned, 4),
            "linear_forecast": lin["forecast"],
            "ensemble_forecast": round(ensemble, 4),
            "final_mse": round(loss.item(), 6),
            "note": "2-layer net + linear ensemble, real gradients"
        }

    def exponential_smoothing(self, series: List[float], alpha: float = 0.3) -> float:
        if not series:
            return 0.0
        s = series[0]
        for v in series[1:]:
            s = alpha * v + (1 - alpha) * s
        return round(s, 4)

    def elo(self, a: float, b: float) -> float:
        return round(1 / (1 + 10 ** ((b - a) / 400)), 4)

    def kelly(self, p: float, decimal_odds: float) -> float:
        b = decimal_odds - 1
        f = (b * p - (1 - p)) / b if b else 0.0
        return round(max(f, 0.0), 4)

    def implied_prob(self, american: float) -> float:
        if american > 0:
            return round(100 / (american + 100), 4)
        return round(-american / (-american + 100), 4)


# =============================================================================
# 6. TRANSLATOR (honest)
# =============================================================================
class Translator:
    def translate(self, text: str, target: str) -> str:
        return (
            f"[translation unavailable offline → '{target}'] "
            "No free unlimited offline model or API key present. "
            "Wire deep-translator, DeepL, Google, or self-hosted LibreTranslate."
        )


# =============================================================================
# 7. TOOLS + NAMED PIPELINES
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
        if name not in self._tools:
            return f"[tool '{name}' not registered]"
        return self._tools[name](*args, **kwargs)

    def list_tools(self):
        return [{"name": n, "description": self._desc[n]} for n in sorted(self._tools)]

    def named_pipelines(self) -> Dict[str, List[str]]:
        return {
            "hash_then_encode": ["hash_sha256", "base64_encode"],
            "stats_then_hash": ["text_stats", "hash_sha256"],
            "normalize_text": ["lower", "reverse_text"],
            "timestamped_hash": ["timestamp_now", "hash_sha256"],
            "json_clean": ["json_pretty"],
            "unit_then_stats": ["unit_convert", "text_stats"],
            "full_fingerprint": ["md5", "hash_sha256", "base64_encode"],
            "case_pipeline": ["lower", "upper", "reverse_text"],
        }

    def run_pipeline(self, name: str, initial) -> Dict[str, Any]:
        pipes = self.named_pipelines()
        if name not in pipes:
            return {"error": f"unknown pipeline '{name}'", "available": list(pipes.keys())}
        current, trace = initial, []
        for step in pipes[name]:
            try:
                current = self.call(step, current)
                trace.append({"tool": step, "ok": True, "preview": str(current)[:80]})
            except Exception as e:
                trace.append({"tool": step, "ok": False, "error": str(e)})
                break
        return {"pipeline": name, "steps": pipes[name], "trace": trace, "final": current}


def build_tools() -> ToolRegistry:
    t = ToolRegistry()

    @t.register("unit_convert", "km/mi, kg/lb, m/ft, C/F")
    def unit_convert(payload):
        value, frm, to = payload
        table = {
            ("km","mi"): 0.621371, ("mi","km"): 1.60934,
            ("kg","lb"): 2.20462, ("lb","kg"): 0.453592,
            ("m","ft"): 3.28084, ("ft","m"): 0.3048,
            ("c","f"): lambda c: c*9/5+32, ("f","c"): lambda f: (f-32)*5/9,
        }
        key = (frm.lower(), to.lower())
        if key not in table:
            return f"[no conversion {frm}->{to}]"
        f = table[key]
        return round(f(value), 4) if callable(f) else round(value * f, 4)

    @t.register("text_stats", "chars / words / reading time")
    def text_stats(text):
        words = str(text).split()
        return {"chars": len(str(text)), "words": len(words), "reading_sec": round(len(words)/3.5, 1)}

    @t.register("hash_sha256", "SHA-256 hex")
    def hash_sha256(text):
        return hashlib.sha256(str(text).encode()).hexdigest()

    @t.register("md5", "MD5 hex")
    def md5(text):
        return hashlib.md5(str(text).encode()).hexdigest()

    @t.register("base64_encode", "Base64 encode")
    def b64e(text):
        return base64.b64encode(str(text).encode()).decode()

    @t.register("base64_decode", "Base64 decode")
    def b64d(text):
        return base64.b64decode(str(text).encode()).decode()

    @t.register("timestamp_now", "UTC ISO timestamp")
    def ts(_=None):
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @t.register("json_pretty", "Pretty-print JSON")
    def jpretty(s):
        try:
            return json.dumps(json.loads(s), indent=2)
        except Exception as e:
            return f"[json error: {e}]"

    @t.register("word_count", "Word count")
    def wc(text):
        return len(str(text).split())

    @t.register("reverse_text", "Reverse string")
    def rev(text):
        return str(text)[::-1]

    @t.register("upper", "Uppercase")
    def up(text):
        return str(text).upper()

    @t.register("lower", "Lowercase")
    def lo(text):
        return str(text).lower()

    return t


# =============================================================================
# 8. EXPERIMENTAL THOUGHT LOOP
# =============================================================================
class ExperimentalThoughtLoop:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.history = []

    def seed(self):
        seeds = {
            "ley_lines": "Ley lines are hypothetical alignments of ancient sites. Mainstream science treats them as cultural patterns or coincidence, not physical force lines.",
            "gravity": "Gravity is spacetime curvature caused by mass-energy (general relativity) or a long-range attractive force (Newtonian approximation).",
            "magnetism": "Magnetism arises from moving charges and intrinsic particle moments; governed by Maxwell equations and QED. Fields can attract or repel.",
            "information": "Information can be quantified (Shannon entropy) and is physical; Landauer's principle links erasure to thermodynamic cost.",
            "geometry": "Geometry studies properties of space. Differential geometry underpins general relativity and modern gauge theories.",
        }
        for cid, text in seeds.items():
            self.kb.add(cid, text, force=True)
        return {"seeded": list(seeds.keys())}

    def mix(self, concepts: List[str] = None) -> Dict[str, Any]:
        if concepts is None:
            concepts = ["ley lines", "gravity", "magnetism", "information", "geometry"]
        retrieved = []
        for c in concepts:
            retrieved.extend(self.kb.query(c, top_k=2))
        seen, unique = set(), []
        for r in retrieved:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique.append(r)
        analogies = []
        for a, b in itertools.combinations(unique, 2):
            text = (
                f"Experimental analogy [{a['id']} ↔ {b['id']}]: treating the structure in "
                f"'{a['excerpt'][:50]}...' as analogous to '{b['excerpt'][:50]}...' suggests exploring "
                f"whether geometric or informational language can re-frame the other concept. "
                f"This is speculative knowledge-play only — not a physical claim."
            )
            analogies.append(text)
            self.kb.ingest_and_grow(text, source_id=f"analogy_{a['id']}_{b['id']}")
        score = min(1.0, len(analogies) * 0.15 + len(unique) * 0.1)
        record = {
            "concepts": concepts,
            "unique_retrieved": len(unique),
            "analogies_generated": len(analogies),
            "experimental_interest_score": round(score, 3),
            "sample": analogies[0] if analogies else None,
            "note": "Exploratory analogy generation only. No scientific claim."
        }
        self.history.append(record)
        return record


# =============================================================================
# 9. REACTIVE PLANNER
# =============================================================================
class ReactivePlanner:
    def plan(self, goal: str) -> List[Dict[str, Any]]:
        g = goal.lower()
        if any(k in g for k in ["ley", "gravity", "magnetism", "experimental", "mix"]):
            return [
                {"task": "seed concepts", "payload": None},
                {"task": "mix concepts", "payload": ["ley lines", "gravity", "magnetism", "information", "geometry"]},
                {"task": "search my knowledge", "payload": "experimental analogy"},
                {"task": "kb stats", "payload": None},
            ]
        if any(k in g for k in ["predict", "forecast", "trend", "learn"]):
            return [
                {"task": "learned forecast", "payload": [1.0, 2.1, 3.0, 4.2, 5.5, 6.8, 8.0]},
                {"task": "linear forecast", "payload": [1.0, 2.1, 3.0, 4.2, 5.5, 6.8, 8.0]},
            ]
        if any(k in g for k in ["math", "equation", "calculus"]):
            return [
                {"task": "solve equation", "payload": ("x**2 - 5*x + 6 = 0", "x")},
                {"task": "derivative", "payload": ("x**3 + 2*x", "x")},
                {"task": "atlas search", "payload": "theorem"},
            ]
        if any(k in g for k in ["tool", "pipeline", "hash"]):
            return [
                {"task": "list pipelines", "payload": None},
                {"task": "run pipeline", "payload": ("full_fingerprint", "orchestrator-combined")},
            ]
        return [
            {"task": "search my knowledge", "payload": goal},
            {"task": "kb stats", "payload": None},
        ]

    def react(self, last_result: Any) -> Optional[Dict[str, Any]]:
        if isinstance(last_result, dict) and last_result.get("analogies_generated", 0) > 2:
            return {"task": "search my knowledge", "payload": "speculative knowledge-play"}
        if isinstance(last_result, dict) and "ensemble_forecast" in last_result:
            return {"task": "tool:text_stats", "payload": str(last_result)}
        return None


# =============================================================================
# 10. MATH ATLAS (in-memory)
# =============================================================================
class MathAtlas:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._init()
        self._populate()

    def _init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS language_forms (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE, family TEXT, description TEXT, example TEXT
        );
        CREATE TABLE IF NOT EXISTS formulas (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE, domain TEXT, statement TEXT,
            latex TEXT, unicode TEXT, status TEXT, proof_status TEXT
        );
        """)

    def _populate(self):
        langs = [
            ("Natural-language mathematics", "Expository", "Ordinary language", "For every real x, x² ≥ 0"),
            ("Symbolic algebra", "Algebraic", "Variables & operators", "a² + b² = c²"),
            ("First-order logic", "Formal logic", "Quantifiers & connectives", "∀x (Prime(x) ∧ x>2 → Odd(x))"),
            ("Set theory (ZFC)", "Foundational", "Sets & membership", "{x ∈ ℝ | x² ≥ 0} = ℝ"),
            ("Differential-form notation", "Geometry", "Forms & exterior derivative", "dω = 0"),
            ("Probability notation", "Statistical", "Random variables", "P(A|B) = P(B|A)P(A)/P(B)"),
            ("Calculus notation", "Analysis", "Limits, derivatives, integrals", "∫ f' = f(b)-f(a)"),
            ("Tensor / index notation", "Physics", "Indexed tensors", "R_μν − ½Rg_μν = 8πGT_μν"),
            ("Lambda calculus", "Computational", "Abstraction & application", "λf.λx.f (f x)"),
            ("Category theory", "Abstract", "Objects & morphisms", "F ∘ G : C → E"),
            ("Modal logic", "Philosophical", "Necessity & possibility", "□P → ◇P"),
            ("Matrix notation", "Linear algebra", "Vectors & matrices", "Ax = b"),
        ]
        cur = self.conn.cursor()
        for row in langs:
            cur.execute("INSERT OR IGNORE INTO language_forms (name,family,description,example) VALUES (?,?,?,?)", row)
        formulas = [
            ("Fundamental theorem of calculus", "Analysis", "Integration and differentiation are inverses",
             r"\int_a^b f' = f(b)-f(a)", "∫_a^b f' = f(b)-f(a)", "theorem", "proven"),
            ("Bayes' theorem", "Probability", "Posterior ∝ likelihood × prior",
             r"P(A|B)=P(B|A)P(A)/P(B)", "P(A|B)=P(B|A)P(A)/P(B)", "theorem", "proven"),
            ("Pythagorean theorem", "Geometry", "a² + b² = c² in right triangles",
             r"a^2+b^2=c^2", "a²+b²=c²", "theorem", "proven"),
            ("Shannon entropy", "Information theory", "Expected negative log probability",
             r"H(X)=-\sum p\log p", "H(X)=−Σ p log p", "definition", "accepted"),
            ("Stokes' theorem", "Differential geometry", "∫_∂Ω ω = ∫_Ω dω",
             r"\int_{\partial\Omega}\omega=\int_\Omega d\omega", "∫_∂Ω ω = ∫_Ω dω", "theorem", "proven"),
            ("Riemann hypothesis", "Number theory", "Non-trivial zeros have real part 1/2",
             r"\zeta(s)=0 \Rightarrow Re(s)=1/2", "ζ(s)=0 ⇒ Re(s)=½", "conjecture", "unproven"),
            ("Central limit theorem", "Probability", "Normalized sums converge to normal",
             r"(\bar X-\mu)/(\sigma/\sqrt n) \to N(0,1)", "(X̄-μ)/(σ/√n)→N(0,1)", "theorem", "proven"),
            ("Cantor's theorem", "Set theory", "|S| < |P(S)|",
             r"|S|<|\mathcal{P}(S)|", "|S| < |P(S)|", "theorem", "proven"),
            ("Law of large numbers", "Probability", "Sample mean → expected value",
             r"\bar X_n \to \mu", "X̄ₙ → μ", "theorem", "proven"),
            ("Axiom of choice", "Set theory", "Choice function exists for nonempty families",
             r"\forall F \exists f ...", "∀F ∃f ...", "axiom", "independent"),
            ("Goldbach's conjecture", "Number theory", "Every even integer > 2 is sum of two primes",
             r"\forall n>2 even \exists p,q prime: n=p+q", "∀n>2 even ∃p,q prime: n=p+q", "conjecture", "unproven"),
            ("Zorn's lemma", "Set theory", "Every chain has upper bound ⇒ maximal element exists",
             r"(∀ chains ∃ ub) ⇒ ∃ maximal", "(∀chains ∃ub) ⇒ ∃maximal", "theorem", "proven"),
        ]
        for row in formulas:
            cur.execute("INSERT OR IGNORE INTO formulas (name,domain,statement,latex,unicode,status,proof_status) VALUES (?,?,?,?,?,?,?)", row)
        self.conn.commit()

    def search(self, q: str, limit=8) -> List[Dict]:
        cur = self.conn.cursor()
        like = f"%{q}%"
        cur.execute(
            "SELECT name, domain, status, unicode FROM formulas WHERE name LIKE ? OR statement LIKE ? OR domain LIKE ? LIMIT ?",
            (like, like, like, limit)
        )
        return [dict(r) for r in cur.fetchall()]

    def show(self, name: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM formulas WHERE name = ?", (name,))
        row = cur.fetchone()
        return dict(row) if row else None

    def summary(self) -> Dict[str, int]:
        cur = self.conn.cursor()
        return {
            "language_forms": cur.execute("SELECT COUNT(*) FROM language_forms").fetchone()[0],
            "formulas": cur.execute("SELECT COUNT(*) FROM formulas").fetchone()[0],
        }

    def close(self):
        self.conn.close()


# =============================================================================
# 11. ROUTER
# =============================================================================
class Router:
    def __init__(self, kb, math_e, logic, code, pred, trans, tools, thought, planner, atlas):
        self.kb, self.math, self.logic = kb, math_e, logic
        self.code, self.pred, self.trans = code, pred, trans
        self.tools, self.thought, self.planner = tools, thought, planner
        self.atlas = atlas

    def route(self, task: str, payload: Any = None) -> Dict[str, Any]:
        t = task.lower().strip()

        if task.startswith("tool:"):
            return {"engine": "tool", "result": self.tools.call(task.split(":", 1)[1].strip(), payload)}

        if t == "plan" or t.startswith("plan "):
            goal = payload if payload else task[5:].strip()
            return {"engine": "planner", "result": self.planner.plan(goal)}

        if "seed concepts" in t:
            return {"engine": "thought.seed", "result": self.thought.seed()}
        if "mix concepts" in t:
            return {"engine": "thought.mix", "result": self.thought.mix(payload)}

        if "ingest" in t:
            return {"engine": "kb.ingest", "result": self.kb.ingest_and_grow(payload or "")}
        if "kb stats" in t:
            return {"engine": "kb.stats", "result": self.kb.stats()}

        if "atlas search" in t:
            return {"engine": "atlas.search", "result": self.atlas.search(payload or "")}
        if "atlas show" in t:
            return {"engine": "atlas.show", "result": self.atlas.show(payload or "")}
        if "atlas summary" in t:
            return {"engine": "atlas.summary", "result": self.atlas.summary()}

        if "learned forecast" in t or "learned trend" in t:
            return {"engine": "pred.learned", "result": self.pred.learned_forecast(payload)}
        if "linear forecast" in t:
            return {"engine": "pred.linear", "result": self.pred.linear_regression_forecast(payload)}
        if "exponential" in t:
            return {"engine": "pred.exp", "result": self.pred.exponential_smoothing(payload)}
        if any(k in t for k in ["trend", "predict", "forecast"]):
            return {"engine": "pred.trend", "result": self.pred.trend_forecast(payload)}
        if "elo" in t:
            return {"engine": "pred.elo", "result": self.pred.elo(*payload)}
        if "kelly" in t:
            return {"engine": "pred.kelly", "result": self.pred.kelly(*payload)}
        if "odds" in t or "implied" in t:
            return {"engine": "pred.implied", "result": self.pred.implied_prob(payload)}

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
            op = "eigenvals" if "eigen" in t else "rref" if "rref" in t else "det"
            return {"engine": "math.matrix", "result": self.math.matrix_ops(payload, op)}
        if "prime" in t or "factorize" in t or "factorial" in t:
            op = "factorize" if "factor" in t else "factorial" if "factor" in t else "is_prime"
            return {"engine": "math.nt", "result": self.math.number_theory(payload, op)}
        if "gcd" in t or "lcm" in t:
            return {"engine": "math.gcd", "result": self.math.gcd_lcm(*payload)}
        if any(k in t for k in ["simplify", "calculate", "solve"]) and payload:
            return {"engine": "math.simp", "result": self.math.simplify(payload)}

        if "satisfiable" in t:
            return {"engine": "logic.sat", "result": self.logic.is_satisfiable(payload)}
        if "truth table" in t:
            return {"engine": "logic.tt", "result": self.logic.truth_table(*payload)}

        if "code language" in t or "detect language" in t:
            return {"engine": "code", "result": self.code.detect(payload)}
        if "list languages" in t:
            return {"engine": "code.list", "result": self.code.list_supported()}
        if "missing languages" in t:
            return {"engine": "code.missing", "result": self.code.list_missing()}

        if "translate" in t:
            return {"engine": "trans", "result": self.trans.translate(*payload)}

        if any(k in t for k in ["lookup", "search", "knowledge", "recall"]):
            return {"engine": "kb", "result": self.kb.query(payload)}

        if "list tools" in t:
            return {"engine": "tools", "result": self.tools.list_tools()}
        if "list pipelines" in t:
            return {"engine": "pipelines", "result": self.tools.named_pipelines()}
        if "run pipeline" in t:
            name, init = payload
            return {"engine": "pipeline", "result": self.tools.run_pipeline(name, init)}

        return {"engine": "none", "result": f"[no handler for '{task}']"}


# =============================================================================
# 12. AGENT LOOP
# =============================================================================
class AgentLoop:
    def __init__(self, router: Router, planner: ReactivePlanner):
        self.router = router
        self.planner = planner
        self.history = []

    def run(self, tasks: List[Dict[str, Any]], react: bool = True) -> List[Dict[str, Any]]:
        results = []
        prev = None
        i = 0
        task_list = list(tasks)
        while i < len(task_list):
            task = task_list[i]
            payload = task.get("payload")
            if payload == "$PREV":
                payload = prev
            try:
                out = self.router.route(task["task"], payload)
            except Exception as e:
                out = {"engine": "error", "result": f"[agent error: {e}]"}
            rec = {"task": task["task"], "payload_preview": str(payload)[:80] if payload is not None else None, **out}
            self.history.append(rec)
            results.append(rec)
            prev = out.get("result")
            if react and i == len(task_list) - 1:
                extra = self.planner.react(prev)
                if extra:
                    task_list.append(extra)
            i += 1
        return results

    def run_goal(self, goal: str) -> List[Dict[str, Any]]:
        plan = self.planner.plan(goal)
        print(f"[PLANNER] Goal: {goal}")
        print(f"[PLANNER] Initial plan ({len(plan)} steps):")
        for i, s in enumerate(plan, 1):
            print(f"  {i}. {s['task']}")
        return self.run(plan, react=True)


# =============================================================================
# REPORTS
# =============================================================================
GAP_REPORT = """
REMAINING GAP REPORT
====================
Request                               | Status                         | Bottleneck
--------------------------------------+--------------------------------+---------------------------
Autonomous planning                   | PARTIAL (reactive heuristic)   | Needs LLM for real planning
Large / real learned model            | PARTIAL (2-layer + ensemble)   | No GPU hours / large data
All tool combinations (up to 20)      | REPLACED by named pipelines    | Combinatorial explosion
All mathematical notation systems     | PARTIAL (12 forms)             | Open-ended catalogue
All remaining programming languages   | PARTIAL (~40 + missing list)   | Needs trained classifier
Real translation API                  | NO (honest stub)               | No offline model / API key
Execute Kaggle-style training         | NO (plan only)                 | External compute required
Self-growing understanding            | PARTIAL (novelty-filtered KB)  | Additive only
Ley-lines/gravity/magnetism insight   | PARTIAL (scored analogies)     | Analogy ≠ discovery
World model / GRU / MoE / beyond      | NO                             | Architectural + compute
"""

CHECKLIST = [
    ("Single combined workable script", "YES", "This file merges both predecessors"),
    ("Knowledge base + novelty filter + growth", "YES", "Hash dedup + ingest"),
    ("Reactive planner + agent loop", "PARTIAL", "Can insert follow-up; still rule-based"),
    ("Tiny learned model + ensemble", "PARTIAL", "2-layer net + linear; real gradients"),
    ("Named multi-tool pipelines", "YES", "8 useful pipelines"),
    ("Sympy math coverage", "YES", "Solve/diff/int/limit/series/matrix/nt"),
    ("Math language atlas", "YES", "12 forms + 12 formulas + search/show"),
    ("Logic (SAT + truth tables)", "YES", "Propositional only"),
    ("Code languages", "PARTIAL", "~40 + explicit missing list"),
    ("Translation", "NO", "Honest stub"),
    ("Experimental thought loops", "PARTIAL", "Multi-concept mixing + interest score"),
    ("Large model / world model / self-awaken", "NO", "Requires external resources"),
]


def print_checklist():
    print("\n=== CHECKLIST ===")
    for item, status, note in CHECKLIST:
        print(f"[{status:7}] {item}\n           → {note}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 72)
    print("ORCHESTRATOR COMBINED — definitive single-file system")
    print("=" * 72)

    kb = KnowledgeBase()
    math_e = MathEngine()
    logic = LogicEngine()
    code = CodeLangDetector()
    pred = PredictiveScorer()
    trans = Translator()
    tools = build_tools()
    thought = ExperimentalThoughtLoop(kb)
    planner = ReactivePlanner()
    atlas = MathAtlas()

    print(f"[ATLAS] {atlas.summary()}")

    kb.add("note1", "TT Oracle uses ELO rankings and a cushion engine for table tennis betting.", force=True)
    kb.add("note2", "Jarvis is a layered autonomous desktop agent using MCP tools and local models.", force=True)

    router = Router(kb, math_e, logic, code, pred, trans, tools, thought, planner, atlas)
    agent = AgentLoop(router, planner)

    demo = [
        {"task": "solve equation", "payload": ("x**2 - 4 = 0", "x")},
        {"task": "derivative", "payload": ("x**3 + 2*x", "x")},
        {"task": "limit", "payload": ("sin(x)/x", "x", "0")},
        {"task": "matrix eigenvals", "payload": [[2, 1], [1, 2]]},
        {"task": "is prime", "payload": 97},
        {"task": "satisfiable", "payload": "A & ~A"},
        {"task": "what code language", "payload": "fn main() { let mut x = 5; println!(\"{}\", x); }"},
        {"task": "list languages", "payload": None},
        {"task": "missing languages", "payload": None},
        {"task": "learned forecast", "payload": [1.0, 2.2, 3.1, 4.5, 5.8, 7.0, 8.3]},
        {"task": "elo", "payload": (1800, 1650)},
        {"task": "kelly", "payload": (0.55, 2.0)},
        {"task": "atlas search", "payload": "entropy"},
        {"task": "atlas show", "payload": "Bayes' theorem"},
        {"task": "list tools", "payload": None},
        {"task": "list pipelines", "payload": None},
        {"task": "run pipeline", "payload": ("full_fingerprint", "orchestrator-combined")},
        {"task": "tool:unit_convert", "payload": (100, "km", "mi")},
        {"task": "translate", "payload": ("hello", "japanese")},
        {"task": "search my knowledge", "payload": "table tennis"},
    ]

    print("\n=== CORE DEMO ===")
    for r in agent.run(demo, react=False):
        res = r["result"]
        if isinstance(res, (list, dict)) and len(str(res)) > 150:
            res = str(res)[:150] + " ..."
        print(f"  [{r['engine']:<14}] {r['task'][:34]:34s} → {res}")

    print("\n=== AUTONOMOUS + REACTIVE GOAL ===")
    results = agent.run_goal(
        "study ley lines, gravity, magnetism, information and geometry; mix experimentally"
    )
    for r in results:
        res = r["result"]
        if isinstance(res, dict) and len(str(res)) > 130:
            res = {k: (str(v)[:65] + "..." if len(str(v)) > 65 else v) for k, v in list(res.items())[:5]}
        print(f"  [{r['engine']:<14}] {r['task'][:34]:34s} → {res}")

    print("\n=== FINAL KB STATE ===")
    print(f"  {kb.stats()}")

    print_checklist()
    print(GAP_REPORT)
    atlas.close()
    print("=" * 72)
    print("ORCHESTRATOR COMBINED — DEMO COMPLETE")
    print("=" * 72)
