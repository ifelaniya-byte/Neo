#!/usr/bin/env python3
"""
Cleared-LLM gateway: refuse any subject not double-pass cleared.

Does not call a real model by default. Provides a safe interface that:
  - accepts only subjects with allowed_for_llm=True (or runs double-pass first)
  - refuses blocked / uncleared inputs
  - never claims world-oracle authority
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from engineers import DoublePassEngineerGate, EngineerVerdict


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GatewayResult:
    status: str  # "ok" | "refused" | "error"
    reason: str = ""
    allowed_for_llm: bool = False
    engineer_verdict: Optional[str] = None
    response: Optional[str] = None
    subject_id: Optional[str] = None
    timestamp: str = field(default_factory=_utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "allowed_for_llm": self.allowed_for_llm,
            "engineer_verdict": self.engineer_verdict,
            "response": self.response,
            "subject_id": self.subject_id,
            "timestamp": self.timestamp,
        }


class ClearedLLMGateway:
    """
    LLM interpretation only after Stationary → NonStationary → Stationary PASS.

    llm_fn: optional callable(prompt: str, subject: Any) -> str
    If llm_fn is None, returns a deterministic stub response for cleared subjects.
    """

    def __init__(
        self,
        ledger_path: Optional[str] = None,
        llm_fn: Optional[Callable[..., str]] = None,
        require_fresh_double_pass: bool = True,
    ):
        self.gate = DoublePassEngineerGate(
            ledger_path=ledger_path or "artifacts/llm_gateway_ledger.jsonl"
        )
        self.llm_fn = llm_fn
        self.require_fresh_double_pass = require_fresh_double_pass
        self.refusal_log: List[Dict[str, Any]] = []

    def _already_cleared(self, subject: Any) -> bool:
        if isinstance(subject, dict):
            if subject.get("allowed_for_llm") is True:
                return True
            meta = subject.get("metadata") or {}
            if isinstance(meta, dict) and meta.get("allowed_for_llm") is True:
                return True
            eng = subject.get("engineer") or subject.get("double_pass") or {}
            if isinstance(eng, dict) and eng.get("allowed_for_llm") is True:
                return True
        return False

    def interpret(
        self,
        subject: Any,
        subject_id: str = "llm_subject",
        subject_type: str = "dict",
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Fast refuse: explicit deny flag
        if isinstance(subject, dict) and subject.get("allowed_for_llm") is False:
            res = GatewayResult(
                status="refused",
                reason="subject.allowed_for_llm is False",
                allowed_for_llm=False,
                subject_id=subject_id,
            )
            self.refusal_log.append(res.to_dict())
            return res.to_dict()

        allowed = False
        verdict = None

        if self.require_fresh_double_pass or not self._already_cleared(subject):
            # Always prefer a fresh double-pass for safety
            result = self.gate.run(subject, subject_id=subject_id, subject_type=subject_type)
            d = result.to_dict()
            verdict = d.get("final_verdict")
            allowed = bool(result.allowed_for_llm) and verdict == "PASS"
        else:
            allowed = True
            verdict = "PASS_CACHED"

        if not allowed:
            res = GatewayResult(
                status="refused",
                reason="not_cleared_by_double_pass",
                allowed_for_llm=False,
                engineer_verdict=str(verdict),
                subject_id=subject_id,
            )
            self.refusal_log.append(res.to_dict())
            return res.to_dict()

        # Cleared — optional LLM call
        text_prompt = prompt or (
            "Summarize this cleared simulation-assurance artifact. "
            "Do not claim complete knowledge or live trading capability.\n\n"
            + json.dumps(subject if not isinstance(subject, str) else {"text": subject}, default=str)[:4000]
        )
        if self.llm_fn is not None:
            try:
                response = self.llm_fn(text_prompt, subject)
            except Exception as e:
                return GatewayResult(
                    status="error",
                    reason=f"llm_fn_error:{e}",
                    allowed_for_llm=True,
                    engineer_verdict=str(verdict),
                    subject_id=subject_id,
                ).to_dict()
        else:
            response = (
                "[cleared-stub] Subject passed double-pass. "
                "No external LLM configured. "
                "This is simulation-assurance output only — not a world oracle, not live trading."
            )

        return GatewayResult(
            status="ok",
            reason="cleared",
            allowed_for_llm=True,
            engineer_verdict=str(verdict),
            response=response,
            subject_id=subject_id,
        ).to_dict()

    def interpret_file(self, path: Union[str, Path], subject_id: Optional[str] = None) -> Dict[str, Any]:
        path = Path(path)
        raw = path.read_text(encoding="utf-8")
        try:
            subject = json.loads(raw)
        except json.JSONDecodeError:
            subject = {"text": raw, "path": str(path)}
        return self.interpret(subject, subject_id=subject_id or path.name, subject_type="doc")
