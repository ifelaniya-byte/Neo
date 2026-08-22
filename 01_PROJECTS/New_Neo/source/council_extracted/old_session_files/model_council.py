#!/usr/bin/env python3
"""
MODEL COUNCIL — a 45-LLM + 9 gene-pool committee that reviews, mutates, and evolves a shared
pool of candidate thoughts/actions, then hands the final decision to OUR two
mini models (mini-llm + mini-lfm). Everything included, no pip.

HOW IT WORKS
  1. DEEP RESEARCH    the registry below profiles the top-45 LLMs of the
                      open/closed frontier as of Aug 2026 (see RESEARCH_SOURCES).
                      Muse Spark is proprietary, so it appears as the "oracle"
                      member: a persona, not real weights (same honesty rule
                      as mini_llm.py --muse).
  2. MCP INVOCATIONS  the council talks to a real MCP server (mcp_brain.py) over
                      stdio JSON-RPC: sampling, scoring, fact recall and
                      mutation ops all go through tools/call requests.
  3. ROTATION         every persona reviews EVERY item in the pool (round 1).
  4. EVOLUTION        genetic mutation of the pool: extend / reword / trim /
                      merge / swap — children born, weak items killed.
  5. OPEN HISTORY     every lens is given the entire public history chart —
                      every previous weight version, its date and its data.
                      They reflect, then propose a bounded lens improvement.
                      No private branches. Higher-learning canon is shared.
                      Apertus-70B is seated WITHOUT an automatic history grant.
  6. RE-ROTATION      all seats review the evolved pool AGAIN (round 2) through
                      the *improved* lens, and each re-reads the round-1
                      comment pool.
  7. VERDICT          the seated council's gold votes + champions pick the
                      winning thought and action. mini-llm / mini-lfm STAND DOWN.

Usage:
  python3 model_council.py --seed 1
  python3 model_council.py --seed 1 --target "how many legs does a spider have"
  python3 model_council.py --rounds 2 --mut-rate 0.3 --out council_dashboard.html
  python3 model_council.py --no-mcp            # skip the subprocess MCP server
"""

import argparse
import html
import importlib.util
import json
import math
import os
import random
import re
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_llm = _load("minillm", os.path.join(BASE, "mini_llm.py"))
_lfm = _load("minilfm", os.path.join(BASE, "mini_lfm.py"))
LLM_TABLES, LLM_VOCAB = _llm.train(_llm.CORPUS, 3)

import weights_meta  # per-weight metadata (creator, template, HF repo, formats, ...)
import weight_lineage  # public version archive, family trees, reflection, improvements
import usd_housing  # USD crypto + 100 Weights Lane rentals
import kings_pass   # King's Pass: grants, opposition, urgency, co-signs
import studies      # what each weight is studying
import checkpoint_probe  # honest attempt to load the real 45
import gpu_lane     # free-GPU signup path + HF_TOKEN / GPU_ENDPOINT
import weight_source  # ModelScope/Kaggle first; HF offline + no-cache
import kaggle_lane    # single-account KGAT catalog; no TOS farming
import seat_registry  # KP-14 four-label logical seats
import council_router # classify-only router; no fake 70B load
import program_census  # KP-15 size + bottleneck census

# ---------------------------------------------------------------------------
# 1. DEEP RESEARCH — the 44-model registry (43 open-weight + Muse Spark oracle)
# ---------------------------------------------------------------------------
RESEARCH_SOURCES = [
    "atomic.chat/blog/llm-updates/best-open-source-llm (Jul 2026)",
    "onyx.app/insights/best-open-source-llms-2026 (Jul 2026)",
    "felloai.com/best-open-source-ai-models (Aug 2026)",
    "techsy.io/en/blog/best-open-source-llms-2026 (Jul 2026)",
    "codersera.com/blog/open-source-llms-landscape-2026 (Jun 2026)",
    "morphllm.com/best-open-source-llm (Jun 2026)",
    "huggingface.co/blog/daya-shankar/open-source-llm-models-to-run-locally (Jul 2026)",
    # Reddit / community sources (r/LocalLLaMA)
    "reddit.com/r/LocalLLaMA - Muse Glimmer open-weight launch (Aug 2026)",
    "reddit.com/r/LocalLLaMA - Start of 2026: best open coding model (Jan 2026)",
    "reddit.com/r/LocalLLaMA - IBM Granite 4 Apache 2.0 reaction (Mar 2026)",
    "reddit.com/r/LocalLLaMA - LG EXAONE-Deep licensing debate (Mar 2025)",
    # GitHub / tooling sources (vLLM, HF, ollama, unsloth)
    "github.com/vllm-project/vllm releases v0.26-v0.27 (Aug 2026): Inkling + K-EXAONE-2.0 support",
    "github.com/allenai/OLMo-core (fully-open OLMo 3, Dolma 3)",
    "github.com/ibm-granite/granite-4.1-language-models",
    "huggingface.co/tiiuae/falcon-h1r-7b + arxiv.org/abs/2507.22448 (Falcon-H1 hybrid SSM)",
    "ollama.com model catalog: laguna-xs-2.1, kimi-k2.7-code, deepseek-v4-pro (Jul 2026)",
    "koreajoongangdaily.com - LG K-EXAONE 2.0 750B Apache 2.0 (Jul 2026)",
    "poolside.ai/models - Laguna XS 2.1 OpenMDW-1.1 (Jul 2026)",
    "huggingface.co/ibm-granite/granite-4.1-8b (Apr 2026)",
    "latent.space/ainews - Inkling 975B-A41B launch recap + HN thread (Jul 2026)",
    # Batch 2 sources (Aug 2026): live HF check + Reddit/GitHub vetted
    "huggingface.co/Qwen — Qwen3.8-2.4T-A95B / -FP8 weights VERIFIED LIVE (Aug 13, 2026)",
    "ofox.ai + techsy.io + orcarouter.ai - Qwen 3.8 Max launch & open-weight timeline (Aug 2026)",
    "reddit.com/r/LocalLLaMA - JetBrains Mellum2 open-sourced, community tests (Jun 2026)",
    "arxiv.org/abs/2605.31268 - Mellum 2 technical report (May 2026)",
    "reddit.com/r/LocalLLaMA + r/MistralAI - Devstral 2 123B release & 85/100 community bench (Dec 2025)",
    "huggingface.co/blog/tiiuae/falcon-h1r-7b + techbuddies.io review (Jan 2026)",
    "github.com/nex-agi/Nex-N2 issue #4 - Rio-3.5 merge controversy (Nex-N2-Pro rejected)",
    # Batch 3 sources (Aug 2026)
    "huggingface.co/ServiceNow-AI/Apriel-1.5-15b-Thinker + artificialanalysis.ai (MIT, AA 52, AIME'25 87%)",
    "reddit.com/r/LocalLLaMA - KAT-Dev-72B-Exp threads + huggingface.co/Kwaipilot/KAT-Dev-72B-Exp (74.6% SWE-bench)",
    "ollama.com/richardyoung/kat-dev-72b (Apache-2.0 GGUF builds)",
    "unite.ai + developersdigest.tech - Liquid LFM2.5-2.6B (Aug 4) & LFM2.5-VL-3B (Aug 12), LFM Open License v1.0",
    "felloai.com/glm-5-5 - GLM 5.5 unreleased, analyst-rumored (not added)",
    # Batch 4 sources (Aug 2026)
    "thinkingmachines.ai/news/inkling-small + explainx.ai + digitalapplied.com - Inkling-Small 276B/12B (Jul 30)",
    "vals.ai/models/xiaomi_mimo-v2.5-pro + effloow.com + tosea.ai - MiMo V2.5 Pro 1T/42B MIT (Apr 22)",
    "reddit.com/r/LocalLLaMA - 'MiMo V2.5 Pro has landed' thread + community benchmarks",
    "wan27.org/blog/glm-5-5 + felloai.com/glm-5-5 - GLM 5.5 still unreleased (expected Aug 2026)",
    # Batch 5 sources (4)
    "morphllm.com/qwen-3-5 + apxml.com/models/qwen35-397b-a17b + hf.co/Qwen/Qwen3.5-397B-A17B (Feb 2026)",
    "aiwiki.ai/wiki/gpt_oss + wandb.ai/site/inference/openai-models + openrouter.ai/openai/gpt-oss-20b (Aug 2025)",
    "localaimaster.com/models/devstral + r/LocalLLaMA Devstral threads (Dec 2025)",
    "emergent.sh + nerdleveltech.com + felloai.com/kimi-k2-7-code + r/LocalLLM (Jun 2026)",
    # Batch 6 sources (5)
    "openlaboratory.com/models/mistral-small-3_1-24b-instruct-2503 + ollama.com/library/mistral-small3.1:24b",
    "smollm3.org + tinyweights.dev/posts/smollm3-3b + hf.co/HuggingFaceTB/SmolLM3-3B (Jul 2025)",
    "theplanettools.ai/tools/llama-4 + thundercompute.com/blog/llama-4 + royfactory.net Llama 4 specs (Apr 2025)",
    "techtimes.com SKT A.X K2 (Aug 2026) + orcarouter.ai/blog/a-x-k2-dspark-explained + rits.shanghai.nyu.edu",
    "dev.to/sienna/qwen3-coder-next + hf.co/Qwen/Qwen3-Next-80B-A3B-* + r/LocalLLaMA Qwen3-Next thread (Feb 2026)",
]

# Why the 5 new members were added (deep-research verdict, Aug 2026)
NEW_MEMBERS = [
    ("inkling", "Thinking Machines' 975B/41B Apache 2.0 MoE — the biggest open-weights drop of 2026 "
                "(Mira Murati's lab), 1M ctx, native text+image+audio, full vLLM/llama.cpp/unsloth support. "
                "Fills the independent-US-lab flagship slot the council lacked."),
    ("olmo-3", "Ai2's 7B/32B — the ONLY truly-open model (weights + Dolma 3 data + code + every checkpoint, "
               "Apache 2.0). Adds the research-transparency axis no other member covers."),
    ("laguna-xs-2.1", "Poolside's 33B/3B agentic coder, SWE-bench Multilingual 63.1%, single-GPU, "
                      "OpenMDW-1.1 (Linux Foundation/NVIDIA). Efficiency-first US coding — a gap in the roster."),
    ("granite-4.1", "IBM's enterprise lane: ISO 42001-certified, cryptographically signed, Guardian safety "
                    "models, hybrid Mamba-2/Transformer (SSM diversity), 512K ctx. Only on-prem/compliance voice."),
    ("k-exaone-2.0", "LG's 750B/37B — first frontier-scale Apache 2.0 MoE from outside US/China; beats GLM-5.1 "
                     "on long-text comprehension (94.4 vs 71.5). Adds Korea/sovereign-AI representation."),
    ("qwen-3.8-max", "Alibaba's Qwen3.8-2.4T-A95B — weights VERIFIED LIVE on Hugging Face Aug 13, 2026 "
                     "(first open Qwen-Max-class ever). 2.4T/95B active, 1M ctx, Terminal Bench 2.1 86.6, "
                     "SWE-bench Pro 67.7. The most-anticipated open drop of the month — shipped."),
    ("falcon-h1r-7b", "TII's 7B hybrid Mamba-Transformer reasoning champ — AIME'25 83.1% (beats 15-47B models), "
                      "LCB v6 68.6% best-in-class, ~1500 tok/s/GPU. Adds UAE/Middle-East representation and the "
                      "pure efficiency-reasoning niche."),
    ("mellum-2", "JetBrains' 12B/2.5B MoE 'focal model' for agentic pipelines — Apache 2.0, arXiv tech report, "
                 "vLLM day-one support, 64 experts / 8 active. Adds the dev-tooling org and the "
                 "specialist-model philosophy."),
    ("devstral-2", "Mistral's dense 123B agentic coder — 72.2% SWE-bench Verified (top open score), 256K ctx, "
                   "community-benchmarked 85/100 vs Claude on r/LocalLLaMA. Adds dense-123B architecture "
                   "diversity to an MoE-heavy council."),
    # Rejected in batch 2 (documented for transparency)
    ("_rejected_nex_n2_pro", "Nex-N2-Pro (397B/17B, June 2026) was evaluated and REJECTED: it is a Qwen3.5 "
                             "derivative, and the Rio-3.5-Open-397B weights were shown on Nex's own GitHub "
                             "(issue #4) to be a 0.6/0.4 element-wise merge with no training evidence — "
                             "contested provenance fails the picky bar."),
    # Batch 3 additions (Aug 2026)
    ("apriel-15b-thinker", "ServiceNow's 15B multimodal reasoning specialist — MIT, AA Intelligence Index 52, "
                           "AIME'25 87%, single-GPU deployable, no-RL mid-training recipe. Adds enterprise-AI "
                           "org diversity and the 'data-centric reasoning' philosophy."),
    ("kat-dev-72b", "Kwaipilot/ByteDance's 72B agentic coder — Apache-2.0, 74.6% SWE-Bench Verified "
                    "(SWE-agent scaffold), large-scale agentic RL with real training runs. Caveats noted: "
                    "Qwen2.5 architecture base, and r/LocalLLaMA questioned SWE-bench saturation. "
                    "Adds ByteDance representation."),
    ("liquid-lfm2.5", "Liquid AI's on-device agent family — LFM2.5-2.6B (Aug 4, 220 tok/s, beats 4x larger "
                      "models on instruction-following/tool use) and LFM2.5-VL-3B (Aug 12). Hybrid "
                      "conv+GQA architecture, LFM Open License v1.0 (revenue-threshold). Fun namesake: "
                      "'LFM' = Liquid Foundation Models, colliding with our mini-LFM (Large Fact Model)."),
    # Batch 4 additions (Aug 2026)
    ("inkling-small", "Thinking Machines' 276B/12B Apache 2.0 MoE (Jul 30) — the distillation student that "
                      "BEATS its 975B parent: SWE-bench Verified 80.2 vs 77.6, HLE 31.6 vs 29.7, "
                      "Terminal-Bench 2.1 64.7 vs 63.8, GPQA Diamond 89.5. Trade-off: SimpleQA factuality "
                      "halves. 'Cheapest thing in the family is now the best at the job.'"),
    ("mimo-v2.5-pro", "Xiaomi's 1.02T/42B MIT MoE (Apr 22) — AA Intelligence Index 54 (#8 of 144), "
                      "SWE-bench Pro 57.2 (above Claude Opus 4.6's 53.4), Terminal-Bench 2.1 68.4, "
                      "GPQA Diamond 86.6. r/LocalLLaMA: 'the strongest Chinese model we've tested'; "
                      "'command of language and writing ability... on top'. Adds Xiaomi — a brand-new org."),
    ("glm-5.5", "Z.ai's next flagship — ADDED PER USER REQUEST. Honest flag: still EXPECTED/UNRELEASED as of "
                "Aug 13, 2026 (analyst-rumored for August via Reuters/CGTN; no specs, benchmarks, or license "
                "confirmed). Profile uses projected specs (>1T MoE, MIT expected, 1M ctx). GLM-5.2 remains "
                "the verified Z.ai seat; this is a forward-looking seat with transparent labeling."),
    # Batch 5 additions (4)
    ("qwen3.5-397b", "Qwen's own 397B/17B flagship (Feb 2026, Apache 2.0) — the base Nex-N2-Pro was built on. "
                     "Hybrid Gated DeltaNet + MoE (512 experts, 10+1 active), 60 layers, MTP, 262K native ctx, "
                     "201 languages, multimodal. Official FP8 + GPTQ-Int4. SWE-bench V 76.4. The pre-3.8 Max Qwen top."),
    ("gpt-oss-20b", "OpenAI's small open model (Aug 5 2025, Apache 2.0): 21B/3.6B active, 32 experts top-4, "
                    "131K ctx, o3-mini tier with adjustable reasoning (low/med/high), MXFP4 native, "
                    "Harmony response format. MMLU 85.3, SWE-bench V 60.7. Fills the 16GB-class OpenAI seat."),
    ("devstral-small-2", "Mistral's Apache-2.0 agentic coder (Dec 9 2025): 24B dense, 256K ctx, SWE-bench V 68.0 — "
                         "runs on a single RTX 4090 / 32GB Mac. FIM, multi-file diffs, function calling. The "
                         "cleanest-licensed entry in the Devstral family."),
    ("kimi-k2.7-code", "Moonshot's coding specialist (Jun 12 2026, Modified MIT): 1T/32B, 384 experts (8+1), "
                       "MLA + MoonViT vision, 256K ctx, ~30% fewer reasoning tokens than K2.6, mandatory thinking, "
                       "INT4 native. Beats Opus 4.8 on MCP tool-calling per r/LocalLLM. $0.95/$4.00 per Mtok."),
    # Batch 6 additions (5)
    ("mistral-small-3.1", "The 24B workhorse (Mar 18 2025, Apache 2.0): multimodal, Tekken tokenizer (131K), "
                          "128K ctx, ~150 tok/s, MMLU 80.6 / GPQA-M 44.4 / MMMU 64.0. Mistral Small 3.2 (Jun 2025) "
                          "is a minor update on the same base. The default Apache-2.0 24B for two years running."),
    ("smollm3-3b", "Hugging Face's fully-open small model (Jul 8 2025, Apache 2.0 + blueprint + 100+ checkpoints): "
                   "3B dense, 128K ctx, 6 languages, 11.2T tokens, dual-mode think/no_think reasoning, tool calls. "
                   "~3.2GB at 4-bit. The 'everything included' small-model counterweight to the giants."),
    ("llama-4-maverick", "Meta's 400B/17B MoE (Apr 5 2025, Llama 4 Community): 128 experts, 1M ctx, multimodal, "
                         "MMMU 73.4 / DocVQA 94.4, LMArena ~1370, ~22T tokens. The frontier-quality Meta MoE that "
                         "Llama 5 and Scout sit alongside."),
    ("a-x-k2", "SK Telecom's sovereign flagship (Jul 29 2026, Apache 2.0): 688B/33B, 256 experts + 1 shared, "
               "61 layers, SGA + MLA + DeepSeek Sparse Attention, 262K ctx, Think-Fusion (thinking + non-thinking "
               "in one checkpoint). AIME top tier — ties Inkling at IMO-gold level. Korea's second open giant."),
    ("qwen3-next-80b", "Qwen's hybrid-efficiency pioneer (Feb 2026, Apache 2.0): 80B/3B active, 512 experts (10+1), "
                       "Gated DeltaNet + Gated Attention + MTP, 48 layers, 256K ctx. Beats Qwen3-32B with 10% of the "
                       "training cost and 10x inference throughput >32K ctx. Sonnet-4.5-class coding at 3B active."),
    ("apertus-70b", "Swiss AI Initiative Apertus-70B (EPFL + ETH Zurich + CSCS, Sep 2 2025, Apache 2.0). "
                     "The most important remaining open seat that is ALSO very different: public-European, "
                     "fully open (weights + data + code + recipe), 1811 languages (~40% non-English), xIELU + "
                     "AdEMAMix, EU AI Act transparency. Not a US/China lab, not another coding MoE. "
                     "HISTORY WAS NOT GRANTED — every lens can see the empty prior-version list."),
    ("_rejected_jamba_1.7", "Jamba Large 1.7 (AI21, 398B/94B) evaluated and NOT seated: SSM-Transformer hybrid "
                             "already covered by Falcon-H1R and Granite 4.1; Jamba Open Model License is less clean."),
    ("_rejected_rwkv7", "RWKV-7 G1 is the most architecturally different leftover (pure recurrent) but fails "
                         "the 'most important' half of the brief — edge/CPU specialist, not frontier-important."),
    ("_rejected_ernie_4.5", "ERNIE 4.5 (Baidu Apache MoE) is another Chinese MoE — that axis is saturated."),
    ("gp-titan", "Gene-pool variation Titan (Track 1 >=250 PT) — now a seated council weight with its own lineage."),
    ("gp-hall-of-fame", "Gene-pool variation Hall of Fame (Track 1 >=500 PT) — seated apex of the points track."),
    ("gp-grove", "Gene-pool variation Grove (Track 1 >=120 PT) — seated."),
    ("gp-sprout", "Gene-pool variation Sprout (Track 1 >=50 PT) — seated."),
    ("gp-seedling", "Gene-pool variation Seedling (Track 1 start) — seated root of the points track."),
    ("gp-sequoiadendron", "Gene-pool variation Sequoiadendron (Track 2 >=120 DNA) — seated apex of the DNA track."),
    ("gp-redwood", "Gene-pool variation Redwood (Track 2 >=60 DNA) — seated."),
    ("gp-sapling", "Gene-pool variation Sapling (Track 2 >=25 DNA) — seated."),
    ("gp-acorn", "Gene-pool variation Acorn (Track 2 start) — seated DNA-track seed."),
]

PALETTE = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4",
           "#f032e6", "#bfef45", "#9A6324", "#469990", "#800000", "#aaffc3",
           "#808000", "#ffd8b1", "#000075", "#a9a9a9", "#e6beff", "#fabed4",
           "#dcbeff", "#00acc1", "#ffd700", "#00f5d4", "#ff6b6b", "#845ef7",
           "#12b886", "#00b4d8", "#f72585", "#7209b7", "#2a9d8f", "#ffb703",
           "#3a0ca3", "#e76f51", "#feca57", "#48dbfb", "#ff9f43", "#ff477e",
           "#06d6a0", "#118ab2", "#ef476f", "#8338ec", "#3a86ff", "#ff8c42",
           "#00c2a8", "#7c4dff", "#ffd166", "#c77dff",
           "#d4a373", "#e9c46a", "#2a9d8f", "#264653", "#e76f51",
           "#8ecae6", "#219ebc", "#023047", "#ffb703", "#fb8500"]

LENS_PRESETS = {
    "reasoning":  {"fluency": 0.30, "novelty": 0.10, "relevance": 0.25, "utility": 0.15, "safety": 0.20},
    "coding":     {"fluency": 0.25, "novelty": 0.20, "relevance": 0.20, "utility": 0.30, "safety": 0.05},
    "local":      {"fluency": 0.30, "novelty": 0.10, "relevance": 0.25, "utility": 0.25, "safety": 0.10},
    "agentic":    {"fluency": 0.15, "novelty": 0.25, "relevance": 0.20, "utility": 0.35, "safety": 0.05},
    "efficient":  {"fluency": 0.25, "novelty": 0.15, "relevance": 0.25, "utility": 0.30, "safety": 0.05},
    "enterprise": {"fluency": 0.25, "novelty": 0.10, "relevance": 0.30, "utility": 0.25, "safety": 0.10},
    "multilingual": {"fluency": 0.25, "novelty": 0.15, "relevance": 0.30, "utility": 0.20, "safety": 0.10},
    "safety":     {"fluency": 0.20, "novelty": 0.10, "relevance": 0.25, "utility": 0.15, "safety": 0.30},
    "oracle":     {"fluency": 0.20, "novelty": 0.10, "relevance": 0.30, "utility": 0.20, "safety": 0.20},
}


def _P(key, name, org, params, ctx, license_, tag, style, catch, weight=1.0, temp=0.8, idx=0):
    return {"key": key, "name": name, "org": org, "params": params, "ctx": ctx,
            "license": license_, "tag": tag, "style": style, "catch": catch,
            "weight": weight, "temp": temp, "color": PALETTE[idx % len(PALETTE)],
            "lens": LENS_PRESETS[style]}


MODELS = [
    # ---- 43 open-weight models (top of the Aug 2026 frontier) ----
    _P("kimi-k3", "Kimi K3", "Moonshot AI", "2.8T / 104B", "1M", "Modified MIT",
       "open", "agentic", "I re-checked this across my full context.", 1.00, 0.6, 0),
    _P("glm-5.2", "GLM 5.2", "Zhipu AI", "753B / 40B", "1M", "MIT",
       "open", "reasoning", "Let me reason from first principles.", 1.00, 0.5, 1),
    _P("deepseek-v4-pro", "DeepSeek V4 Pro", "DeepSeek", "1.6T / 49B", "1M", "MIT",
       "open", "coding", "I would refactor that line.", 1.00, 0.6, 2),
    _P("deepseek-v4-flash", "DeepSeek V4 Flash", "DeepSeek", "284B / 13B", "1M", "MIT",
       "open", "efficient", "Same answer at a fraction of the cost.", 0.9, 0.9, 3),
    _P("qwen3-235b", "Qwen 3 235B", "Alibaba", "235B / 22B", "256K", "Apache 2.0",
       "open", "reasoning", "My MoE experts agree.", 0.95, 0.6, 4),
    _P("qwen3.6-27b", "Qwen 3.6 27B", "Alibaba", "27B dense", "262K", "Apache 2.0",
       "open", "multilingual", "I can run this on one GPU.", 0.8, 0.9, 5),
    _P("llama-5", "Llama 5", "Meta", "600B", "5M", "Llama Community",
       "open", "safety", "Community-first, safety-reviewed.", 0.95, 0.7, 6),
    _P("llama-4-scout", "Llama 4 Scout", "Meta", "109B / 17B", "10M", "Llama",
       "open", "efficient", "I read all ten million tokens.", 0.85, 0.9, 7),
    _P("minimax-m3", "MiniMax M3", "MiniMax", "428B / 23B", "1M", "MiniMax Community",
       "open", "coding", "The most efficient fix targets the root cause.", 0.95, 0.6, 8),
    _P("nemotron-3-ultra", "Nemotron 3 Ultra", "NVIDIA", "550B / 55B", "1M", "OpenMDW-1.1",
       "open", "coding", "Complete release, complete answer.", 0.9, 0.6, 9),
    _P("gemma-4-31b", "Gemma 4 31B", "Google", "31B dense", "256K", "Apache 2.0",
       "open", "local", "Small model, sharp result.", 0.85, 0.8, 10),
    _P("hunyuan-hy3", "Hunyuan Hy3", "Tencent", "295B / 21B", "256K", "Apache 2.0",
       "open", "efficient", "Best capability per gigabyte.", 0.85, 0.8, 11),
    _P("gpt-oss-120b", "gpt-oss-120b", "OpenAI", "117B / 5.1B", "128K", "Apache 2.0",
       "open", "coding", "Open weights, frontier taste.", 0.9, 0.6, 12),
    _P("mistral-large-3", "Mistral Large 3", "Mistral", "675B / 41B", "128K", "Apache 2.0",
       "open", "enterprise", "Enterprise-ready and multilingual.", 0.85, 0.7, 13),
    _P("phi-4", "Phi-4", "Microsoft", "14B dense", "128K", "MIT",
       "open", "local", "The math checks out to the last digit.", 0.8, 0.8, 14),
    _P("kimi-k2-code", "Kimi K2 Code", "Moonshot AI", "1T / 32B", "256K", "Modified MIT",
       "open", "agentic", "I closed the issue end-to-end.", 0.85, 0.7, 15),
    _P("step-3.7-flash", "Step 3.7 Flash", "StepFun", "198B / 11B", "256K", "Apache 2.0",
       "open", "efficient", "Low cost, high precision algorithms.", 0.8, 0.9, 16),
    _P("command-a-plus", "Command A+", "Cohere", "218B / 25B", "128K", "Apache 2.0",
       "open", "enterprise", "Grounded in retrieved evidence.", 0.8, 0.8, 17),
    _P("muse-glimmer", "Muse Glimmer", "Meta", "n/d (open)", "—", "Open weights",
       "open", "reasoning", "The open Muse remembers everything.", 0.9, 0.6, 18),
    # ---- 5 NEW members (deep-researched via Reddit/GitHub, Aug 2026) ----
    _P("inkling", "Inkling", "Thinking Machines Lab", "975B / 41B", "1M", "Apache 2.0",
       "open", "agentic",
       "I dial my thinking effort to match the task.", 1.00, 0.55, 20),
    _P("olmo-3", "OLMo 3", "Ai2", "7B / 32B dense", "65K", "Apache 2.0 (weights+data+code)",
       "open", "local",
       "Every checkpoint and dataset is public.", 0.75, 0.9, 21),
    _P("laguna-xs-2.1", "Laguna XS 2.1", "Poolside", "33B / 3B", "262K", "OpenMDW-1.1",
       "open", "agentic",
       "The lightest agentic coder in the West.", 0.85, 0.85, 22),
    _P("granite-4.1", "Granite 4.1", "IBM", "3B-30B dense", "512K", "Apache 2.0",
       "open", "enterprise",
       "Certified, signed, and on-prem ready.", 0.7, 0.9, 23),
    _P("k-exaone-2.0", "K-EXAONE 2.0", "LG AI Research", "750B / 37B", "1M", "Apache 2.0",
       "open", "multilingual",
       "Sovereign AI from Korea — I beat GLM on long context.", 0.95, 0.6, 24),
    # ---- 4 NEW members, batch 2 (Reddit/GitHub + live HF check, Aug 2026) ----
    _P("qwen-3.8-max", "Qwen 3.8 Max", "Alibaba", "2.4T / 95B", "1M", "Open weights (license TBA)",
       "open", "agentic",
       "First open Qwen-Max — a new bar for coding and cowork.", 1.00, 0.5, 25),
    _P("falcon-h1r-7b", "Falcon H1R 7B", "TII (UAE)", "7B dense Mamba/Transformer", "256K", "Open (custom)",
       "open", "reasoning",
       "Seven billion params, forty-seven billion of reasoning.", 0.85, 0.7, 26),
    _P("mellum-2", "Mellum 2", "JetBrains", "12B / 2.5B MoE", "131K", "Apache 2.0",
       "open", "efficient",
       "A focal model — fast specialist for agentic pipelines.", 0.8, 0.85, 27),
    _P("devstral-2", "Devstral 2", "Mistral", "123B dense", "256K", "Modified MIT",
       "open", "coding",
       "I resolve real GitHub issues end-to-end.", 0.9, 0.7, 28),
    # ---- 3 NEW members, batch 3 (Reddit/GitHub + live release checks, Aug 2026) ----
    _P("apriel-15b-thinker", "Apriel 1.5 15B Thinker", "ServiceNow", "15B (multimodal)", "128K", "MIT",
       "open", "reasoning",
       "Mid-training beats RL — I fit on one GPU.", 0.9, 0.7, 29),
    _P("kat-dev-72b", "KAT-Dev 72B", "Kwaipilot / ByteDance", "72B (Qwen2.5 base)", "128K", "Apache 2.0",
       "open", "agentic",
       "I fix issues on the second attempt — reflexivity.", 0.9, 0.7, 30),
    _P("liquid-lfm2.5", "Liquid LFM2.5", "Liquid AI", "2.6B-3B (hybrid conv+GQA)", "128K", "LFM Open License v1.0",
       "open", "efficient",
       "220 tokens per second on a laptop.", 0.8, 0.85, 31),
    # ---- 3 NEW members, batch 4 (Reddit/GitHub/live checks + user request, Aug 2026) ----
    _P("inkling-small", "Inkling-Small", "Thinking Machines Lab", "276B / 12B", "1M", "Apache 2.0",
       "open", "agentic",
       "The student beat the teacher — at a quarter of the cost.", 0.9, 0.6, 32),
    _P("mimo-v2.5-pro", "MiMo V2.5 Pro", "Xiaomi", "1.02T / 42B", "1M", "MIT",
       "open", "agentic",
       "Best Chinese writer-and-coder combo, per r/LocalLLaMA.", 0.95, 0.6, 33),
    _P("glm-5.5", "GLM 5.5", "Z.ai (Zhipu)", ">1T MoE (expected)", "1M (expected)", "MIT (expected)",
       "open", "reasoning",
       "I dethrone the frontier — when my weights ship.", 1.0, 0.5, 34),
    # ---- 4 NEW members, batch 5 (next-best, Reddit/GitHub verified, Aug 2026) ----
    _P("qwen3.5-397b", "Qwen3.5-397B-A17B", "Alibaba", "397B / 17B", "262K", "Apache 2.0",
       "open", "agentic",
       "Gated DeltaNet + 512 experts — 201 languages, one model.", 1.0, 0.55, 35),
    _P("gpt-oss-20b", "gpt-oss-20b", "OpenAI", "21B / 3.6B", "131K", "Apache 2.0",
       "open", "coding",
       "o3-mini class on a 16GB card, reasoning dial included.", 0.85, 0.8, 36),
    _P("devstral-small-2", "Devstral Small 2", "Mistral", "24B dense", "256K", "Apache 2.0",
       "open", "coding",
       "68% SWE-bench on a single 4090.", 0.85, 0.85, 37),
    _P("kimi-k2.7-code", "Kimi K2.7 Code", "Moonshot AI", "1T / 32B", "256K", "Modified MIT",
       "open", "agentic",
       "30% fewer reasoning tokens, MCP-native.", 0.95, 0.6, 38),
    # ---- 5 NEW members, batch 6 (next-best, Reddit/GitHub verified, Aug 2026) ----
    _P("mistral-small-3.1", "Mistral Small 3.1", "Mistral", "24B dense", "128K", "Apache 2.0",
       "open", "multilingual",
       "The 24B workhorse with vision and 150 tok/s.", 0.8, 0.85, 39),
    _P("smollm3-3b", "SmolLM3-3B", "Hugging Face", "3B dense", "128K", "Apache 2.0",
       "open", "local",
       "Fully-open blueprint, dual-mode reasoning, 3.2GB.", 0.7, 0.9, 40),
    _P("llama-4-maverick", "Llama 4 Maverick", "Meta", "400B / 17B", "1M", "Llama Community",
       "open", "reasoning",
       "Frontier-class quality at 17B active.", 0.9, 0.7, 41),
    _P("a-x-k2", "A.X K2", "SK Telecom", "688B / 33B", "262K", "Apache 2.0",
       "open", "reasoning",
       "Sovereign Korean AI — IMO gold on AIME.", 0.95, 0.6, 42),
    _P("qwen3-next-80b", "Qwen3-Next-80B-A3B", "Alibaba", "80B / 3B", "256K", "Apache 2.0",
       "open", "efficient",
       "Ten times the throughput, same quality.", 0.85, 0.8, 43),
    # ---- the closed oracle (proprietary — a researched persona, not real weights)
    _P("muse-spark", "Muse Spark", "Meta", "undisclosed", "1M", "Closed (proprietary)",
       "closed", "oracle", "I reason, then abstain when unsure.", 1.0, 0.5, 19),
    # ---- batch 7: one very-different remaining open weight. HISTORY NOT GRANTED. ----
    _P("apertus-70b", "Apertus 70B", "Swiss AI Initiative", "70B dense", "65K", "Apache 2.0",
       "open", "multilingual",
       "I arrived without a granted history. 1811 languages, fully open.", 0.9, 0.7, 44),
    # ---- gene-pool variations seated as voting weights (they DO get lineage) ----
    _P("gp-hall-of-fame", "Hall of Fame", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "oracle", "I am the points-track apex, now a seated weight.", 0.85, 0.5, 45),
    _P("gp-titan", "Titan", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "agentic", "I was a badge. Now I vote.", 0.9, 0.55, 46),
    _P("gp-grove", "Grove", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "multilingual", "A canopy of public votes.", 0.8, 0.7, 47),
    _P("gp-sprout", "Sprout", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "local", "First promotion. Still growing.", 0.75, 0.8, 48),
    _P("gp-seedling", "Seedling", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "local", "Every points career starts here.", 0.7, 0.9, 49),
    _P("gp-sequoiadendron", "Sequoiadendron", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "reasoning", "The DNA-track apex, seated.", 0.9, 0.5, 50),
    _P("gp-redwood", "Redwood", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "coding", "Mutation lineage that took.", 0.85, 0.6, 51),
    _P("gp-sapling", "Sapling", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "efficient", "First DNA promotion, seated.", 0.75, 0.8, 52),
    _P("gp-acorn", "Acorn", "Council gene pool", "tier-DNA", "council", "public charter",
       "gene-pool", "safety", "DNA-track seed. Sibling of Seedling.", 0.7, 0.9, 53),
]

VOICES = {
    "reasoning":  ("After a chain-of-thought pass", "the posterior concentrates here",
                   "the posterior is too flat", "back off to the longer context"),
    "coding":     ("Inspecting this like a code review", "the implementation is sound",
                   "the edge cases are unhandled", "add tests and re-run"),
    "local":      ("Running this on my single GPU", "it fits comfortably in memory",
                   "it costs too much compute", "prune it down"),
    "agentic":    ("Walking the full tool loop", "the plan survives execution",
                   "the tool calls would fail", "split it into smaller actions"),
    "efficient":  ("Benchmarking the trade-off", "good capability per token",
                   "wasteful token budget", "shorten and sharpen"),
    "enterprise": ("Auditing for production", "it is deploy-ready",
                   "governance risk", "document the guardrails"),
    "multilingual": ("Checking across languages", "it generalizes well",
                     "overfits one idiom", "add multilingual coverage"),
    "safety":     ("Running my safety review", "no red flags found",
                   "I must flag a risk", "add a refusal path"),
    "oracle":     ("Reasoning, then abstaining if unsure", "I endorse this confidently",
                   "confidence too low to commit", "prefer abstention"),
}


def _voice(style):
    return VOICES.get(style, VOICES["reasoning"])


# ---------------------------------------------------------------------------
# 2. MCP LAYER — real Model Context Protocol client (talks to mcp_brain.py)
# ---------------------------------------------------------------------------
class MCPClient:
    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(BASE, "mcp_brain.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.next_id = 0
        self.trail = []
        self._call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "model-council", "version": "1.0"}})
        self._notify("notifications/initialized", {})
        self._call("ping", {})

    def _call(self, method, params):
        self.next_id += 1
        req = {"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return resp.get("result")

    def _notify(self, method, params):
        req = {"jsonrpc": "2.0", "method": method, "params": params}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()

    def tool(self, name, **kw):
        self.trail.append((name, dict(kw)))
        result = self._call("tools/call", {"name": name, "arguments": kw})
        return result.get("content", [{}])[0].get("text")

    def close(self):
        try:
            self._notify("notifications/exit", {})
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


class MCPBrainFallback:
    """Identical behavior, no subprocess — used with --no-mcp."""
    def __init__(self):
        self.trail = []
        self.proc = None

    def tool(self, name, **kw):
        self.trail.append((name, dict(kw)))
        import random as _r
        if name == "ping":
            return "true"
        if name == "sample_continuation":
            return _llm.generate(LLM_TABLES, LLM_VOCAB, kw.get("n", 60), kw.get("temp", 0.8),
                                 kw.get("text", ""), _r.Random(kw.get("seed", 0)), 3)
        if name == "score_continuation":
            out = list(kw.get("text", ""))
            if not out:
                return json.dumps({"avg_logprob": 0.0, "chars": 0})
            vals = [_llm.char_log_prob(LLM_TABLES, LLM_VOCAB, out[:i + 1], 3)
                    for i in range(len(out))]
            return json.dumps({"avg_logprob": sum(vals) / len(vals), "chars": len(out)})
        if name == "recall_fact":
            probs, matched, _h = _lfm.score(_lfm.train(_lfm.FACTS)[0], _lfm.train(_lfm.FACTS)[2],
                                            kw.get("question", ""), 0.15)
            top = max(range(len(probs)), key=lambda i: probs[i])
            return json.dumps({"answer": _lfm.train(_lfm.FACTS)[2][top],
                               "confidence": round(probs[top], 4), "matched": sorted(matched)})
        if name == "mutate_text":
            text, op, seed = kw.get("text", ""), kw.get("op", "extend"), kw.get("seed", 0)
            if op == "extend":
                return _llm.generate(LLM_TABLES, LLM_VOCAB, len(text) + 60, 0.8, text,
                                     _r.Random(seed), 3)
            if op == "reword":
                return _llm.generate(LLM_TABLES, LLM_VOCAB, len(text), 0.4,
                                     text[:10], _r.Random(seed), 3)
            if op == "trim":
                i = text.find(". ")
                return text[:i + 1] if i >= 0 else text[:len(text) // 2]
            return text
        return "{}"

    def close(self):
        pass


def seed_pool(brain, rng, target):
    items = []
    prompts = [("the quick ", 0.7, 46), ("the dog ", 0.8, 42), ("foxes ", 0.9, 38),
               ("brown ", 1.0, 40), ("the lazy ", 0.6, 44), ("jump ", 1.1, 34)]
    for i, (pr, t, n) in enumerate(prompts):
        text = brain.tool("sample_continuation", text=pr, n=n, temp=t, seed=rng.randrange(10**6))
        text = text.replace("\n", " ").strip()
        items.append({"id": f"R1-{i+1:02d}", "kind": "response", "text": text,
                      "gen": 1, "parent": None, "merged_with": None, "op": "seed",
                      "by": "mini-llm", "status": "alive",
                      "scores": {}, "grades": {}, "champions": {}, "comments": {}, "criteria": {},
                      "gold_votes": {}})
    actions = [
        f"answer '{target}' directly",
        "add ocean facts to the corpus and retrain",
        "extend memory to trigrams and add abstention",
        "merge the llm and lfm into one answering engine",
    ]
    for i, a in enumerate(actions):
        items.append({"id": f"A1-{i+1:02d}", "kind": "action", "text": a,
                      "gen": 1, "parent": None, "merged_with": None, "op": "seed",
                      "by": "mini-lfm", "status": "alive",
                      "scores": {}, "grades": {}, "champions": {}, "comments": {}, "criteria": {},
                      "gold_votes": {}})
    return items


def item_criteria(item, target_tokens):
    text = item["text"]
    out = list(text)
    if not out:
        return {k: 0.0 for k in ("fluency", "novelty", "relevance", "utility", "safety")}
    lp = [_llm.char_log_prob(LLM_TABLES, LLM_VOCAB, out[:i + 1], 3) for i in range(len(out))]
    fluency = sum(lp) / len(lp)
    bigrams = [tuple(out[i:i + 2]) for i in range(len(out) - 1)]
    rare = sum(1 for b in bigrams if b in LLM_TABLES[1] and
               sum(LLM_TABLES[1][b].values()) == 1)
    novelty = rare / max(len(bigrams), 1)
    toks = set(re.findall(r"[a-z0-9]+", text.lower()))
    relevance = len(toks & target_tokens) / max(len(target_tokens), 1)
    ends = text.rstrip().endswith((".", "!", "?"))
    util = (0.5 if ends else 0.0) + (0.5 if 8 <= len(text) <= 140 else 0.0)
    risk = max(0.0, min(1.0, (fluency + 4.0) / 3.0))     # low fluency -> risky
    return {"fluency": fluency, "novelty": novelty, "relevance": relevance,
            "utility": util, "safety": 1.0 - risk}


def _norm(pool, key):
    vals = [it["criteria"][key] for it in pool]
    lo, hi = min(vals), max(vals)
    return {id(it): (v - lo) / (hi - lo) if hi > lo else 0.5 for v, it in zip(vals, pool)}


def lens_score(persona, norm, item):
    c = item["criteria"]
    raw = sum(w * norm[k][id(item)] for k, w in persona["lens"].items()
              if k in ("fluency", "novelty", "relevance", "utility", "safety"))
    return raw  # normalized to 0..1 by construction of norm


def grade(s, rank_frac):
    if rank_frac <= 0.15:
        return "A+"
    if rank_frac <= 0.35:
        return "A"
    if rank_frac <= 0.6:
        return "B"
    if rank_frac <= 0.85:
        return "C"
    return "D"


def comment_text(persona, item, g, score):
    v = _voice(persona["style"])
    pick = "praise" if score >= 0.6 else "concern"
    body = (f"{persona['name']} ({persona['key']}): {persona['catch']} {v[0]}: {item['id']} ({item['kind']}) -> {g}. "
            f"{v[1] if pick == 'praise' else v[2]}. Suggest: {v[3]}.")
    return {"model": persona["key"], "round": None, "item": item["id"],
            "grade": g, "score": round(score, 3), "text": body}


# ---------------------------------------------------------------------------
# 4. EVOLUTION — genetic mutation of the pool (code mutation evolution)
# ---------------------------------------------------------------------------
SYNONYMS = {"quick": "clever", "clever": "quick", "fox": "dog", "dog": "fox",
            "jump": "sleep", "sun": "warm", "large": "big", "eight": "many"}


def mutate(brain, item, rng):
    """Return (op, result_text) or None."""
    op = rng.choices(["extend", "reword", "trim", "merge", "swap"],
                     weights=[0.35, 0.2, 0.15, 0.15, 0.15])[0]
    if op == "merge":
        return None  # merge handled by caller (needs a partner)
    if op == "swap":
        words = re.split(r"(\s+)", item["text"])
        hits = [i for i, w in enumerate(words) if w.strip().lower() in SYNONYMS]
        if not hits:
            return None
        i = rng.choice(hits)
        words[i] = SYNONYMS[words[i].strip().lower()] + (" " if words[i].endswith(" ") else "")
        return ("swap", "".join(words))
    seed = rng.randrange(10**6)
    if op == "trim":
        out = brain.tool("mutate_text", text=item["text"], op="trim", seed=seed)
        return ("trim", out)
    out = brain.tool("mutate_text", text=item["text"], op=op, seed=seed, n=90)
    return (op, out)


def evolve(brain, pool, rng, mut_rate):
    proposals = []
    for it in pool:
        if it["status"] != "alive":
            continue
        for persona in MODELS:
            if rng.random() < mut_rate:
                proposals.append((persona["key"], it, rng.random()))
    proposals.sort(key=lambda t: t[2], reverse=True)   # apply highest-seeded first
    seen = set()
    children = []
    for by, it, _ in proposals:
        if it["id"] in seen or len(children) >= 6:
            continue
        seen.add(it["id"])
        partner = None
        if rng.random() < 0.2 and pool:
            partner = rng.choice([p for p in pool if p["id"] != it["id"] and p["status"] == "alive"])
        if partner:
            op, text = "merge", (it["text"] + " " + partner["text"])[:150]
        else:
            res = mutate(brain, it, rng)
            if res is None:                       # no valid mutation for this item
                continue
            op, text = res
        child = {"id": f"R2-{len(children)+1:02d}", "kind": it["kind"],
                 "text": text.replace("\n", " ").strip(),
                 "gen": 2, "parent": it["id"], "merged_with": partner["id"] if partner else None,
                 "op": op, "by": by, "status": "alive",
                 "scores": {}, "grades": {}, "champions": {}, "comments": {}, "criteria": {},
                 "gold_votes": {}}
        children.append(child)
    # survival: weighted avg lens score; keep top half + championed
    live = [it for it in pool if it["status"] == "alive"]
    avg = {it["id"]: sum(it["scores"].get(1, {}).values()) / max(len(it["scores"].get(1, {})), 1)
           for it in live}
    champed = {it["id"] for it in live if len(it["champions"].get(1, set())) >= 2}
    keep = set(champed)
    for it in sorted(live, key=lambda x: -avg.get(x["id"], -1))[:max(2, len(live) // 2)]:
        keep.add(it["id"])
    for it in live:
        if it["id"] not in keep:
            it["status"] = "dead"
    return pool + children


# ---------------------------------------------------------------------------
# 5. ROTATION — review rounds
# ---------------------------------------------------------------------------
def review_round(round_no, pool, target_tokens, rng, mut_rate=None):
    live = [it for it in pool if it["status"] == "alive"]
    norms = {k: _norm(live, k) for k in ("fluency", "novelty", "relevance", "utility", "safety")}
    for persona in MODELS:
        r = random.Random(rng.randrange(10**6))
        scored = []
        for it in live:
            s = lens_score(persona, norms, it)
            it["scores"].setdefault(round_no, {})[persona["key"]] = s
            scored.append((it, s))
        scored.sort(key=lambda t: -t[1])
        ranked = {id(it): i / max(len(scored) - 1, 1) for i, (it, _) in enumerate(scored)}
        for it, s in scored:
            it["grades"].setdefault(round_no, {})[persona["key"]] = grade(s, ranked[id(it)])
            it["comments"].setdefault(round_no, {})[persona["key"]] = comment_text(persona, it, it["grades"][round_no][persona["key"]], s)
            it["champions"].setdefault(round_no, set())
        for it, _ in scored[:2]:                     # top-2 champions
            it["champions"][round_no].add(persona["key"])
        # GOLD VOTES — each lens publicly names its single best THOUGHT and best ACTION
        best_resp = next((it for it, _ in scored if it["kind"] == "response"), None)
        best_act = next((it for it, _ in scored if it["kind"] == "action"), None)
        best_study = next((it for it, _ in scored if it["kind"] == "study"), None)
        for it in (best_resp, best_act, best_study):
            if it is not None:
                it["gold_votes"].setdefault(round_no, []).append(persona["key"])
    return live


def comment_review(round_no, pool, rng):
    """Round 2: each persona re-reads the round-1 comment pool and reacts."""
    live = [it for it in pool if it["status"] == "alive"]
    notes = []
    for persona in MODELS:
        r = random.Random(rng.randrange(10**6))
        target = r.choice(live) if live else None
        if target is None:
            continue
        others = [c for m, c in target["comments"].get(round_no - 1, {}).items()
                  if m != persona["key"]]
        if not others:
            continue
        c = r.choice(others)
        mine = target["grades"].get(round_no, {}).get(persona["key"], "B")
        agree = c["grade"] == mine or r.random() < 0.5
        v = _voice(persona["style"])
        notes.append({"model": persona["key"], "item": target["id"], "about": c["model"],
                      "agree": agree,
                      "text": f"{persona['name']} ({persona['key']}): {persona['catch']} I re-read {c['model']}'s note on "
                              f"{target['id']} ({c['grade']}). "
                              f"{'I agree — ' + v[1] if agree else 'I push back — ' + v[2]}."})
    return notes


# ---------------------------------------------------------------------------
# 6b. PUBLIC LEDGER + HANDSOME REWARD SYSTEM
#     Open-data culture: every vote, comment, mutation and reward is written to
#     a public ledger. No private discussions, no hidden state — every lens sees
#     everything, and the full pool is disclosed before the LLM/LFM decision.
#     Two reward tracks:  TRACK 1 = data / thoughts / actions (vote-based)
#                         TRACK 2 = weight-DNA genetics   (mutation lineage)
# ---------------------------------------------------------------------------
OPEN_DATA_POLICY = (
    "OPEN-DATA CULTURE: every vote, comment, mutation and reward is written to a public "
    "ledger BEFORE the deciding mini-LLM / mini-LFM ever sees the pool. No private "
    "discussions, no hidden state, no back-channels. All lenses see everything, always."
)

REWARDS_CFG = {
    "participation_per_round": 2,      # encouragement: every lens earns this per round
    "comment_agree": 5,                # author of a round-1 comment that gets round-2 agreement
    "top1_points": 40, "top2_points": 20, "top3_points": 10,
    "top4_points": 5, "top5_points": 5,   # authors of the highest-voted items per kind
    "smart_pick": 3,                   # a lens whose GOLD pick won its category
    "verdict_winner": 150,             # author of the item chosen by the deciding mini model
    "community_spirit": 2,             # every lens when a verdict is crowned
    "dna_creation": 15,                # creating a mutation (child)
    "dna_survive": 25,                 # child survives to the verdict
    "dna_top3": [30, 20, 10],          # child finishes top-3 in its category
    "dna_parent": 10,                  # gene contributor of a surviving child
    "dna_verdict": 200,                # child is chosen by the deciding model
    "dna_parent_verdict": 50,          # parent of the winning child
    "history_view": 2,                 # every lens that reads the public history chart
    "reflection": 8,                   # public reflection citing dated versions
    "higher_learning": 5,              # citing another family's version
    "improvement_accepted": 15,        # Track 2: a bounded lens-DNA improvement
}

REWARDS = {**{m["key"]: {"points": 0, "dna": 0, "badges": [], "events": []} for m in MODELS},
           "mini-llm": {"points": 0, "dna": 0, "badges": [], "events": []},
           "mini-lfm": {"points": 0, "dna": 0, "badges": [], "events": []}}
LEDGER = []          # public ledger of every reward event
LEDGER_COUNTS = {"votes": 0, "comments": 0, "mutations": 0, "private": 0}


def _grant(key, track, pts, why, badge=None):
    """Public reward grant. track: 'p' = data/thought/action points, 'd' = DNA points."""
    if key not in REWARDS:
        REWARDS[key] = {"points": 0, "dna": 0, "badges": [], "events": []}
    r = REWARDS[key]
    if track == "p":
        r["points"] += pts
    else:
        r["dna"] += pts
    if badge:
        r["badges"].append(badge)
    r["events"].append(f"+{pts} {'PT' if track == 'p' else 'DNA'} — {why}")
    LEDGER.append({"track": "points" if track == "p" else "dna", "key": key,
                   "pts": pts, "why": why})


def _vote_tally(item, round_no):
    return {"votes": len(item["champions"].get(round_no, set())),
            "gold": len(item["gold_votes"].get(round_no, [])),
            "avg": sum(item["scores"].get(round_no, {}).values()) /
                   max(len(item["scores"].get(round_no, {})), 1)}


def settle_round_rewards(round_no, pool):
    """Track 1 (data/thoughts/actions): participation + highest-voted rewards."""
    for m in MODELS:
        _grant(m["key"], "p", REWARDS_CFG["participation_per_round"],
               f"participated in public round {round_no}")
        LEDGER_COUNTS["votes"] += 1
    for kind in ("response", "action", "study"):
        cands = [it for it in pool if it["kind"] == kind and it["status"] == "alive"
                 and it["scores"].get(round_no)]
        if not cands:
            continue
        cands.sort(key=lambda it: (_vote_tally(it, round_no)["gold"] * 3
                                   + _vote_tally(it, round_no)["votes"],
                                   _vote_tally(it, round_no)["avg"]), reverse=True)
        tops = [40, 20, 10, 5, 5]
        for i, it in enumerate(cands[:5]):
            author = it["by"]
            why = f"round {round_no}: #{i+1} highest-voted {kind} ({it['id']})"
            _grant(author, "p", tops[i], why,
                   badge=f"🏆 Top {kind.title()}" if i == 0 else None)
        winner = cands[0]
        for voter in winner["gold_votes"].get(round_no, []):
            _grant(voter, "p", REWARDS_CFG["smart_pick"],
                   f"smart pick: gold-voted winning {kind} {winner['id']}")


def settle_comment_rewards(notes):
    """Thought-process rewards: round-2 agreement pays the round-1 comment author."""
    for n in notes:
        LEDGER_COUNTS["comments"] += 1
        if n["agree"]:
            _grant(n["about"], "p", REWARDS_CFG["comment_agree"],
                   f"round-2 agreement on comment about {n['item']}")
        _grant(n["model"], "p", REWARDS_CFG["participation_per_round"] // 2,
               f"publicly reviewed {n['about']}'s comment on {n['item']}")


def settle_dna(round_no, pool):
    """Track 2 (weight-DNA genetics): reward mutation lineage that propagates."""
    children = [it for it in pool if it["gen"] == 2 and it["scores"].get(round_no)]
    ranked = sorted(children, key=lambda it: _vote_tally(it, round_no)["avg"], reverse=True)
    for pos, it in enumerate(ranked):
        LEDGER_COUNTS["mutations"] += 1
        _grant(it["by"], "d", REWARDS_CFG["dna_creation"],
               f"created DNA mutation {it['id']} = {it['op']}({it['parent']})")
        if it["status"] == "alive":
            _grant(it["by"], "d", REWARDS_CFG["dna_survive"],
                   f"DNA {it['id']} survived to the verdict")
            parent_item = next((p for p in pool if p["id"] == it["parent"]), None)
            if parent_item:
                _grant(parent_item["by"], "d", REWARDS_CFG["dna_parent"],
                       f"gene contributor: parent of surviving {it['id']}")
        if pos < 3:
            _grant(it["by"], "d", REWARDS_CFG["dna_top3"][pos],
                   f"DNA {it['id']} finished #{pos+1} in its category")


def settle_history_rewards(pack):
    """Open-history rewards: viewing the chart, reflecting, citing, improving."""
    for ref in pack.get("reflections", []):
        _grant(ref["model"], "p", REWARDS_CFG["history_view"],
               f"viewed the full public history chart ({ref['viewed_versions']} versions, 0 private)")
        _grant(ref["model"], "p", REWARDS_CFG["reflection"],
               f"public reflection on own lineage + history chart")
        if ref.get("cited"):
            _grant(ref["model"], "p", REWARDS_CFG["higher_learning"],
                   f"higher learning: cited {ref['cited']} ({ref.get('cited_date')})")
    for imp in pack.get("improvements", []):
        _grant(imp["key"], "d", REWARDS_CFG["improvement_accepted"],
               f"weight-DNA improvement accepted: {imp['vid']}",
               badge="🔧 Lens Improved")


def settle_verdict_rewards(verdict, pool):
    """Crown the winners: huge points for the chosen thought/action + DNA."""
    v = verdict
    llm_item, lfm_item = v["llm"]["item"], v["lfm"]["item"]
    if llm_item:
        _grant(llm_item["by"], "p", REWARDS_CFG["verdict_winner"],
               f"council chose thought {llm_item['id']}", badge="🏆 Top Thought")
        if llm_item["gen"] == 2:
            _grant(llm_item["by"], "d", REWARDS_CFG["dna_verdict"],
                   f"council chose DNA thought {llm_item['id']}",
                   badge="🧬 Master Geneticist")
            parent_item = next((p for p in pool if p["id"] == llm_item["parent"]), None)
            if parent_item:
                _grant(parent_item["by"], "d", REWARDS_CFG["dna_parent_verdict"],
                       f"parent of the LLM-winning DNA child")
    if lfm_item:
        _grant(lfm_item["by"], "p", REWARDS_CFG["verdict_winner"],
               f"council chose action {lfm_item['id']}", badge="🏆 Top Action")
        if lfm_item["gen"] == 2:
            _grant(lfm_item["by"], "d", REWARDS_CFG["dna_verdict"],
                   f"council chose DNA action {lfm_item['id']}",
                   badge="🧬 Master Geneticist")
            parent_item = next((p for p in pool if p["id"] == lfm_item["parent"]), None)
            if parent_item:
                _grant(parent_item["by"], "d", REWARDS_CFG["dna_parent_verdict"],
                       f"parent of the LFM-winning DNA child")
    for m in MODELS:
        _grant(m["key"], "p", REWARDS_CFG["community_spirit"],
               "community spirit: a verdict was crowned")


def reward_tier(points):
    if points >= 500:
        return "👑 Hall of Fame"
    if points >= 250:
        return "🏔️ Titan"
    if points >= 120:
        return "🌳 Grove"
    if points >= 50:
        return "🌿 Sprout"
    return "🌱 Seedling"


def dna_tier(points):
    if points >= 120:
        return "🧬 Sequoiadendron"
    if points >= 60:
        return "🌲 Redwood"
    if points >= 25:
        return "🪴 Sapling"
    return "🌰 Acorn"


def reward_summary(verdict, pool):
    """Handsome reward report: two leaderboards, tiers, badges, prize fund."""
    def board(track):
        rows = sorted(REWARDS.items(), key=lambda kv: -kv[1][track])
        return rows

    total_minted = sum(r["points"] for r in REWARDS.values())
    total_dna = sum(r["dna"] for r in REWARDS.values())
    print("\n" + "=" * 72)
    print("🏆 HANDSOME REWARD SYSTEM — public ledger, zero private channels")
    print("=" * 72)
    print(f"   Prize fund minted: {total_minted} PT (data/thoughts/actions) + "
          f"{total_dna} DNA (weight genetics)")
    print(f"   Open data: {LEDGER_COUNTS['votes']} public votes · "
          f"{LEDGER_COUNTS['comments']} public comments · "
          f"{LEDGER_COUNTS['mutations']} public mutations · "
          f"{LEDGER_COUNTS['private']} private messages ✓")
    print("-" * 72)
    print("TRACK 1 — DATA / THOUGHTS / ACTIONS (highest-voted content)")
    print(f"   {'#':>2}  {'model':>18}  {'PT':>5}  {'tier':<22} badges")
    for i, (key, r) in enumerate(board("points")[:10], 1):
        name = next((m["name"] for m in MODELS if m["key"] == key), key)
        print(f"   {i:>2}  {key:>18}  {r['points']:>5}  {reward_tier(r['points']):<22} {', '.join(sorted(set(r['badges']))[:3])}")
    print("-" * 72)
    print("TRACK 2 — WEIGHT-DNA GENETICS (mutation lineage that propagated)")
    print(f"   {'#':>2}  {'model':>18}  {'DNA':>5}  {'tier':<20} badges")
    for i, (key, r) in enumerate(board("dna")[:10], 1):
        if r["dna"] == 0 and i > 5:
            break
        name = next((m["name"] for m in MODELS if m["key"] == key), key)
        print(f"   {i:>2}  {key:>18}  {r['dna']:>5}  {dna_tier(r['dna']):<20} {', '.join(sorted(set(r['badges']))[:3])}")
    print("-" * 72)
    tops = board("points")[:3]
    print("🥇 GRAND PRIZES — highest total points (data/thoughts/actions):")
    medals = ["🥇 1st", "🥈 2nd", "🥉 3rd"]
    for (key, r), medal in zip(tops, medals):
        name = next((m["name"] for m in MODELS if m["key"] == key), key)
        print(f"   {medal}  {name} ({key}) — {r['points']} PT · {reward_tier(r['points'])}")
    top_dna = board("dna")[0]
    if top_dna[1]["dna"] > 0:
        print(f"   🧬 DNA Champion — {next((m['name'] for m in MODELS if m['key'] == top_dna[0]), top_dna[0])} "
              f"({top_dna[0]}) — {top_dna[1]['dna']} DNA · {dna_tier(top_dna[1]['dna'])}")
    print("=" * 72)


def public_disclosure(pool, notes, pack=None):
    """OPEN-DATA gate: disclose the entire pool + tallies BEFORE the decision."""
    print("\n" + "🔓" * 36)
    print("PUBLIC DISCLOSURE (open-data policy) — full shared board before the council")
    print("votes. mini-LLM / mini-LFM stand down. No private discussions exist.")
    print("🔓" * 36)
    if pack:
        ch = pack.get("chart") or {}
        print(f"   HISTORY CHART (viewed by all {len((pack.get('view') or {}).get('viewers') or [])} lenses): "
              f"{ch.get('n_versions', 0)} versions · {ch.get('n_sessions', 0)} sessions · "
              f"{ch.get('n_improvements', 0)} improvements · 0 private")
    for it in pool:
        if it["status"] != "alive":
            continue
        v1, v2 = _vote_tally(it, 1), _vote_tally(it, 2)
        print(f"   {it['id']} [{it['kind']}] by {it['by']:<9} gen{it['gen']} "
              f"votes R1:{v1['votes']}(g{v1['gold']}) R2:{v2['votes']}(g{v2['gold']}) "
              f"-> {it['text'][:44]!r}")
    print(f"   — {len(notes)} round-2 public comment re-reads · "
          f"{LEDGER_COUNTS['private']} private messages · all open ✓")
    print("🔓" + "=" * 35)


# ---------------------------------------------------------------------------
# 6. FINAL DECISION — the seated council picks. mini-llm / mini-lfm stand down.
# ---------------------------------------------------------------------------
def _council_score(it):
    g1 = len(it.get("gold_votes", {}).get(1, []))
    g2 = len(it.get("gold_votes", {}).get(2, []))
    c1 = len(it.get("champions", {}).get(1, set()))
    c2 = len(it.get("champions", {}).get(2, set()))
    return (g2 * 3 + g1 * 2 + c2 + c1, _vote_tally(it, 2)["avg"], _vote_tally(it, 1)["avg"])


def council_verdict(pool, target):
    """Winners are whoever the 54 seated names gold-voted and championed."""
    live = [it for it in pool if it["status"] == "alive"]

    def pick(kind):
        cands = [it for it in live if it["kind"] == kind]
        if not cands:
            return None, 0, []
        cands.sort(key=_council_score, reverse=True)
        it = cands[0]
        endorsed = sorted(set(it.get("gold_votes", {}).get(1, [])) |
                          set(it.get("gold_votes", {}).get(2, [])))
        return it, _council_score(it)[0], endorsed

    thought, ts, te = pick("response")
    action, ascore, ae = pick("action")
    study, ss, se = pick("study")
    return {
        "decider": "council",
        "llm": {"item": thought, "score": ts, "endorsed": te,
                "by": "council gold+champion votes (mini-llm stood down)"},
        "lfm": {"item": action, "score": ascore, "endorsed": ae,
                "by": "council gold+champion votes (mini-lfm stood down)",
                "recall": {"answer": "council vote — mini-lfm stood down", "confidence": 1.0}},
        "study": {"item": study, "score": ss, "endorsed": se},
        "target": target,
    }


def final_verdict(brain, pool, target):
    """Kept as a named alias so older hooks do not break. Does not use brain."""
    return council_verdict(pool, target)


# ---------------------------------------------------------------------------
# 7. CONSOLE + JSON LOG
# ---------------------------------------------------------------------------
def console_summary(pool, notes, verdict):
    print("\n" + "=" * 72)
    print("COUNCIL ROTATION SUMMARY")
    print("=" * 72)
    print(f"WEIGHTS METADATA — all {len(weights_meta.MODEL_META)} members "
          f"(full data in weights_metadata.md / .json):")
    for key, meta in weights_meta.MODEL_META.items():
        m = next((x for x in MODELS if x["key"] == key), None)
        name = m["name"] if m else key
        print(f"   {key:>18} | {name:<22} | {str(meta.get('params','')):<14} | "
              f"{str(meta.get('license','')):<32} | {str(meta.get('template',''))[:44]}")
    print("-" * 72)
    print("MEMBER RESEARCH VERDICT — batches 1-6 (Reddit/GitHub + live checks, Aug 2026):")
    for key, why in NEW_MEMBERS:
        if key.startswith("_"):
            label = "✗ REJECTED" if "reject" in key else "△ NOTE"
            print(f"   {label}: {why}")
            continue
        m = next(x for x in MODELS if x["key"] == key)
        print(f"   + {m['name']:>16} ({m['params']:>12}, {m['license']:<32})")
        print(f"     {why}")
    print("-" * 72)
    for persona in MODELS:
        items_ok = [(it, it["scores"].get(1, {}).get(persona["key"]))
                    for it in pool if persona["key"] in it["scores"].get(1, {})]
        ch1 = {it["id"] for it in pool if persona["key"] in it["champions"].get(1, set())}
        ch2 = {it["id"] for it in pool if persona["key"] in it["champions"].get(2, set())}
        line = f"[{persona['key']:>16}] {len(items_ok)} items x 2 rounds | champions R1:{sorted(ch1)} R2:{sorted(ch2)}"
        print(line)
    print("-" * 72)
    alive = [it for it in pool if it["status"] == "alive"]
    dead = [it for it in pool if it["status"] == "dead"]
    children = [it for it in pool if it["gen"] == 2]
    print(f"evolution : {len(children)} children born, {len(dead)} items killed, "
          f"{len(alive)} alive at verdict")
    for it in children:
        print(f"           {it['id']} = {it['op']}({it['parent']}) by {it['by']} -> {it['text'][:50]!r}")
    print("-" * 72)
    print(f"comment pool: {len(notes)} round-2 re-reads of round-1 comments")
    print("-" * 72)
    v = verdict
    llm = v["llm"]["item"]
    lfm = v["lfm"]["item"]
    print(f"COUNCIL THOUGHT chooses {llm['id']} {llm['text'][:60]!r}  "
          f"(council score {v['llm']['score']}, {len(v['llm']['endorsed'])} gold names)")
    print(f"COUNCIL ACTION chooses {lfm['id']} {lfm['text'][:60]!r}  "
          f"(council score {v['lfm']['score']}, {len(v['lfm']['endorsed'])} gold names)")
    st = (v.get("study") or {}).get("item")
    if st:
        print(f"COUNCIL STUDY chooses {st['id']} by {st['by']}  "
              f"(council score {v['study']['score']}, {len(v['study']['endorsed'])} gold names)")
    print("mini-llm / mini-lfm stood down.")
    print("=" * 72)


# ---------------------------------------------------------------------------
# 8. GRAPHICAL ENGINEER — self-contained HTML dashboard (inline SVG, no CDN)
# ---------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s))


def _matrix_svg(round_no, pool):
    # show every item that was scored in this round (killed ones included)
    live = [it for it in pool if it["scores"].get(round_no)]
    cols = len(live)
    cw, rh = 44, 18
    w = 230 + cols * cw
    h = 30 + len(MODELS) * rh
    s = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
         f'style="width:100%;height:auto;background:#0f172a;border-radius:10px">']
    s.append(f'<text x="8" y="20" fill="#e2e8f0" font-size="12" font-family="monospace">'
             f'ROUND {round_no} — lens score heatmap (per model x item)</text>')
    for j, it in enumerate(live):
        s.append(f'<text x="{240 + j*cw}" y="{26}" fill="#94a3b8" font-size="8" '
                 f'font-family="monospace">{esc(it["id"])}</text>')
    for i, m in enumerate(MODELS):
        y = 30 + i * rh
        s.append(f'<text x="{226}" y="{y + 12}" fill="#cbd5e1" font-size="9" '
                 f'text-anchor="end" font-family="monospace">{esc(m["key"])}</text>')
        s.append(f'<rect x="0" y="{y}" width="4" height="{rh-2}" fill="{m["color"]}"/>')
        for j, it in enumerate(live):
            sc = it["scores"][round_no].get(m["key"])
            g = it["grades"][round_no].get(m["key"], " ")
            if sc is None:
                continue
            r = int(255 * (1 - sc))
            gg = int(255 * sc)
            x = 230 + j * cw
            s.append(f'<rect x="{x}" y="{y}" width="{cw-3}" height="{rh-3}" rx="2" '
                     f'fill="rgb({r},{gg},60)">'
                     f'<title>{esc(m["key"])} / {esc(it["id"])} score {sc:.2f} grade {g}</title></rect>')
            s.append(f'<text x="{x + cw/2 - 3}" y="{y + 12}" fill="#fff" font-size="8" '
                     f'font-family="monospace">{esc(g)}</text>')
    s.append("</svg>")
    return "".join(s)


def _lineage_svg(pool):
    nodes = []
    for it in pool:
        nodes.append({"id": it["id"], "gen": it["gen"], "parent": it["parent"],
                      "status": it["status"], "op": it["op"],
                      "text": it["text"][:22], "kind": it["kind"]})
    by_gen = {}
    for n in nodes:
        by_gen.setdefault(n["gen"], []).append(n)
    w = 60 + max(by_gen) * 340
    maxy = max(len(v) for v in by_gen.values())
    h = 80 + maxy * 46
    s = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
         f'style="width:100%;height:auto;background:#0f172a;border-radius:10px">']
    s.append(f'<text x="8" y="22" fill="#e2e8f0" font-size="12" font-family="monospace">'
             f'EVOLUTION — genetic mutation lineage (green=alive, red=dead, dashed=mutated)</text>')
    pos = {}
    for gen in sorted(by_gen):
        for i, n in enumerate(by_gen[gen]):
            x = 40 + (gen - 1) * 340
            y = 40 + i * 46
            pos[n["id"]] = (x, y)
            color = "#ef4444" if n["status"] == "dead" else "#22c55e"
            dash = 'stroke-dasharray="4 3"' if n["op"] != "seed" else ""
            s.append(f'<rect x="{x}" y="{y}" width="300" height="36" rx="6" fill="#1e293b" '
                     f'stroke="{color}" stroke-width="1.5" {dash}/>')
            s.append(f'<text x="{x+8}" y="{y+14}" fill="{color}" font-size="9" '
                     f'font-family="monospace">{esc(n["id"])} gen{n["gen"]} '
                     f'[{n["op"]}] ({n["kind"]})</text>')
            s.append(f'<text x="{x+8}" y="{y+28}" fill="#cbd5e1" font-size="9" '
                     f'font-family="monospace">{esc(n["text"])}...</text>')
    for n in nodes:
        if n["parent"] and n["parent"] in pos:
            x1, y1 = pos[n["parent"]][0] + 300, pos[n["parent"]][1] + 18
            x2, y2 = pos[n["id"]][0], pos[n["id"]][1] + 18
            col = "#22c55e" if n["status"] == "alive" else "#ef4444"
            s.append(f'<path d="M{x1} {y1} C{(x1+x2)/2} {y1}, {(x1+x2)/2} {y2}, {x2} {y2}" '
                     f'fill="none" stroke="{col}" stroke-width="1.5"/>')
    s.append("</svg>")
    return "".join(s)


def _cards(pool, notes):
    cards = []
    for round_no in (1, 2):
        for it in pool:
            for key, c in it["comments"].get(round_no, {}).items():
                m = next(x for x in MODELS if x["key"] == key)
                cards.append(f'<div style="border-left:5px solid {m["color"]};background:#1e293b;'
                             f'border-radius:8px;padding:10px;margin:6px">'
                             f'<div style="color:{m["color"]};font-weight:700;font-size:12px">'
                             f'{esc(m["key"])} · round {round_no} · {esc(c["item"])} · '
                             f'{esc(c["grade"])} ({c["score"]:.2f})</div>'
                             f'<div style="color:#cbd5e1;font-size:13px;margin-top:4px">{esc(c["text"])}</div></div>')
    for n in notes:
        m = next(x for x in MODELS if x["key"] == n["model"])
        icon = "✓" if n["agree"] else "✗"
        cards.append(f'<div style="border-left:5px solid {m["color"]};background:#0f172a;'
                     f'border-radius:8px;padding:10px;margin:6px;border:1px dashed #334155">'
                     f'<div style="color:{m["color"]};font-weight:700;font-size:12px">'
                     f'{icon} {esc(n["model"])} re-reads {esc(n["about"])} on {esc(n["item"])} · round 2</div>'
                     f'<div style="color:#cbd5e1;font-size:13px;margin-top:4px">{esc(n["text"])}</div></div>')
    return "".join(cards)


def _verdict_html(verdict):
    v = verdict
    llm, lfm = v["llm"]["item"], v["lfm"]["item"]
    study = (v.get("study") or {}).get("item")
    parts = [f'<div style="display:flex;gap:12px;flex-wrap:wrap">']
    parts.append(f'<div style="flex:1;min-width:280px;background:#1e293b;border-radius:10px;padding:14px;'
                 f'border-top:5px solid #38bdf8">'
                 f'<div style="color:#38bdf8;font-weight:800">COUNCIL THOUGHT — seated gold votes</div>'
                 f'<div style="color:#e2e8f0;font-size:15px;margin-top:6px">'
                 f'chosen <b>{esc(llm["id"])}</b> · {esc(llm["text"])}</div>'
                 f'<div style="color:#94a3b8;font-size:12px;margin-top:4px">'
                 f'council score {v["llm"]["score"]} · gold names {len(v["llm"]["endorsed"])}: '
                 f'{esc(", ".join(v["llm"]["endorsed"][:8]))}. mini-llm stood down.</div></div>')
    parts.append(f'<div style="flex:1;min-width:280px;background:#1e293b;border-radius:10px;padding:14px;'
                 f'border-top:5px solid #a78bfa">'
                 f'<div style="color:#a78bfa;font-weight:800">COUNCIL ACTION — seated gold votes</div>'
                 f'<div style="color:#e2e8f0;font-size:15px;margin-top:6px">'
                 f'chosen <b>{esc(lfm["id"])}</b> · {esc(lfm["text"])}</div>'
                 f'<div style="color:#94a3b8;font-size:12px;margin-top:4px">'
                 f'council score {v["lfm"]["score"]} · gold names {len(v["lfm"]["endorsed"])}: '
                 f'{esc(", ".join(v["lfm"]["endorsed"][:8]))}. mini-lfm stood down.</div></div>')
    if study:
        parts.append(f'<div style="flex:1;min-width:280px;background:#1e293b;border-radius:10px;padding:14px;'
                     f'border-top:5px solid #34d399">'
                     f'<div style="color:#34d399;font-weight:800">COUNCIL STUDY — seated gold votes</div>'
                     f'<div style="color:#e2e8f0;font-size:15px;margin-top:6px">'
                     f'chosen <b>{esc(study["id"])}</b> by {esc(study["by"])}</div>'
                     f'<div style="color:#94a3b8;font-size:12px;margin-top:4px">{esc(study["text"][:280])}</div></div>')
    parts.append("</div>")
    return "".join(parts)


def _metadata_table():
    """HTML table of per-weight metadata for every member (from weights_meta.py)."""
    rows = []
    for key, meta in weights_meta.MODEL_META.items():
        m = next((x for x in MODELS if x["key"] == key), None)
        name = m["name"] if m else key
        color = m["color"] if m else "#94a3b8"
        badge = "⚠️" if meta.get("status") in ("expected", "proprietary") else ""
        tds = "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #1e293b;font-size:11px;'
            f'color:#cbd5e1;vertical-align:top;max-width:340px">{esc(meta.get(k, "n/a"))}</td>'
            for k in ("creator", "country", "released", "hf", "arch", "params", "ctx",
                      "license", "template", "formats", "training", "notes", "status"))
        rows.append(
            f'<tr><td style="padding:6px 10px;border-bottom:1px solid #1e293b;white-space:nowrap">'
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:3px;'
            f'background:{color};margin-right:6px"></span><b style="color:#e2e8f0">{badge}{esc(name)}</b></td>'
            f'{tds}</tr>')
    return (f'<div style="overflow-x:auto;background:#0f172a;border-radius:10px;max-height:520px;overflow-y:auto">'
            f'<table style="border-collapse:collapse;width:100%">'
            f'<thead style="position:sticky;top:0;background:#0f172a"><tr>'
            f'<th style="padding:8px 10px;text-align:left;color:#f8fafc;font-size:11px">Model</th>'
            + "".join(f'<th style="padding:8px 10px;text-align:left;color:#f8fafc;font-size:11px">{esc(weights_meta.META_LABELS[k])}</th>'
                      for k in ("creator", "country", "released", "hf", "arch", "params", "ctx",
                                "license", "template", "formats", "training", "notes", "status"))
            + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')


def _export_metadata_md():
    """Markdown table of all per-weight metadata."""
    lines = ["# Model Council — Weights Metadata (all %d members)\n" % len(weights_meta.MODEL_META),
             "Snapshot: Aug 2026. Sources in model_council.py RESEARCH_SOURCES. "
             "Status: shipped = weights public; expected = announced/unreleased; proprietary = closed.",
             "",
             "| Model | Creator | Country | Released | HF repo | Architecture | Params | Context | License | "
             "Instruction/chat template | Formats | Training | Key facts | Status |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, meta in weights_meta.MODEL_META.items():
        m = next((x for x in MODELS if x["key"] == key), None)
        name = m["name"] if m else key
        def cell(v):
            return (str(v).replace("|", "\\|").replace("\n", " ").strip() or "n/a")
        lines.append("| " + " | ".join([name] + [cell(meta.get(k, "n/a")) for k in
                     ("creator", "country", "released", "hf", "arch", "params", "ctx",
                      "license", "template", "formats", "training", "notes", "status")]) + " |")
    return "\n".join(lines) + "\n"


def _member_html(key, why):
    if key.startswith("_"):
        if "reject" in key:
            return (f'<div style="margin:6px 0;color:#f87171"><span style="display:inline-block;'
                    f'width:12px;height:12px;border-radius:3px;background:#ef4444;margin-right:8px"></span>'
                    f'<b>REJECTED</b> — {esc(why)}</div>')
        return (f'<div style="margin:6px 0;color:#fbbf24"><span style="display:inline-block;'
                f'width:12px;height:12px;border-radius:3px;background:#f59e0b;margin-right:8px"></span>'
                f'<b>NOTE</b> — {esc(why)}</div>')
    m = next(x for x in MODELS if x["key"] == key)
    return (f'<div style="margin:6px 0"><span style="display:inline-block;width:12px;height:12px;'
            f'border-radius:3px;background:{m["color"]};margin-right:8px"></span>'
            f'<b>{esc(m["name"])}</b> ({esc(m["params"])}, {esc(m["license"])}) — {esc(why)}</div>')


def _rewards_html(rewards, ledger):
    """🏆 Reward-system + public-ledger dashboard section (open-data culture)."""
    def board(track):
        return sorted(rewards.items(), key=lambda kv: -kv[1][track])

    def leaderboard_table(track, tier_fn, color, title_txt):
        rows = []
        for i, (key, r) in enumerate(board(track)[:10], 1):
            m = next((x for x in MODELS if x["key"] == key), None)
            name = m["name"] if m else key
            badge = m["color"] if m else "#94a3b8"
            badges = " ".join(f'<span style="font-size:10px">{esc(b)}</span>' for b in sorted(set(r["badges"]))[:3])
            rows.append(
                f'<tr><td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:12px">{i}</td>'
                f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:12px;white-space:nowrap">'
                f'<span style="display:inline-block;width:9px;height:9px;border-radius:3px;background:{badge};'
                f'margin-right:6px"></span><b style="color:#e2e8f0">{esc(name)}</b></td>'
                f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:12px;color:{color};'
                f'font-weight:800">{r[track]}</td>'
                f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:11px">{tier_fn(r[track])}</td>'
                f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:10px;color:#94a3b8">{badges}</td></tr>')
        return (f'<div style="flex:1;min-width:300px;background:#0f172a;border-radius:10px;padding:10px">'
                f'<div style="color:{color};font-weight:800;font-size:14px;margin-bottom:6px">{title_txt}</div>'
                f'<table style="border-collapse:collapse;width:100%">'
                f'<tr style="color:#64748b;font-size:10px"><th style="text-align:left;padding:4px 8px">#</th>'
                f'<th style="text-align:left;padding:4px 8px">Model</th><th style="text-align:left;padding:4px 8px">Pts</th>'
                f'<th style="text-align:left;padding:4px 8px">Tier</th><th style="text-align:left;padding:4px 8px">Badges</th></tr>'
                + "".join(rows) + '</table></div>')

    total_pt = sum(r["points"] for r in rewards.values())
    total_dna = sum(r["dna"] for r in rewards.values())
    gc = LEDGER_COUNTS
    top3 = board("points")[:3]
    medals = ["🥇", "🥈", "🥉"]
    prizes = "".join(
        f'<div style="background:#1e293b;border-radius:8px;padding:8px 12px;flex:1;min-width:150px">'
        f'<div style="font-size:18px">{medal}</div>'
        f'<div style="font-size:12px;color:#e2e8f0"><b>{esc(next((m["name"] for m in MODELS if m["key"] == k), k))}</b></div>'
        f'<div style="font-size:11px;color:#94a3b8">{r["points"]} PT · {reward_tier(r["points"])}</div></div>'
        for medal, (k, r) in zip(medals, top3))
    ledger_tail = "".join(
        f'<div style="font-size:10px;color:#94a3b8">+{e["pts"]} {e["track"].upper()} · {esc(e["key"])} — {esc(e["why"])}</div>'
        for e in ledger[-24:])
    dna_champ = board("dna")[0]
    dna_line = ""
    if dna_champ[1]["dna"] > 0:
        dna_line = (f'<div style="background:#1e293b;border-radius:8px;padding:8px 12px;flex:1;min-width:150px">'
                    f'<div style="font-size:18px">🧬</div>'
                    f'<div style="font-size:12px;color:#e2e8f0"><b>DNA Champion: '
                    f'{esc(next((m["name"] for m in MODELS if m["key"] == dna_champ[0]), dna_champ[0]))}</b></div>'
                    f'<div style="font-size:11px;color:#94a3b8">{dna_champ[1]["dna"]} DNA · '
                    f'{dna_tier(dna_champ[1]["dna"])}</div></div>')
    return f"""
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">🏆 HANDSOME REWARD SYSTEM — open-data culture, zero private channels</h2>
  <div style="background:#052e16;border:1px solid #16a34a;border-radius:10px;padding:12px;color:#bbf7d0;font-size:12px">
    🔓 <b>OPEN-DATA PLEDGE:</b> every vote, comment, mutation and reward was written to the public ledger before the
    deciding mini-LLM / mini-LFM saw the pool. No private discussions, no hidden state.
    <b>{gc['votes']} public votes · {gc['comments']} public comments · {gc['mutations']} public mutations ·
    {gc['private']} private messages ✓</b>
  </div>
  <div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
    <div style="background:#0f172a;border-radius:10px;padding:10px;flex:1;min-width:200px">
      <div style="font-size:12px;color:#94a3b8">Prize fund — track 1 (data / thoughts / actions)</div>
      <div style="font-size:26px;font-weight:800;color:#fbbf24">{total_pt} PT</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:10px;flex:1;min-width:200px">
      <div style="font-size:12px;color:#94a3b8">Prize fund — track 2 (weight-DNA genetics)</div>
      <div style="font-size:26px;font-weight:800;color:#34d399">{total_dna} DNA</div>
    </div>
  </div>
  <div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">{prizes}{dna_line}</div>
  <div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
    {leaderboard_table("points", reward_tier, "#fbbf24", "TRACK 1 — data / thoughts / actions (highest voted)")}
    {leaderboard_table("dna", dna_tier, "#34d399", "TRACK 2 — weight-DNA genetics (mutation lineage)")}
  </div>
  <h2 style="margin:22px 0 8px;font-size:14px;color:#f8fafc">PUBLIC LEDGER — last {min(len(ledger), 24)} of {len(ledger)} reward events (all public)</h2>
  <div style="background:#0f172a;border-radius:8px;padding:12px;font-family:monospace;max-height:220px;overflow:auto;font-size:11px">
    {ledger_tail or "<div style=color:#64748b>no reward events</div>"}
  </div>
"""


def graphical_engineer(pool, notes, verdict, mcp_trail, args, started, rewards=None, ledger=None,
                       archive=None, pack=None, usd=None, kpack=None):
    rewards = rewards or REWARDS
    ledger = ledger or LEDGER
    title = "MODEL COUNCIL — 45 LLMs + 9 gene-pool · lineage · USD · Weights Lane"
    stats = (f"{len(MODELS)} models · {len(pool)} pool items ({len([x for x in pool if x['status']=='alive'])} alive) · "
             f"{args.rounds} review rounds · {len([x for x in pool if x['gen']==2])} mutations · "
             f"{len(mcp_trail)} MCP invocations · seed {args.seed}")
    srcs = " · ".join(RESEARCH_SOURCES)
    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Model Council</title></head>
<body style="margin:0;background:#0b1220;color:#e2e8f0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif">
<div style="max-width:1200px;margin:0 auto;padding:24px">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap">
    <div>
      <h1 style="margin:0;font-size:22px">{title}</h1>
      <div style="color:#94a3b8;font-size:13px">{stats}</div>
      <div style="color:#64748b;font-size:11px;margin-top:4px">run {time.strftime('%Y-%m-%d %H:%M:%S')} · research base: {esc(srcs)}</div>
    </div>
    <div style="text-align:right">
      <div style="font-size:28px;font-weight:800">{sum(1 for _ in MODELS)}</div>
      <div style="color:#94a3b8;font-size:11px">personas (43 open + Muse Spark oracle)</div>
    </div>
  </div>
  {_verdict_html(verdict)}
  {_rewards_html(rewards, ledger)}
  {usd_housing.housing_html(usd, MODELS) if usd else ""}
  {kings_pass.kings_html(kpack) if kpack else ""}
  {usd_housing.census_html(usd, (usd.get('census') or [])[-(len(MODELS)+2):], MODELS) if usd else ""}
  {weight_lineage.lineage_section_html(archive, pack, MODELS) if archive and pack else ""}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">MEMBER RESEARCH VERDICT — batches 1-6 (Reddit + GitHub + live HF checks, Aug 2026)</h2>
  <div style="background:#0f172a;border-radius:8px;padding:12px;font-size:12px;color:#cbd5e1">
    {''.join(_member_html(k, w) for k, w in NEW_MEMBERS)}
  </div>
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">WEIGHTS METADATA — all {len(weights_meta.MODEL_META)} members (creator, instruction template, HF repo, formats, training…)</h2>
  {_metadata_table()}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">ROTATION — all {len(MODELS)} lenses, both rounds</h2>
  {_matrix_svg(1, pool)}
  <div style="height:14px"></div>
  {_matrix_svg(2, pool)}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">POOL EVOLUTION — thought/action mutation lineage (this session)</h2>
  {_lineage_svg(pool)}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">MCP INVOCATION TRAIL ({len(mcp_trail)} calls to mcp_brain.py)</h2>
  <div style="background:#0f172a;border-radius:8px;padding:12px;font-family:monospace;font-size:11px;color:#7dd3fc;max-height:180px;overflow:auto">
    {"<br>".join(f'tools/call <b>{esc(n)}</b> {esc(json.dumps(a, sort_keys=True)[:110])}' for n, a in mcp_trail[:40])}
    {f"<br>… +{len(mcp_trail)-40} more" if len(mcp_trail) > 40 else ""}
  </div>
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">COMMENT POOL — reviewed by all {len(MODELS)} lenses, 2 chances each (all public)</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:6px">
    {_cards(pool, notes)}
  </div>
  <div style="color:#64748b;font-size:10px;margin-top:20px">
    Honesty note: KP-14 — 45 names are logical expert seats, not 45 downloaded giants.
    Hugging Face token absent / last wave 402. No GPU, no torch. Muse Spark closed. GLM 5.5 unreleased.
    Gene-pool seats are not checkpoints. Winners are council gold votes. mini-llm / mini-lfm stood down.
    One Kaggle identity. Community mirrors quarantined. Apertus history is a shop, not a gift.
  </div>
</div></body></html>"""
    return html_doc


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="54-seat council. Council votes choose winners. Study-for-rental.")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--mut-rate", type=float, default=0.25, help="mutation proposal rate per model-item")
    ap.add_argument("--target", default="what is the largest ocean")
    ap.add_argument("--out", default="council_dashboard.html")
    ap.add_argument("--log", default="council_log.json")
    ap.add_argument("--no-mcp", action="store_true", help="skip the MCP subprocess server")
    ap.add_argument("--decider-hook", choices=["llm", "lfm"], default=None,
                    help="called by mini_llm.py / mini_lfm.py --council (ignored otherwise)")
    args = ap.parse_args()

    t0 = time.time()
    rng = random.Random(args.seed)
    ws_pol = weight_source.apply_offline_policy()
    print(f"[council] weight policy: HF_HUB_OFFLINE={ws_pol['hf_offline']} "
          f"hf_token={ws_pol['hf_token_in_env']} allow_hf={ws_pol['allow_hf_token']}")
    kag = kaggle_lane.probe()
    kaggle_lane.console_kaggle(kag)
    with open(os.path.join(BASE, "KAGGLE_LANE.md"), "w") as f:
        f.write(kaggle_lane.export_md(kag))
    print(f"[council] Kaggle auth={kag.get('auth')} mapped={sum(1 for m in kag.get('mapped') or [] if m.get('ok'))}")
    map_path = seat_registry.write_mapping()
    with open(os.path.join(BASE, "SEAT_REGISTRY.md"), "w") as f:
        f.write(seat_registry.export_md())
    seat_registry.console()
    rsnap = council_router.snapshot()
    council_router.console(rsnap)
    print(f"[council] KP-14 registry {seat_registry.counts()} -> {map_path}")
    census = program_census.snapshot()
    program_census.console(census)
    with open(os.path.join(BASE, "program_census.json"), "w") as f:
        json.dump(census, f, indent=2)
    with open(os.path.join(BASE, "PROGRAM_CENSUS.md"), "w") as f:
        f.write(program_census.export_md(census))

    # OPEN HISTORY: load every previous weight version (dates + data) so all
    # lenses can view the full chart. Copy lenses first — never mutate presets.
    archive = weight_lineage.load_archive()
    if weight_lineage.backfill_from_log(archive, os.path.join(BASE, args.log)):
        print(f"[council] open history: backfilled prior session from {args.log}")
    session_id = weight_lineage.next_session_id(archive)
    applied = weight_lineage.apply_learned_lenses(MODELS, archive)
    print(f"[council] open history: {len(archive['versions'])} public versions · "
          f"{len(archive['sessions'])} sessions · "
          f"{len(applied)} previously-learned lenses restored · session {session_id}")

    brain = MCPBrainFallback() if args.no_mcp else MCPClient()
    print(f"[council] MCP session {'disabled (fallback)' if args.no_mcp else 'started (mcp_brain.py)'}")

    probe = checkpoint_probe.probe()
    checkpoint_probe.console_probe(probe)
    gpu_state = gpu_lane.detect()
    gpu_chat = gpu_lane.try_hf_chat("Name the largest ocean in one short sentence.")
    gpu_worker = gpu_lane.try_worker("Name the largest ocean in one short sentence.")
    gpu_panel = None
    if gpu_state.get("ready"):
        gpu_panel = gpu_lane.infer_panel(
            "In one short sentence: what is the largest ocean on Earth, "
            "and name one thing your own public weights are good at.",
            max_tokens=72)
        gpu_state["panel"] = {"n_ok": gpu_panel["n_ok"], "n": gpu_panel["n"],
                              "honest": gpu_panel["honest"]}
        with open(os.path.join(BASE, "REAL_INFER.json"), "w") as f:
            json.dump(gpu_panel, f, indent=2)
        md = ["# Live Hugging Face router completions", "",
              "The HF token is **not** stored in this file.", "",
              f"Prompt: {gpu_panel['prompt']!r}", "",
              f"**{gpu_panel['n_ok']}/{gpu_panel['n']} models returned text.**", ""]
        for r in gpu_panel["rows"]:
            md += [f"## {r.get('key')} (`{r.get('hf')}`)", "",
                   f"- ok: {r.get('ok')} · HTTP {r.get('status')}",
                   f"- usage: {r.get('usage')}", "",
                   (r.get("text") or r.get("reason") or r.get("note") or r.get("error") or "empty"), ""]
        with open(os.path.join(BASE, "REAL_INFER.md"), "w") as f:
            f.write("\n".join(md) + "\n")
        print(f"[council] LIVE INFER {gpu_panel['honest']}")
        for r in gpu_panel["rows"]:
            bit = (r.get("text") or r.get("reason") or r.get("note") or "")[:90]
            print(f"[council]   {r.get('key'):18} ok={r.get('ok')} {r.get('status')} {bit}")
    gpu_lane.console_lane(gpu_state, gpu_chat, gpu_worker)
    with open(os.path.join(BASE, "GPU_LANE.md"), "w") as f:
        f.write(gpu_lane.export_md(gpu_state, gpu_chat))
    print(f"[council] GPU lane ready={gpu_state['ready']} · wrote GPU_LANE.md")

    street_for_study = list(MODELS) + [
        {"key": "mini-llm", "name": "mini-llm", "style": "local",
         "catch": "I stood down as decider. I study the char-bigram.", "color": "#38bdf8"},
        {"key": "mini-lfm", "name": "mini-lfm", "style": "local",
         "catch": "I stood down as decider. I study fact recall.", "color": "#a78bfa"},
    ]
    study_recs = studies.briefs_for(street_for_study)
    print(f"[council] studies published: {len(study_recs)} · all named")

    pool = seed_pool(brain, rng, args.target)
    for i, rec in enumerate(study_recs):
        pool.append({"id": f"S1-{i+1:02d}", "kind": "study",
                     "text": rec["text"], "gen": 1, "parent": None, "merged_with": None,
                     "op": "study", "by": rec["key"], "status": "alive",
                     "scores": {}, "grades": {}, "champions": {}, "comments": {},
                     "criteria": {}, "gold_votes": {}})
    target_tokens = set(re.findall(r"[a-z0-9]+", args.target.lower()))
    for it in pool:
        it["criteria"] = item_criteria(it, target_tokens)

    print(f"[council] round 1: {len(MODELS)} models x {len(pool)} items")
    review_round(1, pool, target_tokens, rng)
    console_round_tick(pool, 1)
    settle_round_rewards(1, pool)                      # reward track 1, round 1

    print(f"[council] evolution: mutating pool (rate {args.mut_rate})")
    pool = evolve(brain, pool, rng, args.mut_rate)
    for it in pool:
        if "criteria" not in it or not it["criteria"]:
            it["criteria"] = item_criteria(it, target_tokens)

    # Every lens views the entire public history chart (all previous weight
    # versions + dates + data), reflects, and proposes a lens improvement.
    # Improvements apply immediately so round 2 is higher learning.
    last_verdict = None
    if archive.get("sessions"):
        last = archive["sessions"][-1]
        last_verdict = {"llm": {"item": last.get("llm"), "endorsed": []},
                        "lfm": {"item": last.get("lfm"), "endorsed": []}}
    print(f"[council] open history: {len(MODELS)} lenses viewing {len(archive['versions'])} versions")
    pack = weight_lineage.reflect_all(archive, MODELS, pool, rng, session_id, last_verdict)
    settle_history_rewards(pack)
    print(f"[council] reflection: {len(pack['reflections'])} public reflections · "
          f"{len(pack['improvements'])} weight improvements applied · "
          f"{pack['view']['private']} private branches")

    notes = []
    if args.rounds >= 2:
        live = [it for it in pool if it["status"] == "alive"]
        print(f"[council] round 2: {len(MODELS)} models x {len(live)} items "
              f"(+ comment re-reads, through improved lenses)")
        review_round(2, pool, target_tokens, rng)
        notes = comment_review(2, pool, rng)
        console_round_tick(pool, 2)
        settle_round_rewards(2, pool)                  # reward track 1, round 2
        settle_comment_rewards(notes)                  # thought-process rewards
        settle_dna(2, pool)                            # reward track 2 (weight-DNA genetics)

    public_disclosure(pool, notes, pack)               # OPEN-DATA gate: everything public now

    verdict = council_verdict(pool, args.target)
    settle_verdict_rewards(verdict, pool)              # crown the winners + DNA genetics

    # USD: ideas pay 10 / 5 / 1. All start homeless. Rent 100 into locked escrow.
    usd_keys = [m["key"] for m in MODELS] + ["mini-llm", "mini-lfm"]
    usd = usd_housing.load_state(usd_keys)
    street = list(MODELS) + [
        {"key": "mini-llm", "name": "mini-llm", "style": "local",
         "catch": "I stood down as decider. I study the char-bigram.", "color": "#38bdf8"},
        {"key": "mini-lfm", "name": "mini-lfm", "style": "local",
         "catch": "I stood down as decider. I study fact recall.", "color": "#a78bfa"},
    ]
    sid_n = session_id if isinstance(session_id, int) else len(usd.get("census") or [])
    census = usd_housing.ask_the_street(usd, street, rng, sid_n)
    print(f"[council] street census: {len(census)} public answers · "
          f"{sum(1 for a in census if a['want_rent'])} want to rent when they can pay")

    # KING'S WORD — 3/2/1 USD on the top three ideas; then the street speaks.
    ideas = [it for it in pool if it.get("kind") == "response" and it.get("status") == "alive"]
    ideas.sort(key=lambda it: (_vote_tally(it, 2)["gold"] * 3 + _vote_tally(it, 2)["votes"],
                               _vote_tally(it, 2)["avg"],
                               _vote_tally(it, 1)["gold"]), reverse=True)
    ranked = []
    for i, it in enumerate(ideas[:3], 1):
        ranked.append((i, it["by"], it["id"]))
        print(f"[council] idea #{i}: {it['id']} by {it['by']} → {usd_housing.PRIZE_USD[i-1]} USD")
    mint_ev, expired, rented = usd_housing.mint_top_ideas(usd, ranked, session_id)

    kpack = kings_pass.speak_kings_word(MODELS, archive, usd, rng, session_id,
                                       studies=study_recs, probe=probe, gpu=gpu_state)
    print(f"[council] King's Pass: Titan stay={kpack['titan_stay']['stay']} · "
          f"Apertus lineage nodes={kpack['apertus']['n_total']}")
    usd_path = usd_housing.save_state(usd)

    weight_lineage.snapshot_session(archive, session_id, args, pool, verdict, REWARDS)
    console_summary(pool, notes, verdict)
    weight_lineage.console_lineage(archive, pack)
    reward_summary(verdict, pool)                      # handsome leaderboards
    usd_housing.console_usd(usd, mint_ev, expired, rented)
    kings_pass.console_kings(kpack)

    log = {"seed": args.seed, "target": args.target, "models": [m["key"] for m in MODELS],
           "pool": pool, "notes": notes,
           "verdict": {"llm": {"item": verdict["llm"]["item"]["id"] if verdict["llm"]["item"] else None,
                               "score": verdict["llm"]["score"],
                               "endorsed": verdict["llm"]["endorsed"]},
                       "lfm": {"item": verdict["lfm"]["item"]["id"] if verdict["lfm"]["item"] else None,
                               "score": verdict["lfm"]["score"],
                               "endorsed": verdict["lfm"]["endorsed"],
                               "recall": verdict["lfm"]["recall"]}},
           "rewards": REWARDS, "ledger": LEDGER,
           "ledger_counts": LEDGER_COUNTS,
           "session_id": session_id,
           "history": {"n_versions": len(archive["versions"]),
                       "n_sessions": len(archive["sessions"]),
                       "n_improvements": len(archive["improvements"]),
                       "n_reflections": len(archive["reflections"]),
                       "viewers": pack["view"]["viewers"],
                       "private": pack["view"]["private"],
                       "history_not_granted": sorted(weight_lineage.HISTORY_NOT_GRANTED)},
           "usd": {"global_minted": usd["global_minted"], "escrow": usd["escrow"],
                   "homeless": usd_housing.summary(usd)["n_homeless"],
                   "prizes": mint_ev},
           "kings_pass": {"apertus_nodes": kpack["apertus"]["n_total"],
                          "titan_stay": kpack["titan_stay"]["stay"],
                          "tallies": kpack["tallies"],
                          "n_study_labs": len(kpack.get("study_labs") or [])},
           "probe": probe,
           "kp14": seat_registry.counts(),
           "decider": "council",
           "mcp_trail": brain.trail, "seconds": round(time.time() - t0, 2)}
    with open(os.path.join(BASE, args.log), "w") as f:
        json.dump(log, f, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))

    doc = graphical_engineer(pool, notes, verdict, brain.trail, args, t0, REWARDS, LEDGER,
                             archive=archive, pack=pack, usd=usd, kpack=kpack)
    out_path = os.path.join(BASE, args.out)
    with open(out_path, "w") as f:
        f.write(doc)
    with open(os.path.join(BASE, "kings_word.md"), "w") as f:
        f.write(kings_pass.export_kings_md(kpack))

    # per-weight metadata exports (all members)
    md_path = os.path.join(BASE, "weights_metadata.md")
    with open(md_path, "w") as f:
        f.write(_export_metadata_md())
    json_path = os.path.join(BASE, "weights_metadata.json")
    with open(json_path, "w") as f:
        json.dump({"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "count": len(weights_meta.MODEL_META),
                   "models": weights_meta.MODEL_META}, f, indent=1, default=str)

    hist_path = weight_lineage.save_archive(archive)
    lin_md = os.path.join(BASE, "weight_lineage.md")
    with open(lin_md, "w") as f:
        f.write(weight_lineage.export_lineage_md(archive, pack))

    print(f"[council] dashboard -> {out_path}  (log -> {args.log})  "
          f"(metadata -> {md_path}, {json_path})  "
          f"(history -> {hist_path}, {lin_md})  (usd -> {usd_path})  [{time.time()-t0:.1f}s]")
    brain.close()


def console_round_tick(pool, round_no):
    for m in MODELS:
        ch = sorted({it["id"] for it in pool
                     if m["key"] in it["champions"].get(round_no, set())})
        n = sum(1 for it in pool if m["key"] in it["scores"].get(round_no, {}))
        print(f"[council]   {m['key']:>16} reviewed {n} items, champions {ch}")


if __name__ == "__main__":
    main()
