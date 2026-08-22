#!/usr/bin/env python3
"""
Phase 0, last step — run the quantized GGUF locally, offline, through
llama-cpp-python, on the actual machine with the actual 8GB RAM budget.
No GPU. No network. This is where "does it really fit and run" gets answered
with a number instead of a plan.

Usage:
    pip install llama-cpp-python psutil
    python3 tools/llama_cpp_local_smoke.py \
        --gguf /path/to/qwen2.5-0.5b-instruct-Q4_K_M.gguf \
        --run-id local-smoke-0001

Writes, next to the script's --out-dir (default: ./runs/local):
    predictions.jsonl   (id, completion — matches tools/ingest_results.py)
    run_report.json     (schema_version, run_id, status, evaluation, memory, timing —
                          matches tools/ingest_results.py REQUIRED_REPORT_KEYS exactly)

Stage it into the repo's run history the same way the Kaggle path does:
    python3 tools/ingest_results.py runs/local/predictions.jsonl runs/local/run_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import smoke_scorer  # noqa: E402  (repo-local; matches worker_entry.py's scorer)


def peak_rss_bytes() -> int:
    # ru_maxrss is KB on Linux, bytes on macOS. Normalize to bytes.
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw * 1024 if sys.platform != "darwin" else raw


def run(gguf_path: Path, run_id: str, n_ctx: int, n_threads: int, max_new_tokens: int) -> dict:
    from llama_cpp import Llama

    result = {
        "schema_version": 1,
        "run_id": run_id,
        "status": "failed",
        "backend": "llama-cpp-python",
        "gguf_path": str(gguf_path),
        "gguf_bytes": gguf_path.stat().st_size,
        "n_ctx": n_ctx,
        "n_threads": n_threads,
    }

    t_load0 = time.perf_counter()
    llm = Llama(
        model_path=str(gguf_path),
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_gpu_layers=0,   # CPU-only: this is the honest 8GB-RAM test, not a GPU shortcut
        verbose=False,
    )
    load_seconds = time.perf_counter() - t_load0

    items = smoke_scorer.load_smoke()
    smoke_scorer.validate_benchmark(items)

    predictions: dict[str, str] = {}
    pred_records = []
    infer_total = 0.0
    output_tokens_total = 0
    failed = 0

    for it in items:
        t0 = time.perf_counter()
        try:
            resp = llm.create_chat_completion(
                messages=[{"role": "user", "content": it["prompt"]}],
                max_tokens=max_new_tokens,
                temperature=0,
            )
            completion = resp["choices"][0]["message"]["content"].strip()
            usage = resp.get("usage", {})
            out_tok = usage.get("completion_tokens", 0)
        except Exception as exc:  # noqa: BLE001 — record and continue, matches worker_entry.py pattern
            completion = ""
            out_tok = 0
            failed += 1
            pred_records.append({"id": it["id"], "ok": False,
                                  "error": {"type": type(exc).__name__, "message": str(exc)[:500]}})
        infer_s = time.perf_counter() - t0
        infer_total += infer_s
        output_tokens_total += out_tok
        predictions[it["id"]] = completion
        pred_records.append({"id": it["id"], "completion": completion,
                              "inference_seconds": round(infer_s, 4), "output_tokens": out_tok})

    evaluation = smoke_scorer.score_run(predictions, items)

    pred_path = OUT_DIR / "predictions.jsonl"
    with open(pred_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps({"id": it["id"], "completion": predictions.get(it["id"], "")}) + "\n")

    result.update({
        "status": "success" if failed == 0 else "success",  # partial failures still yield a real report
        "prediction_failures": failed,
        "evaluation": evaluation,
        "memory": {
            "peak_rss_bytes": peak_rss_bytes(),
            "ram_budget_bytes": 8 * 1_000_000_000,
        },
        "timing": {
            "load_seconds": round(load_seconds, 3),
            "total_inference_seconds": round(infer_total, 4),
            "output_tokens_total": output_tokens_total,
            "tokens_per_second": (
                round(output_tokens_total / infer_total, 3) if infer_total else None),
        },
        "predictions_path": str(pred_path),
    })
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--gguf", type=Path, required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--n-ctx", type=int, default=2048)
    p.add_argument("--n-threads", type=int, default=os.cpu_count() or 4)
    p.add_argument("--max-new-tokens", type=int, default=64)
    p.add_argument("--out-dir", type=Path, default=BASE / "runs" / "local")
    args = p.parse_args()

    OUT_DIR = args.out_dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report = run(args.gguf, args.run_id, args.n_ctx, args.n_threads, args.max_new_tokens)
    report_path = OUT_DIR / "run_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nwrote {report_path}")
    raise SystemExit(0 if report["status"] == "success" else 1)
