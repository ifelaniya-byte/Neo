# Seat registry — KP-14 (logical experts, verified artifacts)

ACORN_RULE: spoken co-signs beat disapproves; hold-peace is not consent.

The 45 names are **logical expert seats**, not 45 downloaded giants.
A catalog HTTP 200 is a listing, not authenticity.

- Seats catalogued: **56**
- verified-checkpoint: **13**
- verified-api: **2**
- community-quarantine: **2**
- logical-emulated: **39**
- T4 easy / tight: 9 / 6

## Model ladder (what we actually run)

- **tiny-base** `qwen2.5-0.5b` 0.5B Q4~0.25GB — ON DISK here (988 MB BF16). Pipeline smoke test. No torch in this box.
- **tiny-next** `qwen3-0.6b` 0.6B Q4~0.35GB — ModelScope listed ~1.5 GB. Next pull if disk allows.
- **reasoning-base** `r1-distill-1.5b` 1.5B Q4~0.75GB — Reasoning student. NOT DeepSeek V4 Flash.
- **primary-dev** `smollm3-3b` 3B Q4~1.5GB — Kaggle official Keras listing. Primary QLoRA platform.
- **strong-local** `olmo-3-7b` 7B Q4~4.5GB — Ai2 official family on Kaggle. Prefer official over danbth community.
- **mid-infer** `phi-4` 14B Q4~8.0GB — Card on disk. Shards ~7–10 GB Q4. Inference-only until small pipeline works.

## Weekly GPU quota split (percent of whatever hours the account actually gets)

| Work | Share |
|---|---:|
| QLoRA adapter training | 45% |
| Evaluation / regression | 25% |
| Batched inference / data gen | 15% |
| Quantization / compatibility | 10% |
| Contingency | 5% |

CPU sessions: registry, cleaning, prompts, unit tests, aggregation. Do not burn GPU while downloading or deciding the experiment.

## Rejected claims (documented)

- **45 full checkpoints on one Kaggle account** — T4 16GB + ~30h/week cannot host 45 models. Seats are logical experts.
- **helium990/kimi-k3 is Kimi K3** — Community listing. Quarantine. Official live id was moonshotai/Kimi-K3 on HF router (402 now).
- **ravi123a321at/qwen-3-6-27b is official Qwen 3.6 27B** — Community. Official ModelScope is Qwen/Qwen3.6-27B (~15×3.9GB). Too big for T4.
- **arpit1bansal/phi-4 is Microsoft official** — Community. Prefer LLM-Research/Phi-4 (MS) or microsoft/phi-4 (HF, token+credits).
- **DeepSeek-R1-Distill-Qwen-1.5B is DeepSeek V4 Flash** — Different model, different year. Distill is a 1.5B student, not V4.
- **keras/smollm3 is a ModelScope id** — That is a Kaggle model ref. Do not snapshot_download it from ModelScope.
- **google/gemma-4 is a ModelScope id** — Official Gemma 4 on Kaggle is google/gemma-4. Confirm ModelScope separately.
- **70B 4-bit (~38GB) is a normal Dual-T4 job** — Kaggle usually gives ONE T4 16GB, not a guaranteed 2×T4. 70B needs ~35–45GB weights plus KV. Experimental llama.cpp offload is not the weekly plan.
- **Always-on Ollama + ngrok on Kaggle** — Sessions are ephemeral. Tunneling a public API may conflict with platform expectations. Batch artifacts only.
- **3 accounts × 30 GPU hours** — Multi-account / extra-phone farming violates Kaggle TOS. One phone-verified identity.
- **CMAKE_ARGS=-GGUIDE=OFF** — Typo. CUDA llama-cpp uses -DGGML_CUDA=on. Do not ship a broken compile cell.
- **HTTP 200 on a catalog = authentic weights** — A listing proves a listing. Check publisher, license, shards, checksums, trust_remote_code.

## Every seat

| Seat | Status | Domain | Backend | Identifier | T4 | Note |
|---|---|---|---|---|---|---|
| `smollm3-3b` | verified-checkpoint | instruction | kaggle | `keras/smollm3` | easy | Kaggle official Keras SmolLM3. Primary 3B development base. |
| `phi-4` | verified-checkpoint | math | modelscope | `LLM-Research/Phi-4` | tight | MS card on disk. HF★ wave-1 then 402. Mid-size inference only. |
| `gpt-oss-20b` | verified-checkpoint | coding | modelscope | `openai-mirror/gpt-oss-20b` | tight | MS card on disk. T4 possible MXFP4; usually tight after KV. |
| `olmo-3` | verified-checkpoint | instruction | kaggle | `allenai/olmo` | easy | Ai2 official OLMo family. Prefer this over danbth community 7B. |
| `granite-4.1` | verified-checkpoint | safety | kaggle | `ibm-research/granite-4.0` | easy | IBM official Granite 4.0 family on Kaggle. |
| `gemma-4-31b` | verified-checkpoint | instruction | kaggle | `google/gemma-4` | tight | Google official Gemma 4 family (47 inst). Q4 only; often too big after KV. |
| `devstral-small-2` | verified-checkpoint | coding | kaggle | `mistral-ai/devstral-small-2507` | tight | Mistral official Devstral Small. |
| `mistral-small-3.1` | verified-checkpoint | multilingual | kaggle | `mistral-ai/mistral-small-24b` | tight | Mistral official Small 24B. |
| `qwen3.6-27b` | verified-checkpoint | multilingual | modelscope | `Qwen/Qwen3.6-27B` | no | Official MS. ~15×3.9GB. Card on disk. Not a T4 job. Hosted/API when credits return. |
| `apertus-70b` | verified-checkpoint | multilingual | modelscope | `swiss-ai/Apertus-70B-Instruct-2509` | no | Official Swiss AI. Card on disk. HF★ wave-1. 30 shards. Not a T4 job. History still SHOP not gift. |
| `glm-5.2` | verified-checkpoint | reasoning | modelscope | `ZhipuAI/GLM-5.2` | no | Official Zhipu. 282 shards. HF★ wave-1. Hosted only. Sibling of unreleased 5.5. |
| `kimi-k3` | verified-api | planning | hf-api | `moonshotai/Kimi-K3` | no | HF★ wave-1 then 402. Kaggle helium990/kimi-k3 is QUARANTINED community. |
| `falcon-h1r-7b` | community-quarantine | math | kaggle | `manojkumarcs28/falcon-h1r-series` | easy | Community Falcon H1R series. Inspect config/safetensors; trust_remote_code=False. |
| `deepseek-v4-pro` | logical-emulated | coding | hf-api | `deepseek-ai/DeepSeek-V4-Pro` | no | Router listed; later 402. No local shards. Emulate via coding adapter + cache. |
| `deepseek-v4-flash` | logical-emulated | coding | none | `—` | no | Do NOT substitute R1-Distill-1.5B. Emulate via efficient-coding adapter. |
| `qwen3-235b` | logical-emulated | reasoning | kaggle | `qwen-lm/qwen-3` | no | Family listing only. Seat uses Qwen-style prompt + 3B/7B adapter. |
| `llama-5` | logical-emulated | safety | none | `—` | no | No official Llama 5 on Kaggle (only metaresearch/llama-3). Safety prompt + adapter. |
| `llama-4-scout` | logical-emulated | long-doc | hf-api | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | no | Router listed earlier. No official Kaggle Llama 4. Emulate long-doc. |
| `llama-4-maverick` | logical-emulated | critique | none | `—` | no | No official Kaggle Llama 4. Emulate via reasoning adapter. |
| `minimax-m3` | logical-emulated | coding | none | `—` | no | No verified artifact here. |
| `nemotron-3-ultra` | logical-emulated | coding | none | `—` | no | No verified artifact here. |
| `hunyuan-hy3` | logical-emulated | instruction | none | `—` | no | No verified artifact here. Capability-per-GB is a prompt + cost table, not a 295B download. |
| `gpt-oss-120b` | community-quarantine | coding | kaggle | `danielhanchen/gpt-oss-120b` | no | Unsloth community listing. Quarantine until files/license checked. Too big for T4. |
| `mistral-large-3` | logical-emulated | extraction | none | `—` | no | Small/Devstral official, not Large 3. |
| `kimi-k2-code` | logical-emulated | tools | none | `—` | no | No verified local artifact. |
| `step-3.7-flash` | logical-emulated | coding | none | `—` | no | No verified artifact here. |
| `command-a-plus` | logical-emulated | retrieval | none | `—` | no | RAG/citation seat. Implement with retrieval + 3B/7B, not a 218B download. |
| `muse-glimmer` | logical-emulated | creative | none | `—` | no | Open Muse persona. Teacher Spark is closed. |
| `inkling` | logical-emulated | planning | none | `—` | no | No local 975B. Effort-dial is a prompt/decoding setting on a small base. |
| `laguna-xs-2.1` | logical-emulated | tools | none | `—` | easy | Claimed 3B-active coder. No verified files here. Emulate agentic-coding adapter. |
| `k-exaone-2.0` | logical-emulated | long-doc | none | `—` | no | Long-doc sovereign seat. No local 750B. |
| `qwen-3.8-max` | verified-api | tools | hf-api | `Qwen/Qwen3.8-2.4T-A95B` | no | Router listed; 402. Not downloadable here. Teacher/judge only when credits return. |
| `mellum-2` | logical-emulated | coding | none | `—` | easy | Focal IDE model. No verified files here. Coding adapter. |
| `devstral-2` | logical-emulated | coding | none | `—` | no | Use official Devstral Small as the runnable cousin, not as this seat. |
| `apriel-15b-thinker` | logical-emulated | math | none | `—` | tight | No verified local files. Math/reasoning adapter on 3B/7B. |
| `kat-dev-72b` | logical-emulated | coding | none | `—` | no | NOT a Qwen. ByteDance on Qwen2.5 base. No local 72B. |
| `liquid-lfm2.5` | logical-emulated | tools | none | `—` | easy | On-device claim. No verified files here. Not mini-lfm. |
| `inkling-small` | logical-emulated | coding | none | `—` | no | No local 276B. Student-vs-teacher card is a study, not a download. |
| `mimo-v2.5-pro` | logical-emulated | creative | none | `—` | no | No local 1T. |
| `glm-5.5` | logical-emulated | critique | none | `—` | no | UNRELEASED. Day-1 eval pack only. No invented scores. Rumor-talk → sole eviction. |
| `qwen3.5-397b` | logical-emulated | multilingual | kaggle | `qwen-lm/qwen-3` | no | Family listing. Nex-N2-Pro merge still rejected. |
| `kimi-k2.7-code` | logical-emulated | tools | none | `—` | no | Router listed K2.7 earlier. No local files. |
| `a-x-k2` | logical-emulated | math | none | `—` | no | No verified artifact here. |
| `qwen3-next-80b` | logical-emulated | coding | kaggle | `qwen-lm/qwen-3` | no | Family listing. Throughput seat = decoding settings, not 80B download. |
| `muse-spark` | logical-emulated | critique | substrate | `—` | no | CLOSED teacher. Abstain. mini-lfm substrate if a voice is required. |
| `gp-hall-of-fame` | logical-emulated | critique | substrate | `—` | no | Gene-pool badge. Not an external checkpoint. |
| `gp-titan` | logical-emulated | planning | substrate | `—` | no | Gene-pool. King's-gift lab. Not a checkpoint. |
| `gp-grove` | logical-emulated | instruction | substrate | `—` | no | Gene-pool. Not a checkpoint. |
| `gp-sprout` | logical-emulated | instruction | substrate | `—` | no | Gene-pool. Not a checkpoint. |
| `gp-seedling` | logical-emulated | instruction | substrate | `—` | no | Gene-pool. Not a checkpoint. |
| `gp-sequoiadendron` | logical-emulated | critique | substrate | `—` | no | DNA-track apex. Not a checkpoint. |
| `gp-redwood` | logical-emulated | coding | substrate | `—` | no | Gene-pool. Not a checkpoint. |
| `gp-sapling` | logical-emulated | instruction | substrate | `—` | no | Gene-pool. Not a checkpoint. |
| `gp-acorn` | logical-emulated | safety | substrate | `—` | no | Consent ledger. Not a checkpoint. |
| `mini-llm` | verified-checkpoint | instruction | substrate | `mini_llm.py` | easy | Char-bigram substrate. Always on. Stood down as decider. |
| `mini-lfm` | verified-checkpoint | extraction | substrate | `mini_lfm.py` | easy | Naive-Bayes fact recall. Always on. Stood down as decider. |

## Honesty

- This sandbox: no GPU, no torch. Offline Qwen2.5-0.5B is a file, not a running model.
- HF token absent; last live wave ended **402 credits depleted**.
- Kaggle KGAT catalogs; shard download needs a Kaggle runtime.
- Apertus lineage remains a **10 USD/node shop**, not a free tree.
- GLM 5.5 stays unreleased. Muse Spark stays closed.

