#!/usr/bin/env python3
"""
KP-15/16 census. Two totals: project payload vs operational footprint.
No tokens. Generated census files are excluded from the walk.
"""

import json
import os
import time
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))

SKIP_DIR_PAYLOAD = {
    ".git", "__pycache__", ".arena", ".cache", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".venv", "node_modules", ".hf_disabled",
}
SKIP_FILE = {"access_token", ".env", ".netrc", "kaggle.json", ".git-credentials"}
SKIP_SUFFIX = {".pyc"}
GENERATED = {
    "program_census.json", "PROGRAM_CENSUS.md",
}
WEIGHT_EXT = {".safetensors", ".bin", ".gguf", ".pt", ".pth", ".ckpt"}
DATA_EXT = {".jsonl", ".csv", ".parquet", ".sqlite", ".arrow"}
CONFIG_NAMES = {
    "config.json", "tokenizer.json", "tokenizer_config.json",
    "generation_config.json", "special_tokens_map.json",
    "vocab.json", "merges.txt",
}


def classify(path):
    p = path.lower().replace("\\", "/")
    ext = os.path.splitext(p)[1]
    base = os.path.basename(p)
    if "adapter" in p and ext == ".safetensors":
        return "adapters"
    if ext in WEIGHT_EXT:
        return "weight-tensors"
    if p.endswith(".ipynb"):
        return "notebooks"
    if p.endswith(".py"):
        return "source"
    if ext in DATA_EXT:
        return "datasets"
    if base in CONFIG_NAMES:
        return "model-config"
    if base in {"license", "license.txt"} or base.endswith("license"):
        return "weight-metadata"
    if "weights_offline" in p:
        return "weight-metadata"
    if ext in {".html", ".md"}:
        return "docs"
    if ext == ".json":
        if any(w in p for w in ("log", "ledger", "history", "census",
                                "infer", "run_report", "usd_people")):
            return "logs"
        return "json"
    return "other"


def _stat_tree(root, skip_dirs, skip_generated=True):
    rows = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".git")]
        rel_root = os.path.relpath(dirpath, BASE)
        bucket = "." if rel_root == "." else rel_root.split(os.sep)[0]
        for fn in files:
            if fn in SKIP_FILE or os.path.splitext(fn)[1] in SKIP_SUFFIX:
                continue
            if fn.endswith(".kaggle_access_token"):
                continue
            if skip_generated and fn in GENERATED:
                continue
            path = os.path.join(dirpath, fn)
            try:
                st = os.stat(path)
            except OSError:
                continue
            rel = os.path.relpath(path, BASE)
            rows.append({
                "path": rel,
                "bytes": st.st_size,
                "blocks": st.st_blocks * 512,
                "bucket": bucket,
                "ext": os.path.splitext(fn)[1].lower() or "(none)",
                "class": classify(rel),
            })
    return rows


def _sum_path(path):
    if not os.path.exists(path):
        return 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for dp, dns, fns in os.walk(path):
        for fn in fns:
            try:
                total += os.path.getsize(os.path.join(dp, fn))
            except OSError:
                pass
    return total


def snapshot():
    payload_rows = _stat_tree(BASE, SKIP_DIR_PAYLOAD, skip_generated=True)
    by_class = defaultdict(lambda: {"n": 0, "bytes": 0, "blocks": 0})
    by_bucket = defaultdict(lambda: {"n": 0, "bytes": 0})
    for r in payload_rows:
        by_class[r["class"]]["n"] += 1
        by_class[r["class"]]["bytes"] += r["bytes"]
        by_class[r["class"]]["blocks"] += r["blocks"]
        by_bucket[r["bucket"]]["n"] += 1
        by_bucket[r["bucket"]]["bytes"] += r["bytes"]
    logical = sum(r["bytes"] for r in payload_rows)
    physical = sum(r["blocks"] for r in payload_rows)
    caches = {
        "home_cache": _sum_path(os.path.expanduser("~/.cache")),
        "hf_disabled": _sum_path(os.path.join(BASE, "weights_offline", ".hf_disabled")),
        "pycache": _sum_path(os.path.join(BASE, "__pycache__")),
        "git": _sum_path(os.path.join(BASE, ".git")),
        "venv": _sum_path(os.path.join(BASE, ".venv")),
    }
    try:
        import seat_registry
        seats = seat_registry.counts()
    except Exception as e:
        seats = {"error": str(e)[:120]}
    usd_sum = {}
    errors = []
    try:
        usd = json.load(open(os.path.join(BASE, "usd_people.json")))
        people = usd.get("people") or []
        minted_sum = sum(int(p.get("minted", p.get("earned_usd", 0))) for p in people)
        avail_sum = sum(int(p.get("available", p.get("available_usd", 0))) for p in people)
        usd_sum = {
            "n_people": usd.get("n_people"),
            "n_renters": usd.get("n_renters"),
            "global_minted": usd.get("global_minted"),
            "global_available": usd.get("global_available", avail_sum),
            "people_minted_sum": minted_sum,
            "people_available_sum": avail_sum,
            "escrow_locked": usd.get("escrow_locked"),
            "unit": usd.get("unit") or usd.get("currency"),
        }
        if minted_sum != usd.get("global_minted"):
            errors.append(
                f"ledger mismatch: people={minted_sum}, global={usd.get('global_minted')}")
    except Exception as e:
        errors.append(f"usd_people: {e}")
    if isinstance(seats, dict) and "n" in seats:
        status_sum = sum(seats.get(k, 0) for k in (
            "verified-checkpoint", "verified-api",
            "community-quarantine", "logical-emulated"))
        if status_sum != seats.get("n"):
            errors.append("seat status counts do not equal total seats")
    rec = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cwd": BASE,
        "n_files_payload": len(payload_rows),
        "project_payload_bytes": logical,
        "project_payload_physical_bytes": physical,
        "project_payload_mb": round(logical / 1e6, 2),
        "excluded_cache_bytes": caches,
        "git_bytes": caches["git"],
        "environment_bytes": caches["venv"],
        "operational_footprint_bytes": logical + sum(caches.values()),
        "operational_footprint_complete": False,
        "operational_footprint_scope": [
            "project payload",
            "~/.cache",
            "project .venv",
            "project .git",
            "selected pycache paths",
            "weights_offline/.hf_disabled",
        ],
        "operational_footprint_mb": round(
            (logical + sum(caches.values())) / 1e6, 2),
        "by_class": {k: v for k, v in sorted(by_class.items())},
        "by_topdir": {k: v for k, v in sorted(
            by_bucket.items(), key=lambda kv: -kv[1]["bytes"])},
        "largest_20": [
            {"bytes": r["bytes"], "path": r["path"], "class": r["class"]}
            for r in sorted(payload_rows, key=lambda r: -r["bytes"])[:20]
        ],
        "weight_tensors": [
            {"bytes": r["bytes"], "path": r["path"]}
            for r in payload_rows if r["class"] == "weight-tensors"
        ],
        "external_expected_artifacts": [{
            "id": "Qwen/Qwen2.5-0.5B-Instruct",
            "local_state": "absent",
            "expected_tensor_bytes": 988097824,
            "expected_tensor_sha256": "fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe",
        }],
        "historical_census_stale": True,
        "notebooks": [
            {"bytes": r["bytes"], "path": r["path"]}
            for r in payload_rows if r["class"] == "notebooks"
        ],
        "seats": seats,
        "usd": usd_sum,
        "secrets_present": {
            "kaggle_access_token_file": os.path.exists(
                os.path.expanduser("~/.kaggle/access_token")),
            "hf_token_env": bool(os.environ.get("HF_TOKEN")
                                 or os.environ.get("HUGGING_FACE_HUB_TOKEN")),
            "note": "boolean only — values not printed",
        },
        "experiments_completed": 0,
        "adapters_promoted": 0,
        "last_successful_gpu_run": None,
        "measured_peak_vram": None,
        "integrity_errors": errors,
        "integrity_ok": not errors,
        "honesty": (
            "Council USD points are simulated ledger units, not redeemable dollars. "
            "This sandbox has no GPU/torch/transformers. The expected Qwen2.5-0.5B tensor "
            "is absent from this recovered source tree; offline loading is unproven. No adapter "
            "is trained and no GPU run report is present."
        ),
    }
    return rec


def export_md(rec):
    def mb(n):
        return f"{n/1e6:.2f} MB"
    lines = [
        "# KP-16 program census",
        "",
        "ACORN_RULE: spoken co-signs beat disapproves; hold-peace is not consent.",
        "Technical gates still override popularity.",
        "",
        f"- Date: {rec['date']}",
        f"- Payload files: **{rec['n_files_payload']}**",
        f"- Project payload: **{rec['project_payload_mb']} MB**",
        f"- Operational footprint: **{rec['operational_footprint_mb']} MB** "
        f"(payload + caches/git/venv)",
        f"- Integrity: **{rec['integrity_ok']}** {rec.get('integrity_errors')}",
        "",
        "## By class",
        "",
        "| Class | Files | Logical |",
        "|---|---:|---:|",
    ]
    for k, v in rec["by_class"].items():
        lines.append(f"| {k} | {v['n']} | {mb(v['bytes'])} |")
    lines += ["", "## Weight tensors (actual)", ""]
    for r in rec.get("weight_tensors") or []:
        lines.append(f"- `{r['path']}` — {r['bytes']} bytes")
    lines += ["", "## Largest 20", "", "| Bytes | Class | Path |", "|---:|---|---|"]
    for r in rec["largest_20"]:
        lines.append(f"| {r['bytes']} | {r['class']} | `{r['path']}` |")
    lines += [
        "",
        "## Seats / USD",
        "",
        f"- seats: {rec.get('seats')}",
        f"- usd: {rec.get('usd')}",
        "",
        "## Honesty",
        "",
        rec.get("honesty") or "",
        "",
    ]
    return "\n".join(lines) + "\n"


def console(rec):
    print("\n" + "▦" * 72)
    print("KP-16 CENSUS — payload vs footprint, no secrets")
    print("▦" * 72)
    print(f"  payload {rec['project_payload_mb']} MB  "
          f"operational {rec['operational_footprint_mb']} MB  "
          f"files {rec['n_files_payload']}")
    print(f"  tensors {len(rec.get('weight_tensors') or [])}  "
          f"integrity={rec.get('integrity_ok')} {rec.get('integrity_errors')}")
    print(f"  seats {rec.get('seats')}")
    print(f"  usd {rec.get('usd')}")
    print("▦" * 72)


if __name__ == "__main__":
    rec = snapshot()
    jp = os.path.join(BASE, "program_census.json")
    mp = os.path.join(BASE, "PROGRAM_CENSUS.md")
    with open(jp, "w") as f:
        json.dump(rec, f, indent=2)
    with open(mp, "w") as f:
        f.write(export_md(rec))
    console(rec)
    print("wrote", jp, mp)
