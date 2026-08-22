# Patch notes — added on top of council-20260813-r003

Not a numbered council release. No updated CURRENT_STATE.json, no re-signed
manifest, no new REDACTED_SNAPSHOT. r003 source tree plus two files.

## Added
- `kaggle_pack/20_export_gguf.ipynb` — converts the verified Qwen2.5-0.5B
  checkpoint to GGUF and quantizes to Q4_K_M on Kaggle, gated on artifact_gate
  passing and a real FP16 GPU run report existing. Records the llama.cpp
  commit and file hashes it actually produces (git rev-parse after clone,
  never hardcoded).
- `tools/llama_cpp_local_smoke.py` (v3) — runs the quantized GGUF locally
  through llama-cpp-python, no GPU, writes an ingest_results.py-compatible
  run report.

## v3 changes (this round)
A second review caught that `validate_gguf()` raised `SystemExit`, which
`except Exception` in main() cannot catch (SystemExit inherits from
BaseException, not Exception — confirmed with a standalone repro before
fixing). The `finally` block still ran and wrote *a* report, but it was a
bare placeholder with none of the actual validation error. Fixed by raising
a plain `ArtifactValidationError(RuntimeError)` instead. Also added: stale
predictions.jsonl/markers are now cleared before validation (not after —
otherwise a validation failure could leave last run's predictions sitting
next to this run's failure report), completion.marker/failure.marker are
written (mutually exclusive), and basic environment info (python version,
platform, cpu count) is recorded for reproducibility.

Verified against a mocked llama_cpp module: model-load failure, a
validation failure (nonexistent GGUF — this is the specific case the v2
bug affected), and a full success path. All three produce correct reports,
correct markers, and correct exit codes. Not yet run against a real GGUF —
no network/GPU access in this environment.

## Verified before packaging
- The repo's own 18/18 unit test suite (`tests/unit`) passes unchanged with
  both files present.

## Still true / unchanged from r003
- Zero real model tensors present. `COUNCIL_MODEL_DIR` still absent.
- No Kaggle GPU run has actually happened yet.
- Nothing here is promoted into CURRENT_STATE.json. That happens only after
  real Phase 0 evidence is staged via tools/ingest_results.py.

## Known remaining gaps (not fixed this round, noted for later)
- GGUF manifest lookup only supports the `files: {name: {...}}` dict shape
  the export notebook actually writes — not the `outputs: [...]` list shape
  discussed in an earlier draft that this notebook doesn't produce. If the
  export notebook's manifest format ever changes, this needs updating too.
- Per-item failure records aren't separately persisted beyond the aggregate
  failure count — predictions.jsonl only carries id+completion (that's the
  ingest_results.py contract); a fuller per-item error log would need a
  second file.
