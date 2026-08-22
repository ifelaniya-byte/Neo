#!/usr/bin/env python3
"""
GPU LANE — how this sandbox uses free GPU hours after the King signs up.

This box has no GPU. The King signs up elsewhere, then pastes a token or
a worker URL. We never invent a GPU we do not have.

Paths (honest, Aug 2026):
  1. FASTEST — Hugging Face token (free). Router already lists our seats.
     We got 401 without a token. With HF_TOKEN we call the same endpoint.
  2. FREE HOURS — Colab T4 + Kaggle T4 (up to ~60h/week, no card) and
     Lightning AI (~80h/month, phone). Run gpu_worker.py there.
  3. SHARED DATACENTER GPU — HF ZeroGPU (A100/H200, daily seconds).
  4. ONE-TIME CREDITS — RunPod / Lambda ~$10 signup.

T4 16GB can load: SmolLM3-3B, Phi-4 Q4, Falcon-H1R-7B, Granite-4.1-8B,
gpt-oss-20b MXFP4, Liquid LFM2.5. It CANNOT load Kimi K3, Qwen 3.8 Max,
Apertus 70B full, or a rumored 1T GLM-5.5. Giants need hosted inference.

USED BY: model_council.py, kings_pass.py
"""

import json
import os
import time
import urllib.error
import urllib.request

ROUTER_CHAT = "https://router.huggingface.co/v1/chat/completions"
ROUTER_MODELS = "https://router.huggingface.co/v1/models"
TOKEN_FILES = ("/tmp/hf_token", os.path.expanduser("~/.hf_token"))

# Council key → HF router id we have actually seen listed.
PANEL = (
    ("phi-4", "microsoft/phi-4"),
    ("gpt-oss-20b", "openai/gpt-oss-20b"),
    ("qwen3.6-27b", "Qwen/Qwen3.6-27B"),
    ("apertus-70b", "swiss-ai/Apertus-70B-Instruct-2509"),
    ("glm-5.2", "zai-org/GLM-5.2"),
    ("kimi-k3", "moonshotai/Kimi-K3"),
    ("deepseek-v4-pro", "deepseek-ai/DeepSeek-V4-Pro"),
    ("qwen-3.8-max", "Qwen/Qwen3.8-2.4T-A95B"),
)


def load_token():
    """Read HF token from env or a secret file. Never return it in public logs."""
    for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN"):
        v = (os.environ.get(k) or "").strip()
        if v:
            os.environ["HF_TOKEN"] = v
            return v
    for path in TOKEN_FILES:
        try:
            v = open(path).read().strip()
            if v.startswith("hf_"):
                os.environ["HF_TOKEN"] = v
                return v
        except OSError:
            pass
    netrc = os.path.expanduser("~/.netrc")
    try:
        block = open(netrc).read()
        if "huggingface.co" in block and "password" in block:
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("password"):
                    v = line.split(None, 1)[-1].strip()
                    if v.startswith("hf_"):
                        os.environ["HF_TOKEN"] = v
                        return v
    except OSError:
        pass
    return ""

# What a free T4 (16GB) can honestly run at Q4 / MXFP4.
T4_FITS = (
    "smollm3-3b", "phi-4", "falcon-h1r-7b", "granite-4.1",
    "gpt-oss-20b", "liquid-lfm2.5", "mellum-2", "laguna-xs-2.1",
    "gemma-4-31b",  # tight; Q4 / 4-bit only
)
# Need hosted inference or a big rented GPU.
NEEDS_HOSTED = (
    "kimi-k3", "qwen-3.8-max", "apertus-70b", "glm-5.2", "glm-5.5",
    "deepseek-v4-pro", "llama-5", "inkling", "qwen3.5-397b",
)

SIGNUP = [
    {
        "id": "hf-token",
        "title": "Hugging Face token (do this first)",
        "url": "https://huggingface.co/settings/tokens",
        "cost": "free, no card",
        "what": "Create a READ token. This sandbox already reached the router (131 models, 401 without auth).",
        "env": "HF_TOKEN",
        "hours": "rate-limited serverless / Inference Providers, not a reserved GPU",
    },
    {
        "id": "kaggle",
        "title": "Kaggle Notebooks GPU",
        "url": "https://www.kaggle.com/code",
        "cost": "free, no card",
        "what": "Guaranteed ~30 GPU hours/week on T4/P100, 9-hour sessions. More reliable than Colab.",
        "env": "GPU_ENDPOINT (after you run gpu_worker.py with Gradio share)",
        "hours": "~30 h/week T4 16GB",
    },
    {
        "id": "colab",
        "title": "Google Colab free GPU",
        "url": "https://colab.research.google.com",
        "cost": "free, no card",
        "what": "15–30 h/week T4, 12-hour sessions. Throttles at peak. Complement to Kaggle.",
        "env": "GPU_ENDPOINT",
        "hours": "~15–30 h/week T4 16GB",
    },
    {
        "id": "lightning",
        "title": "Lightning AI Studio",
        "url": "https://lightning.ai",
        "cost": "free tier, phone verify",
        "what": "Persistent VS Code cloud. Reported ~80 GPU hours/month on the free plan.",
        "env": "GPU_ENDPOINT",
        "hours": "~80 h/month (verify current quota in-app)",
    },
    {
        "id": "zerogpu",
        "title": "Hugging Face ZeroGPU Space",
        "url": "https://huggingface.co/new-space",
        "cost": "free daily seconds; Pro $9 unlocks more / easier hosting",
        "what": "Time-sliced A100/H200. Host gpu_worker as a Gradio Space, then we call the public URL.",
        "env": "GPU_ENDPOINT",
        "hours": "seconds/day on free; minutes/day on Pro",
    },
    {
        "id": "runpod",
        "title": "RunPod signup credit",
        "url": "https://www.runpod.io",
        "cost": "~$10 one-time credit (card often required)",
        "what": "A few hours of a real H100/4090 if you need one 70B Q4 smoke test.",
        "env": "GPU_ENDPOINT",
        "hours": "~3–30 h depending on GPU",
    },
]


def detect():
    token = load_token()
    or_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
    endpoint = (os.environ.get("GPU_ENDPOINT") or "").strip()
    return {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hf_token": bool(token),
        "openrouter": bool(or_key),
        "gpu_endpoint": endpoint or None,
        "ready": bool(token or or_key or endpoint),
        "t4_fits": list(T4_FITS),
        "needs_hosted": list(NEEDS_HOSTED),
        "signup": SIGNUP,
        "next": (
            "Paste HF_TOKEN into the environment (huggingface.co/settings/tokens). "
            "That is the shortest path. For actual GPU hours, sign up at Kaggle + Colab, "
            "run gpu_worker.py, and set GPU_ENDPOINT to the public Gradio URL."
            if not (token or endpoint)
            else "A credential is present. We will try a real completion this session."
        ),
    }


def try_hf_chat(prompt, model="microsoft/phi-4", max_tokens=48):
    """Call HF router if HF_TOKEN is set. Returns a public receipt."""
    token = (os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or "").strip()
    if not token:
        return {"ok": False, "status": None, "note": "no HF_TOKEN in environment"}
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        ROUTER_CHAT, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "model-council/gpu-lane",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            payload = json.loads(r.read().decode())
        msg = ((payload.get("choices") or [{}])[0].get("message") or {})
        text = (msg.get("content") or "").strip()
        if not text:
            text = (msg.get("reasoning") or msg.get("reasoning_content") or "").strip()
        return {"ok": True, "status": r.status, "model": model, "text": text[:800],
                "usage": payload.get("usage"), "msg_keys": list(msg)}
    except urllib.error.HTTPError as e:
        snippet = ""
        try:
            snippet = e.read()[:240].decode("utf-8", "replace")
        except Exception:
            snippet = ""
        return {"ok": False, "status": e.code, "reason": str(e.reason), "body": snippet, "model": model}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)[:200], "model": model}


def infer_panel(prompt, max_tokens=64):
    """Call every mapped live seat. Public receipts only — no token in the return."""
    rows = []
    for key, hid in PANEL:
        rec = try_hf_chat(prompt, model=hid, max_tokens=max_tokens)
        rec["key"] = key
        rec["hf"] = hid
        rows.append(rec)
        time.sleep(0.25)
    ok = sum(1 for r in rows if r.get("ok") and r.get("text"))
    return {
        "prompt": prompt,
        "n": len(rows),
        "n_ok": ok,
        "n_fail": len(rows) - ok,
        "rows": rows,
        "honest": f"{ok}/{len(rows)} live router completions. Token never written to the ledger.",
    }


def try_worker(prompt):
    """POST {prompt} to GPU_ENDPOINT if the King stood up gpu_worker.py."""
    url = (os.environ.get("GPU_ENDPOINT") or "").rstrip("/")
    if not url:
        return {"ok": False, "note": "no GPU_ENDPOINT"}
    # Gradio 4+ /call/predict or a simple /run we document in gpu_worker.py
    target = url + "/run" if not url.endswith("/run") else url
    body = json.dumps({"prompt": prompt, "max_new_tokens": 64}).encode()
    req = urllib.request.Request(
        target, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "model-council/gpu-lane"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return {"ok": True, "status": r.status, "body": r.read()[:800].decode("utf-8", "replace")}
    except Exception as e:
        return {"ok": False, "error": str(e)[:240]}


def console_lane(state, chat=None, worker=None):
    print("\n" + "▓" * 72)
    print("GPU LANE — free hours after the King signs up")
    print("▓" * 72)
    print("  " + state["next"])
    print(f"  HF_TOKEN set: {state['hf_token']} · OPENROUTER set: {state['openrouter']} · "
          f"GPU_ENDPOINT: {state['gpu_endpoint'] or '—'}")
    print("  Sign up (do #1 today):")
    for row in SIGNUP:
        print(f"     · {row['title']}  {row['url']}")
        print(f"       {row['cost']} · {row['hours']}")
    print("  T4 16GB can run:", ", ".join(T4_FITS))
    print("  Needs hosted / big GPU:", ", ".join(NEEDS_HOSTED))
    if chat:
        print(f"  HF chat: ok={chat.get('ok')} status={chat.get('status')} "
              f"{(chat.get('text') or chat.get('note') or chat.get('reason') or '')[:120]}")
    if worker:
        print(f"  worker: {worker}")
    print("▓" * 72)


def export_md(state, chat=None):
    lines = [
        "# GPU Lane — how the King gets free hours into this sandbox",
        "",
        "This sandbox has **no GPU**. You sign up elsewhere. Then you paste a secret.",
        "",
        "KP-14: treat Kaggle as a **batch lab** on one identity. 70B is not a T4 job.",
        "",
        "## Do this first (10 minutes)",
        "",
        "1. Create a Hugging Face account: https://huggingface.co/join",
        "2. Make a **Read** token: https://huggingface.co/settings/tokens",
        "3. Put it in this environment as `HF_TOKEN`.",
        "4. Re-run the council. We already proved the router lists Kimi K3, GLM 5.2,",
        "   DeepSeek V4 Pro, Qwen 3.8 Max, Apertus 70B Instruct — we got **401** without a token.",
        "",
        "## Free GPU hours (if you want a real card, not just hosted inference)",
        "",
    ]
    for row in SIGNUP:
        lines += [
            f"### {row['title']}",
            f"- URL: {row['url']}",
            f"- Cost: {row['cost']}",
            f"- Hours: {row['hours']}",
            f"- What: {row['what']}",
            f"- Env var we read: `{row['env']}`",
            "",
        ]
    lines += [
        "## What fits where (honesty)",
        "",
        f"- **Free T4 16GB (Colab/Kaggle):** {', '.join(T4_FITS)}",
        f"- **Need hosted inference or a rented 70B+ box:** {', '.join(NEEDS_HOSTED)}",
        "- A rumored 1T GLM-5.5 will **not** load on a free T4. Day-1 for 5.5 is hosted inference or a paid H100.",
        "",
        "## Worker",
        "",
        "Upload `gpu_worker.py` to Colab or Kaggle, run it, copy the public Gradio URL,",
        "set `GPU_ENDPOINT` to that URL. The council will POST prompts to `/run`.",
        "",
        f"## This session",
        "",
        f"- HF_TOKEN present: **{state['hf_token']}**",
        f"- GPU_ENDPOINT: `{state['gpu_endpoint'] or 'none'}`",
        f"- Ready: **{state['ready']}**",
        f"- Next: {state['next']}",
        "",
    ]
    if chat:
        lines += ["### Chat attempt", "", f"```\n{json.dumps(chat, indent=2)[:1200]}\n```", ""]
    return "\n".join(lines) + "\n"
