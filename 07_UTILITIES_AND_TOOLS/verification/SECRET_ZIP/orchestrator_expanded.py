"""
ORCHESTRATOR EXPANDED — honest single-file system with real components + clear limits.

FEASIBLE ADDITIONS IMPLEMENTED:
  - Autonomous planning: simple goal decomposition + sequential plan execution with $PREV chaining
  - Learned trend model: tiny torch linear regressor trained on the fly (real parameters, not closed-form only)
  - Expanded ToolRegistry with more tools + automatic generation of 2- and 3-tool combination examples
    (full 20-tool combinatorial enumeration is deliberately omitted — it is ~1e18 combinations and
    serves no practical purpose; we show the mechanism and sample real multi-tool pipelines)
  - Full sympy coverage for algebra / calculus / number theory / matrices / logic already present;
    additional helpers for series, limits, discrete math
  - Expanded code-language signatures (now ~40 languages) + explicit list of still-missing families
  - Knowledge growth loop: ingest text → extract claims → add to KB → re-query
  - Experimental thought-loop module that mixes concepts (ley lines / gravity / magnetism) as
    pure knowledge-ingestion + analogy generation — labeled as exploratory, not scientific claim
  - Training-compute plan section (Kaggle GPU hours style) printed at end
  - Translation remains an honest offline stub (no free reliable offline model or unrestricted
    public API key is present; real wiring instructions included)

STILL NOT ACHIEVABLE IN THIS SCRIPT:
  - True world model / autonomous scientific discovery
  - Trained large MoE/GRU/LLM
  - Exhaustive 20-tool combination table
  - Genuine offline multi-language translation
  - "Self-awakening" beyond the simple ingest→KB growth loop shown here
"""

import re
import math
import json
import hashlib
import base64
import datetime
import statistics
import itertools
import random
from collections import defaultdict
from typing import List, Dict, Callable, Any, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn

try:
    import sympy
    from sympy import symbols, simplify, solve, diff, integrate, Matrix, limit, series, factorial, binomial
    from sympy.logic.inference import satisfiable
    from sympy.ntheory import isprime, factorint
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

# =============================================================================
# 1. KNOWLEDGE BASE — TF-IDF + growth / ingest
# =============================================================================
class KnowledgeBase:
    def __init__(self):
        self.docs: List[Dict[str, str]] = []
        self._df = defaultdict(int)
        self.growth_log: List[str] = []

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9']+", text.lower())

    def add(self, doc_id: str, text: str):
        self.docs.append({"id": doc_id, "text": text})
        for tok in set(self._tokenize(text)):
            self._df[tok] += 1

    def query(self, q: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.docs:
            return []
        q_tokens = self._tokenize(q)
        n_docs = len(self.docs)
        scored = []
        for doc in self.docs:
            d_tokens = self._tokenize(doc["text"])
            tf = defaultdict(int)
            for t in d_tokens:
                tf[t] += 1
            score = 0.0
            for qt in q_tokens:
                if qt in tf:
                    idf = math.log((n_docs + 1) / (self._df.get(qt, 0) + 1)) + 1
                    score += (tf[qt] / max(len(d_tokens), 1)) * idf
            if score > 0:
                scored.append({"id": doc["id"], "score": round(score, 4), "excerpt": doc["text"][:200]})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def ingest_and_grow(self, source_text: str, source_id: str = None) -> Dict[str, Any]:
        """Simple autonomous growth: split into sentences, keep non-trivial ones, add to KB."""
        if source_id is None:
            source_id = f"ingest_{len(self.docs)}_{hashlib.md5(source_text.encode()).hexdigest()[:8]}"
        sentences = re.split(r'(?<=[.!?])\s+', source_text.strip())
        added = []
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if len(sent) < 25:
                continue
            doc_id = f"{source_id}_s{i}"
            self.add(doc_id, sent)
            added.append(doc_id)
            self.growth_log.append(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] + {doc_id}: {sent[:80]}...")
        return {"source_id": source_id, "sentences_added": len(added), "total_docs_now": len(self.docs)}

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump({"docs": self.docs, "growth_log": self.growth_log}, f, indent=2)

    def load(self, path: str):
        with open(path) as f:
            data = json.load(f)
        for d in data.get("docs", []):
            self.add(d["id"], d["text"])
        self.growth_log = data.get("growth_log", [])


# =============================================================================
# 2. MATH ENGINE — expanded sympy coverage
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
                eq = sympy.Eq(sympy.sympify(lhs), sympy.sympify(rhs))
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
            if op == "det":
                return str(m.det())
            if op == "inverse":
                return str(m.inv())
            if op == "transpose":
                return str(m.T)
            if op == "eigenvals":
                return str(m.eigenvals())
            if op == "rank":
                return str(m.rank())
            return f"[unknown matrix op: {op}]"
        except Exception as e:
            return f"[math error: {e}]"

    def number_theory(self, n: int, op: str = "is_prime") -> Any:
        try:
            if op == "is_prime":
                return bool(isprime(n)) if HAS_SYMPY else self._is_prime_fallback(n)
            if op == "factorize":
                return str(factorint(n)) if HAS_SYMPY else "[sympy unavailable]"
            if op == "factorial":
                return str(factorial(n)) if HAS_SYMPY else str(math.factorial(n))
            return f"[unknown number theory op: {op}]"
        except Exception as e:
            return f"[math error: {e}]"

    def _is_prime_fallback(self, n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def gcd_lcm(self, a: int, b: int) -> Dict[str, int]:
        g = math.gcd(a, b)
        l = abs(a * b) // g if g else 0
        return {"gcd": g, "lcm": l}

    def discrete(self, n: int, k: int = None, op: str = "binomial") -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            if op == "binomial" and k is not None:
                return str(binomial(n, k))
            if op == "factorial":
                return str(factorial(n))
            return f"[unknown discrete op: {op}]"
        except Exception as e:
            return f"[math error: {e}]"


# =============================================================================
# 3. LOGIC ENGINE
# =============================================================================
class LogicEngine:
    def is_satisfiable(self, expr: str) -> str:
        if not HAS_SYMPY:
            return "[sympy unavailable]"
        try:
            parsed = sympy.sympify(expr)
            result = satisfiable(parsed)
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
# 4. CODE LANGUAGE DETECTOR — expanded signatures + missing list
# =============================================================================
class CodeLangDetector:
    SIGNATURES = {
        "python":     [r"def \w+\(", r"import \w+", r"elif ", r":\s*$", r"self\."],
        "javascript": [r"function\s+\w+\(", r"const\s+\w+\s*=", r"=>", r"console\.log"],
        "typescript": [r"interface \w+", r":\s*(string|number|boolean)\b", r"import .* from"],
        "rust":       [r"fn\s+\w+\(", r"let mut", r"->\s*\w+", r"println!", r"impl "],
        "java":       [r"public class", r"System\.out\.println", r"public static void"],
        "csharp":     [r"using System", r"Console\.WriteLine", r"public static void Main"],
        "cpp":        [r"#include\s*<iostream>", r"std::", r"cout\s*<<", r"namespace "],
        "c":          [r"#include\s*<stdio\.h>", r"int main\(", r"printf\("],
        "go":         [r"package main", r"func \w+\(", r"fmt\.Println"],
        "ruby":       [r"puts ", r"require '", r"\bend\b", r"def \w+"],
        "php":        [r"<\?php", r"\$\w+\s*="],
        "swift":      [r"func \w+\(", r"import Swift", r"var \w+:\s*\w+"],
        "kotlin":     [r"fun \w+\(", r"val \w+", r"println\("],
        "sql":        [r"SELECT .* FROM", r"INSERT INTO", r"CREATE TABLE"],
        "html":       [r"<html", r"<div", r"<!DOCTYPE"],
        "css":        [r"\{[^}]*:\s*[^;]+;[^}]*\}", r"@media", r"px;"],
        "bash":       [r"#!/bin/bash", r"\becho\b", r"\$\{.*\}"],
        "r":          [r"<-\s*function", r"library\(", r"\bdisp\("],
        "scala":      [r"object \w+", r"def \w+\(", r"val \w+:"],
        "haskell":    [r"::\s*\w+", r"->", r"where\b", r"data \w+"],
        "lua":        [r"function\s+\w+", r"local\s+\w+", r"end\b"],
        "perl":       [r"\$\w+\s*=", r"use strict", r"print\s+"],
        "matlab":     [r"function\s+.*=", r"end\b", r"%\s"],
        "julia":      [r"function\s+\w+", r"end\b", r"using\s+\w+"],
        "dart":       [r"void\s+main", r"print\(", r"import 'package:"],
        "elixir":     [r"defmodule\s+", r"def\s+\w+", r"IO\.puts"],
        "erlang":     [r"-module\(", r"-export\(", r"io:format"],
        "clojure":    [r"\(defn\s+", r"\(ns\s+", r"\(let\s+\["],
        "fsharp":     [r"let\s+\w+\s*=", r"module\s+\w+", r"printfn"],
        "ocaml":      [r"let\s+\w+\s*=", r"module\s+\w+", r"->"],
        "groovy":     [r"def\s+\w+\s*=", r"println\s+", r"class\s+\w+"],
        "powershell": [r"\$\w+\s*=", r"Write-Host", r"Get-\w+"],
        "vba":        [r"Sub\s+\w+", r"Dim\s+\w+", r"End Sub"],
        "fortran":    [r"PROGRAM\s+\w+", r"END PROGRAM", r"INTEGER\s*::"],
        "cobol":      [r"IDENTIFICATION DIVISION", r"PROCEDURE DIVISION"],
        "assembly":   [r"mov\s+\w+", r"section\s+\.text", r"call\s+\w+"],
        "prolog":     [r":-", r"\?-", r"\w+\(.*\)\."],
        "scheme":     [r"\(define\s+", r"\(lambda\s+", r"\(let\s+\("],
        "lisp":       [r"\(defun\s+", r"\(setq\s+", r"\(lambda\s+"],
        "solidity":   [r"pragma solidity", r"contract\s+\w+", r"function\s+\w+"],
        "zig":        [r"const\s+\w+\s*=", r"pub fn\s+", r"@import"],
        "nim":        [r"proc\s+\w+", r"echo\s+", r"import\s+\w+"],
        "crystal":    [r"def\s+\w+", r"puts\s+", r"class\s+\w+"],
    }

    # Families / languages still missing or only partially covered by heuristics
    MISSING_OR_WEAK = [
        "APL / J / K (array languages)",
        "Ada",
        "Agda / Coq / Lean (proof assistants — need different detection)",
        "ALGOL family remnants",
        "Ballerina",
        "Chapel",
        "Clean",
        "D",
        "Elm",
        "Forth",
        "Gleam",
        "Hack",
        "Idris",
        "Io",
        "Mercury",
        "Nix",
        "Objective-C (partial overlap with C)",
        "Pony",
        "PureScript",
        "Racket (Scheme dialect)",
        "ReasonML / ReScript",
        "Smalltalk",
        "Tcl",
        "V (Vlang)",
        "WebAssembly text format (wat)",
        "Wolfram Language / Mathematica",
        "most domain-specific languages (DSLs) and obscure academic languages",
    ]

    def detect(self, code: str) -> str:
        scores = defaultdict(int)
        for lang, patterns in self.SIGNATURES.items():
            for pat in patterns:
                if re.search(pat, code, re.IGNORECASE | re.MULTILINE):
                    scores[lang] += 1
        return max(scores, key=scores.get) if scores else "unknown"

    def list_supported(self) -> List[str]:
        return sorted(self.SIGNATURES.keys())

    def list_missing(self) -> List[str]:
        return self.MISSING_OR_WEAK


# =============================================================================
# 5. PREDICTIVE SCORER + LEARNED TREND MODEL
# =============================================================================
class TinyTrendNet(nn.Module):
    """Minimal linear model: learns slope + intercept from a short series."""
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, x):
        return self.linear(x)


class PredictiveScorer:
    def __init__(self):
        self.device = torch.device("cpu")

    def trend_forecast(self, series: List[float], window: int = 3) -> Dict[str, float]:
        if len(series) < 2:
            return {"forecast": series[-1] if series else 0.0, "confidence": 0.0}
        window = min(window, len(series))
        recent = series[-window:]
        deltas = [recent[i + 1] - recent[i] for i in range(len(recent) - 1)]
        avg_delta = statistics.mean(deltas) if deltas else 0.0
        forecast = series[-1] + avg_delta
        variance = statistics.pvariance(recent) if len(recent) > 1 else 0.0
        confidence = 1 / (1 + variance)
        return {"forecast": round(forecast, 4), "confidence": round(confidence, 4)}

    def linear_regression_forecast(self, series: List[float], steps_ahead: int = 1) -> Dict[str, float]:
        n = len(series)
        if n < 2:
            return {"forecast": series[-1] if series else 0.0, "slope": 0.0}
        xs = list(range(n))
        x_mean, y_mean = statistics.mean(xs), statistics.mean(series)
        num = sum((xs[i] - x_mean) * (series[i] - y_mean) for i in range(n))
        den = sum((xs[i] - x_mean) ** 2 for i in range(n))
        slope = num / den if den else 0.0
        intercept = y_mean - slope * x_mean
        forecast = intercept + slope * (n - 1 + steps_ahead)
        return {"forecast": round(forecast, 4), "slope": round(slope, 4)}

    def learned_trend_forecast(self, series: List[float], steps_ahead: int = 1, epochs: int = 80) -> Dict[str, Any]:
        """Train a tiny torch linear model on the series itself (real gradient steps)."""
        if len(series) < 3:
            return {"error": "need at least 3 points", "forecast": series[-1] if series else 0.0}
        xs = torch.tensor([[float(i)] for i in range(len(series))], dtype=torch.float32)
        ys = torch.tensor([[float(v)] for v in series], dtype=torch.float32)
        model = TinyTrendNet()
        opt = torch.optim.Adam(model.parameters(), lr=0.05)
        loss_fn = nn.MSELoss()
        for _ in range(epochs):
            opt.zero_grad()
            pred = model(xs)
            loss = loss_fn(pred, ys)
            loss.backward()
            opt.step()
        with torch.no_grad():
            next_x = torch.tensor([[float(len(series) - 1 + steps_ahead)]], dtype=torch.float32)
            forecast = model(next_x).item()
            slope = model.linear.weight.item()
            intercept = model.linear.bias.item()
        return {
            "forecast": round(forecast, 4),
            "learned_slope": round(slope, 4),
            "learned_intercept": round(intercept, 4),
            "final_train_mse": round(loss.item(), 6),
            "note": "tiny linear net trained with real gradients on the supplied series"
        }

    def exponential_smoothing_forecast(self, series: List[float], alpha: float = 0.3) -> float:
        if not series:
            return 0.0
        s = series[0]
        for val in series[1:]:
            s = alpha * val + (1 - alpha) * s
        return round(s, 4)

    def elo_win_probability(self, rating_a: float, rating_b: float) -> float:
        return round(1 / (1 + 10 ** ((rating_b - rating_a) / 400)), 4)

    def implied_probability_from_american_odds(self, odds: float) -> float:
        if odds > 0:
            return round(100 / (odds + 100), 4)
        return round(-odds / (-odds + 100), 4)

    def kelly_criterion(self, win_prob: float, decimal_odds: float) -> float:
        b = decimal_odds - 1
        q = 1 - win_prob
        f = (b * win_prob - q) / b if b else 0.0
        return round(max(f, 0.0), 4)


# =============================================================================
# 6. TRANSLATOR — honest stub + wiring note
# =============================================================================
class Translator:
    def translate(self, text: str, target_lang: str) -> str:
        return (
            f"[translation unavailable offline for target '{target_lang}'] "
            f"To make this real: install deep-translator or call a cloud API "
            f"(Google, DeepL, LibreTranslate self-hosted) inside this method. "
            f"No free unlimited offline model is present in this sandbox."
        )


# =============================================================================
# 7. TOOL REGISTRY + COMBINATION GENERATOR
# =============================================================================
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, name: str, description: str = ""):
        def wrapper(fn):
            self._tools[name] = fn
            self._descriptions[name] = description or fn.__doc__ or ""
            return fn
        return wrapper

    def call(self, name: str, *args, **kwargs):
        if name not in self._tools:
            return f"[tool '{name}' not registered]"
        return self._tools[name](*args, **kwargs)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": n, "description": self._descriptions.get(n, "")} for n in sorted(self._tools)]

    def generate_combinations(self, max_k: int = 3) -> Dict[str, List[Tuple[str, ...]]]:
        """Generate all combinations of size 2..max_k. Deliberately capped; k=20 is impossible."""
        names = list(self._tools.keys())
        result = {}
        for k in range(2, min(max_k, len(names)) + 1):
            combos = list(itertools.combinations(names, k))
            # keep a manageable sample if too many
            if len(combos) > 50:
                random.seed(42)
                combos = random.sample(combos, 50)
            result[f"{k}-tool"] = combos
        return result


def build_default_tools() -> ToolRegistry:
    tools = ToolRegistry()

    @tools.register("unit_convert", "Convert between common units (km/mi, kg/lb, m/ft, C/F)")
    def unit_convert_tool(payload):
        value, from_unit, to_unit = payload
        table = {
            ("km", "mi"): 0.621371, ("mi", "km"): 1.60934,
            ("kg", "lb"): 2.20462, ("lb", "kg"): 0.453592,
            ("m", "ft"): 3.28084, ("ft", "m"): 0.3048,
            ("c", "f"): lambda c: c * 9 / 5 + 32,
            ("f", "c"): lambda f: (f - 32) * 5 / 9,
        }
        key = (from_unit.lower(), to_unit.lower())
        if key not in table:
            return f"[no conversion for {from_unit} -> {to_unit}]"
        factor = table[key]
        return round(factor(value), 4) if callable(factor) else round(value * factor, 4)

    @tools.register("text_stats", "Character / word count and rough reading time")
    def text_stats_tool(text):
        words = text.split()
        return {"chars": len(text), "words": len(words), "reading_time_sec": round(len(words) / 3.5, 1)}

    @tools.register("hash_sha256", "SHA-256 hex digest of a string")
    def hash_tool(text):
        return hashlib.sha256(text.encode()).hexdigest()

    @tools.register("base64_encode", "Base64 encode a string")
    def b64_encode_tool(text):
        return base64.b64encode(text.encode()).decode()

    @tools.register("base64_decode", "Base64 decode a string")
    def b64_decode_tool(text):
        return base64.b64decode(text.encode()).decode()

    @tools.register("timestamp_now", "UTC ISO timestamp")
    def timestamp_tool(_=None):
        return datetime.datetime.utcnow().isoformat() + "Z"

    @tools.register("json_pretty", "Pretty-print a JSON string")
    def json_pretty_tool(obj_str):
        try:
            return json.dumps(json.loads(obj_str), indent=2)
        except Exception as e:
            return f"[json error: {e}]"

    @tools.register("word_count", "Simple word counter")
    def word_count_tool(text):
        return len(text.split())

    @tools.register("reverse_text", "Reverse a string")
    def reverse_tool(text):
        return text[::-1]

    @tools.register("upper", "Upper-case a string")
    def upper_tool(text):
        return text.upper()

    @tools.register("lower", "Lower-case a string")
    def lower_tool(text):
        return text.lower()

    @tools.register("md5", "MD5 hex digest")
    def md5_tool(text):
        return hashlib.md5(text.encode()).hexdigest()

    return tools


# =============================================================================
# 8. EXPERIMENTAL THOUGHT LOOP (ley lines / gravity / magnetism)
#    Purely knowledge-ingestion + analogy generation. Labeled exploratory.
# =============================================================================
class ExperimentalThoughtLoop:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.history: List[Dict[str, Any]] = []

    def seed_concepts(self):
        seeds = [
            ("ley_lines", "Ley lines are hypothetical alignments of ancient sites and landscape features; modern science treats them as cultural or coincidence patterns rather than physical force lines."),
            ("gravity", "Gravity is the curvature of spacetime caused by mass-energy (general relativity) or equivalently a force (Newtonian approximation). It is always attractive and long-range."),
            ("magnetism", "Magnetism arises from moving electric charges and intrinsic magnetic moments of particles; described by Maxwell equations and quantum electrodynamics. Can attract or repel."),
        ]
        for cid, text in seeds:
            self.kb.add(cid, text)
        return {"seeded": [c[0] for c in seeds]}

    def mix_concepts(self, concepts: List[str] = None) -> Dict[str, Any]:
        """Generate experimental analogies by retrieving related KB entries and combining statements."""
        if concepts is None:
            concepts = ["ley lines", "gravity", "magnetism"]
        retrieved = []
        for c in concepts:
            hits = self.kb.query(c, top_k=2)
            retrieved.extend(hits)
        # Simple combinatorial mixing of excerpts
        analogies = []
        for a, b in itertools.combinations(retrieved, 2):
            analogy = (
                f"Experimental analogy: if we treat the pattern described in '{a['id']}' "
                f"({a['excerpt'][:60]}...) as structurally similar to '{b['id']}' "
                f"({b['excerpt'][:60]}...), then a mixed hypothesis could explore whether "
                f"geometric alignments might be re-interpreted through field or curvature language. "
                f"This remains speculative knowledge-play, not established physics."
            )
            analogies.append(analogy)
            # Grow the KB with the analogy itself
            self.kb.ingest_and_grow(analogy, source_id=f"analogy_{a['id']}_{b['id']}")
        record = {
            "concepts": concepts,
            "retrieved": retrieved,
            "analogies_generated": len(analogies),
            "sample_analogy": analogies[0] if analogies else None,
            "note": "Exploratory only — no physical claim is made."
        }
        self.history.append(record)
        return record


# =============================================================================
# 9. AUTONOMOUS PLANNER (simple decomposition)
# =============================================================================
class AutonomousPlanner:
    """Heuristic goal decomposer. Not an LLM planner — rule + keyword based."""

    TEMPLATES = {
        "research": ["search knowledge", "ingest related text", "summarize findings"],
        "math": ["solve equation", "derivative", "integral", "simplify"],
        "predict": ["learned trend", "linear forecast", "elo"],
        "code": ["detect language", "hash", "text stats"],
        "mix": ["seed concepts", "mix concepts", "search knowledge"],
    }

    def plan(self, goal: str) -> List[Dict[str, Any]]:
        g = goal.lower()
        steps = []
        # Order matters: more specific experimental goals first
        if any(k in g for k in ["ley", "gravity", "magnetism", "mix the concepts", "experimental"]):
            steps = [
                {"task": "seed concepts", "payload": None},
                {"task": "mix concepts", "payload": ["ley lines", "gravity", "magnetism"]},
                {"task": "search my knowledge", "payload": "experimental analogy field curvature"},
            ]
        elif any(k in g for k in ["math", "equation", "derivative", "integral"]):
            steps = [{"task": "solve equation", "payload": ("x**2 - 5*x + 6 = 0", "x")}]
        elif any(k in g for k in ["predict", "forecast", "trend"]):
            steps = [{"task": "learned trend", "payload": [1.0, 2.2, 3.1, 4.5, 5.8, 7.0]}]
        elif any(k in g for k in ["research", "study", "learn", "ingest"]):
            steps = [
                {"task": "search my knowledge", "payload": goal},
                {"task": "ingest text", "payload": f"User goal context: {goal}"},
            ]
        else:
            steps = [
                {"task": "search my knowledge", "payload": goal},
                {"task": "tool:text_stats", "payload": goal},
            ]
        return steps


# =============================================================================
# 10. ROUTER
# =============================================================================
class Router:
    def __init__(self, kb, math_engine, logic_engine, code_detector, predictor,
                 translator, tools, thought_loop, planner):
        self.kb = kb
        self.math = math_engine
        self.logic = logic_engine
        self.code = code_detector
        self.predictor = predictor
        self.translator = translator
        self.tools = tools
        self.thought = thought_loop
        self.planner = planner

    def route(self, task: str, payload: Any = None) -> Dict[str, Any]:
        t = task.lower().strip()

        if task.startswith("tool:"):
            return {"engine": "tool", "result": self.tools.call(task.split(":", 1)[1].strip(), payload)}

        if t == "plan" or t.startswith("plan "):
            goal = payload if payload else task[5:].strip()
            return {"engine": "planner", "result": self.planner.plan(goal)}

        if "seed concepts" in t:
            return {"engine": "thought.seed", "result": self.thought.seed_concepts()}

        if "mix concepts" in t or "thought loop" in t:
            return {"engine": "thought.mix", "result": self.thought.mix_concepts(payload)}

        if "ingest" in t:
            return {"engine": "kb.ingest", "result": self.kb.ingest_and_grow(payload or "")}

        if "learned trend" in t or "learned forecast" in t:
            return {"engine": "predictor.learned", "result": self.predictor.learned_trend_forecast(payload)}

        if "derivative" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.derivative", "result": self.math.derivative(*args)}
        if "integral" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.integral", "result": self.math.integral(*args)}
        if "limit" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.limit", "result": self.math.limit(*args)}
        if "series" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.series", "result": self.math.series_expand(*args)}
        if "equation" in t:
            args = payload if isinstance(payload, (list, tuple)) else (payload,)
            return {"engine": "math.solve_equation", "result": self.math.solve_equation(*args)}
        if "matrix" in t:
            op = "eigenvals" if "eigen" in t else "inverse" if "inverse" in t else "transpose" if "transpose" in t else "det"
            return {"engine": "math.matrix", "result": self.math.matrix_ops(payload, op)}
        if "factorize" in t or "prime" in t or "factorial" in t:
            op = "factorize" if "factorize" in t else "factorial" if "factorial" in t else "is_prime"
            return {"engine": "math.number_theory", "result": self.math.number_theory(payload, op)}
        if "gcd" in t or "lcm" in t:
            return {"engine": "math.gcd_lcm", "result": self.math.gcd_lcm(*payload)}
        if any(k in t for k in ["simplify", "calculate", "solve"]) and payload:
            return {"engine": "math.simplify", "result": self.math.simplify(payload)}

        if "satisfiable" in t:
            return {"engine": "logic.satisfiable", "result": self.logic.is_satisfiable(payload)}
        if "truth table" in t:
            expr, variables = payload
            return {"engine": "logic.truth_table", "result": self.logic.truth_table(expr, variables)}

        if "code language" in t or "detect language" in t:
            return {"engine": "code_lang", "result": self.code.detect(payload)}
        if "list languages" in t or "supported languages" in t:
            return {"engine": "code_lang.list", "result": self.code.list_supported()}
        if "missing languages" in t:
            return {"engine": "code_lang.missing", "result": self.code.list_missing()}

        if "linear forecast" in t:
            return {"engine": "predictor.linear", "result": self.predictor.linear_regression_forecast(payload)}
        if "exponential" in t:
            return {"engine": "predictor.exp_smooth", "result": self.predictor.exponential_smoothing_forecast(payload)}
        if any(k in t for k in ["trend", "predict", "forecast"]):
            return {"engine": "predictor.trend", "result": self.predictor.trend_forecast(payload)}
        if "elo" in t:
            return {"engine": "predictor.elo", "result": self.predictor.elo_win_probability(*payload)}
        if "kelly" in t:
            return {"engine": "predictor.kelly", "result": self.predictor.kelly_criterion(*payload)}
        if "implied probability" in t or "odds" in t:
            return {"engine": "predictor.implied_prob", "result": self.predictor.implied_probability_from_american_odds(payload)}

        if "translate" in t:
            text, lang = payload
            return {"engine": "translator", "result": self.translator.translate(text, lang)}

        if any(k in t for k in ["lookup", "recall", "search", "knowledge"]):
            return {"engine": "knowledge_base", "result": self.kb.query(payload)}

        if "list tools" in t:
            return {"engine": "tools.list", "result": self.tools.list_tools()}
        if "tool combinations" in t or "tool combos" in t:
            return {"engine": "tools.combos", "result": self.tools.generate_combinations(max_k=3)}

        return {"engine": "none", "result": f"[no handler matched for: '{task}']"}


# =============================================================================
# 11. AGENT LOOP
# =============================================================================
class AgentLoop:
    def __init__(self, router: Router):
        self.router = router
        self.history: List[Dict[str, Any]] = []

    def run(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        prev_result = None
        for task in tasks:
            payload = task.get("payload")
            if payload == "$PREV":
                payload = prev_result
            try:
                out = self.router.route(task["task"], payload)
            except Exception as e:
                out = {"engine": "error", "result": f"[agent error: {e}]"}
            record = {"task": task["task"], "payload": str(payload)[:120] if payload is not None else None, **out}
            self.history.append(record)
            results.append(record)
            prev_result = out.get("result")
        return results

    def run_goal(self, goal: str) -> List[Dict[str, Any]]:
        """Autonomous path: plan then execute the plan."""
        plan = self.router.route("plan", goal)["result"]
        print(f"[PLANNER] Goal: {goal}")
        print(f"[PLANNER] Generated {len(plan)} steps:")
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step['task']}")
        return self.run(plan)

    def save_history(self, path: str):
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2, default=str)


# =============================================================================
# TRAINING COMPUTE PLAN (honest)
# =============================================================================
TRAINING_COMPUTE_PLAN = """
REAL TRAINING COMPUTE PLAN (Kaggle-style GPU hours)
===================================================
What this script cannot do:
  - Allocate real GPU hours, pay for cloud, or run multi-day training jobs.
  - The environment here is a short-lived sandbox.

Practical path if you want a genuine small learned model beyond the tiny trend net:

1. Data
   - Collect 10k–100k domain examples (e.g. table-tennis match histories, or scientific abstracts).
   - Clean + tokenize. Keep a strict held-out split.

2. Model size that fits free/cheap tiers
   - 10M–100M parameter transformer or GRU.
   - Kaggle free tier: ~30 GPU hours / week (P100 or T4).
   - Google Colab free: intermittent T4/V100, subject to disconnection.
   - For serious runs: buy 100–500 A100 hours on Lambda / RunPod / Vast.ai (~$1–2 / hour).

3. Training recipe (sketch)
   - Start with character or BPE tokenizer.
   - Train 3–10 epochs with AdamW, cosine schedule, gradient checkpointing.
   - Log train vs held-out loss every epoch (as Oracle_Honest_and_Hard already does).
   - Export weights + report.

4. Integration back into this orchestrator
   - Replace PredictiveScorer.learned_trend_forecast with a loaded torch checkpoint.
   - Or add a new engine that runs inference on the trained model.

5. Cost estimate (order of magnitude)
   - Tiny trend net (what we have): seconds on CPU — free.
   - 50M param model, 5 epochs on 50k sequences: ~2–8 GPU hours → free on Kaggle or <$20 on cheap cloud.
   - Anything "better than existing LLMs": millions of GPU-hours and is outside script scope.

This plan is the honest boundary: the script can host inference and tiny on-the-fly training;
large-scale learning requires external compute you provision yourself.
"""


# =============================================================================
# CHECKLIST
# =============================================================================
CHECKLIST = [
    ("One combined system in one file",                "YES",     "Expanded single script."),
    ("Knowledge base + autonomous growth",             "YES",     "TF-IDF + ingest_and_grow + growth_log."),
    ("Router across specialized handlers",             "YES",     "Rule-based + new thought/planner routes."),
    ("Autonomous planning",                            "PARTIAL", "Heuristic goal → step list → AgentLoop execution. Not LLM planning."),
    ("Learned predictive model",                       "PARTIAL", "Tiny torch linear net trained with real gradients on supplied series."),
    ("Tool registry + combinations",                   "PARTIAL", "12 tools + auto 2- and 3-tool combo samples. Full 20-tool enumeration omitted (combinatorial explosion)."),
    ("Mathematical coverage",                          "PARTIAL", "Sympy: simplify/solve/diff/integrate/limit/series/matrix/number-theory/discrete."),
    ("Logic / formal reasoning",                       "PARTIAL", "Propositional SAT + truth tables."),
    ("Code languages",                                 "PARTIAL", "~40 signatures. Explicit missing list provided."),
    ("All spoken languages / translation",             "NO",      "Honest offline stub + wiring instructions."),
    ("World model / scientific discovery",             "NO",      "Experimental thought loops are analogy generation only."),
    ("GRU / MoE LLM",                                  "NO",      "Requires external training compute (see plan)."),
    ("Self-growing understanding beyond ingest",       "PARTIAL", "KB grows by ingestion + analogy writing; no genuine scientific insight generation."),
    ("Ley-lines / gravity / magnetism mixing",         "YES*",    "Implemented as labeled experimental knowledge play, not physics claim."),
]


def print_checklist():
    print("\n=== HONEST CHECKLIST ===")
    for item, status, note in CHECKLIST:
        print(f"[{status:7}] {item}\n           -> {note}")


# =============================================================================
# DEMO
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("ORCHESTRATOR EXPANDED — DEMO")
    print("=" * 70)

    kb = KnowledgeBase()
    math_engine = MathEngine()
    logic_engine = LogicEngine()
    code_detector = CodeLangDetector()
    predictor = PredictiveScorer()
    translator = Translator()
    tools = build_default_tools()
    thought = ExperimentalThoughtLoop(kb)
    planner = AutonomousPlanner()

    kb.add("note1", "TT Oracle uses ELO rankings and a cushion engine for table tennis betting decisions.")
    kb.add("note2", "Jarvis is a layered autonomous desktop agent using MCP tools and local Ollama models.")

    router = Router(kb, math_engine, logic_engine, code_detector, predictor,
                    translator, tools, thought, planner)
    agent = AgentLoop(router)

    # --- Classic capability demo ---
    demo_tasks = [
        {"task": "solve equation",     "payload": ("x**2 - 4 = 0", "x")},
        {"task": "derivative",         "payload": ("x**3 + 2*x", "x")},
        {"task": "integral",           "payload": ("2*x", "x")},
        {"task": "limit",              "payload": ("sin(x)/x", "x", "0")},
        {"task": "series expand",      "payload": ("exp(x)", "x", 5)},
        {"task": "matrix eigenvals",   "payload": [[1, 2], [2, 1]]},
        {"task": "is prime",           "payload": 97},
        {"task": "satisfiable",        "payload": "A & ~A"},
        {"task": "what code language", "payload": "fn main() { let mut x = 5; println!(\"{}\", x); }"},
        {"task": "list languages",     "payload": None},
        {"task": "missing languages",  "payload": None},
        {"task": "learned trend",      "payload": [1.0, 2.1, 3.0, 4.2, 5.1, 6.3]},
        {"task": "elo win probability","payload": (1800, 1650)},
        {"task": "kelly criterion",    "payload": (0.55, 2.0)},
        {"task": "search my knowledge","payload": "table tennis betting"},
        {"task": "list tools",         "payload": None},
        {"task": "tool combinations",  "payload": None},
        {"task": "tool:unit_convert",  "payload": (100, "km", "mi")},
        {"task": "tool:hash_sha256",   "payload": "hello world"},
        {"task": "translate",          "payload": ("hello", "japanese")},
    ]

    print("\n=== CORE DEMO TASKS ===")
    for r in agent.run(demo_tasks):
        # compact print
        res = r["result"]
        if isinstance(res, list) and len(res) > 5:
            res = f"[{len(res)} items] sample={res[:3]} ..."
        elif isinstance(res, dict) and len(str(res)) > 200:
            res = {k: (str(v)[:80] + "..." if len(str(v)) > 80 else v) for k, v in list(res.items())[:6]}
        print(f"  [{r['engine']}] {r['task'][:40]:40s} → {res}")

    # --- Autonomous planning demo ---
    print("\n=== AUTONOMOUS PLANNING DEMO (ley-lines / gravity / magnetism) ===")
    plan_results = agent.run_goal("study ley lines, gravity and magnetism and mix the concepts experimentally")
    for r in plan_results:
        res = r["result"]
        if isinstance(res, dict):
            res = {k: (str(v)[:100] + "..." if len(str(v)) > 100 else v) for k, v in res.items()}
        print(f"  [{r['engine']}] {r['task'][:40]:40s} → {res}")

    # --- Knowledge growth check ---
    print("\n=== KB AFTER GROWTH ===")
    print(f"  Total documents: {len(kb.docs)}")
    print(f"  Growth log entries: {len(kb.growth_log)}")
    hits = kb.query("experimental analogy", top_k=2)
    for h in hits:
        print(f"  hit: {h['id']} score={h['score']} | {h['excerpt'][:90]}...")

    print_checklist()
    print(TRAINING_COMPUTE_PLAN)
    print("=" * 70)
    print("DEMO COMPLETE — all runnable components executed.")
    print("=" * 70)
