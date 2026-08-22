#!/usr/bin/env python3
"""
Promote candidate facts into Known-Settled DB only after double-pass engineers clear them.
Hardened: every promotion is signed into a promotion ledger; verify before append.
Offline only — never mutates mid-replay silently.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from engineers import DoublePassEngineerGate, EngineerVerdict
from known_settled_db import SettledEntry, Confidence, get_settled_db
from signed_ledger import SignedLedger


@dataclass
class CandidateFact:
    id: str
    field: str
    statement: str
    formal: str
    assumptions: List[str]
    regime: str
    tags: List[str]
    source: str = "manual"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PromotionService:
    def __init__(
        self,
        ledger_path: Optional[str] = None,
        promote_log: Optional[str] = None,
        signed_ledger_path: Optional[str] = None,
    ):
        self.gate = DoublePassEngineerGate(
            ledger_path=ledger_path or "artifacts/promotion_ledger.jsonl"
        )
        self.promote_log = Path(promote_log or "artifacts/promoted_facts.jsonl")
        self.promote_log.parent.mkdir(parents=True, exist_ok=True)
        self.db = get_settled_db()
        self.signed = SignedLedger(
            path=signed_ledger_path or "artifacts/promotion_signed.jsonl"
        )

    def evaluate(self, candidate: CandidateFact) -> Dict[str, Any]:
        rej = self.db.reject_completeness_claim(candidate.statement + " " + candidate.formal)
        subject = candidate.to_dict()
        result = self.gate.run(subject, candidate.id, "dict")
        allowed = result.allowed_for_llm and rej.get("ok", True)
        return {
            "candidate_id": candidate.id,
            "double_pass": result.final_verdict.value if hasattr(result.final_verdict, "value") else str(result.final_verdict),
            "allowed_for_llm": result.allowed_for_llm,
            "completeness_ok": rej.get("ok", True),
            "promote_eligible": allowed and result.final_verdict == EngineerVerdict.PASS,
            "detail": result.to_dict(),
            "rejection": rej,
        }

    def promote(
        self,
        candidate: CandidateFact,
        force: bool = False,
        human_confirm: bool = True,
    ) -> Dict[str, Any]:
        evaluation = self.evaluate(candidate)
        if not evaluation["promote_eligible"] and not force:
            self.signed.append("promotion_rejected", {
                "candidate_id": candidate.id,
                "reason": "not_eligible",
            })
            return {"promoted": False, "reason": "not_eligible", "evaluation": evaluation}

        if candidate.id in getattr(self.db, "entries", {}) and not force:
            return {"promoted": False, "reason": "already_exists", "evaluation": evaluation}

        if not human_confirm and not force:
            return {"promoted": False, "reason": "human_confirm_required", "evaluation": evaluation}

        # Signed append BEFORE mutating KSKB
        signed_entry = self.signed.append("promotion_accepted", {
            "candidate": candidate.to_dict(),
            "evaluation_summary": {
                "double_pass": evaluation["double_pass"],
                "allowed_for_llm": evaluation["allowed_for_llm"],
            },
            "human_confirm": human_confirm,
        })

        # Verify ledger integrity after append
        verify = self.signed.verify_file()
        if not verify.get("ok"):
            return {
                "promoted": False,
                "reason": "signature_verify_failed",
                "verify": verify,
                "evaluation": evaluation,
            }

        entry = SettledEntry(
            id=candidate.id,
            field=candidate.field,
            statement=candidate.statement,
            formal=candidate.formal,
            assumptions=candidate.assumptions,
            regime=candidate.regime,
            tags=list(candidate.tags) + [f"source:{candidate.source}"],
            confidence=Confidence.SETTLED,
        )
        try:
            if hasattr(self.db, "entries"):
                self.db.entries[candidate.id] = entry
            if hasattr(self.db, "export"):
                data = self.db.export()
                Path("artifacts/known_settled_export.json").write_text(
                    json.dumps(data, indent=2, default=str)
                )
            elif hasattr(self.db, "to_dict"):
                Path("artifacts/known_settled_export.json").write_text(
                    json.dumps(self.db.to_dict(), indent=2, default=str)
                )
        except Exception as e:
            return {"promoted": False, "reason": f"db_append_failed:{e}", "evaluation": evaluation}

        with self.promote_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "promoted_at": datetime.now(timezone.utc).isoformat(),
                "candidate": candidate.to_dict(),
                "signature": signed_entry.signature,
                "entry_id": signed_entry.entry_id,
                "algorithm": signed_entry.algorithm,
            }, default=str) + "\n")

        return {
            "promoted": True,
            "candidate_id": candidate.id,
            "signature": signed_entry.signature,
            "entry_id": signed_entry.entry_id,
            "algorithm": signed_entry.algorithm,
            "verify": verify,
            "evaluation": evaluation,
        }

    def verify_promotion_ledger(self) -> Dict[str, Any]:
        return self.signed.verify_file()
