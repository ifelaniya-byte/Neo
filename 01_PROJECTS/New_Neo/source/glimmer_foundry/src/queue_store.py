"""Restart-safe file-backed task queue."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class FileQueue:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def put(self, prompt: str, meta: Optional[dict] = None) -> str:
        task_id = str(uuid.uuid4())
        record = {
            "id": task_id,
            "prompt": prompt,
            "meta": meta or {},
            "enqueued_at": time.time(),
            "status": "pending",
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
        return task_id

    def get_pending(self, limit: int = 1) -> list[dict]:
        pending = []
        if not self.path.exists():
            return pending
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("status") == "pending":
                    pending.append(rec)
                    if len(pending) >= limit:
                        break
        return pending

    def mark_done(self, task_id: str, result: Any = None) -> None:
        self._rewrite(task_id, "done", result)

    def mark_failed(self, task_id: str, error: str) -> None:
        self._rewrite(task_id, "failed", {"error": error})

    def depth(self) -> int:
        return len(self.get_pending(limit=10_000))

    def _rewrite(self, task_id: str, status: str, result: Any) -> None:
        if not self.path.exists():
            return
        lines = self.path.read_text().splitlines()
        new_lines = []
        for line in lines:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("id") == task_id:
                rec["status"] = status
                rec["finished_at"] = time.time()
                if result is not None:
                    rec["result"] = result
            new_lines.append(json.dumps(rec))
        self.path.write_text("\n".join(new_lines) + ("\n" if new_lines else ""))
