#!/usr/bin/env python3
"""
SHADOW ALPHABET — cryptographic verification layer for the Mathematical Language Atlas
=====================================================================================
Implements the architecture you described:

  Anatomy of a Shadow Entry
  -------------------------
  • shadow_word   — deterministic hyphenated ID (domain + hash prefix)
  • shadow_phrase — poetic NL sentence (domain + seeded verb + object)
  • shadow_stack  — JSON stack-machine program for verification
  • shadow_hash   — SHA-256 fingerprint of the sealed payload

  Mechanics
  ---------
  • Generation (sealing): concatenate core fields → SHA-256 → store
  • Verification (audit): reconstruct payload → re-hash → compare
  • Any single-character corruption flips the hash → COMPROMISED

  Purpose (framing)
  -----------------
  Tamper-evident integrity for long-term mathematical archives.
  Poetic bridge + executable stack + cryptographic seal.
  DNA / civilizational time-capsule encoding is stated as intended purpose;
  this script implements the digital verification engine only (no DNA synthesis
  hardware is present in this environment).

This module is self-contained and runnable. It can sit beside
orchestrator_combined / complete / evolved as the integrity layer.
"""

from __future__ import annotations
import hashlib
import json
import random
import sqlite3
import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# Lexicons for poetic shadow phrases (fixed lists → deterministic under seed)
# ---------------------------------------------------------------------------
VERBS = [
    "binds", "folds", "lifts", "projects", "seals", "reflects", "stabilizes",
    "transforms", "compresses", "verifies", "encodes", "decodes", "maps",
    "traces", "anchors", "resolves", "propagates", "absorbs", "emits", "converges",
]

OBJECTS = [
    "boundary", "kernel", "spectrum", "measure", "morphism", "invariant",
    "residue", "operator", "distribution", "functor", "gradient", "lattice",
    "fiber", "sheaf", "cobordism", "attractor", "eigenstate", "partition",
    "trajectory", "signal",
]

# ---------------------------------------------------------------------------
# Core deterministic generators
# ---------------------------------------------------------------------------
def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_shadow_word(name: str, domain: str) -> str:
    """
    Deterministic hyphenated identifier:
      <normalized-domain>-<8-char hash prefix of name>
    """
    dom = re_normalize(domain)
    prefix = _sha256(name)[:8]
    return f"{dom}-{prefix}"


def re_normalize(s: str) -> str:
    import re
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"


def make_shadow_phrase(name: str, domain: str) -> str:
    """
    Poetic sentence. RNG seeded by hash of formula name → same name = same phrase forever.
    """
    seed = int(_sha256(name)[:16], 16)
    rng = random.Random(seed)
    verb = rng.choice(VERBS)
    obj = rng.choice(OBJECTS)
    return f"the {domain.lower()} {verb} the {obj} and verifies {re_normalize(name)}"


def make_shadow_stack(
    name: str,
    domain: str,
    statement: str,
    latex: str,
    unicode_text: str,
    shadow_word: str,
    shadow_phrase: str,
    shadow_hash: str,
) -> List[List[str]]:
    """Miniature stack-machine program any decipherer can re-run."""
    return [
        ["PUSH_CONTEXT", name],
        ["PUSH_DOMAIN", domain],
        ["PUSH_STATEMENT", statement],
        ["PUSH_LATEX", latex or ""],
        ["PUSH_UNICODE", unicode_text or ""],
        ["PUSH_SHADOW_WORD", shadow_word],
        ["PUSH_SHADOW_PHRASE", shadow_phrase],
        ["EXPECT_HASH", shadow_hash],
        ["ASSERT_NONEMPTY"],
        ["VERIFY"],
        ["SEAL"],
    ]


def build_payload(
    name: str,
    domain: str,
    statement: str,
    latex: str,
    unicode_text: str,
    shadow_word: str,
    shadow_phrase: str,
) -> str:
    """Canonical concatenation used for hashing. Order is part of the contract."""
    parts = [
        name or "",
        domain or "",
        statement or "",
        latex or "",
        unicode_text or "",
        shadow_word or "",
        shadow_phrase or "",
    ]
    return "\n".join(parts)


def seal_formula(
    name: str,
    domain: str,
    statement: str,
    latex: str = "",
    unicode_text: str = "",
) -> Dict[str, Any]:
    """
    Full sealing lifecycle:
      1. shadow_word
      2. shadow_phrase
      3. payload (without hash)
      4. shadow_hash = SHA-256(payload)
      5. shadow_stack (includes EXPECT_HASH)
    """
    shadow_word = make_shadow_word(name, domain)
    shadow_phrase = make_shadow_phrase(name, domain)
    payload = build_payload(name, domain, statement, latex, unicode_text, shadow_word, shadow_phrase)
    shadow_hash = _sha256(payload)
    shadow_stack = make_shadow_stack(
        name, domain, statement, latex, unicode_text,
        shadow_word, shadow_phrase, shadow_hash
    )
    return {
        "name": name,
        "domain": domain,
        "statement": statement,
        "latex": latex,
        "unicode": unicode_text,
        "shadow_word": shadow_word,
        "shadow_phrase": shadow_phrase,
        "shadow_stack": shadow_stack,
        "shadow_hash": shadow_hash,
        "sealed_at": NOW,
        "payload_preview": payload[:120] + ("..." if len(payload) > 120 else ""),
    }


# ---------------------------------------------------------------------------
# Verification engine
# ---------------------------------------------------------------------------
def verify_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconstruct payload from current fields, re-hash, compare to stored shadow_hash
    and to EXPECT_HASH inside the stack.
    """
    name = entry.get("name", "")
    domain = entry.get("domain", "")
    statement = entry.get("statement", "")
    latex = entry.get("latex", "")
    unicode_text = entry.get("unicode", "")
    shadow_word = entry.get("shadow_word", "")
    shadow_phrase = entry.get("shadow_phrase", "")
    stored_hash = entry.get("shadow_hash", "")
    stack = entry.get("shadow_stack", [])

    # Reconstruct
    payload = build_payload(name, domain, statement, latex, unicode_text, shadow_word, shadow_phrase)
    recomputed = _sha256(payload)

    # EXPECT_HASH from stack
    expect_from_stack = None
    for op in stack:
        if op and op[0] == "EXPECT_HASH" and len(op) > 1:
            expect_from_stack = op[1]
            break

    match_stored = recomputed == stored_hash
    match_stack = (expect_from_stack is None) or (recomputed == expect_from_stack)
    nonempty = all([
        bool(name.strip()),
        bool(domain.strip()),
        bool(statement.strip()),
        bool(shadow_word.strip()),
        bool(shadow_phrase.strip()),
        bool(stored_hash.strip()),
    ])

    status = "INTACT" if (match_stored and match_stack and nonempty) else "COMPROMISED"
    return {
        "name": name,
        "status": status,
        "match_stored_hash": match_stored,
        "match_stack_expect": match_stack,
        "assert_nonempty": nonempty,
        "stored_hash": stored_hash,
        "recomputed_hash": recomputed,
        "expect_from_stack": expect_from_stack,
    }


def run_stack(stack: List[List[str]], entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal interpreter for the shadow stack.
    Supports the operations defined in the architecture.
    """
    machine = []
    log = []
    sealed = False
    verified = False

    for op in stack:
        if not op:
            continue
        code = op[0]
        arg = op[1] if len(op) > 1 else None

        if code.startswith("PUSH_"):
            machine.append(arg)
            log.append(f"PUSH {code[5:]} → {str(arg)[:40]}")
        elif code == "EXPECT_HASH":
            machine.append(arg)
            log.append(f"EXPECT_HASH {arg[:16]}...")
        elif code == "ASSERT_NONEMPTY":
            ok = all(x is not None and str(x).strip() != "" for x in machine)
            log.append(f"ASSERT_NONEMPTY → {ok}")
            if not ok:
                return {"ok": False, "log": log, "reason": "empty value on stack"}
        elif code == "VERIFY":
            # top of stack should be expected hash; recompute from entry
            result = verify_entry(entry)
            verified = result["status"] == "INTACT"
            log.append(f"VERIFY → {result['status']}")
            if not verified:
                return {"ok": False, "log": log, "reason": "hash mismatch", "detail": result}
        elif code == "SEAL":
            sealed = verified
            log.append(f"SEAL → {'sealed' if sealed else 'refused'}")
        else:
            log.append(f"UNKNOWN_OP {code}")

    return {"ok": sealed, "log": log, "verified": verified, "sealed": sealed}


# ---------------------------------------------------------------------------
# Atlas store with shadow columns
# ---------------------------------------------------------------------------
class ShadowAtlas:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS formulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            statement TEXT NOT NULL,
            latex TEXT,
            unicode TEXT,
            shadow_word TEXT,
            shadow_phrase TEXT,
            shadow_stack TEXT,
            shadow_hash TEXT,
            sealed_at TEXT,
            status TEXT DEFAULT 'SEALED'
        );
        CREATE TABLE IF NOT EXISTS verification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formula_name TEXT,
            status TEXT,
            detail TEXT,
            checked_at TEXT
        );
        """)
        self.conn.commit()

    def add_and_seal(
        self,
        name: str,
        domain: str,
        statement: str,
        latex: str = "",
        unicode_text: str = "",
    ) -> Dict[str, Any]:
        entry = seal_formula(name, domain, statement, latex, unicode_text)
        cur = self.conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO formulas
               (name, domain, statement, latex, unicode,
                shadow_word, shadow_phrase, shadow_stack, shadow_hash, sealed_at, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                entry["name"], entry["domain"], entry["statement"],
                entry["latex"], entry["unicode"],
                entry["shadow_word"], entry["shadow_phrase"],
                json.dumps(entry["shadow_stack"]), entry["shadow_hash"],
                entry["sealed_at"], "SEALED",
            ),
        )
        self.conn.commit()
        return entry

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM formulas WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        d["shadow_stack"] = json.loads(d["shadow_stack"] or "[]")
        return d

    def verify_shadows(self) -> List[Dict[str, Any]]:
        """Audit every sealed formula. Logs COMPROMISED entries."""
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM formulas")
        names = [r[0] for r in cur.fetchall()]
        results = []
        for name in names:
            entry = self.get(name)
            v = verify_entry(entry)
            # also run the stack
            stack_result = run_stack(entry["shadow_stack"], entry)
            v["stack_ok"] = stack_result["ok"]
            v["stack_log_tail"] = stack_result["log"][-3:]
            if v["status"] != "INTACT" or not stack_result["ok"]:
                v["status"] = "COMPROMISED"
                cur.execute(
                    "UPDATE formulas SET status = ? WHERE name = ?",
                    ("COMPROMISED", name),
                )
            cur.execute(
                "INSERT INTO verification_log (formula_name, status, detail, checked_at) VALUES (?,?,?,?)",
                (name, v["status"], json.dumps(v), NOW),
            )
            results.append(v)
        self.conn.commit()
        return results

    def corrupt_for_demo(self, name: str, field: str = "latex", new_value: str = "CORRUPTED") -> bool:
        """Intentionally corrupt a field to demonstrate detection."""
        cur = self.conn.cursor()
        if field not in ("latex", "unicode", "statement", "domain"):
            return False
        cur.execute(f"UPDATE formulas SET {field} = ? WHERE name = ?", (new_value, name))
        self.conn.commit()
        return True

    def list_entries(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT name, domain, shadow_word, shadow_phrase, shadow_hash, status FROM formulas"
        )
        return [dict(r) for r in cur.fetchall()]

    def close(self):
        self.conn.close()


# ---------------------------------------------------------------------------
# Seed formulas (including Euler identity as in the specification example)
# ---------------------------------------------------------------------------
SEED_FORMULAS = [
    {
        "name": "Fundamental theorem of calculus",
        "domain": "Analysis",
        "statement": "Integration and differentiation are inverse operations under suitable conditions.",
        "latex": r"\int_a^b f'(x)\,dx = f(b)-f(a)",
        "unicode": "∫_a^b f'(x) dx = f(b) − f(a)",
    },
    {
        "name": "Pythagorean theorem",
        "domain": "Geometry",
        "statement": "In a right triangle, the square of the hypotenuse equals the sum of the squares of the legs.",
        "latex": r"a^2+b^2=c^2",
        "unicode": "a² + b² = c²",
    },
    {
        "name": "Euler's identity",
        "domain": "Complex analysis",
        "statement": "The complex exponential of i times pi plus one equals zero.",
        "latex": r"e^{i\pi}+1=0",
        "unicode": "e^{iπ} + 1 = 0",
    },
    {
        "name": "Bayes' theorem",
        "domain": "Probability",
        "statement": "Posterior probability is proportional to likelihood times prior.",
        "latex": r"P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}",
        "unicode": "P(A|B) = P(B|A)P(A) / P(B)",
    },
    {
        "name": "Stokes' theorem",
        "domain": "Differential geometry",
        "statement": "Integral of a form over a boundary equals integral of its exterior derivative over the region.",
        "latex": r"\int_{\partial\Omega}\omega=\int_\Omega d\omega",
        "unicode": "∫_{∂Ω} ω = ∫_Ω dω",
    },
]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 74)
    print("SHADOW ALPHABET — cryptographic verification engine")
    print("Anatomy: shadow_word | shadow_phrase | shadow_stack | shadow_hash")
    print("=" * 74)

    atlas = ShadowAtlas()

    print("\n[SEAL] Sealing seed formulas...")
    for f in SEED_FORMULAS:
        entry = atlas.add_and_seal(
            name=f["name"],
            domain=f["domain"],
            statement=f["statement"],
            latex=f.get("latex", ""),
            unicode_text=f.get("unicode", ""),
        )
        print(f"\n  • {entry['name']}")
        print(f"    shadow_word  : {entry['shadow_word']}")
        print(f"    shadow_phrase: {entry['shadow_phrase']}")
        print(f"    shadow_hash  : {entry['shadow_hash'][:32]}...")
        print(f"    stack ops    : {len(entry['shadow_stack'])} instructions")

    print("\n[AUDIT] verify_shadows() on intact atlas...")
    results = atlas.verify_shadows()
    for r in results:
        print(f"  {r['status']:12}  {r['name']}")

    print("\n[DEMO] Corrupt Pythagorean theorem latex (a^2+b^2=c^2 → a^2+b^2=c^3)...")
    atlas.corrupt_for_demo("Pythagorean theorem", "latex", r"a^2+b^2=c^3")
    results2 = atlas.verify_shadows()
    for r in results2:
        flag = "← DETECTED" if r["status"] == "COMPROMISED" else ""
        print(f"  {r['status']:12}  {r['name']}  {flag}")

    print("\n[STACK] Run shadow stack for Euler's identity...")
    euler = atlas.get("Euler's identity")
    stack_out = run_stack(euler["shadow_stack"], euler)
    print(f"  stack ok={stack_out['ok']}  sealed={stack_out.get('sealed')}")
    for line in stack_out["log"]:
        print(f"    {line}")

    print("\n[LIST] All entries (word / phrase / status)")
    for e in atlas.list_entries():
        print(f"  [{e['status']}] {e['shadow_word']}")
        print(f"         {e['shadow_phrase']}")

    print("\n" + "=" * 74)
    print("SUMMARY")
    print("  Shadow Alphabet is the integrity layer of the Mathematical Language Atlas.")
    print("  • Human: poetic translation of rigid logic")
    print("  • Machine: zero-trust SHA-256 + stack verification")
    print("  • Archive: tamper-evident seal for long-term preservation")
    print("  DNA / civilizational encoding is purpose framing; this script")
    print("  implements the digital verification engine that such systems require.")
    print("=" * 74)

    atlas.close()
