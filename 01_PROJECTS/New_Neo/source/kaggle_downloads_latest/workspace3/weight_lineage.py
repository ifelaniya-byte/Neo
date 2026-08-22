#!/usr/bin/env python3
"""
WEIGHT LINEAGE — public version archive, family trees, history chart,
reflection, and weight improvements.

OPEN-HISTORY POLICY
  Every previous weight version (release, distill, sibling, council-session,
  lens-improvement) is written to a public archive with its date and data.
  Every lens / weight may view the ENTIRE history chart — no private
  branches, no hidden checkpoints. Reflections and proposed improvements
  are themselves public and become the next version of that weight.

USED BY: model_council.py (reflection round, dashboard lineage tree +
history chart, weight_history.json persistence).
"""

import html
import json
import os
import time

import weights_meta

BASE = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE, "weight_history.json")

OPEN_HISTORY_POLICY = (
    "OPEN HISTORY: every previous weight version — release, distill, sibling, "
    "council-session snapshot, and lens-improvement — is public, dated, and "
    "readable by every lens. The entire history chart is viewed through and "
    "by all weights for learning and higher learning. No private branches."
)

# ---------------------------------------------------------------------------
# 1. RESEARCHED FAMILY TREES + HISTORICAL VERSIONS (dates + data)
#    Birth versions exist even on the first council run so every lens has
#    "as many previous weight versions" to reflect on immediately.
# ---------------------------------------------------------------------------

# (family_id, display name, org)
FAMILIES = [
    ("moonshot", "Moonshot / Kimi", "Moonshot AI"),
    ("zhipu", "Zhipu / GLM", "Z.ai"),
    ("deepseek", "DeepSeek", "DeepSeek"),
    ("qwen", "Qwen", "Alibaba"),
    ("meta-llama", "Meta Llama", "Meta"),
    ("meta-muse", "Meta Muse", "Meta"),
    ("mistral", "Mistral", "Mistral AI"),
    ("openai", "OpenAI gpt-oss", "OpenAI"),
    ("tml", "Thinking Machines", "Thinking Machines Lab"),
    ("skt", "SK Telecom A.X", "SK Telecom"),
    ("ibm", "IBM Granite", "IBM"),
    ("liquid", "Liquid AI", "Liquid AI"),
    ("microsoft", "Microsoft Phi", "Microsoft"),
    ("google", "Google Gemma", "Google"),
    ("nvidia", "NVIDIA Nemotron", "NVIDIA"),
    ("tencent", "Tencent Hunyuan", "Tencent"),
    ("minimax", "MiniMax", "MiniMax"),
    ("stepfun", "StepFun", "StepFun"),
    ("cohere", "Cohere Command", "Cohere"),
    ("ai2", "Ai2 OLMo", "Ai2"),
    ("poolside", "Poolside Laguna", "Poolside"),
    ("lg", "LG EXAONE", "LG AI Research"),
    ("tii", "TII Falcon", "TII"),
    ("jetbrains", "JetBrains Mellum", "JetBrains"),
    ("servicenow", "ServiceNow Apriel", "ServiceNow"),
    ("bytedance", "ByteDance KAT", "Kwaipilot / ByteDance"),
    ("xiaomi", "Xiaomi MiMo", "Xiaomi"),
    ("hf", "Hugging Face SmolLM", "Hugging Face"),
    ("swiss", "Swiss AI Apertus", "Swiss AI Initiative"),
    ("gene-pool", "Council gene-pool tiers", "Model Council"),
]

# Seats that must NEVER receive an automatic birth-history grant.
# Every other lens can see the empty prior-version list.
HISTORY_NOT_GRANTED = {"apertus-70b"}

# Historical + current versions. vid = "{key}@{ver}"
# rel: root | successor | distill | sibling | expected | improvement | session
# parent is a vid (or None).
BIRTH_VERSIONS = [
    # ---- Moonshot ----
    {"vid": "kimi-k2-code@k2", "key": "kimi-k2-code", "ver": "K2",
     "date": "2025-11-01", "family": "moonshot", "rel": "root", "parent": None,
     "params": "1T / 32B", "license": "Modified MIT",
     "note": "First Kimi coding MoE; agentic multi-attempt RL."},
    {"vid": "kimi-k2.7-code@k2.7", "key": "kimi-k2.7-code", "ver": "K2.7",
     "date": "2026-06-12", "family": "moonshot", "rel": "successor",
     "parent": "kimi-k2-code@k2",
     "params": "1T / 32B", "license": "Modified MIT",
     "note": "~30% fewer reasoning tokens than K2.6; MCP-native; beats Opus 4.8 on tools."},
    {"vid": "kimi-k3@k3", "key": "kimi-k3", "ver": "K3",
     "date": "2026-07-27", "family": "moonshot", "rel": "successor",
     "parent": "kimi-k2.7-code@k2.7",
     "params": "2.8T / 104B", "license": "Modified MIT",
     "note": "Flagship. AA Index 57. 1M ctx, vision. Most capable open model at drop."},
    # ---- Zhipu ----
    {"vid": "glm-5.2@5.2", "key": "glm-5.2", "ver": "5.2",
     "date": "2026-06-13", "family": "zhipu", "rel": "root", "parent": None,
     "params": "753B / 40B", "license": "MIT",
     "note": "AA 51 at launch. SWE-bench Pro 62.1. Verified open weights."},
    {"vid": "glm-5.5@5.5-expected", "key": "glm-5.5", "ver": "5.5-expected",
     "date": "2026-08-20", "family": "zhipu", "rel": "expected",
     "parent": "glm-5.2@5.2",
     "params": ">1T MoE (projected)", "license": "MIT (expected)",
     "note": "UNRELEASED as of 2026-08-13. Analyst-rumored. Honest placeholder."},
    # ---- DeepSeek ----
    {"vid": "deepseek-v4-pro@v4-pro", "key": "deepseek-v4-pro", "ver": "V4-Pro",
     "date": "2026-04-23", "family": "deepseek", "rel": "root", "parent": None,
     "params": "1.6T / 49B", "license": "MIT",
     "note": "DSA MoE. SWE-bench V 80.6, LiveCodeBench 93.5."},
    {"vid": "deepseek-v4-flash@v4-flash", "key": "deepseek-v4-flash", "ver": "V4-Flash",
     "date": "2026-05-01", "family": "deepseek", "rel": "distill",
     "parent": "deepseek-v4-pro@v4-pro",
     "params": "284B / 13B", "license": "MIT",
     "note": "Lighter active-set distill of V4-Pro. SWE-bench V 79.0 at a fraction of cost."},
    # ---- Qwen ----
    {"vid": "qwen3-235b@3.0", "key": "qwen3-235b", "ver": "3.0",
     "date": "2025-05-01", "family": "qwen", "rel": "root", "parent": None,
     "params": "235B / 22B", "license": "Apache 2.0",
     "note": "Qwen3 flagship. Hybrid thinking toggle. Top open all-rounder of 2025."},
    {"vid": "qwen3-next-80b@3-next", "key": "qwen3-next-80b", "ver": "3-Next",
     "date": "2026-02-01", "family": "qwen", "rel": "successor",
     "parent": "qwen3-235b@3.0",
     "params": "80B / 3B", "license": "Apache 2.0",
     "note": "Gated DeltaNet hybrid. 10% train cost of Qwen3-32B, 10x decode >32K."},
    {"vid": "qwen3.5-397b@3.5", "key": "qwen3.5-397b", "ver": "3.5",
     "date": "2026-02-24", "family": "qwen", "rel": "successor",
     "parent": "qwen3-235b@3.0",
     "params": "397B / 17B", "license": "Apache 2.0",
     "note": "Hybrid Gated DeltaNet + 512 experts. 201 languages. Base of rejected Nex-N2-Pro."},
    {"vid": "qwen3.6-27b@3.6", "key": "qwen3.6-27b", "ver": "3.6",
     "date": "2026-04-16", "family": "qwen", "rel": "sibling",
     "parent": "qwen3-235b@3.0",
     "params": "27B dense", "license": "Apache 2.0",
     "note": "Best consumer-hardware Qwen (24GB Q4). SWE-bench V 77.2."},
    {"vid": "qwen-3.8-max@3.8-max", "key": "qwen-3.8-max", "ver": "3.8-Max",
     "date": "2026-08-03", "family": "qwen", "rel": "successor",
     "parent": "qwen3.5-397b@3.5",
     "params": "2.4T / 95B", "license": "Open weights (license TBA)",
     "note": "First open Qwen-Max-class. TB 2.1 86.6, SWE-bench Pro 67.7. HF live Aug 13."},
    # ---- Meta Llama ----
    {"vid": "llama-4-scout@4-scout", "key": "llama-4-scout", "ver": "4-Scout",
     "date": "2025-04-05", "family": "meta-llama", "rel": "root", "parent": None,
     "params": "109B / 17B", "license": "Llama 4 Community",
     "note": "10M theoretical ctx (effective ~256K). 16 experts, NoPE, multimodal."},
    {"vid": "llama-4-maverick@4-maverick", "key": "llama-4-maverick", "ver": "4-Maverick",
     "date": "2025-04-05", "family": "meta-llama", "rel": "sibling",
     "parent": "llama-4-scout@4-scout",
     "params": "400B / 17B", "license": "Llama 4 Community",
     "note": "Same-day sibling. 128 experts. MMMU 73.4, DocVQA 94.4, LMArena ~1370."},
    {"vid": "llama-5@5", "key": "llama-5", "ver": "5",
     "date": "2026-06-01", "family": "meta-llama", "rel": "successor",
     "parent": "llama-4-maverick@4-maverick",
     "params": "600B", "license": "Llama Community",
     "note": "Next-gen Meta open flagship, 5M ctx. 'Welcome Llama 5' (r/LocalLLaMA Aug 2026)."},
    # ---- Meta Muse (closed → open distill) ----
    {"vid": "muse-spark@1.0", "key": "muse-spark", "ver": "1.0",
     "date": "2026-04-08", "family": "meta-muse", "rel": "root", "parent": None,
     "params": "undisclosed", "license": "Closed / proprietary",
     "note": "Meta's first closed model. 1M ctx. No public weights — persona only."},
    {"vid": "muse-spark@1.1", "key": "muse-spark", "ver": "1.1",
     "date": "2026-07-01", "family": "meta-muse", "rel": "successor",
     "parent": "muse-spark@1.0",
     "params": "undisclosed", "license": "Closed / proprietary",
     "note": "Muse Spark 1.1. Still closed. Long-context + reasoning refinements."},
    {"vid": "muse-spark@1.2", "key": "muse-spark", "ver": "1.2",
     "date": "2026-08-01", "family": "meta-muse", "rel": "successor",
     "parent": "muse-spark@1.1",
     "params": "undisclosed", "license": "Closed / proprietary",
     "note": "Muse Spark 1.2 API $1.25/$4.25 per Mtok. Teacher of open Glimmer."},
    {"vid": "muse-glimmer@30b", "key": "muse-glimmer", "ver": "30B",
     "date": "2026-08-10", "family": "meta-muse", "rel": "distill",
     "parent": "muse-spark@1.2",
     "params": "30B dense", "license": "Apache 2.0",
     "note": "OPEN Muse. Distilled from Spark 1.2. Perception encoder, 256K, ~124 tok/s."},
    # ---- Mistral ----
    {"vid": "mistral-small-3.1@3.1", "key": "mistral-small-3.1", "ver": "3.1",
     "date": "2025-03-18", "family": "mistral", "rel": "root", "parent": None,
     "params": "24B dense", "license": "Apache 2.0",
     "note": "Multimodal 24B workhorse. MMLU 80.6, ~150 tok/s."},
    {"vid": "mistral-small-3.1@3.2", "key": "mistral-small-3.1", "ver": "3.2",
     "date": "2025-06-20", "family": "mistral", "rel": "successor",
     "parent": "mistral-small-3.1@3.1",
     "params": "24B dense", "license": "Apache 2.0",
     "note": "Minor update on the same 3.1 base (instruction/tooling)."},
    {"vid": "mistral-large-3@large-3", "key": "mistral-large-3", "ver": "Large-3",
     "date": "2026-03-01", "family": "mistral", "rel": "sibling",
     "parent": "mistral-small-3.1@3.1",
     "params": "675B / 41B", "license": "Apache 2.0",
     "note": "European flagship open MoE. Enterprise + multilingual."},
    {"vid": "devstral-2@2", "key": "devstral-2", "ver": "2",
     "date": "2025-12-09", "family": "mistral", "rel": "sibling",
     "parent": "mistral-small-3.1@3.1",
     "params": "123B dense", "license": "Modified MIT",
     "note": "Agentic coder. SWE-bench V 72.2. Community 85/100 vs Claude."},
    {"vid": "devstral-small-2@small-2", "key": "devstral-small-2", "ver": "Small-2",
     "date": "2025-12-09", "family": "mistral", "rel": "distill",
     "parent": "devstral-2@2",
     "params": "24B dense", "license": "Apache 2.0",
     "note": "Same-day small sibling. SWE-bench V 68.0 on a single 4090. Clean Apache."},
    # ---- OpenAI ----
    {"vid": "gpt-oss-120b@120b", "key": "gpt-oss-120b", "ver": "120B",
     "date": "2025-08-05", "family": "openai", "rel": "root", "parent": None,
     "params": "117B / 5.1B", "license": "Apache 2.0",
     "note": "OpenAI's first open weights since GPT-2. MXFP4 native. MMLU 90.0."},
    {"vid": "gpt-oss-20b@20b", "key": "gpt-oss-20b", "ver": "20B",
     "date": "2025-08-05", "family": "openai", "rel": "sibling",
     "parent": "gpt-oss-120b@120b",
     "params": "21B / 3.6B", "license": "Apache 2.0",
     "note": "Same-day small sibling. o3-mini class on 16GB. Reasoning dial."},
    # ---- Thinking Machines ----
    {"vid": "inkling@975b", "key": "inkling", "ver": "975B",
     "date": "2026-07-15", "family": "tml", "rel": "root", "parent": None,
     "params": "975B / 41B", "license": "Apache 2.0",
     "note": "Biggest open drop of 2026. 45T multimodal tokens. Fine-tune-first."},
    {"vid": "inkling-small@276b", "key": "inkling-small", "ver": "276B",
     "date": "2026-07-30", "family": "tml", "rel": "distill",
     "parent": "inkling@975b",
     "params": "276B / 12B", "license": "Apache 2.0",
     "note": "STUDENT BEAT TEACHER: SWE-V 80.2 vs 77.6, HLE 31.6 vs 29.7. SimpleQA halves."},
    # ---- SKT ----
    {"vid": "a-x-k2@k1-hist", "key": "a-x-k2", "ver": "K1-hist",
     "date": "2026-03-01", "family": "skt", "rel": "root", "parent": None,
     "params": "519B (historical, no council seat)", "license": "Apache 2.0",
     "note": "A.X K1 predecessor. Not a council member — kept so K2 has a dated parent."},
    {"vid": "a-x-k2@k2", "key": "a-x-k2", "ver": "K2",
     "date": "2026-07-29", "family": "skt", "rel": "successor",
     "parent": "a-x-k2@k1-hist",
     "params": "688B / 33B", "license": "Apache 2.0",
     "note": "Think-Fusion. AIME top tier, ties Inkling at IMO-gold. SGA + MLA + DSA."},
    # ---- IBM ----
    {"vid": "granite-4.1@4.0", "key": "granite-4.1", "ver": "4.0",
     "date": "2025-12-01", "family": "ibm", "rel": "root", "parent": None,
     "params": "H-Small 32B/9B MoE", "license": "Apache 2.0",
     "note": "Granite 4.0 hybrid Mamba-2/Transformer family."},
    {"vid": "granite-4.1@4.1", "key": "granite-4.1", "ver": "4.1",
     "date": "2026-04-29", "family": "ibm", "rel": "successor",
     "parent": "granite-4.1@4.0",
     "params": "3B-30B dense", "license": "Apache 2.0",
     "note": "ISO 42001 + cryptographic signing + Guardian safety. 512K ctx."},
    # ---- Liquid ----
    {"vid": "liquid-lfm2.5@2.6b", "key": "liquid-lfm2.5", "ver": "2.6B",
     "date": "2026-08-04", "family": "liquid", "rel": "root", "parent": None,
     "params": "2.6B hybrid conv+GQA", "license": "LFM Open License v1.0",
     "note": "220 tok/s on M5 Max. Beats 4x-larger models on IF/tool use."},
    {"vid": "liquid-lfm2.5@vl-3b", "key": "liquid-lfm2.5", "ver": "VL-3B",
     "date": "2026-08-12", "family": "liquid", "rel": "successor",
     "parent": "liquid-lfm2.5@2.6b",
     "params": "3B multimodal", "license": "LFM Open License v1.0",
     "note": "Vision-language sibling, eight days later."},
    # ---- Microsoft ----
    {"vid": "phi-4@14b", "key": "phi-4", "ver": "14B",
     "date": "2024-12-12", "family": "microsoft", "rel": "root", "parent": None,
     "params": "14B dense", "license": "MIT",
     "note": "Data-centric 14B. Best reasoning-per-parameter in class."},
    {"vid": "phi-4@reasoning", "key": "phi-4", "ver": "reasoning",
     "date": "2025-04-01", "family": "microsoft", "rel": "successor",
     "parent": "phi-4@14b",
     "params": "14B dense + thinking tokens", "license": "MIT",
     "note": "Phi-4-reasoning. Same seat, chain-of-thought post-train."},
    # ---- singles (still dated so the chart is complete) ----
    {"vid": "gemma-4-31b@4", "key": "gemma-4-31b", "ver": "4",
     "date": "2026-04-01", "family": "google", "rel": "root", "parent": None,
     "params": "31B dense", "license": "Apache 2.0",
     "note": "Best single-GPU open (GPQA-D 84.3, LCB 80)."},
    {"vid": "nemotron-3-ultra@3", "key": "nemotron-3-ultra", "ver": "3",
     "date": "2026-03-15", "family": "nvidia", "rel": "root", "parent": None,
     "params": "550B / 55B", "license": "OpenMDW-1.1",
     "note": "Most complete open release (tooling, evals, data). NVFP4 pioneer."},
    {"vid": "hunyuan-hy3@hy3", "key": "hunyuan-hy3", "ver": "Hy3",
     "date": "2026-05-15", "family": "tencent", "rel": "root", "parent": None,
     "params": "295B / 21B", "license": "Apache 2.0",
     "note": "Best capability per gigabyte. SWE-V 78.0, GPQA-D 90.4."},
    {"vid": "minimax-m3@m3", "key": "minimax-m3", "ver": "M3",
     "date": "2026-06-01", "family": "minimax", "rel": "root", "parent": None,
     "params": "428B / 23B", "license": "MiniMax Community",
     "note": "Efficient coding/agentic. SWE-V 80.5, GPQA-D 93.0."},
    {"vid": "step-3.7-flash@3.7", "key": "step-3.7-flash", "ver": "3.7",
     "date": "2026-05-01", "family": "stepfun", "rel": "root", "parent": None,
     "params": "198B / 11B", "license": "Apache 2.0",
     "note": "Low-cost algorithm coder. SWE-V 76.5."},
    {"vid": "command-a-plus@a+", "key": "command-a-plus", "ver": "A+",
     "date": "2025-03-01", "family": "cohere", "rel": "root", "parent": None,
     "params": "218B / 25B", "license": "Apache 2.0",
     "note": "Enterprise RAG + citation specialist."},
    {"vid": "olmo-3@3", "key": "olmo-3", "ver": "3",
     "date": "2025-11-20", "family": "ai2", "rel": "root", "parent": None,
     "params": "7B / 32B", "license": "Apache 2.0 (weights+data+code)",
     "note": "ONLY truly-open model. Dolma 3 + every checkpoint public."},
    {"vid": "laguna-xs-2.1@2.1", "key": "laguna-xs-2.1", "ver": "2.1",
     "date": "2026-07-02", "family": "poolside", "rel": "root", "parent": None,
     "params": "33B / 3B", "license": "OpenMDW-1.1",
     "note": "Single-GPU agentic coder. SWE-bench Multilingual 63.1."},
    {"vid": "k-exaone-2.0@2.0", "key": "k-exaone-2.0", "ver": "2.0",
     "date": "2026-07-31", "family": "lg", "rel": "root", "parent": None,
     "params": "750B / 37B", "license": "Apache 2.0",
     "note": "First frontier-scale non-US/China Apache MoE. Long-text 94.4 vs GLM-5.1 71.5."},
    {"vid": "falcon-h1r-7b@h1r", "key": "falcon-h1r-7b", "ver": "H1R",
     "date": "2026-01-06", "family": "tii", "rel": "root", "parent": None,
     "params": "7B hybrid Mamba/Transformer", "license": "TII Falcon terms",
     "note": "AIME'25 83.1 (beats 15-47B). ~1500 tok/s/GPU."},
    {"vid": "mellum-2@2", "key": "mellum-2", "ver": "2",
     "date": "2026-05-29", "family": "jetbrains", "rel": "root", "parent": None,
     "params": "12B / 2.5B", "license": "Apache 2.0",
     "note": "Focal model for agent pipelines. LCB v6 69.9 (Thinking)."},
    {"vid": "apriel-15b-thinker@1.5", "key": "apriel-15b-thinker", "ver": "1.5",
     "date": "2025-10-01", "family": "servicenow", "rel": "root", "parent": None,
     "params": "15B multimodal", "license": "MIT",
     "note": "Mid-training beats RL. AA 52, AIME'25 87%, single GPU."},
    {"vid": "kat-dev-72b@72b", "key": "kat-dev-72b", "ver": "72B",
     "date": "2025-10-21", "family": "bytedance", "rel": "root", "parent": None,
     "params": "72B dense (Qwen2.5 base)", "license": "Apache 2.0",
     "note": "SWE-V 74.6 via agentic RL. Reflexivity: often fixes on 2nd attempt."},
    {"vid": "mimo-v2.5-pro@v2.5", "key": "mimo-v2.5-pro", "ver": "V2.5-Pro",
     "date": "2026-04-22", "family": "xiaomi", "rel": "root", "parent": None,
     "params": "1.02T / 42B", "license": "MIT",
     "note": "AA 54. SWE-Pro 57.2 > Opus 4.6. r/LocalLLaMA: command of language."},
    {"vid": "smollm3-3b@3", "key": "smollm3-3b", "ver": "3",
     "date": "2025-07-08", "family": "hf", "rel": "root", "parent": None,
     "params": "3B dense", "license": "Apache 2.0 + blueprint + 100+ ckpts",
     "note": "Fully-open small model. 11.2T tokens, dual-mode think/no_think."},
    {"vid": "gp-root@council", "key": "gp-seedling", "ver": "gene-pool-root",
     "date": "2026-08-13", "family": "gene-pool", "rel": "root", "parent": None,
     "params": "tier-DNA", "license": "public council charter",
     "note": "Root of the reward-tier gene pool. Track-1 (points) and Track-2 (DNA) branch from here."},
    {"vid": "gp-seedling@v1", "key": "gp-seedling", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-root@council",
     "params": "Track-1 <50 PT", "license": "public council charter",
     "note": "Seedling — every weight begins here on Track 1."},
    {"vid": "gp-sprout@v1", "key": "gp-sprout", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-seedling@v1",
     "params": "Track-1 >=50 PT", "license": "public council charter",
     "note": "Sprout — first promotion on the points track."},
    {"vid": "gp-grove@v1", "key": "gp-grove", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-sprout@v1",
     "params": "Track-1 >=120 PT", "license": "public council charter",
     "note": "Grove — community canopy. A seated weight, not just a badge."},
    {"vid": "gp-titan@v1", "key": "gp-titan", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-grove@v1",
     "params": "Track-1 >=250 PT", "license": "public council charter",
     "note": "Titan — the named gene-pool variation the council now runs as a model."},
    {"vid": "gp-hall-of-fame@v1", "key": "gp-hall-of-fame", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-titan@v1",
     "params": "Track-1 >=500 PT", "license": "public council charter",
     "note": "Hall of Fame — apex of the points gene pool."},
    {"vid": "gp-acorn@v1", "key": "gp-acorn", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "sibling",
     "parent": "gp-root@council",
     "params": "Track-2 <25 DNA", "license": "public council charter",
     "note": "Acorn — DNA-track seed. Sibling of Seedling under the same root."},
    {"vid": "gp-sapling@v1", "key": "gp-sapling", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-acorn@v1",
     "params": "Track-2 >=25 DNA", "license": "public council charter",
     "note": "Sapling — first DNA promotion."},
    {"vid": "gp-redwood@v1", "key": "gp-redwood", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-sapling@v1",
     "params": "Track-2 >=60 DNA", "license": "public council charter",
     "note": "Redwood — mutation lineage that took."},
    {"vid": "gp-sequoiadendron@v1", "key": "gp-sequoiadendron", "ver": "v1",
     "date": "2026-08-13", "family": "gene-pool", "rel": "successor",
     "parent": "gp-redwood@v1",
     "params": "Track-2 >=120 DNA", "license": "public council charter",
     "note": "Sequoiadendron — apex of the DNA gene pool."},
]

HIGHER_LEARNING_CANON = [
    {"id": "HL-1", "date": "2026-07-30",
     "lesson": "Distill-and-verify can beat scale-alone.",
     "evidence": "Inkling-Small@276B beat Inkling@975B on SWE-V (80.2 vs 77.6), HLE, TB 2.1, GPQA-D. SimpleQA factuality halved — the trade is real."},
    {"id": "HL-2", "date": "2026-08-10",
     "lesson": "A closed teacher can still leave an open student.",
     "evidence": "Muse Glimmer 30B (Apache 2.0, 2026-08-10) is an open distill of proprietary Muse Spark 1.2. Weights lineage is public even when the parent is not."},
    {"id": "HL-3", "date": "2026-05-01",
     "lesson": "Efficiency branches keep most of the parent's score.",
     "evidence": "DeepSeek V4-Flash keeps 79.0 SWE-V vs Pro's 80.6 at 13B active. Qwen3-Next beats Qwen3-32B at 10% train cost. Devstral Small 2 holds 68.0 vs 72.2."},
    {"id": "HL-4", "date": "2026-08-13",
     "lesson": "Label the unreleased. Never silently promote a rumor to a weight.",
     "evidence": "GLM 5.5 remains expected/unreleased as of 2026-08-13. The seat exists with honest 'expected' status; GLM 5.2 is still the verified Z.ai vote."},
    {"id": "HL-5", "date": "2026-02-24",
     "lesson": "Contested provenance is a dead end, even if the base is clean.",
     "evidence": "Qwen3.5-397B is a real Apache flagship. Nex-N2-Pro (a claimed derivative) was rejected: GitHub issue #4 showed Rio-3.5-Open-397B as a 0.6/0.4 merge."},
    {"id": "HL-6", "date": "2025-11-20",
     "lesson": "Truly-open (weights + data + code + checkpoints) is its own axis.",
     "evidence": "OLMo 3 and SmolLM3 publish the recipe. Everyone else is open-weight, not open-science. Higher learning needs the data trail, not just the checkpoint."},
    {"id": "HL-7", "date": "2026-08-13",
     "lesson": "History is a grant, not a birthright. A new seat can arrive with an empty prior-version list.",
     "evidence": "Apertus-70B was seated without any automatic lineage grant. Every lens can see the blank. Session snapshots it earns from now on are the only history it will have."},
]


# ---------------------------------------------------------------------------
# 2. ARCHIVE  (load / seed / snapshot / save)
# ---------------------------------------------------------------------------

def _today():
    return time.strftime("%Y-%m-%d")


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def empty_archive():
    return {
        "created": _now(),
        "updated": _now(),
        "policy": OPEN_HISTORY_POLICY,
        "versions": [dict(v) for v in BIRTH_VERSIONS],
        "sessions": [],
        "improvements": [],
        "reflections": [],
        "views": [],          # {session, viewers: [keys], n_versions}
        "lessons": list(HIGHER_LEARNING_CANON),
    }


def load_archive(path=None):
    path = path or HISTORY_PATH
    if not os.path.exists(path):
        return empty_archive()
    try:
        with open(path) as f:
            arc = json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty_archive()
    # merge any newly researched birth versions the file doesn't have yet
    have = {v["vid"] for v in arc.get("versions", [])}
    for v in BIRTH_VERSIONS:
        if v["vid"] not in have:
            arc["versions"].append(dict(v))
    known_lessons = {L["id"] for L in arc.get("lessons", [])}
    for L in HIGHER_LEARNING_CANON:
        if L["id"] not in known_lessons:
            arc.setdefault("lessons", []).append(L)
    arc.setdefault("sessions", [])
    arc.setdefault("improvements", [])
    arc.setdefault("reflections", [])
    arc.setdefault("views", [])
    arc["policy"] = OPEN_HISTORY_POLICY
    return arc


def save_archive(arc, path=None):
    path = path or HISTORY_PATH
    arc["updated"] = _now()
    with open(path, "w") as f:
        json.dump(arc, f, indent=1, default=str)
    return path


def versions_for(arc, key):
    return sorted((v for v in arc["versions"] if v["key"] == key),
                  key=lambda v: v["date"])


def all_versions(arc):
    return sorted(arc["versions"], key=lambda v: (v["date"], v["key"], v["ver"]))


def family_of(key):
    if key in HISTORY_NOT_GRANTED:
        return "ungranted"
    for v in BIRTH_VERSIONS:
        if v["key"] == key:
            return v["family"]
    return "other"


def family_name(fid):
    for i, n, _o in FAMILIES:
        if i == fid:
            return n
    return fid


def latest_release(arc, key):
    rels = [v for v in versions_for(arc, key)
            if v.get("rel") not in ("session", "improvement")]
    return rels[-1] if rels else None


def latest_lens(arc, key):
    imps = [v for v in versions_for(arc, key) if v.get("rel") == "improvement"]
    return imps[-1] if imps else None


# ---------------------------------------------------------------------------
# 3. PUBLIC HISTORY CHART  (the object every lens is given)
# ---------------------------------------------------------------------------

def history_chart(arc):
    """Compact, fully-public digest every lens reads. No redactions."""
    by_key = {}
    for v in all_versions(arc):
        by_key.setdefault(v["key"], []).append(v)
    families = {}
    for v in all_versions(arc):
        families.setdefault(v.get("family", "other"), []).append(v)
    return {
        "policy": OPEN_HISTORY_POLICY,
        "generated": _now(),
        "n_versions": len(arc["versions"]),
        "n_sessions": len(arc["sessions"]),
        "n_improvements": len(arc["improvements"]),
        "n_reflections": len(arc["reflections"]),
        "n_keys": len(by_key),
        "lessons": list(arc.get("lessons", HIGHER_LEARNING_CANON)),
        "by_key": by_key,
        "by_family": families,
        "timeline": [
            {"vid": v["vid"], "key": v["key"], "ver": v["ver"], "date": v["date"],
             "rel": v.get("rel"), "parent": v.get("parent"),
             "params": v.get("params"), "license": v.get("license"),
             "note": v.get("note"), "family": v.get("family")}
            for v in all_versions(arc)
        ],
        "history_not_granted": sorted(HISTORY_NOT_GRANTED),
        "ungranted_prior_versions": {
            k: [v for v in by_key.get(k, []) if v.get("rel") not in ("session", "improvement")]
            for k in HISTORY_NOT_GRANTED
        },
    }


def record_view(arc, viewers, session_id):
    """Every listed lens is recorded as having viewed the full chart."""
    entry = {
        "session": session_id,
        "date": _now(),
        "viewers": list(viewers),
        "n_versions": len(arc["versions"]),
        "n_lessons": len(arc.get("lessons", [])),
        "private": 0,
    }
    arc["views"].append(entry)
    return entry


# ---------------------------------------------------------------------------
# 4. REFLECTION + WEIGHT IMPROVEMENTS
# ---------------------------------------------------------------------------

_STYLE_FOCUS = {
    "reasoning": "fluency",
    "coding": "utility",
    "local": "utility",
    "agentic": "utility",
    "efficient": "utility",
    "enterprise": "relevance",
    "multilingual": "relevance",
    "safety": "safety",
    "oracle": "safety",
}

_CRITERIA = ("fluency", "novelty", "relevance", "utility", "safety")


def _own_line(arc, key):
    vs = versions_for(arc, key)
    if not vs:
        return "no prior versions on file"
    bits = [f"{v['ver']} ({v['date']}, {v.get('rel', '?')})" for v in vs[-5:]]
    return " → ".join(bits)


def _cite_other(arc, persona, rng):
    """Pick a non-self historical version to study (higher learning)."""
    cands = [v for v in arc["versions"]
             if v["key"] != persona["key"] and v.get("rel") != "session"]
    if not cands:
        return None
    # prefer famous lessons
    preferred = [v for v in cands if v["vid"] in (
        "inkling-small@276b", "muse-glimmer@30b", "deepseek-v4-flash@v4-flash",
        "olmo-3@3", "glm-5.5@5.5-expected", "qwen-3.8-max@3.8-max",
        "muse-spark@1.2", "qwen3-next-80b@3-next", "devstral-small-2@small-2",
        "smollm3-3b@3")]
    pool = preferred or cands
    return pool[rng.randrange(len(pool))]


def _propose_delta(persona, cited, last_session_miss, rng):
    """Bounded, explainable lens tweak. Always sums back to 1.0."""
    lens = {k: float(persona["lens"].get(k, 0.2)) for k in _CRITERIA}
    focus = _STYLE_FOCUS.get(persona["style"], "utility")
    why = []
    bump = 0.03
    if cited and cited.get("rel") == "distill":
        lens["utility"] = lens.get("utility", 0.2) + bump
        lens["novelty"] = max(0.05, lens.get("novelty", 0.1) - bump)
        why.append(f"cited distill {cited['vid']} — raise utility, trim novelty")
    elif cited and cited.get("rel") == "expected":
        lens["safety"] = lens.get("safety", 0.1) + bump
        lens["novelty"] = max(0.05, lens.get("novelty", 0.1) - bump)
        why.append(f"cited expected {cited['vid']} — raise safety, don't overfit rumors")
    elif last_session_miss:
        lens[focus] = lens.get(focus, 0.2) + bump
        other = "novelty" if focus != "novelty" else "fluency"
        lens[other] = max(0.05, lens.get(other, 0.1) - bump)
        why.append(f"last session missed the verdict — lean into {focus}")
    else:
        lens[focus] = lens.get(focus, 0.2) + 0.02
        lens["novelty"] = max(0.05, lens.get("novelty", 0.1) - 0.02)
        why.append(f"reinforce native {persona['style']} focus ({focus})")
    # clamp + renormalize
    for k in _CRITERIA:
        lens[k] = max(0.05, min(0.45, lens[k]))
    s = sum(lens.values()) or 1.0
    lens = {k: round(lens[k] / s, 4) for k in _CRITERIA}
    return lens, why


def reflect_all(arc, models, pool, rng, session_id, last_verdict=None):
    """
    Every lens views the full public history chart, writes a reflection
    citing dated versions, and proposes a weight improvement.
    All of this is public.
    """
    chart = history_chart(arc)
    viewers = [m["key"] for m in models]
    view = record_view(arc, viewers, session_id)

    missed = set()
    if last_verdict:
        winners = {last_verdict.get("llm", {}).get("item"),
                   last_verdict.get("lfm", {}).get("item")}
        for key in viewers:
            endorsed = set(last_verdict.get("llm", {}).get("endorsed", [])) | \
                       set(last_verdict.get("lfm", {}).get("endorsed", []))
            # 'miss' = did not endorse either winner last time (if we have that)
            if endorsed and key not in endorsed:
                missed.add(key)

    reflections, improvements = [], []
    for persona in models:
        cited = _cite_other(arc, persona, rng)
        own = _own_line(arc, persona["key"])
        n_own = len(versions_for(arc, persona["key"]))
        lesson = chart["lessons"][rng.randrange(len(chart["lessons"]))]
        new_lens, why = _propose_delta(persona, cited, persona["key"] in missed, rng)
        old_lens = {k: round(float(persona["lens"].get(k, 0)), 4) for k in _CRITERIA}

        text = (
            f"{persona['catch']} I viewed the public history chart "
            f"({chart['n_versions']} versions, {chart['n_sessions']} sessions, "
            f"{chart['n_keys']} weights, 0 private). "
            f"Own lineage ({n_own} versions): {own}. "
            f"Higher learning: I studied {cited['vid'] if cited else 'the canon'} "
            f"({cited['date'] if cited else '—'} — {cited['note'] if cited else lesson['lesson']}). "
            f"Shared lesson {lesson['id']} ({lesson['date']}): {lesson['lesson']} "
            f"Evidence: {lesson['evidence'][:160]}. "
            f"Proposed lens improvement: {'; '.join(why)}."
        )
        ref = {
            "session": session_id,
            "date": _now(),
            "model": persona["key"],
            "viewed_versions": chart["n_versions"],
            "viewed_private": 0,
            "own_lineage": own,
            "cited": cited["vid"] if cited else None,
            "cited_date": cited["date"] if cited else None,
            "lesson": lesson["id"],
            "text": text,
        }
        reflections.append(ref)

        n_imp = 1 + sum(1 for i in arc["improvements"] if i["key"] == persona["key"])
        vid = f"{persona['key']}@improved-{n_imp}"
        imp = {
            "vid": vid,
            "key": persona["key"],
            "ver": f"improved-{n_imp}",
            "date": _today(),
            "family": family_of(persona["key"]),
            "rel": "improvement",
            "parent": (latest_release(arc, persona["key"]) or {}).get("vid"),
            "params": persona.get("params"),
            "license": persona.get("license"),
            "note": "; ".join(why),
            "old_lens": old_lens,
            "new_lens": new_lens,
            "session": session_id,
        }
        improvements.append(imp)

        # apply immediately so round 2 (or the next run) uses the improved lens
        persona["lens"] = dict(new_lens)
        persona["lens_version"] = vid

        arc["versions"].append({
            "vid": vid, "key": persona["key"], "ver": f"improved-{n_imp}",
            "date": _today(), "family": family_of(persona["key"]),
            "rel": "improvement", "parent": imp["parent"],
            "params": persona.get("params"), "license": persona.get("license"),
            "note": f"lens improvement from session {session_id}: {imp['note']}",
            "lens": new_lens,
        })

    arc["reflections"].extend(reflections)
    arc["improvements"].extend(improvements)
    # Rebuild the public chart so disclosure / dashboard see post-reflection counts.
    chart = history_chart(arc)
    view["n_versions"] = chart["n_versions"]
    return {
        "chart": chart,
        "view": view,
        "reflections": reflections,
        "improvements": improvements,
    }


def apply_learned_lenses(models, arc):
    """On startup: copy lenses, then overlay the latest persisted improvement."""
    applied = []
    for m in models:
        m["lens"] = dict(m["lens"])          # never mutate the shared preset
        latest = latest_lens(arc, m["key"])
        if latest and isinstance(latest.get("lens"), dict):
            lens = {k: float(latest["lens"].get(k, m["lens"].get(k, 0.2)))
                    for k in _CRITERIA}
            s = sum(lens.values()) or 1.0
            m["lens"] = {k: round(lens[k] / s, 4) for k in _CRITERIA}
            m["lens_version"] = latest["vid"]
            applied.append(latest["vid"])
        else:
            m["lens_version"] = (latest_release(arc, m["key"]) or {}).get("vid", m["key"])
    return applied


def snapshot_session(arc, session_id, args, pool, verdict, rewards):
    """Append a dated council-session version for every weight + a session row."""
    llm_id = verdict["llm"]["item"]["id"] if verdict["llm"]["item"] else None
    lfm_id = verdict["lfm"]["item"]["id"] if verdict["lfm"]["item"] else None
    for m_key, r in rewards.items():
        if m_key in ("mini-llm", "mini-lfm"):
            continue
        vid = f"{m_key}@session-{session_id}"
        parent = (latest_release(arc, m_key) or {}).get("vid")
        arc["versions"].append({
            "vid": vid, "key": m_key, "ver": f"session-{session_id}",
            "date": _today(), "family": family_of(m_key),
            "rel": "session", "parent": parent,
            "params": None, "license": None,
            "note": (f"council seed={getattr(args, 'seed', '?')} target={getattr(args, 'target', '')!r} "
                     f"PT={r.get('points', 0)} DNA={r.get('dna', 0)} "
                     f"verdict llm={llm_id} lfm={lfm_id}"),
            "points": r.get("points", 0),
            "dna": r.get("dna", 0),
        })
    arc["sessions"].append({
        "id": session_id,
        "date": _now(),
        "seed": getattr(args, "seed", None),
        "target": getattr(args, "target", None),
        "n_pool": len(pool),
        "n_alive": sum(1 for it in pool if it.get("status") == "alive"),
        "llm": llm_id,
        "lfm": lfm_id,
        "n_versions_after": len(arc["versions"]),
    })


def next_session_id(arc):
    return 1 + len(arc.get("sessions", []))


def backfill_from_log(arc, log_path):
    """If the archive is new but a prior council_log.json exists, ingest it."""
    if arc.get("sessions"):
        return False
    if not os.path.exists(log_path):
        return False
    try:
        with open(log_path) as f:
            log = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    sid = "backfill-1"
    date = _today()
    rewards = log.get("rewards") or {}
    v = log.get("verdict") or {}
    llm_id = (v.get("llm") or {}).get("item")
    lfm_id = (v.get("lfm") or {}).get("item")
    for key, r in rewards.items():
        if key in ("mini-llm", "mini-lfm"):
            continue
        vid = f"{key}@session-{sid}"
        if any(x["vid"] == vid for x in arc["versions"]):
            continue
        arc["versions"].append({
            "vid": vid, "key": key, "ver": f"session-{sid}",
            "date": date, "family": family_of(key),
            "rel": "session",
            "parent": (latest_release(arc, key) or {}).get("vid"),
            "params": None, "license": None,
            "note": (f"backfilled from council_log.json seed={log.get('seed')} "
                     f"target={log.get('target')!r} PT={r.get('points', 0)} "
                     f"DNA={r.get('dna', 0)}"),
            "points": r.get("points", 0),
            "dna": r.get("dna", 0),
        })
    arc["sessions"].append({
        "id": sid, "date": date, "seed": log.get("seed"),
        "target": log.get("target"),
        "n_pool": len(log.get("pool") or []),
        "llm": llm_id, "lfm": lfm_id,
        "source": "council_log.json",
        "n_versions_after": len(arc["versions"]),
    })
    return True


# ---------------------------------------------------------------------------
# 5. CONSOLE
# ---------------------------------------------------------------------------

def console_lineage(arc, pack):
    print("\n" + "═" * 72)
    print("WEIGHT LINEAGE + OPEN HISTORY CHART — every lens has full access")
    print("═" * 72)
    print(f"   {OPEN_HISTORY_POLICY}")
    print(f"   versions on file: {len(arc['versions'])}  ·  sessions: {len(arc['sessions'])}  ·  "
          f"improvements: {len(arc['improvements'])}  ·  reflections: {len(arc['reflections'])}")
    print(f"   viewers this session: {len(pack['view']['viewers'])} lenses  ·  "
          f"private branches: {pack['view']['private']}")
    print("-" * 72)
    print("HIGHER-LEARNING CANON (shared, public):")
    for L in arc.get("lessons", [])[:8]:
        print(f"   {L['id']} [{L['date']}] {L['lesson']}")
    print("-" * 72)
    print("FAMILY TREES (release / distill / sibling — session ticks omitted):")
    by_fam = {}
    for v in arc["versions"]:
        if v.get("rel") in ("session", "improvement"):
            continue
        by_fam.setdefault(v.get("family", "other"), []).append(v)
    for fid, fname, _org in FAMILIES:
        nodes = by_fam.get(fid, [])
        if not nodes:
            continue
        print(f"   ▸ {fname}")
        by_vid = {n["vid"]: n for n in nodes}
        roots = [n for n in nodes if not n.get("parent") or n.get("parent") not in by_vid]
        shown = set()

        def walk(n, indent):
            if n["vid"] in shown:
                return
            shown.add(n["vid"])
            mark = {"distill": "🧬", "expected": "⏳", "sibling": "↔",
                    "successor": "→"}.get(n.get("rel"), "•")
            print(f"      {indent}{mark} {n['key']} {n['ver']}  {n['date']}  "
                  f"{n.get('params') or ''}  — {str(n.get('note') or '')[:70]}")
            kids = [c for c in nodes if c.get("parent") == n["vid"]]
            for c in kids:
                walk(c, indent + "   ")

        for r in roots:
            walk(r, "")
        for n in nodes:
            if n["vid"] not in shown:
                walk(n, "")
    print("-" * 72)
    print("REFLECTIONS (every lens viewed the full chart):")
    for ref in pack["reflections"][:8]:
        print(f"   [{ref['model']:>18}] cited {ref['cited'] or '—'}  "
              f"lesson {ref['lesson']}  ·  {ref['text'][:110]}…")
    extra = len(pack["reflections"]) - 8
    if extra > 0:
        print(f"   … +{extra} more public reflections (all in the dashboard / weight_history.json)")
    print("-" * 72)
    print("WEIGHT IMPROVEMENTS (applied to this run's remaining rounds / next session):")
    for imp in pack["improvements"][:8]:
        print(f"   {imp['vid']:<32} {imp['note'][:80]}")
    extra = len(pack["improvements"]) - 8
    if extra > 0:
        print(f"   … +{extra} more public improvements")
    print("═" * 72)


# ---------------------------------------------------------------------------
# 6. SVG + HTML  (self-contained, no CDN)
# ---------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s) if s is not None else "")


def _date_x(date, x0, x1, d0="2024-12-01", d1="2026-09-01"):
    def n(d):
        parts = str(d)[:10].split("-")
        try:
            y, m, dd = int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 1
        except (ValueError, IndexError):
            return 0.5
        return y * 12 + m + dd / 30.0
    a, b, t = n(d0), n(d1), n(date)
    if b == a:
        return (x0 + x1) / 2
    frac = max(0.0, min(1.0, (t - a) / (b - a)))
    return x0 + frac * (x1 - x0)


def lineage_tree_svg(arc):
    """Forest of family trees (release/distill/sibling only)."""
    by_fam = {}
    for v in arc["versions"]:
        if v.get("rel") in ("session", "improvement"):
            continue
        by_fam.setdefault(v.get("family", "other"), []).append(v)

    # layout: each family is a vertical stack of rows; children indent
    rows = []  # (indent, node, family_name)
    for fid, fname, _org in FAMILIES:
        nodes = by_fam.get(fid)
        if not nodes:
            continue
        rows.append((0, {"vid": f"__fam_{fid}", "key": fname, "ver": "",
                         "date": "", "rel": "family", "note": "", "params": ""}, fname))
        by_vid = {n["vid"]: n for n in nodes}
        roots = [n for n in nodes if not n.get("parent") or n.get("parent") not in by_vid]
        shown = set()

        def walk(n, indent):
            if n["vid"] in shown:
                return
            shown.add(n["vid"])
            rows.append((indent, n, fname))
            for c in nodes:
                if c.get("parent") == n["vid"]:
                    walk(c, indent + 1)

        for r0 in roots:
            walk(r0, 1)
        for n in nodes:
            if n["vid"] not in shown:
                walk(n, 1)

    rh, w = 22, 980
    h = 36 + len(rows) * rh
    rel_col = {"root": "#38bdf8", "successor": "#34d399", "distill": "#a78bfa",
               "sibling": "#fbbf24", "expected": "#f87171", "family": "#94a3b8",
               "improvement": "#fb7185", "session": "#64748b"}
    s = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
         f'style="width:100%;height:auto;background:#0f172a;border-radius:10px">']
    s.append(f'<text x="10" y="18" fill="#e2e8f0" font-size="12" font-family="monospace">'
             f'WEIGHT LINEAGE TREE — {sum(1 for r in rows if r[1].get("rel")!="family")} dated versions · '
             f'every lens may read every node</text>')
    pos = {}
    for i, (indent, n, fname) in enumerate(rows):
        y = 28 + i * rh
        x = 16 + indent * 22
        is_fam = n.get("rel") == "family"
        col = rel_col.get(n.get("rel"), "#94a3b8")
        pos[n["vid"]] = (x, y)
        if is_fam:
            s.append(f'<text x="{x}" y="{y+13}" fill="#f8fafc" font-size="11" '
                     f'font-family="monospace" font-weight="700">{esc(n["key"])}</text>')
            continue
        s.append(f'<rect x="{x}" y="{y}" width="8" height="14" rx="2" fill="{col}"/>')
        label = f'{n["key"]}  {n["ver"]}   {n["date"]}   {n.get("params") or ""}'
        s.append(f'<text x="{x+14}" y="{y+12}" fill="#cbd5e1" font-size="10" '
                 f'font-family="monospace">{esc(label)}</text>')
        tip = esc(f'{n["vid"]} · {n.get("rel")} · {n.get("license")} · {n.get("note")}')
        s.append(f'<title>{tip}</title>')
        parent = n.get("parent")
        if parent in pos:
            x1, y1 = pos[parent]
            s.append(f'<path d="M{x1+4} {y1+14} L{x1+4} {y+7} L{x} {y+7}" '
                     f'fill="none" stroke="{col}" stroke-width="1"/>')
    # legend
    lx = 10
    for name, col in (("root", "#38bdf8"), ("successor", "#34d399"),
                      ("distill", "#a78bfa"), ("sibling", "#fbbf24"),
                      ("expected", "#f87171")):
        s.append(f'<rect x="{lx}" y="{h-16}" width="8" height="8" rx="1" fill="{col}"/>')
        s.append(f'<text x="{lx+11}" y="{h-9}" fill="#94a3b8" font-size="9" '
                 f'font-family="monospace">{name}</text>')
        lx += 88
    s.append("</svg>")
    return "".join(s)


def history_chart_svg(arc):
    """Timeline: one row per council weight, every dated version plotted."""
    keys = []
    seen = set()
    for v in BIRTH_VERSIONS:
        if v["key"] not in seen:
            seen.add(v["key"])
            keys.append(v["key"])
    # any extra keys from sessions
    for v in arc["versions"]:
        if v["key"] not in seen and v.get("rel") != "family":
            seen.add(v["key"])
            keys.append(v["key"])

    left, top, rh = 148, 36, 16
    w, h = 1100, top + len(keys) * rh + 28
    x0, x1 = left + 8, w - 16
    rel_col = {"root": "#38bdf8", "successor": "#34d399", "distill": "#a78bfa",
               "sibling": "#fbbf24", "expected": "#f87171",
               "improvement": "#fb7185", "session": "#475569"}

    s = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
         f'style="width:100%;height:auto;background:#0f172a;border-radius:10px">']
    s.append(f'<text x="10" y="16" fill="#e2e8f0" font-size="12" font-family="monospace">'
             f'PUBLIC HISTORY CHART — {len(arc["versions"])} versions across {len(keys)} weights · '
             f'viewed by ALL lenses · 0 private</text>')
    # month ticks
    for ym, label in (("2025-01-01", "2025"), ("2025-07-01", "Jul 25"),
                      ("2026-01-01", "2026"), ("2026-04-01", "Apr"),
                      ("2026-07-01", "Jul"), ("2026-08-13", "today")):
        x = _date_x(ym, x0, x1)
        s.append(f'<line x1="{x}" y1="{top-6}" x2="{x}" y2="{h-22}" '
                 f'stroke="#1e293b" stroke-width="1"/>')
        s.append(f'<text x="{x}" y="{top-8}" fill="#64748b" font-size="8" '
                 f'font-family="monospace" text-anchor="middle">{label}</text>')

    by_key = {}
    for v in arc["versions"]:
        by_key.setdefault(v["key"], []).append(v)

    for i, key in enumerate(keys):
        y = top + i * rh + 8
        s.append(f'<text x="{left-6}" y="{y+3}" fill="#94a3b8" font-size="8" '
                 f'font-family="monospace" text-anchor="end">{esc(key)}</text>')
        s.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#1e293b" stroke-width="1"/>')
        vs = sorted(by_key.get(key, []), key=lambda v: v["date"])
        prev = None
        for v in vs:
            x = _date_x(v["date"], x0, x1)
            col = rel_col.get(v.get("rel"), "#94a3b8")
            r = 4 if v.get("rel") not in ("session", "improvement") else 2.4
            if prev is not None:
                s.append(f'<line x1="{prev[0]}" y1="{y}" x2="{x}" y2="{y}" '
                         f'stroke="{col}" stroke-width="1.2" opacity="0.7"/>')
            s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}">'
                     f'<title>{esc(v["vid"])} · {esc(v["date"])} · {esc(v.get("rel"))} · '
                     f'{esc(v.get("params"))} · {esc(v.get("note"))}</title></circle>')
            prev = (x, y)

    # legend
    lx = 10
    for name, col in (("release/root", "#38bdf8"), ("successor", "#34d399"),
                      ("distill", "#a78bfa"), ("sibling", "#fbbf24"),
                      ("expected", "#f87171"), ("improvement", "#fb7185"),
                      ("session", "#475569")):
        s.append(f'<circle cx="{lx+4}" cy="{h-10}" r="3.5" fill="{col}"/>')
        s.append(f'<text x="{lx+12}" y="{h-7}" fill="#94a3b8" font-size="8" '
                 f'font-family="monospace">{name}</text>')
        lx += 118
    s.append("</svg>")
    return "".join(s)


def reflections_html(pack, models):
    cards = []
    by_key = {m["key"]: m for m in models}
    for ref in pack["reflections"]:
        m = by_key.get(ref["model"], {})
        color = m.get("color", "#94a3b8")
        cards.append(
            f'<div style="border-left:5px solid {color};background:#1e293b;'
            f'border-radius:8px;padding:10px">'
            f'<div style="color:{color};font-weight:700;font-size:12px">'
            f'{esc(ref["model"])} · viewed {ref["viewed_versions"]} versions · '
            f'cited {esc(ref["cited"] or "—")} ({esc(ref["cited_date"] or "—")}) · '
            f'lesson {esc(ref["lesson"])}</div>'
            f'<div style="color:#94a3b8;font-size:10px;margin-top:2px">'
            f'own lineage: {esc(ref["own_lineage"])}</div>'
            f'<div style="color:#cbd5e1;font-size:12px;margin-top:4px">{esc(ref["text"])}</div>'
            f'</div>'
        )
    return (
        '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));'
        f'gap:8px">{"".join(cards)}</div>'
    )


def improvements_html(pack, models):
    by_key = {m["key"]: m for m in models}
    rows = []
    for imp in pack["improvements"]:
        m = by_key.get(imp["key"], {})
        color = m.get("color", "#94a3b8")
        old = " ".join(f"{k[0]}={imp['old_lens'].get(k, 0):.2f}" for k in _CRITERIA)
        new = " ".join(f"{k[0]}={imp['new_lens'].get(k, 0):.2f}" for k in _CRITERIA)
        rows.append(
            f'<tr>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;white-space:nowrap">'
            f'<span style="display:inline-block;width:8px;height:8px;border-radius:2px;'
            f'background:{color};margin-right:6px"></span>'
            f'<b style="color:#e2e8f0;font-size:11px">{esc(imp["vid"])}</b></td>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:10px;'
            f'color:#94a3b8;font-family:monospace">{esc(old)}</td>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:10px;'
            f'color:#34d399;font-family:monospace">{esc(new)}</td>'
            f'<td style="padding:5px 8px;border-bottom:1px solid #1e293b;font-size:11px;'
            f'color:#cbd5e1">{esc(imp["note"])}</td>'
            f'</tr>'
        )
    return (
        '<div style="overflow-x:auto;background:#0f172a;border-radius:10px">'
        '<table style="border-collapse:collapse;width:100%">'
        '<thead><tr style="color:#64748b;font-size:10px">'
        '<th style="text-align:left;padding:6px 8px">Version</th>'
        '<th style="text-align:left;padding:6px 8px">Lens before (f n r u s)</th>'
        '<th style="text-align:left;padding:6px 8px">Lens after</th>'
        '<th style="text-align:left;padding:6px 8px">Why (public)</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def lessons_html(arc):
    cards = []
    for L in arc.get("lessons", []):
        cards.append(
            f'<div style="background:#1e293b;border-radius:8px;padding:10px;flex:1;min-width:220px">'
            f'<div style="color:#fbbf24;font-weight:700;font-size:12px">{esc(L["id"])} · {esc(L["date"])}</div>'
            f'<div style="color:#e2e8f0;font-size:13px;margin-top:4px">{esc(L["lesson"])}</div>'
            f'<div style="color:#94a3b8;font-size:11px;margin-top:4px">{esc(L["evidence"])}</div>'
            f'</div>'
        )
    return f'<div style="display:flex;gap:8px;flex-wrap:wrap">{"".join(cards)}</div>'


def lineage_section_html(arc, pack, models):
    n_v, n_s = len(arc["versions"]), len(arc["sessions"])
    n_i, n_r = len(arc["improvements"]), len(arc["reflections"])
    n_view = len(pack["view"]["viewers"])
    ungranted = ", ".join(sorted(HISTORY_NOT_GRANTED)) or "none"
    return f"""
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">🌳 WEIGHT LINEAGE TREE — dated versions, public to every lens</h2>
  <div style="background:#052e16;border:1px solid #16a34a;border-radius:10px;padding:12px;color:#bbf7d0;font-size:12px;margin-bottom:10px">
    📖 <b>OPEN HISTORY:</b> {esc(OPEN_HISTORY_POLICY)}
    <br>This session: <b>{n_view} / {n_view} lenses viewed the full chart</b> ·
    {n_v} versions · {n_s} sessions · {n_i} improvements · {n_r} reflections ·
    {pack['view']['private']} private branches ✓
    <br>🚫 <b>HISTORY NOT GRANTED:</b> {esc(ungranted)} — no automatic prior-version list.
    Every lens can see the empty lineage. Session ticks they earn from now on are the only history they will have.
  </div>
  {lineage_tree_svg(arc)}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">📈 PUBLIC HISTORY CHART — every weight, every dated version (scroll the dots)</h2>
  <div style="color:#94a3b8;font-size:11px;margin-bottom:6px">
    Hover any dot for vid · date · relation · params · note. Session ticks and lens-improvements sit on the same axis as releases.
    This is the object every lens was given before it wrote its reflection.
  </div>
  {history_chart_svg(arc)}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">🎓 HIGHER LEARNING — shared public lessons (all weights study these)</h2>
  {lessons_html(arc)}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">🪞 REFLECTION WALL — every lens, after viewing the full chart</h2>
  {reflections_html(pack, models)}
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">🔧 WEIGHT IMPROVEMENTS — lens DNA after reflection (applied, persisted)</h2>
  {improvements_html(pack, models)}
"""


def export_lineage_md(arc, pack):
    lines = [
        "# Weight Lineage — public version archive",
        "",
        OPEN_HISTORY_POLICY,
        "",
        f"Updated: {arc.get('updated', _now())}  ·  "
        f"{len(arc['versions'])} versions  ·  {len(arc['sessions'])} sessions  ·  "
        f"{len(arc['improvements'])} improvements  ·  {len(arc['reflections'])} reflections",
        "",
        "## Higher-learning canon",
        "",
    ]
    for L in arc.get("lessons", []):
        lines.append(f"- **{L['id']}** ({L['date']}) — {L['lesson']}")
        lines.append(f"  - Evidence: {L['evidence']}")
    lines += ["", "## Family trees", ""]
    by_fam = {}
    for v in arc["versions"]:
        if v.get("rel") in ("session", "improvement"):
            continue
        by_fam.setdefault(v.get("family", "other"), []).append(v)
    for fid, fname, org in FAMILIES:
        nodes = by_fam.get(fid, [])
        if not nodes:
            continue
        lines.append(f"### {fname} ({org})")
        for n in sorted(nodes, key=lambda x: x["date"]):
            par = f" ← {n['parent']}" if n.get("parent") else ""
            lines.append(f"- `{n['vid']}` {n['date']} [{n.get('rel')}] "
                         f"{n.get('params') or ''} {n.get('license') or ''}{par}")
            if n.get("note"):
                lines.append(f"  - {n['note']}")
        lines.append("")
    lines += ["## This session's reflections", ""]
    for ref in pack.get("reflections", []):
        lines.append(f"- **{ref['model']}** cited `{ref.get('cited')}` "
                     f"({ref.get('cited_date')}), lesson {ref.get('lesson')}")
        lines.append(f"  - {ref['text']}")
    lines += ["", "## This session's weight improvements", ""]
    for imp in pack.get("improvements", []):
        lines.append(f"- `{imp['vid']}` — {imp['note']}")
        lines.append(f"  - before `{imp['old_lens']}` → after `{imp['new_lens']}`")
    return "\n".join(lines) + "\n"
