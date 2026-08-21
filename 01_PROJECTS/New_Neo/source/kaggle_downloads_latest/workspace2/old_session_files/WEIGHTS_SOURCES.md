# Weight sources — ModelScope first, HF offline, no cache

HF token is **not** used unless `WEIGHTS_ALLOW_HF_TOKEN=1`.
HF Hub is forced **offline**. No `~/.cache/huggingface`.

- Date: 2026-08-13 16:30:52
- HF_HUB_OFFLINE: `1`
- HF_TOKEN in env: `False`
- ModelScope: **up**
- Kaggle: API `404` — Kaggle API HTTP 404 without kaggle.json. HTML catalog at kaggle.com/models loads; weight download needs a Kaggle token.

## Pulled from ModelScope: Qwen/Qwen2.5-0.5B-Instruct

- `config.json` — 659 bytes — downloaded
- `generation_config.json` — 242 bytes — downloaded
- `tokenizer_config.json` — 7305 bytes — downloaded
- `LICENSE` — 11343 bytes — downloaded
- `README.md` — 4917 bytes — downloaded
- `model.safetensors` — 988097824 bytes — downloaded

## Cards only (no multi-GB shards)

- **qwen3.6-27b** `Qwen/Qwen3.6-27B` listed 29 files
  - `config.json` 4308 B
  - `LICENSE` 11343 B
  - `generation_config.json` 202 B
- **phi-4** `LLM-Research/Phi-4` listed 22 files
  - `config.json` 802 B
  - `LICENSE` 1105 B
  - `generation_config.json` 184 B

## Honesty

- No torch / no GPU here. A `.safetensors` on disk is not a running model.
- Phi-4 and Qwen3.6-27B shards are multi-GB — cards only.
- Kaggle weight download needs `~/.kaggle/kaggle.json` (not present).
- HF Inference Providers stay unused until credits reappear.


## Extra ModelScope cards (no shards)

- **glm-5.2** `ZhipuAI/GLM-5.2` listed 297 · shards 282
  - `config.json` 3732 B
  - `LICENSE` 1065 B
  - `generation_config.json` 194 B
- **apertus-70b** `swiss-ai/Apertus-70B-Instruct-2509` listed 44 · shards 30
  - `config.json` 901 B
  - `generation_config.json` 126 B
- **gpt-oss-20b** `openai-mirror/gpt-oss-20b` listed 21 · shards 4
  - `config.json` 1806 B
  - `LICENSE` 11357 B
  - `generation_config.json` 177 B
