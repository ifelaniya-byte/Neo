#!/usr/bin/env python3
"""
WEIGHT SOURCE — ModelScope / Kaggle first. Hugging Face offline + no-cache.

Policy (King's Word):
  1. Never use the HF token unless WEIGHTS_ALLOW_HF_TOKEN=1 AND ModelScope
     (and Kaggle) cannot serve the file.
  2. Hugging Face stays OFFLINE until included credits reappear.
  3. Built-in no-cache: do not write ~/.cache/huggingface.
  4. Local copies live under weights_offline/ (ModelScope-origin).

This sandbox still has no GPU and no torch. A pulled .safetensors is a
local file, not a running checkpoint.

USED BY: model_council.py, gpu_lane.py
"""

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OFFLINE_ROOT = os.path.join(BASE, "weights_offline")
MS_API = "https://www.modelscope.cn/api/v1/models"
MS_RESOLVE = "https://www.modelscope.cn/models/{mid}/resolve/master/{path}"

# Prefer these ModelScope ids (no HF token). Tiny first.
MS_CATALOG = {
    "qwen2.5-0.5b": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen3.6-27b": "Qwen/Qwen3.6-27B",
    "phi-4": "LLM-Research/Phi-4",
    "internlm2-1.8b": "Shanghai_AI_Laboratory/internlm2-1_8b",
}

UA = "model-council/weight-source"


def apply_offline_policy():
    """Force HF offline + no implicit token + no HF cache. Call at process start."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    # built-in no-cache: point HF home at a discarded dir we never create
    os.environ["HF_HOME"] = os.path.join(OFFLINE_ROOT, ".hf_disabled")
    os.environ["HF_HUB_CACHE"] = os.path.join(OFFLINE_ROOT, ".hf_disabled", "hub")
    os.environ["TRANSFORMERS_CACHE"] = os.path.join(OFFLINE_ROOT, ".hf_disabled", "transformers")
    if os.environ.get("WEIGHTS_ALLOW_HF_TOKEN") != "1":
        os.environ.pop("HF_TOKEN", None)
        os.environ.pop("HUGGING_FACE_HUB_TOKEN", None)
    os.makedirs(OFFLINE_ROOT, exist_ok=True)
    return {
        "hf_offline": os.environ.get("HF_HUB_OFFLINE"),
        "hf_token_in_env": bool(os.environ.get("HF_TOKEN")),
        "allow_hf_token": os.environ.get("WEIGHTS_ALLOW_HF_TOKEN") == "1",
        "offline_root": OFFLINE_ROOT,
    }


def _ctx():
    return ssl.create_default_context()


def _get(url, dest=None, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        data = r.read()
        if dest:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
        return r.status, data, dict(r.headers)


def ms_model(mid):
    status, raw, _ = _get(f"{MS_API}/{mid}", timeout=20)
    return json.loads(raw.decode())


def ms_files(mid):
    status, raw, _ = _get(
        f"{MS_API}/{mid}/repo/files?Revision=master&Recursive=1&PageSize=80",
        timeout=25)
    d = json.loads(raw.decode())
    data = d.get("Data") or {}
    return data.get("Files") or []


def ms_pull_file(mid, rel, dest=None, timeout=180):
    dest = dest or os.path.join(OFFLINE_ROOT, "modelscope", mid.replace("/", "__"), rel)
    url = MS_RESOLVE.format(mid=mid, path=urllib.parse.quote(rel))
    status, data, hdrs = _get(url, dest=dest, timeout=timeout)
    return {"ok": status == 200, "status": status, "bytes": len(data),
            "path": dest, "source": "modelscope", "mid": mid, "file": rel}


def kaggle_status():
    """Prefer Bearer KGAT token. Legacy kaggle.json is optional."""
    rec = {"ok": False, "source": "kaggle", "api": None, "note": ""}
    token = ""
    tp = os.path.expanduser("~/.kaggle/access_token")
    try:
        token = open(tp).read().strip()
    except OSError:
        token = (os.environ.get("KAGGLE_API_TOKEN") or "").strip()
    rec["has_access_token"] = token.startswith("KGAT_")
    rec["has_kaggle_json"] = os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json"))
    headers = {"User-Agent": UA}
    if rec["has_access_token"]:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(
            "https://www.kaggle.com/api/v1/models/list?search=phi&pageSize=1",
            headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=_ctx()) as r:
            rec["api"] = r.status
            rec["ok"] = True
            rec["note"] = "Bearer KGAT accepted. Catalog works. Shard download still needs kagglehub/CLI on a Kaggle runtime."
    except urllib.error.HTTPError as e:
        rec["api"] = e.code
        rec["note"] = f"Kaggle API HTTP {e.code}. Token present={rec['has_access_token']}."
    except Exception as e:
        rec["note"] = str(e)[:200]
    return rec


def pull_small_qwen():
    """Pull Qwen2.5-0.5B-Instruct metadata + weights from ModelScope (no HF)."""
    mid = MS_CATALOG["qwen2.5-0.5b"]
    out = {"mid": mid, "files": [], "errors": []}
    wanted = [
        "config.json", "generation_config.json", "tokenizer_config.json",
        "LICENSE", "README.md", "model.safetensors",
    ]
    files = { (f.get("Path") or f.get("Name")): f for f in ms_files(mid) }
    out["listed"] = sorted(files)
    for rel in wanted:
        meta = files.get(rel) or {}
        size = int(meta.get("Size") or 0)
        dest = os.path.join(OFFLINE_ROOT, "modelscope", mid.replace("/", "__"), rel)
        if os.path.exists(dest) and os.path.getsize(dest) == size and size > 0:
            out["files"].append({"file": rel, "bytes": size, "path": dest, "cached": True, "ok": True})
            continue
        timeout = 900 if rel.endswith(".safetensors") else 60
        try:
            rec = ms_pull_file(mid, rel, dest=dest, timeout=timeout)
            rec["listed_size"] = size
            out["files"].append(rec)
        except Exception as e:
            out["errors"].append({"file": rel, "error": str(e)[:200]})
    return out


def pull_cards_only():
    """Configs/licenses for bigger seats — never the multi-GB shards."""
    cards = []
    for key, mid in (
        ("qwen3.6-27b", MS_CATALOG["qwen3.6-27b"]),
        ("phi-4", MS_CATALOG["phi-4"]),
    ):
        row = {"key": key, "mid": mid, "files": [], "errors": []}
        try:
            listing = ms_files(mid)
            names = { (f.get("Path") or f.get("Name")): f for f in listing }
            row["n_listed"] = len(names)
            for rel in ("config.json", "LICENSE", "generation_config.json"):
                if rel not in names:
                    continue
                rec = ms_pull_file(mid, rel)
                row["files"].append(rec)
        except Exception as e:
            row["errors"].append(str(e)[:200])
        cards.append(row)
    return cards


def report():
    pol = apply_offline_policy()
    rec = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "policy": pol,
        "kaggle": kaggle_status(),
        "modelscope_ok": False,
        "modelscope_error": None,
    }
    try:
        info = ms_model("Qwen/Qwen2.5-0.5B-Instruct")
        rec["modelscope_ok"] = (info.get("Code") == 200)
        rec["qwen05_license"] = (info.get("Data") or {}).get("License")
        rec["qwen05_downloads"] = (info.get("Data") or {}).get("Downloads")
    except Exception as e:
        rec["modelscope_error"] = str(e)[:200]
    return rec


def console_sources(rec, pull=None, cards=None):
    print("\n" + "▒" * 72)
    print("WEIGHT SOURCE — ModelScope / Kaggle first · HF offline · no cache")
    print("▒" * 72)
    p = rec.get("policy") or {}
    print(f"  HF_HUB_OFFLINE={p.get('hf_offline')}  HF_TOKEN in env={p.get('hf_token_in_env')}  "
          f"allow_hf_token={p.get('allow_hf_token')}")
    print(f"  local root: {p.get('offline_root')}")
    print(f"  ModelScope: {'up' if rec.get('modelscope_ok') else 'down'}  "
          f"Qwen2.5-0.5B-Instruct license={rec.get('qwen05_license')} dl={rec.get('qwen05_downloads')}")
    k = rec.get("kaggle") or {}
    print(f"  Kaggle: api={k.get('api')} json={k.get('has_kaggle_json')} — {k.get('note')}")
    if pull:
        print("  Pulled Qwen2.5-0.5B-Instruct:")
        for f in pull.get("files") or []:
            print(f"     {'ok' if f.get('ok') else 'no':>3} {f.get('file')}  {f.get('bytes')} B  "
                  f"{'(already local)' if f.get('cached') else ''}")
        for e in pull.get("errors") or []:
            print(f"     ERR {e}")
    if cards:
        for c in cards:
            print(f"  card {c['key']} ({c['mid']}) listed={c.get('n_listed')} "
                  f"got={len(c.get('files') or [])}")
    print("▒" * 72)


def export_md(rec, pull=None, cards=None):
    lines = [
        "# Weight sources — ModelScope first, HF offline, no cache",
        "",
        "HF token is **not** used unless `WEIGHTS_ALLOW_HF_TOKEN=1`.",
        "HF Hub is forced **offline**. No `~/.cache/huggingface`.",
        "",
        f"- Date: {rec.get('date')}",
        f"- HF_HUB_OFFLINE: `{ (rec.get('policy') or {}).get('hf_offline') }`",
        f"- HF_TOKEN in env: `{ (rec.get('policy') or {}).get('hf_token_in_env') }`",
        f"- ModelScope: **{'up' if rec.get('modelscope_ok') else 'down'}**",
        f"- Kaggle: API `{ (rec.get('kaggle') or {}).get('api') }` — {(rec.get('kaggle') or {}).get('note')}",
        "",
    ]
    if pull:
        lines += ["## Pulled from ModelScope: Qwen/Qwen2.5-0.5B-Instruct", ""]
        for f in pull.get("files") or []:
            lines.append(f"- `{f.get('file')}` — {f.get('bytes')} bytes — "
                         f"{'local hit' if f.get('cached') else 'downloaded'}")
        for e in pull.get("errors") or []:
            lines.append(f"- ERROR `{e.get('file')}`: {e.get('error')}")
        lines.append("")
    if cards:
        lines += ["## Cards only (no multi-GB shards)", ""]
        for c in cards:
            lines.append(f"- **{c['key']}** `{c['mid']}` listed {c.get('n_listed')} files")
            for f in c.get("files") or []:
                lines.append(f"  - `{f.get('file')}` {f.get('bytes')} B")
        lines.append("")
    lines += [
        "## Honesty",
        "",
        "- No torch / no GPU here. A `.safetensors` on disk is not a running model.",
        "- Phi-4 and Qwen3.6-27B shards are multi-GB — cards only.",
        "- Kaggle weight download needs `~/.kaggle/kaggle.json` (not present).",
        "- HF Inference Providers stay unused until credits reappear.",
        "",
    ]
    return "\n".join(lines) + "\n"
