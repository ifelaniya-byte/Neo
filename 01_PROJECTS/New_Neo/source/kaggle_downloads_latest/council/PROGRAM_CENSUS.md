# KP-16 program census

ACORN_RULE: spoken co-signs beat disapproves; hold-peace is not consent.
Technical gates still override popularity.

- Date: 2026-08-13 19:34:29
- Payload files: **99**
- Project payload: **12.87 MB**
- Operational footprint: **14.43 MB** (payload + caches/git/venv)
- Integrity: **True** []

## By class

| Class | Files | Logical |
|---|---:|---:|
| datasets | 3 | 0.04 MB |
| docs | 18 | 5.83 MB |
| json | 10 | 0.09 MB |
| logs | 6 | 6.32 MB |
| model-config | 10 | 0.01 MB |
| notebooks | 7 | 0.03 MB |
| other | 3 | 0.02 MB |
| source | 37 | 0.50 MB |
| weight-metadata | 5 | 0.03 MB |

## Weight tensors (actual)


## Largest 20

| Bytes | Class | Path |
|---:|---|---|
| 5454832 | docs | `council_dashboard.html` |
| 2570219 | logs | `council_log.json` |
| 2556674 | logs | `weight_history.json` |
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
| 22547 | source | `studies.py` |
| 21531 | source | `seat_registry.py` |
| 18802 | other | `registry/seats.yaml` |
| 13860 | datasets | `datasets/smoke-v2.jsonl` |

## Seats / USD

- seats: {'verified-checkpoint': 13, 'verified-api': 2, 'community-quarantine': 2, 'logical-emulated': 39, 'n': 56, 't4_easy': 9, 't4_tight': 6}
- usd: {'n_people': 56, 'n_renters': 56, 'global_minted': 136, 'global_available': 136, 'people_minted_sum': 136, 'people_available_sum': 136, 'escrow_locked': 0, 'unit': 'Council USD points — not redeemable US dollars'}

## Honesty

Council USD points are simulated ledger units, not redeemable dollars. This sandbox has no GPU/torch/transformers. The expected Qwen2.5-0.5B tensor is absent from this recovered source tree; offline loading is unproven. No adapter is trained and no GPU run report is present.

