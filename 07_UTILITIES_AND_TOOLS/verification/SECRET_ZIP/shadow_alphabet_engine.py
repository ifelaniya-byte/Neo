#!/usr/bin/env python3
"""
SHADOW ALPHABET ENGINE
======================
Your definition (paraphrased):
  Use the English alphabet to map textual gradients (and related structure)
  in order to relate and partially compute across mathematical languages.

What this module actually does (honest, runnable):
  1. Treats a–z as a 26-dimensional base axis (plus optional digits / case).
  2. Encodes any text into a normalized gradient vector over that axis.
  3. Computes gradient signatures, distances, and directional "textual gradients"
     between mathematical language forms and formulas.
  4. Ranks mathematical languages by similarity in this shadow space.
  5. Provides a small algebra of operations (blend, difference, project)
     so the mapping is computable, not merely decorative.

What it does NOT do:
  - It does not replace sympy, type theory, or any formal system.
  - It does not "fully compute all mathematical languages."
  - It is a coordinate / similarity layer over English orthography applied
    to a catalogue of mathematical languages — a useful tool, not a universal
    foundation for mathematics.

This is designed to sit alongside orchestrator_evolved.py / combined / complete.
"""

from __future__ import annotations
import re
import math
import json
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Optional

# ---------------------------------------------------------------------------
# Core alphabet axis
# ---------------------------------------------------------------------------
ENGLISH = "abcdefghijklmnopqrstuvwxyz"
AXIS = {ch: i for i, ch in enumerate(ENGLISH)}  # a=0 … z=25
DIM = len(ENGLISH)


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def encode(text: str, include_digits: bool = False) -> List[float]:
    """
    Map text → gradient vector of length 26 (English letters).
    Value at position i = relative frequency of letter ENGLISH[i].
    Optional: fold digits 0-9 into the first 10 slots as a weak extra signal.
    """
    t = _normalize_text(text)
    counts = [0.0] * DIM
    total = 0
    for ch in t:
        if ch in AXIS:
            counts[AXIS[ch]] += 1.0
            total += 1
        elif include_digits and ch.isdigit():
            counts[int(ch) % DIM] += 0.5
            total += 0.5
    if total == 0:
        return counts
    return [c / total for c in counts]


def signature(text: str) -> Dict[str, Any]:
    """Human-readable + vector signature."""
    vec = encode(text)
    # dominant letters
    ranked = sorted(
        [(ENGLISH[i], vec[i]) for i in range(DIM) if vec[i] > 0],
        key=lambda x: -x[1]
    )[:8]
    # centroid on the a–z line (0=a … 25=z)
    centroid = sum(i * vec[i] for i in range(DIM))
    # spread (second moment)
    spread = math.sqrt(sum(((i - centroid) ** 2) * vec[i] for i in range(DIM))) if any(vec) else 0.0
    return {
        "vector": [round(v, 5) for v in vec],
        "centroid": round(centroid, 4),
        "spread": round(spread, 4),
        "dominant": ranked,
        "text_preview": text[:80],
    }


def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def textual_gradient(text_a: str, text_b: str) -> Dict[str, Any]:
    """
    Directional gradient from A to B in shadow-alphabet space.
    Positive components = letters more present in B than A.
    """
    va, vb = encode(text_a), encode(text_b)
    delta = [vb[i] - va[i] for i in range(DIM)]
    # letters that increased / decreased most
    increased = sorted(
        [(ENGLISH[i], delta[i]) for i in range(DIM) if delta[i] > 1e-6],
        key=lambda x: -x[1]
    )[:6]
    decreased = sorted(
        [(ENGLISH[i], delta[i]) for i in range(DIM) if delta[i] < -1e-6],
        key=lambda x: x[1]
    )[:6]
    return {
        "from": text_a[:60],
        "to": text_b[:60],
        "delta_vector": [round(d, 5) for d in delta],
        "cosine_similarity": round(cosine(va, vb), 4),
        "euclidean_distance": round(euclidean(va, vb), 4),
        "letters_increased": increased,
        "letters_decreased": decreased,
        "centroid_shift": round(
            sum(i * vb[i] for i in range(DIM)) - sum(i * va[i] for i in range(DIM)), 4
        ),
    }


def blend(texts: List[str], weights: Optional[List[float]] = None) -> List[float]:
    """Weighted average of gradient vectors (shadow blend)."""
    if not texts:
        return [0.0] * DIM
    vecs = [encode(t) for t in texts]
    if weights is None:
        weights = [1.0 / len(vecs)] * len(vecs)
    s = sum(weights)
    weights = [w / s for w in weights]
    out = [0.0] * DIM
    for v, w in zip(vecs, weights):
        for i in range(DIM):
            out[i] += w * v[i]
    return out


# ---------------------------------------------------------------------------
# Mathematical-language catalogue (lightweight, aligned with evolved atlas)
# ---------------------------------------------------------------------------
MATH_LANGUAGES = [
    {"name": "Natural-language mathematics", "family": "Expository",
     "example": "For every real number x, x squared is nonnegative."},
    {"name": "Symbolic algebra", "family": "Algebraic",
     "example": "a squared plus b squared equals c squared"},
    {"name": "First-order logic", "family": "Formal logic",
     "example": "for all x if prime x and x greater than two then odd x"},
    {"name": "Set theory ZFC", "family": "Foundational",
     "example": "the set of x in reals such that x squared is nonnegative equals the reals"},
    {"name": "Category theory", "family": "Abstract structural",
     "example": "functor F composed with G from C to E"},
    {"name": "Tensor index notation", "family": "Physics",
     "example": "ricci tensor minus half scalar curvature times metric equals stress energy"},
    {"name": "Differential form notation", "family": "Geometry",
     "example": "exterior derivative of omega equals zero"},
    {"name": "Matrix notation", "family": "Linear algebra",
     "example": "matrix A times vector x equals vector b"},
    {"name": "Probability notation", "family": "Statistical",
     "example": "probability of A given B equals probability of B given A times probability of A over probability of B"},
    {"name": "Calculus Leibniz Newton", "family": "Analysis",
     "example": "integral from a to b of the derivative of f equals f of b minus f of a"},
    {"name": "Modal logic", "family": "Philosophical logic",
     "example": "necessarily P implies possibly P"},
    {"name": "Lambda calculus", "family": "Computational",
     "example": "lambda f lambda x f of f of x"},
    {"name": "Type theory", "family": "Foundational CS",
     "example": "context gamma proves term t has type T"},
    {"name": "Umbral shadow letters Whitehead", "family": "Shadow umbral",
     "example": "greek letter alpha as shadow of roman a assigning overlap properties"},
    {"name": "Umbral calculus", "family": "Shadow umbral",
     "example": "umbral power a to the n evaluates to sequence term a sub n"},
    {"name": "Combinatorial shadow", "family": "Shadow umbral",
     "example": "shadow of family A is all sets obtained by deleting one element from a member"},
    {"name": "Shadow theory semantics", "family": "Shadow umbral",
     "example": "every man denotes a shadow of individual type rather than higher type quantifier"},
    {"name": "Logic Alphabet Zellweger", "family": "Alternative logical alphabet",
     "example": "sixteen geometric letter shapes for the sixteen binary truth connectives"},
    {"name": "Dual opposite systems", "family": "Shadow dual",
     "example": "opposite category C op and dual vector space V star"},
]


class ShadowAlphabetEngine:
    """
    Uses the English alphabet as a gradient coordinate system over
    mathematical language descriptions and examples.
    """

    def __init__(self, languages: List[Dict[str, str]] = None):
        self.languages = languages or MATH_LANGUAGES
        self._cache: Dict[str, List[float]] = {}
        for lang in self.languages:
            key = lang["name"]
            blob = f"{lang['name']} {lang['family']} {lang['example']}"
            self._cache[key] = encode(blob)

    def encode_text(self, text: str) -> Dict[str, Any]:
        return signature(text)

    def gradient_between(self, text_a: str, text_b: str) -> Dict[str, Any]:
        return textual_gradient(text_a, text_b)

    def language_vector(self, name: str) -> Optional[List[float]]:
        return self._cache.get(name)

    def rank_languages(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Rank mathematical languages by cosine similarity in shadow space."""
        qv = encode(query)
        ranked = []
        for lang in self.languages:
            name = lang["name"]
            sim = cosine(qv, self._cache[name])
            ranked.append({
                "name": name,
                "family": lang["family"],
                "similarity": round(sim, 4),
                "example_preview": lang["example"][:70],
            })
        ranked.sort(key=lambda x: -x["similarity"])
        return ranked[:top_k]

    def pairwise_gradient(self, name_a: str, name_b: str) -> Dict[str, Any]:
        la = next((l for l in self.languages if l["name"] == name_a), None)
        lb = next((l for l in self.languages if l["name"] == name_b), None)
        if not la or not lb:
            return {"error": "language name not found", "available": [l["name"] for l in self.languages]}
        blob_a = f"{la['name']} {la['family']} {la['example']}"
        blob_b = f"{lb['name']} {lb['family']} {lb['example']}"
        return textual_gradient(blob_a, blob_b)

    def cluster_by_family(self) -> Dict[str, Any]:
        """Average gradient vector per family + nearest language to that center."""
        families = defaultdict(list)
        for lang in self.languages:
            families[lang["family"]].append(lang["name"])
        out = {}
        for fam, names in families.items():
            center = blend([f"{n} " + next(l["example"] for l in self.languages if l["name"] == n) for n in names])
            # nearest language to center
            best, best_sim = None, -1.0
            for n in names:
                sim = cosine(center, self._cache[n])
                if sim > best_sim:
                    best_sim, best = sim, n
            out[fam] = {
                "count": len(names),
                "centroid_preview": [round(x, 4) for x in center[:8]],
                "nearest_language": best,
                "nearest_similarity": round(best_sim, 4),
            }
        return out

    def project_formula(self, formula_text: str, top_k: int = 5) -> Dict[str, Any]:
        """Project a raw formula / statement into shadow space and rank languages."""
        sig = signature(formula_text)
        ranking = self.rank_languages(formula_text, top_k=top_k)
        return {
            "formula_signature": {
                "centroid": sig["centroid"],
                "spread": sig["spread"],
                "dominant": sig["dominant"],
            },
            "nearest_languages": ranking,
            "note": "Projection is orthographic gradient similarity, not formal equivalence.",
        }

    def full_report(self) -> Dict[str, Any]:
        return {
            "axis": "English a–z (26-dimensional frequency gradients)",
            "language_count": len(self.languages),
            "families": sorted({l["family"] for l in self.languages}),
            "cluster_summary": self.cluster_by_family(),
            "capability": (
                "Maps textual gradients over the English alphabet to relate mathematical "
                "language descriptions. Does not formally compute or prove statements "
                "inside those languages."
            ),
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 72)
    print("SHADOW ALPHABET ENGINE — English-alphabet textual gradients")
    print("for relating mathematical languages")
    print("=" * 72)

    engine = ShadowAlphabetEngine()

    print("\n[1] Encode a short mathematical phrase")
    print(engine.encode_text("for all x, x squared is nonnegative"))

    print("\n[2] Textual gradient between two descriptions")
    g = engine.gradient_between(
        "symbolic algebra with variables and equations",
        "first order logic with quantifiers and predicates",
    )
    print({k: g[k] for k in ["cosine_similarity", "euclidean_distance", "centroid_shift",
                              "letters_increased", "letters_decreased"]})

    print("\n[3] Rank mathematical languages for query: 'shadow umbral quantifier'")
    for row in engine.rank_languages("shadow umbral quantifier individual type", top_k=6):
        print(f"  {row['similarity']:.3f}  {row['name']}  [{row['family']}]")

    print("\n[4] Pairwise gradient: Combinatorial shadow → Umbral calculus")
    pg = engine.pairwise_gradient("Combinatorial shadow", "Umbral calculus")
    if "error" not in pg:
        print({k: pg[k] for k in ["cosine_similarity", "centroid_shift", "letters_increased"]})

    print("\n[5] Project a formula-like string into language space")
    proj = engine.project_formula(
        "the integral from a to b of the derivative of f equals f of b minus f of a"
    )
    print("  signature centroid/spread:", proj["formula_signature"]["centroid"],
          proj["formula_signature"]["spread"])
    print("  nearest languages:")
    for row in proj["nearest_languages"][:4]:
        print(f"    {row['similarity']:.3f}  {row['name']}")

    print("\n[6] Family clusters in shadow space")
    clusters = engine.cluster_by_family()
    for fam, info in list(clusters.items())[:8]:
        print(f"  {fam}: n={info['count']} nearest={info['nearest_language']} sim={info['nearest_similarity']}")

    print("\n[7] Full capability report")
    report = engine.full_report()
    print(json.dumps({k: report[k] for k in ["axis", "language_count", "families", "capability"]}, indent=2))

    print("\n" + "=" * 72)
    print("DONE — Shadow alphabet maps English-letter gradients over a catalogue")
    print("of mathematical languages. It does not formally compute those languages.")
    print("=" * 72)
