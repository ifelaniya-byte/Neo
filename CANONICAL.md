# Canonical source vs distribution

## Policy (Fix A — adopted)

| Role | What | Edit? |
|------|------|-------|
| **Canonical** | Multi-file package under this directory (`engineers.py`, `pipeline.py`, `megacompact16/`, `adapters/`, `ci/`, …) | **YES — only place humans edit** |
| **Distribution** | `megacompact_condensed_spine.py`, `megacompact_condensed_engine.py` | **NO — generated only** |

```bash
# After editing modules:
python build_condense.py
# Optional smoke:
python megacompact_condensed_spine.py adversarial
```

- Condensed files start with `GENERATED — DO NOT EDIT`.
- Full integrations package remains the product surface (CI, schemas, pipeline, PRODUCT.md).
- Roles stay separate: full = develop; condensed = optional drop after build.
- Speed and product work target the **full** tree; regenerate condensed afterward.

## Rejected

- Hand-editing the ~6k-line condensed spine as primary source
- Dropping double-pass to “simplify”
