#!/usr/bin/env python3
"""
Hardened signed ledgers for promotion and verification events.

Local HMAC-SHA256 (always available) + optional Ed25519 when cryptography
is installed. Never used for live chain signing — artifact integrity only.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SignedEntry:
    entry_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: str
    key_id: str
    algorithm: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SigningKeyStore:
    """Local key material for ledger integrity. Never for live chain txs."""

    def __init__(self, key_dir: Optional[str] = None):
        self.key_dir = Path(key_dir or "artifacts/keys")
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.hmac_path = self.key_dir / "ledger_hmac.key"
        self.meta_path = self.key_dir / "key_meta.json"
        self._hmac_key: Optional[bytes] = None
        self._ed25519 = False
        self._ed25519_priv = None
        self._ed25519_pub_hex: Optional[str] = None
        self.key_id = "unset"
        self._load_or_create()

    def _load_or_create(self) -> None:
        if self.hmac_path.exists():
            self._hmac_key = self.hmac_path.read_bytes()
        else:
            self._hmac_key = secrets.token_bytes(32)
            self.hmac_path.write_bytes(self._hmac_key)
            try:
                os.chmod(self.hmac_path, 0o600)
            except OSError:
                pass
        meta = {
            "key_id": hashlib.sha256(self._hmac_key).hexdigest()[:16],
            "algorithms": ["HMAC-SHA256"],
            "purpose": "artifact_ledger_integrity_only",
            "created": _utc_now(),
        }
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives import serialization

            priv_path = self.key_dir / "ledger_ed25519.pem"
            if priv_path.exists():
                pem = priv_path.read_bytes()
                self._ed25519_priv = serialization.load_pem_private_key(pem, password=None)
            else:
                self._ed25519_priv = Ed25519PrivateKey.generate()
                pem = self._ed25519_priv.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                priv_path.write_bytes(pem)
                try:
                    os.chmod(priv_path, 0o600)
                except OSError:
                    pass
            pub = self._ed25519_priv.public_key()
            pub_bytes = pub.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            self._ed25519_pub_hex = pub_bytes.hex()
            meta["algorithms"].append("Ed25519")
            meta["ed25519_public_hex"] = self._ed25519_pub_hex
            self._ed25519 = True
        except Exception:
            self._ed25519 = False
        if self.meta_path.exists():
            old = json.loads(self.meta_path.read_text())
            meta["created"] = old.get("created", meta["created"])
            meta["key_id"] = old.get("key_id", meta["key_id"])
        self.meta_path.write_text(json.dumps(meta, indent=2))
        self.key_id = meta["key_id"]

    def sign_hmac(self, payload: Dict[str, Any]) -> str:
        assert self._hmac_key is not None
        return hmac.new(self._hmac_key, _canonical(payload), hashlib.sha256).hexdigest()

    def verify_hmac(self, payload: Dict[str, Any], signature: str) -> bool:
        expected = self.sign_hmac(payload)
        return hmac.compare_digest(expected, signature)

    def sign_ed25519(self, payload: Dict[str, Any]) -> Optional[str]:
        if not self._ed25519 or self._ed25519_priv is None:
            return None
        sig = self._ed25519_priv.sign(_canonical(payload))
        return sig.hex()

    def algorithms(self) -> List[str]:
        algs = ["HMAC-SHA256"]
        if self._ed25519:
            algs.append("Ed25519")
        return algs


class SignedLedger:
    """Append-only signed JSONL ledger for promotions and verification events."""

    def __init__(
        self,
        path: Optional[str] = None,
        key_store: Optional[SigningKeyStore] = None,
        prefer_ed25519: bool = True,
    ):
        self.path = Path(path or "artifacts/signed_ledger.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.keys = key_store or SigningKeyStore()
        self.prefer_ed25519 = prefer_ed25519

    def append(self, event_type: str, payload: Dict[str, Any]) -> SignedEntry:
        body = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": _utc_now(),
            "key_id": self.keys.key_id,
        }
        alg = "HMAC-SHA256"
        sig = self.keys.sign_hmac(body)
        if self.prefer_ed25519:
            ed = self.keys.sign_ed25519(body)
            if ed:
                alg = "Ed25519+HMAC-SHA256"
                body["hmac_sha256"] = sig
                sig = ed
        entry_id = hashlib.sha256(_canonical(body) + sig.encode()).hexdigest()[:16]
        entry = SignedEntry(
            entry_id=entry_id,
            event_type=event_type,
            payload=payload,
            timestamp=body["timestamp"],
            key_id=self.keys.key_id,
            algorithm=alg,
            signature=sig,
        )
        record = entry.to_dict()
        if "hmac_sha256" in body:
            record["hmac_sha256"] = body["hmac_sha256"]
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return entry

    def verify_file(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"ok": True, "n": 0, "failures": []}
        failures = []
        n = 0
        with self.path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                n += 1
                rec = json.loads(line)
                body = {
                    "event_type": rec["event_type"],
                    "payload": rec["payload"],
                    "timestamp": rec["timestamp"],
                    "key_id": rec["key_id"],
                }
                alg = rec.get("algorithm", "HMAC-SHA256")
                if "HMAC" in alg:
                    hmac_sig = rec.get("hmac_sha256") or (
                        rec["signature"] if alg == "HMAC-SHA256" else None
                    )
                    if hmac_sig is None or not self.keys.verify_hmac(body, hmac_sig):
                        failures.append({
                            "line": line_no,
                            "entry_id": rec.get("entry_id"),
                            "reason": "hmac_mismatch",
                        })
                if "Ed25519" in alg and self.keys._ed25519_priv is not None:
                    try:
                        pub = self.keys._ed25519_priv.public_key()
                        pub.verify(bytes.fromhex(rec["signature"]), _canonical(body))
                    except Exception as e:
                        failures.append({
                            "line": line_no,
                            "entry_id": rec.get("entry_id"),
                            "reason": f"ed25519_fail:{e}",
                        })
        return {"ok": len(failures) == 0, "n": n, "failures": failures}

    def recent(self, n: int = 10) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").strip().splitlines()
        out = []
        for line in lines[-n:]:
            if line.strip():
                out.append(json.loads(line))
        return out
