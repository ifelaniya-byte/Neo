"""Settled RAG: only documents with license, as-of date, and checksum."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).parent
_CORPUS = _ROOT / "corpus.jsonl"


@dataclass
class SettledDoc:
    doc_id: str
    title: str
    text: str
    license: str
    as_of: str  # YYYY-MM-DD
    source: str
    tags: List[str] = field(default_factory=list)

    def checksum(self) -> str:
        blob = f"{self.doc_id}|{self.title}|{self.text}|{self.license}|{self.as_of}|{self.source}"
        return hashlib.sha256(blob.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["checksum"] = self.checksum()
        return d


def _ensure_seed_corpus() -> None:
    if _CORPUS.exists():
        return
    seeds = [
        SettledDoc(
            doc_id="seed-causality",
            title="Time-causal feature availability",
            text=(
                "A feature may only be used at decision time t if its availability "
                "timestamp is less than or equal to t. Future-leaking features are invalid."
            ),
            license="CC0-1.0",
            as_of="2026-01-01",
            source="internal-policy",
            tags=["causality", "ml"],
        ),
        SettledDoc(
            doc_id="seed-net-pnl",
            title="Net PnL accounting identity",
            text=(
                "Net PnL equals realized output minus input cost, gas, protocol fees, "
                "borrow fees, bridge fees, slippage, revert cost, and other configured costs."
            ),
            license="CC0-1.0",
            as_of="2026-01-01",
            source="internal-policy",
            tags=["accounting", "defi"],
        ),
        SettledDoc(
            doc_id="seed-abstain",
            title="Abstention as control",
            text=(
                "When uncertainty is high, constraints fail, or data is stale, the system "
                "must abstain rather than force a trade decision."
            ),
            license="CC0-1.0",
            as_of="2026-01-01",
            source="internal-policy",
            tags=["safety", "abstention"],
        ),
    ]
    with open(_CORPUS, "w", encoding="utf-8") as f:
        for d in seeds:
            f.write(json.dumps(d.to_dict()) + "\n")


def load_corpus() -> List[Dict[str, Any]]:
    _ensure_seed_corpus()
    docs = []
    with open(_CORPUS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def add_document(doc: SettledDoc) -> Dict[str, Any]:
    """Append only if license and as_of present (settled RAG contract)."""
    if not doc.license or not doc.as_of or not doc.text.strip():
        return {"ok": False, "reason": "missing license, as_of, or text"}
    _ensure_seed_corpus()
    with open(_CORPUS, "a", encoding="utf-8") as f:
        f.write(json.dumps(doc.to_dict()) + "\n")
    return {"ok": True, "doc_id": doc.doc_id, "checksum": doc.checksum()}


def search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    q = query.lower().split()
    hits = []
    for d in load_corpus():
        blob = (d.get("title", "") + " " + d.get("text", "") + " " + " ".join(d.get("tags", []))).lower()
        score = sum(1 for t in q if t in blob)
        if score:
            hits.append((score, d))
    hits.sort(key=lambda x: -x[0])
    return [h for _, h in hits[:limit]]
