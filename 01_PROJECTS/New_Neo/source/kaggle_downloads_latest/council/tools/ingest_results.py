#!/usr/bin/env python3
"""Validate and stage a returned benchmark run without making runtime claims.

This tool accepts two local files only. It does not download, extract archives,
execute returned code, or update CURRENT_STATE.json. A human/reviewer must
inspect the staged evidence before a later release changes runtime state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import smoke_scorer

MAX_INPUT_BYTES = 25 * 1024 * 1024
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
REQUIRED_REPORT_KEYS = {"schema_version", "run_id", "status", "evaluation", "memory", "timing"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_predictions(path: Path, expected_ids: set[str]) -> dict[str, str]:
    predictions: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or set(("id", "completion")) - set(row):
                raise ValueError(f"prediction line {line_no} lacks id or completion")
            ident, completion = row["id"], row["completion"]
            if not isinstance(ident, str) or not isinstance(completion, str):
                raise ValueError(f"prediction line {line_no} has non-string id or completion")
            if ident in predictions:
                raise ValueError(f"duplicate prediction id: {ident}")
            predictions[ident] = completion
    if set(predictions) != expected_ids:
        missing, extra = sorted(expected_ids - set(predictions)), sorted(set(predictions) - expected_ids)
        raise ValueError(f"prediction IDs do not match benchmark; missing={missing[:5]} extra={extra[:5]}")
    return predictions


def ingest(predictions_path: Path, report_path: Path, destination: Path) -> Path:
    for path in (predictions_path, report_path):
        if not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError(f"invalid input file: {path.name}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    missing = REQUIRED_REPORT_KEYS - set(report) if isinstance(report, dict) else REQUIRED_REPORT_KEYS
    if missing:
        raise ValueError(f"run report missing required keys: {sorted(missing)}")
    run_id = report["run_id"]
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        raise ValueError("run_id must be 1–80 safe filename characters")
    if report["status"] != "success":
        raise ValueError("only a successful worker report may be staged as a completed run")

    items = smoke_scorer.load_smoke()
    smoke_scorer.validate_benchmark(items)
    predictions = load_predictions(predictions_path, {x["id"] for x in items})
    evaluation = smoke_scorer.score_run(predictions, items)
    staging_parent = destination / ".staging"
    staging_parent.mkdir(parents=True, exist_ok=True)
    final = destination / run_id
    if final.exists():
        raise FileExistsError(f"run already exists: {run_id}")
    with tempfile.TemporaryDirectory(dir=staging_parent) as td:
        stage = Path(td)
        shutil.copy2(predictions_path, stage / "predictions.jsonl")
        shutil.copy2(report_path, stage / "run_report.json")
        (stage / "evaluation.json").write_text(json.dumps(evaluation, indent=2) + "\n", encoding="utf-8")
        receipt = {"run_id": run_id, "benchmark_sha256": hashlib.sha256((BASE / "datasets" / "smoke-v2.jsonl").read_bytes()).hexdigest(), "predictions_sha256": digest(predictions_path), "run_report_sha256": digest(report_path), "promotion": "staged-only; CURRENT_STATE.json unchanged"}
        (stage / "ingest_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        shutil.move(str(stage), str(final))
    return final


def main() -> int:
    p = argparse.ArgumentParser(description="Validate and stage a returned run")
    p.add_argument("predictions", type=Path)
    p.add_argument("run_report", type=Path)
    p.add_argument("--runs-dir", type=Path, default=BASE / "runs")
    args = p.parse_args()
    try:
        result = ingest(args.predictions.resolve(), args.run_report.resolve(), args.runs_dir.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"INGEST_REJECTED {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"INGEST_STAGED {result}")
    print("STATE_UNCHANGED review staged evidence before a release promotion")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
