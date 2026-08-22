# KP-16 program census

ACORN_RULE: spoken co-signs beat disapproves; hold-peace is not consent.
Technical gates still override popularity.

- Date: 2026-08-13 18:03:07
- Payload files: **85**
- Project payload: **1012.38 MB**
- Operational footprint: **1012.43 MB** (payload + caches/git/venv)
- Integrity: **True** []

## By class

| Class | Files | Logical |
|---|---:|---:|
| datasets | 2 | 0.03 MB |
| docs | 13 | 5.81 MB |
| json | 7 | 0.09 MB |
| logs | 5 | 6.32 MB |
| model-config | 16 | 11.50 MB |
| notebooks | 4 | 0.01 MB |
| other | 2 | 0.02 MB |
| source | 28 | 0.46 MB |
| weight-metadata | 7 | 0.04 MB |
| weight-tensors | 1 | 988.10 MB |

## Weight tensors (actual)

- `weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/model.safetensors` — 988097824 bytes

## Largest 20

| Bytes | Class | Path |
|---:|---|---|
| 988097824 | weight-tensors | `weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/model.safetensors` |
| 7031645 | model-config | `weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/tokenizer.json` |
| 5454832 | docs | `council_dashboard.html` |
| 2776833 | model-config | `weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/vocab.json` |
| 2570219 | logs | `council_log.json` |
| 2556674 | logs | `weight_history.json` |
| 1671839 | model-config | `weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/merges.txt` |
| 1120413 | logs | `usd_ledger.json` |
| 217577 | docs | `kings_word.md` |
| 100400 | source | `model_council.py` |
| 76819 | docs | `weight_lineage.md` |
| 66158 | source | `kings_pass.py` |
| 65258 | logs | `usd_people.json` |
| 57966 | source | `weight_lineage.py` |
| 40153 | source | `usd_housing.py` |
| 37430 | source | `weights_meta.py` |
| 33044 | json | `weights_metadata.json` |
| 25234 | json | `registry/seats.json` |
| 24479 | json | `mapping.json` |
| 23074 | docs | `weights_metadata.md` |

## Seats / USD

- seats: {'verified-checkpoint': 13, 'verified-api': 2, 'community-quarantine': 2, 'logical-emulated': 39, 'n': 56, 't4_easy': 9, 't4_tight': 6}
- usd: {'n_people': 56, 'n_renters': 56, 'global_minted': 136, 'global_available': 136, 'people_minted_sum': 136, 'people_available_sum': 136, 'escrow_locked': 0, 'unit': 'Council USD points — not redeemable US dollars'}

## Honesty

Council USD points are simulated ledger units, not redeemable dollars. This sandbox has no GPU/torch/transformers. Qwen2.5-0.5B files are complete on disk; offline load is unproven here. HF token absent. Kaggle token present (not printed). No adapter trained. No GPU run_report yet.

