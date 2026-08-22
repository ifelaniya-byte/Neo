#!/usr/bin/env python3
"""
KAGGLE LANE — single-account API. Token never printed.

Auth: ~/.kaggle/access_token or KAGGLE_API_TOKEN (KGAT_…).
This sandbox is not a Kaggle GPU. We catalog + plan. We do not
start 32 workers, ngrok, or extra accounts.

TOS: one phone-verified identity. Multi-account GPU farming is rejected.

USED BY: model_council.py, weight_source.py
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
API = "https://www.kaggle.com/api/v1"
TOKEN_PATHS = (
    os.path.expanduser("~/.kaggle/access_token"),
    os.path.join(BASE, ".kaggle_access_token"),
)
UA = "model-council/kaggle-lane"

# Prefer org-owned or clearly labeled unofficial.
MAP = {
    "phi-4": ("arpit1bansal/phi-4", "community Phi-4 listing, not Microsoft official"),
    "gemma-4-31b": ("google/gemma-4", "Google official Gemma 4 family"),
    "olmo-3": ("danbth/olmo-3-7b-instruct", "community OLMo-3-7B-Instruct"),
    "olmo-family": ("allenai/olmo", "Ai2 official OLMo"),
    "granite-4.1": ("ibm-research/granite-4.0", "IBM official Granite 4.0 family"),
    "gpt-oss-20b": ("danielhanchen/gpt-oss-20b", "Unsloth gpt-oss-20b listing"),
    "gpt-oss-120b": ("danielhanchen/gpt-oss-120b", "Unsloth gpt-oss-120b listing"),
    "smollm3-3b": ("keras/smollm3", "Keras official SmolLM3"),
    "qwen3-family": ("qwen-lm/qwen-3", "Qwen official Qwen-3 family"),
    "qwen3.6-27b": ("ravi123a321at/qwen-3-6-27b", "community Qwen 3.6 27B — verify files"),
    "kimi-k3": ("helium990/kimi-k3", "community Kimi K3 — verify files"),
    "falcon-h1r-7b": ("manojkumarcs28/falcon-h1r-series", "community Falcon H1R series"),
    "devstral-small-2": ("mistral-ai/devstral-small-2507", "Mistral official Devstral Small"),
    "mistral-small-3.1": ("mistral-ai/mistral-small-24b", "Mistral official Small 24B"),
    "llama-family": ("metaresearch/llama-3", "Meta Llama 3 on Kaggle — Llama 4/5 not listed as official"),
}


def load_token():
    v = (os.environ.get("KAGGLE_API_TOKEN") or "").strip()
    if v.startswith("KGAT_"):
        return v
    for path in TOKEN_PATHS:
        try:
            t = open(path).read().strip()
            if t.startswith("KGAT_"):
                os.environ["KAGGLE_API_TOKEN"] = t
                return t
        except OSError:
            pass
    return ""


def _get(url):
    token = load_token()
    if not token:
        raise RuntimeError("no Kaggle token")
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, json.loads(r.read().decode())


def search_models(q, n=6):
    status, data = _get(f"{API}/models/list?search={urllib.parse.quote(q)}&pageSize={n}")
    return data.get("models") or []


def model_get(ref):
    status, data = _get(f"{API}/models/{ref}/get")
    inst = data.get("instances") or []
    return {
        "ref": data.get("ref"),
        "title": data.get("title"),
        "author": data.get("author"),
        "n_instances": len(inst) if isinstance(inst, list) else 0,
        "instances": [
            {"slug": i.get("slug"), "framework": i.get("framework"),
             "version": i.get("versionNumber")}
            for i in (inst[:8] if isinstance(inst, list) else [])
        ],
    }


def probe():
    rec = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "token_present": bool(load_token()),
        "auth": False,
        "competitions_sample": [],
        "mapped": [],
        "tos": (
            "Single phone-verified account only. Multi-account GPU farming "
            "violates Kaggle TOS and is not implemented."
        ),
        "sandbox": (
            "This box is not a Kaggle T4. We can catalog and push kernels "
            "if the API allows; we cannot host 32 Ollama/ngrok workers here."
        ),
    }
    if not rec["token_present"]:
        rec["error"] = "no KGAT token in ~/.kaggle/access_token or KAGGLE_API_TOKEN"
        return rec
    try:
        status, comps = _get(f"{API}/competitions/list?page=1")
        rec["auth"] = status == 200
        if isinstance(comps, list):
            rec["competitions_sample"] = [c.get("titleNullable") or c.get("title") for c in comps[:3]]
    except Exception as e:
        rec["error"] = str(e)[:200]
        return rec
    for key, (ref, note) in MAP.items():
        row = {"key": key, "ref": ref, "note": note}
        try:
            row.update(model_get(ref))
            row["ok"] = True
        except Exception as e:
            row["ok"] = False
            row["error"] = str(e)[:160]
        rec["mapped"].append(row)
    return rec


def console_kaggle(rec):
    print("\n" + "▤" * 72)
    print("KAGGLE LANE — one account, Bearer KGAT, no TOS farming")
    print("▤" * 72)
    print("  " + rec.get("tos"))
    print("  " + rec.get("sandbox"))
    print(f"  token present: {rec.get('token_present')}  auth: {rec.get('auth')}")
    if rec.get("competitions_sample"):
        print("  competitions:", ", ".join(rec["competitions_sample"]))
    print("  mapped council seats:")
    for m in rec.get("mapped") or []:
        mark = "ok" if m.get("ok") else "no"
        print(f"     {mark} {m.get('key'):18} {m.get('ref')}  "
              f"inst={m.get('n_instances')}  {m.get('note','')[:50]}")
    print("▤" * 72)


def export_md(rec):
    lines = [
        "# Kaggle lane — single account",
        "",
        rec.get("tos", ""),
        "",
        rec.get("sandbox", ""),
        "",
        f"- Auth: **{rec.get('auth')}** (token present: {rec.get('token_present')})",
        f"- Date: {rec.get('date')}",
        "",
        "## Weekly free budget (one identity)",
        "",
        "| Resource | Typical free quota |",
        "|---|---|",
        "| GPU T4/P100 | ~30 h/week |",
        "| Concurrent GPU sessions | 2 |",
        "| Session length | ~9 h GPU / 12 h CPU |",
        "| CPU notebooks | unlimited |",
        "",
        "## KP-14 — what you run ON Kaggle (one identity, batch only)",
        "",
        "Kaggle is a **batch lab**, not an always-on API. Sessions die. Do not ngrok Ollama.",
        "",
        "1. `kaggle_00_environment_check.ipynb` on **CPU** first. Do not burn GPU deciding.",
        "2. `kaggle_10_download_verify.ipynb` — ModelScope official tiny ladder only + SHA-256.",
        "3. `kaggle_worker_template.ipynb` — sequential 4-bit, one 0.5B–9B model, `trust_remote_code=False`.",
        "4. `kaggle_30_train_qlora.ipynb` — one adapter per domain (coding / math / retrieval).",
        "5. Giants (Kimi K3, Qwen 3.8 Max, Apertus 70B, GLM 5.2 282 shards) do **not** fit a T4.",
        "6. Dual-T4 is **not guaranteed**. 70B 4-bit is not a weekly plan.",
        "",
        "Quota split of whatever hours you actually get: QLoRA 45% · eval 25% · batch infer 15% · quant 10% · contingency 5%.",
        "",
        "## Mapped listings (verify files before you trust them)",
        "",
    ]
    for m in rec.get("mapped") or []:
        st = "listed" if m.get("ok") else "missing"
        lines.append(f"- `{m.get('key')}` → `{m.get('ref')}` ({st}, {m.get('n_instances', 0)} instances) — {m.get('note')}")
    lines += [
        "",
        "## Not implemented (on purpose)",
        "",
        "- Multi-account / extra phone numbers",
        "- 32 parallel Ollama+ngrok workers from this sandbox",
        "- Auto-spend of the depleted HF Inference Provider quota",
        "",
    ]
    return "\n".join(lines) + "\n"
