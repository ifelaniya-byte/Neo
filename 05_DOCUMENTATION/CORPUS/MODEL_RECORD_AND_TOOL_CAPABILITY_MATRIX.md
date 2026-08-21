# Model Record and Tool Capability Matrix

This file is the operational index for the model-record corpus. It is deliberately conservative: a capability is marked as demonstrated only when the corpus contains an execution or inspection record supporting it.

| Record | Corpus role | Strongest demonstrated contribution | Main verification warning |
|---|---|---|---|
| Claude | critic / auditor / implementer | deep source inspection, architecture critique, test-driven correction, GPU/Kaggle workflows, model/system integration review | frequently corrected earlier overclaims; historical claims still require current reproduction |
| Devin | implementation engineer | archive comparison, concrete integration work, configuration/dependency edits, pipeline construction | proposed integrations sometimes began from stubs and needed real runtime verification |
| Grok | broad explorer | candidate discovery, architecture brainstorming, Kaggle/Omega/model-routing exploration | several provider/model claims were later corrected; raw transcript is huge and heterogeneous |
| Qwen | artifact builder / math experimenter | Mathematical Language Atlas, SPICE, SQLite/FTS compiler artifacts, code generation | transcript contains copy/paste mistakes and generated claims; preserve execution results separately from prose |
| Perplexity | research/world-model designer | world-model architecture, orthogonal subsystem design, GPU/Kaggle deployment concepts | numerical "power multiplier" claims are hypotheses unless experimentally reproduced |
| LMArena / GPT corpus | comparative model interaction | model comparisons, benchmark context, broad design sessions, Kaggle debugging | raw session archive is not a normalized benchmark database |
| OmniRoute analysis | provider/model researcher | free-model taxonomy, capability-aware routing, provider corrections | free/catalog status changes; live-test before dependency |

## Demonstrated tool classes

### Repository and code

- GitHub repository inspection/search.
- Branch/commit/PR workflows.
- Python execution.
- Node syntax checking.
- AST inspection.
- TypeScript compilation.
- Vite production builds.
- ZIP validation.
- Dependency-graph construction.
- Full-file and multi-file source review.

### Data and knowledge

- SQLite.
- SQLite FTS5.
- JSON/JSONL.
- Structured ledgers.
- Provenance markers.
- Formula/equivalence/dependency graphs.
- Retrieval indexes.
- Model metadata manifests.

### Mathematics

- SymPy-backed algebra.
- Equation solving.
- Derivatives/integrals.
- Matrix operations.
- primality/factorization.
- propositional satisfiability/truth tables.
- notation detection.
- LaTeX/Unicode parsing, with known detector edge cases.

### AI/model execution

- OpenRouter inference/routing.
- Local GGUF workflows.
- llama.cpp-style CPU inference.
- PyTorch training/inference.
- CUDA execution.
- ONNX Runtime.
- YOLOv8 inference.
- Tesseract.js OCR.
- model councils/ensembles as experimental orchestration.

### Cloud/GPU

- Kaggle kernel metadata construction.
- Kaggle CLI push/poll/output retrieval.
- GPU-enabled Kaggle jobs.
- CUDA device detection.
- multi-GPU threaded workload experiments.
- checkpointed experiment ledgers.

### Engineering infrastructure

- Champion/challenger evaluation.
- multi-run benchmarks.
- deterministic-output checks.
- static policy gates.
- compile gates.
- regression gates.
- canary/shadow concepts.
- rollback histories.
- filesystem watchers.
- file-stability detection.
- atomic job claiming.
- SQLite-backed state machines.
- FFmpeg compression.
- chunked/resumable uploads.
- retries and exponential backoff.

## Capabilities explicitly NOT established by the corpus

- frontier-level learned reasoning merely from orchestration code;
- semantic embeddings from hash vectors;
- complete world models without trained dynamics and data;
- autonomous planning merely from keyword/template planners;
- genuine causal discovery without appropriate data/assumptions;
- superintelligence;
- oracle access from symbolic notation;
- self-awareness from generated narratives;
- unlimited cloud GPU access;
- model catalog claims without live API testing;
- integration merely because a module exists in the repository.

## Capability test contract

For any future capability claim, record:

```text
CAPABILITY
  -> source record
  -> source implementation
  -> dependency availability
  -> test
  -> runtime observation
  -> failure behavior
  -> reproducibility
  -> current status
```

If any required evidence is absent, use `UNVERIFIED`, `PARTIAL`, or `EXPERIMENTAL` rather than upgrading the claim.

## Model-to-engineering loop

```text
MODEL RECORDS
      |
      v
candidate ideas
      |
      +----------------+
      |                |
      v                v
STATIONARY       NON-STATIONARY
ENGINEER         ENGINEER
      |                |
      +-------+--------+
              v
        candidate design
              |
              v
        implementation
              |
              v
       executable tests
              |
              v
         runtime evidence
              |
              v
       promotion decision
```

The model records provide breadth. The engineers provide independent analysis. The executable system provides the final evidence.
