# Every seated model — offline files vs live tokens

**As of 2026-08-13 (this sandbox). KP-14.**  
HF token is **not** on disk. Kaggle KGAT **is** on disk (HTTP 200). ModelScope is up **without** any token.

45 names are **logical expert seats**. A catalog HTTP 200 is a listing, not authenticity.

| Channel | Status now | What it can do |
|---|---|---|
| **ModelScope** (no token) | **UP** | Pull cards + small weights. 988 MB Qwen2.5-0.5B-Instruct offline. |
| **Kaggle** (`~/.kaggle/access_token`) | **ACTIVE 200** | Catalog / list instances. Shard download needs a Kaggle runtime. |
| **Hugging Face router** | **NO TOKEN** (last live use: 200 then **402**) | Do not call until credits return. `WEIGHTS_ALLOW_HF_TOKEN=1` only then. |
| **This box GPU / torch** | **NONE** | A `.safetensors` on disk is not a running model. |

HF Hub is forced **offline + no-cache**. Multi-account Kaggle farming is **not** implemented.

Legend  
- **W** = full weight file on disk here  
- **C** = config/license card on disk here  
- **MS / KG / HF★ / HF·** = same as before  
- **status** = KP-14 label (`verified-checkpoint` / `verified-api` / `community-quarantine` / `logical-emulated`)

See `SEAT_REGISTRY.md` and `mapping.json` for the full table (domain, backend, T4 fit, note).

## What is actually usable right now

**Offline, no token**
- One real checkpoint file: Qwen2.5-0.5B-Instruct (cannot *run* it here)
- Cards for GLM 5.2, Phi-4, Qwen 3.6 27B, Apertus 70B, gpt-oss-20b

**Online, Kaggle token active**
- Browse official families (Gemma 4, Qwen-3, Granite 4.0, SmolLM3, Devstral Small, Mistral Small)
- Upload `kaggle_00_environment_check.ipynb` then `kaggle_worker_template.ipynb` on a **single** T4
- T4 will **not** load Kimi K3 / Qwen-Max / Apertus 70B / GLM 5.2

**Online, HF token**
- Not present. Last state: wave 1 real answers from Phi-4, Apertus 70B, GLM 5.2, Kimi K3; then **402**

**Never callable as claimed weights**
- GLM 5.5 (unreleased)  
- Muse Spark (closed)  
- Gene-pool nine  
- Community mirrors until quarantined files are verified (`trust_remote_code=False`)

## Rejected this pass (KP-14)

- 45 full checkpoints on one account  
- helium990/kimi-k3 as official Kimi K3  
- R1-Distill-1.5B as DeepSeek V4 Flash  
- keras/smollm3 as a ModelScope id  
- Dual-T4 70B as a normal weekly job  
- Always-on Ollama + ngrok  
- 3 accounts × 30 GPU hours (TOS)  
- `CMAKE_ARGS=-GGUIDE=OFF` (typo; not shipped)
