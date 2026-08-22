# Atlas Shadow Unified — Clean Package

**Primary entry point:** `atlas_shadow_unified.py`

This is a consolidated symbolic reasoning / self-verification architecture.
It is **not** a trained LLM and not AGI. It is a structured Python system that
combines:

- Knowledge pod with novelty filtering
- Sympy math engine + propositional logic
- Code-language detector
- Mathematical Language Atlas with cryptographic “shadow seals”
- Tool registry + planner + router + agent
- Tiny optional neural predictor (falls back to linear least-squares without torch)
- Staged reasoning pipeline + reflective loop
- Hard integrity gates and a self-certification harness

## Honest limits

- Symbolic / control-flow architecture only
- No frontier language model inside
- No real-world scientific discovery claims
- Translation remains a stub
- Exhaustive combinatorial tool tables are deliberately bounded

## Quick start

```bash
# Optional but recommended
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install sympy torch    # torch is optional; system falls back cleanly without it

# Run the primary demo
python atlas_shadow_unified.py

# Run the built-in certification harness
python certify_system.py

# Run the independent external test suite
python tests_independent.py
```

## Package layout (cleaned)

| File | Role |
|------|------|
| `atlas_shadow_unified.py` | **Primary** – full system |
| `certify_system.py` | Built-in certification harness |
| `tests_independent.py` | Independent external tests (this suite) |
| `recursive_optimizer.py` | Telemetry / candidate evaluation helper |
| `shadow_alphabet.py` / `shadow_alphabet_engine.py` | Supporting modules |
| `unified_orchestrator.py` + other `orchestrator_*.py` | Historical iterative variants (kept for reference; primary is atlas_shadow_unified) |
| `FINAL_CERTIFICATION.md` | Last known clean certification report |
| `README_SECRET_ZIP.txt` | Original package notes |

## What “certification” means here

`certify_system.py` runs a series of local gates:

- All Python files compile
- SourceEngineer AST audit passes
- SuperMathCodingGate (symbolic math + logic + code checks)
- Stationary full verification of formula seals
- Staged reasoning pipeline
- Reflective loop
- Intentional corruption + reseal recovery
- Telemetry single-invocation invariant

A clean run ends with `"all_ok": true`.

The independent suite in `tests_independent.py` asserts on concrete values
(roots of equations, ranking of retrieval, actual corruption detection, etc.)
so it is harder for a self-reported flag to hide a real bug.

## Requirements

- Python 3.10+
- `sympy` (required for full math surface)
- `torch` (optional – predictor falls back to linear least-squares)

## License / use

Provided as-is for study and extension. Treat the grandiose framing in some
of the older variant files as historical; the primary script and this README
are the authoritative description of capability.
