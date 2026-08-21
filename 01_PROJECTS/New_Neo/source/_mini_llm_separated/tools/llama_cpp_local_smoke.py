#!/usr/bin/env python3
"""
Phase 0, last step — run the quantized GGUF locally, offline, through
llama-cpp-python, on the actual machine with the actual 8GB RAM budget.
No GPU. No network.

v2: fixes false-success reporting, a dead/duplicated record path, and a
load-failure path that previously produced no report at all.

Usage:
    pip install llama-cpp-python
    python3 tools/llama_cpp_local_smoke.py \
        --gguf /path/to/qwen2.5-0.5b-instruct-Q4_K_M.gguf \
        --manifest /path/to/gguf_manifest.json \
        --run-id local-smoke-0001

Writes to --out-dir (default: ./runs/local):
    predictions.jsonl   (id, completion — matches tools/ingest_results.py)
    run_report.json     (schema_version, run_id, status, evaluation, memory,
                          timing — matches ingest_results.py's REQUIRED_REPORT_KEYS)

Stage into repo run history the same way the Kaggle path does:
    python3 tools/ingest_results.py runs/local/predictions.jsonl runs/local/run_report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

# Windows compatibility for memory tracking
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False
    import psutil
    HAS_PSUTIL = True

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import smoke_scorer  # noqa: E402  (repo-local; same scorer worker_entry.py uses)


def peak_rss_bytes() -> int:
    if HAS_RESOURCE:
        # ru_maxrss is KB on Linux, bytes on macOS. Normalize to bytes.
        raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return raw * 1024 if sys.platform != "darwin" else raw
    elif HAS_PSUTIL:
        # Windows fallback using psutil
        process = psutil.Process()
        return process.memory_info().rss
    else:
        return 0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, value: object) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(value, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


class ArtifactValidationError(RuntimeError):
    """A supplied GGUF or manifest failed a mandatory gate.

    Deliberately a normal Exception subclass, not SystemExit. SystemExit
    inherits from BaseException, so `except Exception` in main() would not
    catch it -- the finally block would still write a report (finally
    always runs), but that report would be a bare placeholder with none of
    the actual error detail. Confirmed with a standalone repro before this
    fix went in.
    """


def validate_gguf(gguf_path: Path, manifest_path: Path | None) -> dict:
    if not gguf_path.is_file():
        raise ArtifactValidationError(f"GGUF does not exist: {gguf_path}")
    if gguf_path.suffix.lower() != ".gguf":
        raise ArtifactValidationError(f"expected a .gguf file, got: {gguf_path.name}")
    if gguf_path.stat().st_size < 1_000_000:
        raise ArtifactValidationError(f"GGUF is implausibly small ({gguf_path.stat().st_size} bytes)")

    digest = sha256_file(gguf_path)
    record = {"filename": gguf_path.name, "bytes": gguf_path.stat().st_size, "sha256": digest}

    if manifest_path is not None:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = manifest.get("files", {}).get(gguf_path.name)
        if expected is None:
            raise ArtifactValidationError(f"{gguf_path.name} not listed in {manifest_path}")
        if expected.get("sha256") != digest:
            raise ArtifactValidationError(
                f"GGUF hash mismatch: manifest says {expected.get('sha256')}, "
                f"actual file is {digest} — do not trust this artifact")
        record["manifest_verified"] = True
    else:
        record["manifest_verified"] = False

    return record


def run(gguf_info: dict, gguf_path: Path, out_dir: Path, n_ctx: int, n_threads: int,
        max_new_tokens: int) -> dict:
    from llama_cpp import Llama

    t_load0 = time.perf_counter()
    llm = Llama(
        model_path=str(gguf_path),
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_gpu_layers=0,   # CPU-only: the honest 8GB-RAM test, not a GPU shortcut
        seed=0,
        verbose=False,
    )
    load_seconds = time.perf_counter() - t_load0

    items = smoke_scorer.load_smoke()
    smoke_scorer.validate_benchmark(items)

    pred_path = out_dir / "predictions.jsonl"
    if pred_path.exists():
        pred_path.unlink()

    predictions: dict[str, str] = {}
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
            out_tok = int((resp.get("usage") or {}).get("completion_tokens") or 0)
            failed_this = False
        except Exception as exc:  # noqa: BLE001 — one record per item, success or failure
            completion = ""
            out_tok = 0
            failed_this = True
            failed += 1

        infer_s = round(time.perf_counter() - t0, 4)
        infer_total += infer_s
        output_tokens_total += out_tok
        predictions[it["id"]] = completion
        append_jsonl(pred_path, {"id": it["id"], "completion": completion})  # ingest_results.py format
        _ = failed_this  # kept for clarity; per-item failure isn't separately persisted beyond count

    evaluation = smoke_scorer.score_run(predictions, items)

    return {
        "status": "success" if failed == 0 else "partial-failure",
        "prediction_failures": failed,
        "predictions_written": len(predictions),
        "gguf": {**gguf_info, "quantization_hint": "unknown-not-read-from-gguf-metadata"},
        "benchmark": {
            "name": "smoke-v2",
            "records": len(items),
            "sha256": sha256_file(Path(smoke_scorer.SMOKE)),  # SMOKE is a str in the repo's scorer
            "scorer_sha256": sha256_file(Path(smoke_scorer.__file__)),
        },
        "generation": {"temperature": 0, "max_new_tokens": max_new_tokens, "n_ctx": n_ctx, "seed": 0},
        "evaluation": evaluation,
        "memory": {
            "peak_rss_bytes": peak_rss_bytes(),
            "ram_budget_bytes": 8 * 1_000_000_000,  # 8 GB decimal, matches the stated hardware spec
        },
        "timing": {
            "load_seconds": round(load_seconds, 3),
            "total_inference_seconds": round(infer_total, 4),
            "output_tokens_total": output_tokens_total,
            "tokens_per_second": (
                round(output_tokens_total / infer_total, 3) if infer_total else None),
        },
        "predictions_path": str(pred_path),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--gguf", type=Path, required=True)
    p.add_argument("--manifest", type=Path, default=None,
                    help="gguf_manifest.json from 20_export_gguf.ipynb — if given, the GGUF's "
                         "hash is checked against it before loading")
    p.add_argument("--run-id", required=True)
    p.add_argument("--n-ctx", type=int, default=2048)
    p.add_argument("--n-threads", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)),
                    help="default is conservative (<=4, leaves a core free) so an 8GB box stays usable")
    p.add_argument("--max-new-tokens", type=int, default=64)
    p.add_argument("--out-dir", type=Path, default=BASE / "runs" / "local")
    args = p.parse_args()

    OUT_DIR = args.out_dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUT_DIR / "run_report.json"
    completion_marker = OUT_DIR / "completion.marker"
    failure_marker = OUT_DIR / "failure.marker"

    # Clear stale evidence from a prior run BEFORE validation, not after --
    # otherwise a validation failure can leave last run's predictions.jsonl
    # sitting next to this run's failure report, which invites someone to
    # pair the wrong predictions with the wrong report.
    for stale in (OUT_DIR / "predictions.jsonl", completion_marker, failure_marker):
        stale.unlink(missing_ok=True)

    report = {
        "schema_version": 2,
        "run_id": args.run_id,
        "status": "failure",
        "environment": {
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "cpu_count": os.cpu_count(),
        },
    }
    try:
        gguf_info = validate_gguf(args.gguf, args.manifest)
        report.update(run(gguf_info, args.gguf, OUT_DIR, args.n_ctx, args.n_threads, args.max_new_tokens))
    except Exception as exc:
        # A load/run failure still produces a report — this is the fix for the "no report on
        # load failure" defect.
        report["status"] = "failure"
        report["error"] = {"type": type(exc).__name__, "message": str(exc)[:1000],
                            "trace_tail": traceback.format_exc()[-3000:]}
    finally:
        atomic_write_json(report_path, report)
        # Markers are written only after the report itself is safely on disk,
        # and are mutually exclusive -- a leftover marker from a previous run
        # was already cleared above, so only the current outcome's marker exists.
        if report["status"] == "success":
            atomic_write_text(completion_marker, args.run_id + "\n")
        else:
            atomic_write_text(failure_marker, args.run_id + "\n")

    print(json.dumps(report, indent=2))
    print(f"\nwrote {report_path}")
    raise SystemExit(0 if report["status"] == "success" else 1)
