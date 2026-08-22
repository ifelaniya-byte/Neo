# Kaggle T4 — first (and only) GPU objective

**ACORN_RULE** still applies. This is **one model**, **FP16**, **smoke-v2 (60)**, **one account**.

This Arena sandbox has **no GPU**. You run these steps on kaggle.com.

Do **not** start QLoRA. Do **not** load a second model. Prefer **Internet OFF** once the Dataset is attached.

CUSD is **136**, not 120. It is not money.

---

## Files to upload (`kaggle_pack/`)

| File | Why |
|---|---|
| `artifact_gate.py` | Re-hash + tokenizer offline-safe check |
| `worker_entry.py` | Isolated FP16 worker, exit 1 on fail |
| `smoke_scorer.py` | Decimal / exact / heuristic safety |
| `datasets/smoke-v2.jsonl` | Immutable 60-item bench |
| `datasets/smoke-v2.manifest.json` | sha256 `d880d026bbc799847774506043cfb44c6c0ce4846384393412e6f6e273d34bee` |
| `registry/qwen25_05b_manifest.json` | Local file pins |
| `00_cpu_preflight.ipynb` | CPU only |
| `01` = repo `kaggle_worker_template.ipynb` | GPU after preflight |

Also upload the **9 Qwen files** as private Dataset `council-qwen05` if Apache-2.0 private storage is acceptable.

---

## Option B (preferred): persistent Dataset

1. Kaggle → Datasets → New Dataset → **private** → `council-qwen05`  
   Upload `weights_offline/modelscope/Qwen__Qwen2.5-0.5B-Instruct/` (all 9 files). No tokens.
2. Code → New Notebook → **Accelerator = None** → Add Input: `council-qwen05` + this pack.
3. Run `00_cpu_preflight.ipynb`. Required: gate rc 0, config+tokenizer load, 60-item validate.
4. Duplicate notebook or new GPU notebook. **Accelerator = GPU T4**. **Internet OFF**. Same inputs.
5. First GPU cell: print `torch.cuda.is_available()` and save `environment.json` (no env dump).
6. One short single-prompt worker, then full smoke-v2 batch (`kaggle_worker_template.ipynb`).
7. Save Version as `qwen05-smoke-v2-fp16-run1`. Download outputs even if it fails.

## Option A (same session, Internet ON)

Only if you will not create a Dataset. Download ModelScope **and run the worker in the same session**. `/tmp` dies when the session dies. Still run artifact_gate on the downloaded dir. Still use **smoke-v2**, not smoke_v1.

---

## Success (run 1)

```
environment.json
worker_request.json
worker_result.json   ok=true  mode=benchmark  attempted=60  written=60
predictions.jsonl    60 lines
evaluation.json
run_report.json
completion.marker
process return code 0
```

Run 2 in a **fresh** session before anyone says runtime-verified.

## Stop

Hash mismatch · tokenizer/config load fail · remote code · missing scorer · second model · QLoRA · ngrok · tokens in cells · public Dataset without license review.
