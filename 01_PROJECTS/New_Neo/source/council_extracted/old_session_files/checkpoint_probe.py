#!/usr/bin/env python3
"""
CHECKPOINT PROBE — honest attempt to reach the real 45 weights.

This sandbox has: no GPU, no torch, ~20 GB disk, no HF/OpenRouter token.
We still try the public Hugging Face router so the ledger can show receipts
instead of a silent assumption.

USED BY: model_council.py, kings_pass.py
"""

import json
import time
import urllib.error
import urllib.request

ROUTER_MODELS = "https://router.huggingface.co/v1/models"
ROUTER_CHAT = "https://router.huggingface.co/v1/chat/completions"

# Map our council keys to HF router ids we actually saw listed (2026-08-13).
WANTED = {
    "kimi-k3": "moonshotai/Kimi-K3",
    "glm-5.2": "zai-org/GLM-5.2",
    "deepseek-v4-pro": "deepseek-ai/DeepSeek-V4-Pro",
    "deepseek-v4-flash": "deepseek-ai/DeepSeek-V4-Flash",
    "qwen3.6-27b": "Qwen/Qwen3.6-27B",
    "qwen-3.8-max": "Qwen/Qwen3.8-2.4T-A95B",
    "phi-4": "microsoft/phi-4",
    "gemma-4-31b": "google/gemma-4-31B-it",
    "gpt-oss-20b": "openai/gpt-oss-20b",
    "gpt-oss-120b": "openai/gpt-oss-120b",
    "llama-4-scout": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "apertus-70b": "swiss-ai/Apertus-70B-Instruct-2509",
    "kimi-k2.7-code": "moonshotai/Kimi-K2.7-Code",
}


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "model-council/probe"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())


def _post(url, body, timeout=20):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "model-council/probe"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())


def probe():
    """Try to list and then call a real small open weight. Always returns a public receipt."""
    rec = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "gpu": False,
        "torch": False,
        "api_token": False,
        "disk_note": "~20 GB free; a single 70B GGUF does not fit",
        "router_ok": False,
        "n_router_models": 0,
        "listed_wanted": {},
        "chat_attempt": None,
        "loaded_checkpoints": 0,
        "honest": (
            "The 45 named LLMs are NOT running. Hugging Face router lists many of "
            "their real ids, but chat completions return 401 Unauthorized without a token. "
            "Muse Spark is closed. GLM 5.5 is unreleased. Gene-pool seats are not checkpoints."
        ),
    }
    try:
        status, payload = _get(ROUTER_MODELS)
        ids = [m.get("id") for m in (payload.get("data") or [])]
        rec["router_ok"] = status == 200
        rec["n_router_models"] = len(ids)
        idset = set(ids)
        rec["listed_wanted"] = {k: {"hf": v, "listed": v in idset} for k, v in WANTED.items()}
    except Exception as e:
        rec["router_error"] = str(e)[:200]

    try:
        status, payload = _post(ROUTER_CHAT, {
            "model": "microsoft/phi-4",
            "messages": [{"role": "user", "content": "Name the largest ocean in one word."}],
            "max_tokens": 8,
        })
        rec["chat_attempt"] = {"status": status, "body": str(payload)[:240]}
        rec["loaded_checkpoints"] = 1
    except urllib.error.HTTPError as e:
        snippet = ""
        try:
            snippet = e.read()[:180].decode("utf-8", "replace")
        except Exception:
            snippet = ""
        rec["chat_attempt"] = {
            "status": e.code,
            "reason": str(e.reason),
            "body": snippet,
            "note": "Real endpoint reached. Auth required. No token in this sandbox.",
        }
    except Exception as e:
        rec["chat_attempt"] = {"status": None, "error": str(e)[:200]}
    return rec


def console_probe(rec):
    print("\n" + "░" * 72)
    print("CHECKPOINT PROBE — attempt to load the real 45")
    print("░" * 72)
    print("  " + rec["honest"])
    print(f"  router: {'up' if rec.get('router_ok') else 'down'} · "
          f"{rec.get('n_router_models', 0)} models listed")
    for k, row in (rec.get("listed_wanted") or {}).items():
        mark = "listed" if row.get("listed") else "not listed"
        print(f"     {k:>18}  {row['hf']:<48} {mark}")
    chat = rec.get("chat_attempt") or {}
    print(f"  chat try (phi-4): status={chat.get('status')} {chat.get('reason') or chat.get('note') or ''}")
    print(f"  loaded real checkpoints this session: {rec.get('loaded_checkpoints', 0)}")
    print("░" * 72)
