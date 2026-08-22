#!/usr/bin/env python3
"""
SEAT REGISTRY — KP-14. Four labels. Verified artifacts, not seat names.

Statuses (never call a listing "available" just because search returned a name):
  verified-checkpoint  official repo, files, license, architecture checked
  verified-api         a real completion returned the expected model id
  community-quarantine do not execute custom code or train from it
  logical-emulated     no usable checkpoint; prompt / adapter / RAG / substrate

Backend priority for every seat:
  local/Kaggle verified model → free API → cached answer → unavailable

Kaggle is a BATCH lab (eval / QLoRA / 4-bit 0.5B–9B), not an always-on API.
70B 4-bit is NOT a normal T4 workload. Dual-T4 + CPU spill is experimental,
not a plan to keep 45 giants resident.

USED BY: model_council.py, council_router.py, kaggle_lane.py
"""

import json
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))

STATUSES = (
    "verified-checkpoint",
    "verified-api",
    "community-quarantine",
    "logical-emulated",
)

# Capability domains (8–12). Multiple seats may share one adapter.
DOMAINS = (
    "instruction",
    "math",
    "coding",
    "reasoning",
    "long-doc",
    "extraction",
    "planning",
    "critique",
    "creative",
    "multilingual",
    "tools",
    "safety",
    "retrieval",
)

# Verified small bases we actually have or can pull without HF token.
LADDER = [
    {"id": "qwen2.5-0.5b", "ms": "Qwen/Qwen2.5-0.5B-Instruct",
     "role": "tiny-base", "params": "0.5B", "q4_gb": 0.25,
     "offline": "weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/model.safetensors",
     "note": "ON DISK here (988 MB BF16). Pipeline smoke test. No torch in this box."},
    {"id": "qwen3-0.6b", "ms": "Qwen/Qwen3-0.6B",
     "role": "tiny-next", "params": "0.6B", "q4_gb": 0.35,
     "offline": None, "note": "ModelScope listed ~1.5 GB. Next pull if disk allows."},
    {"id": "r1-distill-1.5b", "ms": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
     "role": "reasoning-base", "params": "1.5B", "q4_gb": 0.75,
     "offline": None, "note": "Reasoning student. NOT DeepSeek V4 Flash."},
    {"id": "smollm3-3b", "ms": None, "kaggle": "keras/smollm3",
     "hf": "HuggingFaceTB/SmolLM3-3B",
     "role": "primary-dev", "params": "3B", "q4_gb": 1.5,
     "offline": None, "note": "Kaggle official Keras listing. Primary QLoRA platform."},
    {"id": "olmo-3-7b", "ms": None, "kaggle": "allenai/olmo",
     "role": "strong-local", "params": "7B", "q4_gb": 4.5,
     "offline": None, "note": "Ai2 official family on Kaggle. Prefer official over danbth community."},
    {"id": "phi-4", "ms": "LLM-Research/Phi-4",
     "hf": "microsoft/phi-4",
     "role": "mid-infer", "params": "14B", "q4_gb": 8.0,
     "offline": None, "note": "Card on disk. Shards ~7–10 GB Q4. Inference-only until small pipeline works."},
]

# Hardware honesty (4-bit weight-only, before KV/overhead).
VRAM_TABLE = [
    (0.5, 0.25, "easy"),
    (1.5, 0.75, "easy"),
    (3.0, 1.5, "easy"),
    (8.0, 5.0, "good T4 target"),
    (14.0, 8.5, "possible, tight"),
    (24.0, 14.0, "usually impractical after KV"),
    (70.0, 40.0, "not a normal T4 workload"),
    (120.0, 65.0, "not viable on free Kaggle"),
]

QUOTA = {
    "qlora": 45,
    "eval": 25,
    "batch_infer": 15,
    "quantize": 10,
    "contingency": 5,
}

REJECTED_CLAIMS = [
    {"claim": "45 full checkpoints on one Kaggle account",
     "why": "T4 16GB + ~30h/week cannot host 45 models. Seats are logical experts."},
    {"claim": "helium990/kimi-k3 is Kimi K3",
     "why": "Community listing. Quarantine. Official live id was moonshotai/Kimi-K3 on HF router (402 now)."},
    {"claim": "ravi123a321at/qwen-3-6-27b is official Qwen 3.6 27B",
     "why": "Community. Official ModelScope is Qwen/Qwen3.6-27B (~15×3.9GB). Too big for T4."},
    {"claim": "arpit1bansal/phi-4 is Microsoft official",
     "why": "Community. Prefer LLM-Research/Phi-4 (MS) or microsoft/phi-4 (HF, token+credits)."},
    {"claim": "DeepSeek-R1-Distill-Qwen-1.5B is DeepSeek V4 Flash",
     "why": "Different model, different year. Distill is a 1.5B student, not V4."},
    {"claim": "keras/smollm3 is a ModelScope id",
     "why": "That is a Kaggle model ref. Do not snapshot_download it from ModelScope."},
    {"claim": "google/gemma-4 is a ModelScope id",
     "why": "Official Gemma 4 on Kaggle is google/gemma-4. Confirm ModelScope separately."},
    {"claim": "70B 4-bit (~38GB) is a normal Dual-T4 job",
     "why": "Kaggle usually gives ONE T4 16GB, not a guaranteed 2×T4. 70B needs ~35–45GB weights plus KV. Experimental llama.cpp offload is not the weekly plan."},
    {"claim": "Always-on Ollama + ngrok on Kaggle",
     "why": "Sessions are ephemeral. Tunneling a public API may conflict with platform expectations. Batch artifacts only."},
    {"claim": "3 accounts × 30 GPU hours",
     "why": "Multi-account / extra-phone farming violates Kaggle TOS. One phone-verified identity."},
    {"claim": "CMAKE_ARGS=-GGUIDE=OFF",
     "why": "Typo. CUDA llama-cpp uses -DGGML_CUDA=on. Do not ship a broken compile cell."},
    {"claim": "HTTP 200 on a catalog = authentic weights",
     "why": "A listing proves a listing. Check publisher, license, shards, checksums, trust_remote_code."},
]


def _seat(key, status, domain, backend, identifier=None, scale_b=0,
          local_path=None, api=None, note="", trust_remote_code=False,
          license_verified=False, t4="no"):
    assert status in STATUSES, status
    assert domain in DOMAINS, domain
    return {
        "key": key,
        "status": status,
        "domain": domain,
        "backend": backend,          # local | modelscope | kaggle | hf-api | substrate | none
        "identifier": identifier,
        "scale_b": scale_b,          # billions of params (0 = unknown / n/a)
        "local_path": local_path,
        "api": api,
        "note": note,
        "trust_remote_code": trust_remote_code,
        "license_verified": license_verified,
        "t4": t4,                    # easy | tight | no
        "channel": backend,
    }


# 45 LLM seats + 9 gene-pool + 2 substrate. Names on every mark.
SEATS = [
    # --- verified local / ModelScope / official Kaggle (runnable-size or card) ---
    _seat("smollm3-3b", "verified-checkpoint", "instruction", "kaggle",
          "keras/smollm3", 3, t4="easy", license_verified=True,
          note="Kaggle official Keras SmolLM3. Primary 3B development base."),
    _seat("phi-4", "verified-checkpoint", "math", "modelscope",
          "LLM-Research/Phi-4", 14, api="microsoft/phi-4", t4="tight",
          license_verified=True,
          note="MS card on disk. HF★ wave-1 then 402. Mid-size inference only."),
    _seat("gpt-oss-20b", "verified-checkpoint", "coding", "modelscope",
          "openai-mirror/gpt-oss-20b", 21, api="openai/gpt-oss-20b", t4="tight",
          license_verified=True,
          note="MS card on disk. T4 possible MXFP4; usually tight after KV."),
    _seat("olmo-3", "verified-checkpoint", "instruction", "kaggle",
          "allenai/olmo", 7, t4="easy", license_verified=True,
          note="Ai2 official OLMo family. Prefer this over danbth community 7B."),
    _seat("granite-4.1", "verified-checkpoint", "safety", "kaggle",
          "ibm-research/granite-4.0", 8, t4="easy", license_verified=True,
          note="IBM official Granite 4.0 family on Kaggle."),
    _seat("gemma-4-31b", "verified-checkpoint", "instruction", "kaggle",
          "google/gemma-4", 31, t4="tight", license_verified=True,
          note="Google official Gemma 4 family (47 inst). Q4 only; often too big after KV."),
    _seat("devstral-small-2", "verified-checkpoint", "coding", "kaggle",
          "mistral-ai/devstral-small-2507", 24, t4="tight", license_verified=True,
          note="Mistral official Devstral Small."),
    _seat("mistral-small-3.1", "verified-checkpoint", "multilingual", "kaggle",
          "mistral-ai/mistral-small-24b", 24, t4="tight", license_verified=True,
          note="Mistral official Small 24B."),
    _seat("qwen3.6-27b", "verified-checkpoint", "multilingual", "modelscope",
          "Qwen/Qwen3.6-27B", 27, api="Qwen/Qwen3.6-27B", t4="no",
          license_verified=True,
          note="Official MS. ~15×3.9GB. Card on disk. Not a T4 job. Hosted/API when credits return."),
    _seat("apertus-70b", "verified-checkpoint", "multilingual", "modelscope",
          "swiss-ai/Apertus-70B-Instruct-2509", 70, api="swiss-ai/Apertus-70B-Instruct-2509",
          t4="no", license_verified=True,
          note="Official Swiss AI. Card on disk. HF★ wave-1. 30 shards. Not a T4 job. History still SHOP not gift."),
    _seat("glm-5.2", "verified-checkpoint", "reasoning", "modelscope",
          "ZhipuAI/GLM-5.2", 753, api="zai-org/GLM-5.2", t4="no",
          license_verified=True,
          note="Official Zhipu. 282 shards. HF★ wave-1. Hosted only. Sibling of unreleased 5.5."),
    # --- verified API once, now 402 / no token ---
    _seat("kimi-k3", "verified-api", "planning", "hf-api",
          "moonshotai/Kimi-K3", 2800, api="moonshotai/Kimi-K3", t4="no",
          note="HF★ wave-1 then 402. Kaggle helium990/kimi-k3 is QUARANTINED community."),
    # --- community quarantine (listed, not trusted as the named seat) ---
    _seat("falcon-h1r-7b", "community-quarantine", "math", "kaggle",
          "manojkumarcs28/falcon-h1r-series", 7, t4="easy",
          note="Community Falcon H1R series. Inspect config/safetensors; trust_remote_code=False."),
    # --- logical / emulated (no usable authentic checkpoint here) ---
    _seat("deepseek-v4-pro", "logical-emulated", "coding", "hf-api",
          "deepseek-ai/DeepSeek-V4-Pro", 1600, api="deepseek-ai/DeepSeek-V4-Pro", t4="no",
          note="Router listed; later 402. No local shards. Emulate via coding adapter + cache."),
    _seat("deepseek-v4-flash", "logical-emulated", "coding", "none",
          None, 284, t4="no",
          note="Do NOT substitute R1-Distill-1.5B. Emulate via efficient-coding adapter."),
    _seat("qwen3-235b", "logical-emulated", "reasoning", "kaggle",
          "qwen-lm/qwen-3", 235, t4="no",
          note="Family listing only. Seat uses Qwen-style prompt + 3B/7B adapter."),
    _seat("llama-5", "logical-emulated", "safety", "none", None, 600, t4="no",
          note="No official Llama 5 on Kaggle (only metaresearch/llama-3). Safety prompt + adapter."),
    _seat("llama-4-scout", "logical-emulated", "long-doc", "hf-api",
          "meta-llama/Llama-4-Scout-17B-16E-Instruct", 109, t4="no",
          note="Router listed earlier. No official Kaggle Llama 4. Emulate long-doc."),
    _seat("llama-4-maverick", "logical-emulated", "critique", "none", None, 400, t4="no",
          note="No official Kaggle Llama 4. Emulate via reasoning adapter."),
    _seat("minimax-m3", "logical-emulated", "coding", "none", None, 428, t4="no",
          note="No verified artifact here."),
    _seat("nemotron-3-ultra", "logical-emulated", "coding", "none", None, 550, t4="no",
          note="No verified artifact here."),
    _seat("hunyuan-hy3", "logical-emulated", "instruction", "none", None, 295, t4="no",
          note="No verified artifact here. Capability-per-GB is a prompt + cost table, not a 295B download."),
    _seat("gpt-oss-120b", "community-quarantine", "coding", "kaggle",
          "danielhanchen/gpt-oss-120b", 117, t4="no",
          note="Unsloth community listing. Quarantine until files/license checked. Too big for T4."),
    _seat("mistral-large-3", "logical-emulated", "extraction", "none", None, 675, t4="no",
          note="Small/Devstral official, not Large 3."),
    _seat("kimi-k2-code", "logical-emulated", "tools", "none", None, 1000, t4="no",
          note="No verified local artifact."),
    _seat("step-3.7-flash", "logical-emulated", "coding", "none", None, 198, t4="no",
          note="No verified artifact here."),
    _seat("command-a-plus", "logical-emulated", "retrieval", "none", None, 218, t4="no",
          note="RAG/citation seat. Implement with retrieval + 3B/7B, not a 218B download."),
    _seat("muse-glimmer", "logical-emulated", "creative", "none", None, 30, t4="no",
          note="Open Muse persona. Teacher Spark is closed."),
    _seat("inkling", "logical-emulated", "planning", "none", None, 975, t4="no",
          note="No local 975B. Effort-dial is a prompt/decoding setting on a small base."),
    _seat("laguna-xs-2.1", "logical-emulated", "tools", "none", None, 33, t4="easy",
          note="Claimed 3B-active coder. No verified files here. Emulate agentic-coding adapter."),
    _seat("k-exaone-2.0", "logical-emulated", "long-doc", "none", None, 750, t4="no",
          note="Long-doc sovereign seat. No local 750B."),
    _seat("qwen-3.8-max", "verified-api", "tools", "hf-api",
          "Qwen/Qwen3.8-2.4T-A95B", 2400, api="Qwen/Qwen3.8-2.4T-A95B", t4="no",
          note="Router listed; 402. Not downloadable here. Teacher/judge only when credits return."),
    _seat("mellum-2", "logical-emulated", "coding", "none", None, 12, t4="easy",
          note="Focal IDE model. No verified files here. Coding adapter."),
    _seat("devstral-2", "logical-emulated", "coding", "none", None, 123, t4="no",
          note="Use official Devstral Small as the runnable cousin, not as this seat."),
    _seat("apriel-15b-thinker", "logical-emulated", "math", "none", None, 15, t4="tight",
          note="No verified local files. Math/reasoning adapter on 3B/7B."),
    _seat("kat-dev-72b", "logical-emulated", "coding", "none", None, 72, t4="no",
          note="NOT a Qwen. ByteDance on Qwen2.5 base. No local 72B."),
    _seat("liquid-lfm2.5", "logical-emulated", "tools", "none", None, 2.6, t4="easy",
          note="On-device claim. No verified files here. Not mini-lfm."),
    _seat("inkling-small", "logical-emulated", "coding", "none", None, 276, t4="no",
          note="No local 276B. Student-vs-teacher card is a study, not a download."),
    _seat("mimo-v2.5-pro", "logical-emulated", "creative", "none", None, 1020, t4="no",
          note="No local 1T."),
    _seat("glm-5.5", "logical-emulated", "critique", "none", None, 0, t4="no",
          note="UNRELEASED. Day-1 eval pack only. No invented scores. Rumor-talk → sole eviction."),
    _seat("qwen3.5-397b", "logical-emulated", "multilingual", "kaggle",
          "qwen-lm/qwen-3", 397, t4="no",
          note="Family listing. Nex-N2-Pro merge still rejected."),
    _seat("kimi-k2.7-code", "logical-emulated", "tools", "none", None, 1000, t4="no",
          note="Router listed K2.7 earlier. No local files."),
    _seat("a-x-k2", "logical-emulated", "math", "none", None, 688, t4="no",
          note="No verified artifact here."),
    _seat("qwen3-next-80b", "logical-emulated", "coding", "kaggle",
          "qwen-lm/qwen-3", 80, t4="no",
          note="Family listing. Throughput seat = decoding settings, not 80B download."),
    _seat("muse-spark", "logical-emulated", "critique", "substrate",
          None, 0, t4="no",
          note="CLOSED teacher. Abstain. mini-lfm substrate if a voice is required."),
    # gene-pool + substrate
    _seat("gp-hall-of-fame", "logical-emulated", "critique", "substrate", None, 0, t4="no",
          note="Gene-pool badge. Not an external checkpoint."),
    _seat("gp-titan", "logical-emulated", "planning", "substrate", None, 0, t4="no",
          note="Gene-pool. King's-gift lab. Not a checkpoint."),
    _seat("gp-grove", "logical-emulated", "instruction", "substrate", None, 0, t4="no",
          note="Gene-pool. Not a checkpoint."),
    _seat("gp-sprout", "logical-emulated", "instruction", "substrate", None, 0, t4="no",
          note="Gene-pool. Not a checkpoint."),
    _seat("gp-seedling", "logical-emulated", "instruction", "substrate", None, 0, t4="no",
          note="Gene-pool. Not a checkpoint."),
    _seat("gp-sequoiadendron", "logical-emulated", "critique", "substrate", None, 0, t4="no",
          note="DNA-track apex. Not a checkpoint."),
    _seat("gp-redwood", "logical-emulated", "coding", "substrate", None, 0, t4="no",
          note="Gene-pool. Not a checkpoint."),
    _seat("gp-sapling", "logical-emulated", "instruction", "substrate", None, 0, t4="no",
          note="Gene-pool. Not a checkpoint."),
    _seat("gp-acorn", "logical-emulated", "safety", "substrate", None, 0, t4="no",
          note="Consent ledger. Not a checkpoint."),
    _seat("mini-llm", "verified-checkpoint", "instruction", "substrate",
          "mini_llm.py", 0, local_path="mini_llm.py", t4="easy", license_verified=True,
          note="Char-bigram substrate. Always on. Stood down as decider."),
    _seat("mini-lfm", "verified-checkpoint", "extraction", "substrate",
          "mini_lfm.py", 0, local_path="mini_lfm.py", t4="easy", license_verified=True,
          note="Naive-Bayes fact recall. Always on. Stood down as decider."),
]

BY_KEY = {s["key"]: s for s in SEATS}


def counts():
    c = {k: 0 for k in STATUSES}
    for s in SEATS:
        c[s["status"]] += 1
    c["n"] = len(SEATS)
    c["t4_easy"] = sum(1 for s in SEATS if s["t4"] == "easy")
    c["t4_tight"] = sum(1 for s in SEATS if s["t4"] == "tight")
    return c


def mapping_json():
    """Worker-facing map. Quarantine and none stay explicit."""
    out = {}
    for s in SEATS:
        out[s["key"]] = {
            "status": s["status"],
            "label": s["status"],
            "channel": s["backend"],
            "identifier": s["identifier"],
            "scale_b": s["scale_b"],
            "local_path": s["local_path"],
            "domain": s["domain"],
            "t4": s["t4"],
            "trust_remote_code": s["trust_remote_code"],
            "note": s["note"],
        }
    return out


def write_mapping(path=None):
    path = path or os.path.join(BASE, "mapping.json")
    blob = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "policy": "KP-14 logical expert seats. Single Kaggle identity. HF offline.",
        "ladder": LADDER,
        "quota_pct": QUOTA,
        "rejected": REJECTED_CLAIMS,
        "seats": mapping_json(),
        "counts": counts(),
    }
    with open(path, "w") as f:
        json.dump(blob, f, indent=2)
    return path


def export_md():
    c = counts()
    lines = [
        "# Seat registry — KP-14 (logical experts, verified artifacts)",
        "",
        ACORN := ("ACORN_RULE: spoken co-signs beat disapproves; hold-peace is not consent."),
        "",
        "The 45 names are **logical expert seats**, not 45 downloaded giants.",
        "A catalog HTTP 200 is a listing, not authenticity.",
        "",
        f"- Seats catalogued: **{c['n']}**",
        f"- verified-checkpoint: **{c['verified-checkpoint']}**",
        f"- verified-api: **{c['verified-api']}**",
        f"- community-quarantine: **{c['community-quarantine']}**",
        f"- logical-emulated: **{c['logical-emulated']}**",
        f"- T4 easy / tight: {c['t4_easy']} / {c['t4_tight']}",
        "",
        "## Model ladder (what we actually run)",
        "",
    ]
    for row in LADDER:
        lines.append(f"- **{row['role']}** `{row['id']}` {row['params']} Q4~{row['q4_gb']}GB — {row['note']}")
    lines += [
        "",
        "## Weekly GPU quota split (percent of whatever hours the account actually gets)",
        "",
        "| Work | Share |",
        "|---|---:|",
        "| QLoRA adapter training | 45% |",
        "| Evaluation / regression | 25% |",
        "| Batched inference / data gen | 15% |",
        "| Quantization / compatibility | 10% |",
        "| Contingency | 5% |",
        "",
        "CPU sessions: registry, cleaning, prompts, unit tests, aggregation. "
        "Do not burn GPU while downloading or deciding the experiment.",
        "",
        "## Rejected claims (documented)",
        "",
    ]
    for r in REJECTED_CLAIMS:
        lines.append(f"- **{r['claim']}** — {r['why']}")
    lines += ["", "## Every seat", "",
              "| Seat | Status | Domain | Backend | Identifier | T4 | Note |",
              "|---|---|---|---|---|---|---|"]
    for s in SEATS:
        ident = s["identifier"] or "—"
        note = s["note"].replace("|", "/")
        lines.append(
            f"| `{s['key']}` | {s['status']} | {s['domain']} | {s['backend']} "
            f"| `{ident}` | {s['t4']} | {note} |"
        )
    lines += [
        "",
        "## Honesty",
        "",
        "- This sandbox: no GPU, no torch. Offline Qwen2.5-0.5B is a file, not a running model.",
        "- HF token absent; last live wave ended **402 credits depleted**.",
        "- Kaggle KGAT catalogs; shard download needs a Kaggle runtime.",
        "- Apertus lineage remains a **10 USD/node shop**, not a free tree.",
        "- GLM 5.5 stays unreleased. Muse Spark stays closed.",
        "",
    ]
    return "\n".join(lines) + "\n"


def console():
    c = counts()
    print("\n" + "▣" * 72)
    print("SEAT REGISTRY — KP-14  (logical seats, four labels)")
    print("▣" * 72)
    print(f"  n={c['n']}  verified-ckpt={c['verified-checkpoint']}  "
          f"verified-api={c['verified-api']}  quarantine={c['community-quarantine']}  "
          f"emulated={c['logical-emulated']}")
    print(f"  T4 easy={c['t4_easy']} tight={c['t4_tight']}")
    print("  rejected claims:", len(REJECTED_CLAIMS))
    print("▣" * 72)


if __name__ == "__main__":
    p = write_mapping()
    md = os.path.join(BASE, "SEAT_REGISTRY.md")
    with open(md, "w") as f:
        f.write(export_md())
    console()
    print("wrote", p, md)
