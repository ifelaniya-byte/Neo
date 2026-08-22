# Kaggle lane — single account

Single phone-verified account only. Multi-account GPU farming violates Kaggle TOS and is not implemented.

This box is not a Kaggle T4. We can catalog and push kernels if the API allows; we cannot host 32 Ollama/ngrok workers here.

- Auth: **True** (token present: True)
- Date: 2026-08-13 17:51:24

## Weekly free budget (one identity)

| Resource | Typical free quota |
|---|---|
| GPU T4/P100 | ~30 h/week |
| Concurrent GPU sessions | 2 |
| Session length | ~9 h GPU / 12 h CPU |
| CPU notebooks | unlimited |

## KP-14 — what you run ON Kaggle (one identity, batch only)

Kaggle is a **batch lab**, not an always-on API. Sessions die. Do not ngrok Ollama.

1. `kaggle_00_environment_check.ipynb` on **CPU** first. Do not burn GPU deciding.
2. `kaggle_10_download_verify.ipynb` — ModelScope official tiny ladder only + SHA-256.
3. `kaggle_worker_template.ipynb` — sequential 4-bit, one 0.5B–9B model, `trust_remote_code=False`.
4. `kaggle_30_train_qlora.ipynb` — one adapter per domain (coding / math / retrieval).
5. Giants (Kimi K3, Qwen 3.8 Max, Apertus 70B, GLM 5.2 282 shards) do **not** fit a T4.
6. Dual-T4 is **not guaranteed**. 70B 4-bit is not a weekly plan.

Quota split of whatever hours you actually get: QLoRA 45% · eval 25% · batch infer 15% · quant 10% · contingency 5%.

## Mapped listings (verify files before you trust them)

- `phi-4` → `arpit1bansal/phi-4` (listed, 1 instances) — community Phi-4 listing, not Microsoft official
- `gemma-4-31b` → `google/gemma-4` (listed, 47 instances) — Google official Gemma 4 family
- `olmo-3` → `danbth/olmo-3-7b-instruct` (listed, 1 instances) — community OLMo-3-7B-Instruct
- `olmo-family` → `allenai/olmo` (listed, 16 instances) — Ai2 official OLMo
- `granite-4.1` → `ibm-research/granite-4.0` (listed, 10 instances) — IBM official Granite 4.0 family
- `gpt-oss-20b` → `danielhanchen/gpt-oss-20b` (listed, 1 instances) — Unsloth gpt-oss-20b listing
- `gpt-oss-120b` → `danielhanchen/gpt-oss-120b` (listed, 1 instances) — Unsloth gpt-oss-120b listing
- `smollm3-3b` → `keras/smollm3` (listed, 1 instances) — Keras official SmolLM3
- `qwen3-family` → `qwen-lm/qwen-3` (listed, 45 instances) — Qwen official Qwen-3 family
- `qwen3.6-27b` → `ravi123a321at/qwen-3-6-27b` (listed, 1 instances) — community Qwen 3.6 27B — verify files
- `kimi-k3` → `helium990/kimi-k3` (listed, 10 instances) — community Kimi K3 — verify files
- `falcon-h1r-7b` → `manojkumarcs28/falcon-h1r-series` (listed, 1 instances) — community Falcon H1R series
- `devstral-small-2` → `mistral-ai/devstral-small-2507` (listed, 2 instances) — Mistral official Devstral Small
- `mistral-small-3.1` → `mistral-ai/mistral-small-24b` (listed, 2 instances) — Mistral official Small 24B
- `llama-family` → `metaresearch/llama-3` (listed, 8 instances) — Meta Llama 3 on Kaggle — Llama 4/5 not listed as official

## Not implemented (on purpose)

- Multi-account / extra phone numbers
- 32 parallel Ollama+ngrok workers from this sandbox
- Auto-spend of the depleted HF Inference Provider quota

