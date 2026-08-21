# Neo Full Corpus Reconstruction

**Date:** 2026-08-21
**Status:** RECONSTRUCTED FROM THE REPOSITORY CORPUS
**Purpose:** Provide a single synopsis of the model records, engineering conversations, tool capabilities, architectural discoveries, and epistemic rules that must remain in context when working on Neo/SROS.

## 1. Scope and completeness

This document reconstructs the **chat material that is actually present in the Neo repository**, especially the `05_DOCUMENTATION/AI_Models/` corpus and the related architecture/system records.

It does **not** claim access to private chat histories that are not stored in Neo. The model records themselves contain historical chat transcripts, pasted prompts, tool traces, code reviews, experiments, and conclusions. They are the available historical corpus.

The current `AI_Models` directory contains seven records:

1. `Claude_Assessment.txt` — ~191 KB
2. `Devin_Info.txt` — ~6.6 KB
3. `Grok_Review.txt` — ~1.69 MB
4. `LMArena_Benchmarks.txt` — ~827 KB
5. `OmniRoute_Analysis.txt` — ~52 KB
6. `Perplexity_Capabilities.txt` — ~140 KB
7. `QWEN_Models.txt` — ~312 KB

There is **no standalone GPT/ChatGPT file currently present**. GPT/ChatGPT material is embedded in the broader LMArena/model conversation corpus and other records. Do not invent a missing standalone record.

The raw files remain authoritative historical evidence. This document is a reconstruction/synthesis layer and must not replace the originals.

---

# 2. Program identity reconstructed from the corpus

Neo has accumulated several apparently different projects, but the current organizing intent is:

```text
                         NEO ENGINEERING SYSTEM
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
     MODEL RECORDS           WORLD MODELS           ENGINEERING
          |                       |                       |
   Claude / Grok /          UAIR / world          Stationary
   Devin / Qwen /           simulation            Engineer
   Perplexity /             state models          Non-Stationary
   LMArena / etc.                                  Engineer
          |                       |                       |
          +-----------------------+-----------------------+
                                  |
                                  v
                  STATE RESOLUTIONS OPERATION SOLVER
                                  |
                       validated resolution
```

The engineers are therefore **members of a larger engineering system**, not two isolated LLM calls.

SROS is the current primary program architecture. Its contract accepts state, objective, constraints, available operations, evaluation criteria, optional transition model, and evidence; it returns a regime, resolution, assumptions, transition prediction, validation, confidence/fitness, and unresolved risks.

---

# 3. Historical model-record synopsis

## 3.1 Claude corpus

Claude's record is the largest and most technically corrective corpus. It repeatedly performs a useful pattern:

**read code -> inspect implementation -> test claims -> identify mismatch -> distinguish documented intent from executable reality -> patch only what is supported -> re-test.**

Major themes:

### A. Symbolic mathematics and ACADIAR

Claude strongly separated:

- symbolic representation;
- executable computation;
- oracle-relative computation;
- non-computable mathematical objects.

The resulting rule is important for Neo: **a symbolic label is not a new computational capability**. A Python object naming a higher ordinal does not compute with that ordinal. Such representations can still be valuable as bookkeeping, provenance, guards, or educational structures.

### B. OmniRoute / DeepSeek coding-agent system

Claude inspected the OmniRoute archives and found that the more complete archive fixed a syntax error in `openrouter.js`, added a mock provider, added execution-proof recording, and added `better-sqlite3`.

The stronger archive was still not production-complete. The record identified:

- OpenRouter HTTP 402 prevented live-model validation;
- planner performance was substantially weaker than isolated memory/routing/tools/critic components;
- streaming was unimplemented;
- the local embedding provider was not semantic embedding retrieval;
- cost tracking was placeholder logic;
- the React frontend was essentially a scaffold;
- Windows-built SQLite binaries required rebuild on other OSes;
- a large portion of the adversarial test suite consisted of placeholders that could not fail.

This is one of the strongest examples in the corpus of why **"verified" must mean executed/asserted, not merely traced by reading**.

### C. Recursive optimization / Champion-Challenger architecture

The corpus developed a much stronger replacement for direct self-modification:

```text
Observe
  -> Diagnose
  -> Hypothesize
  -> Generate candidates
  -> Sandbox
  -> Compile
  -> Test
  -> Property / behavioral / security checks
  -> Stationary verification
  -> Multi-run benchmark
  -> Canary / shadow evaluation
  -> Promotion gate
  -> Promote or rollback
  -> Post-verify
  -> Telemetry
  -> Next challenger
```

The key contract became conceptually:

```text
Promote(C) =
    Correct(C)
    AND Stationary(C)
    AND Improvement(C)
    AND RegressionOK(C)
    AND Reproducible(C)
```

rather than simply promoting a candidate because its measured fitness was higher.

The record explicitly rejects fabricated memory/error measurements, single-run benchmarking, arbitrary raw metric combinations, and direct hot-swapping.

### D. Model-lineage / evolutionary learning

Claude developed a model-lineage idea in which versions of Qwen, Llama, Phi, etc. are represented as explicit trajectories:

```text
family -> versions -> deltas -> performance -> breakthroughs -> stagnation -> patterns
```

The proposed system loads historical variants, evaluates them, identifies evolution deltas, compares apex versions, extracts repeated improvement patterns, and uses a meta-model to recommend future experiments.

This is valuable as an **experimental methodology**, but historical lineage metrics must be treated as unverified unless the actual model files, datasets, evaluation procedure, and results exist.

### E. GPU / training infrastructure

The Claude corpus includes real PyTorch GPU experiments and Kaggle bridge work. It distinguishes actual learned PyTorch components from hand-written pseudo-learning.

It also makes an important hardware distinction:

- tensor/matrix units perform the matrix arithmetic and determine feasible throughput;
- precision mode can directly change representational precision;
- VRAM/HBM constrains what model/batch can fit;
- NVLink/InfiniBand enables multi-GPU scaling;
- CPU/RAM/storage mostly feed and stage computation;
- hardware does not have a fixed percentage contribution to final weight quality.

The corpus explicitly rejects inventing percentage attribution for hardware components when no empirical dataset establishes those percentages.

### F. Mathematical Language Atlas / SPICE

The corpus contains a real SQLite-backed mathematical atlas concept with:

- language forms;
- formulas;
- cross-language mappings;
- equivalences;
- dependencies;
- proof statuses;
- full-text search;
- detection of notation systems;
- rendering;
- compiler commands.

A recorded build reached 19/19 tests for a smaller Diamond Build, including language loading, formula loading, FTS, equivalence/dependency queries, and notation detection.

The record also caught real bugs:

- FTS staleness after inserts;
- tuple results silently disappearing in the printer;
- Unicode-only detectors failing on LaTeX commands;
- tensor LaTeX Greek subscripts being misclassified;
- `P(x)` causing probability/first-order-logic collisions.

These are excellent examples of the desired engineering method: **test the actual representation formats the system stores, not just the happy-path format used by the detector.**

### G. Vision / OmniVision-X / Fusion

The corpus includes real browser-side OCR and ONNX inference work. Tesseract.js OCR was tested on rendered text, and YOLOv8n ONNX inference was tested on a known COCO image.

It also caught a critical integration problem: a real saliency compressor and verification state machine existed in the repository but were not imported by the running pipeline. Documentation had overstated their status.

This establishes another core rule:

> **Dead code is not integrated capability.**

### H. Omniscient world model

The corpus proposes multi-scale dynamics, physics-informed constraints, causal discovery, graph representations, diffusion futures, inverse action inference, ensemble uncertainty, memory, hierarchical planning, latent geometry, information bottlenecks, contrastive learning, MPC, Bayesian uncertainty, sparse interaction networks, and multitask learning.

The later critique is more important than the earlier marketing-style numbers: multiplying theoretical "power gains" across paradigms is not empirical evidence. A stronger world model must be evaluated against a defined environment, dataset, baseline, held-out set, horizon, and failure criteria.

### I. Agent OS

The corpus contains a production-style shared-directory agent architecture using:

- filesystem watchers;
- file-stability detection;
- SQLite job state;
- atomic job claiming;
- validation;
- compression;
- chunking;
- resumable uploads;
- retries/backoff;
- worker pools;
- crash recovery.

This is a reusable pattern for an engineering execution substrate.

---

## 3.2 Devin corpus

Devin's record is shorter but strongly execution-oriented.

It inspected multiple Glimmer Foundry archives and distinguished:

- Muse Glimmer 30B integration;
- LoRA training;
- holdout promotion/rollback;
- deterministic text verification;
- safety guards;
- an E2B sandbox verifier stub;
- Groq teacher distillation;
- Hugging Face synchronization;
- model-selection/fusion logic.

It identified that the archives were **not actually one integrated pipeline**. In particular, the E2B verifier was a stub, the real code-execution verification path was missing, and the requested LFM model integration was absent.

The useful Devin capability pattern is:

```text
inspect files
-> compare archives
-> identify integration gaps
-> edit concrete files
-> update configuration
-> update dependencies
-> execute/check
```

This is an engineering/execution role, not merely a model-ranking role.

---

## 3.3 Grok corpus

`Grok_Review.txt` is the largest raw model transcript in the repository. The normal file renderer currently returns an empty parsed body, but the repository Git blob is populated; the blob contains a large chronological conversation corpus.

Themes visible in the recovered blob include:

- Kaggle kernel debugging;
- Omega/engine experiments;
- model rotation laboratories;
- 45-model/open-weight evaluation ideas;
- CPU/GPU execution;
- model benchmark optimization;
- free-model routing;
- local model deployment;
- PowerShell/GitHub workflows;
- model lineage/evolution concepts;
- SRO/SROS discussion;
- recursive optimization;
- agentic architectures;
- experiments involving cloned cognitive states.

Grok's most useful contribution to the model-selection corpus was broad candidate discovery, but later OmniRoute analysis corrected several of its claims. This demonstrates why Grok is an **input to verification**, not an authority.

---

## 3.4 LMArena corpus

`LMArena_Benchmarks.txt` is not a clean benchmark database. It is a large accumulated chat/session record containing model interactions, Kaggle debugging, SRO questions, architecture requests, benchmark discussions, and other historical work.

Treat it as:

**historical conversation evidence + benchmark context**, not as a normalized benchmark truth table.

Important themes include:

- Kaggle kernel versioning and stale notebook/script problems;
- open-weight model evaluation;
- model rotation experiments;
- benchmark optimization;
- SRO/SROS terminology;
- large-scale architecture brainstorming.

Any numeric result extracted from LMArena must retain its original experiment context and should be independently reproduced before becoming a current engineering metric.

---

## 3.5 Qwen corpus

`QWEN_Models.txt` is heavily oriented around the Mathematical Language Atlas and SPICE / Diamond Capsule Compiler work.

Key verified historical artifact:

- 30 language forms;
- 55 formulas;
- cross-language links;
- equivalences;
- dependencies;
- SQLite/FTS;
- notation detection;
- rendering;
- a 19/19 local test result.

It also introduced **SPICE — Single-Paste Ingest/Compile/Export**, a methodology for transferring a large chat-derived artifact to another LLM through one self-contained script.

The important architectural lesson is that a transfer capsule should be treated as a **serialized knowledge/artifact package**, not as proof that every claim inside the conversation was true.

---

## 3.6 Perplexity corpus

Perplexity's record focuses heavily on world-model design and dense knowledge representations.

The major architecture proposed was an Omniscient-style world model with:

- multi-scale temporal representation;
- physics-informed constraints;
- causal discovery;
- graph networks;
- generative future modeling;
- inverse action inference;
- ensemble uncertainty;
- memory-augmented learning.

A later, stronger formulation adds:

- schema/feature contracts;
- action-conditioned dynamics;
- probabilistic predictions;
- bootstrap ensembles;
- conformal calibration;
- change-point/regime detection;
- causal hypotheses;
- counterfactual simulation;
- retrieval memory;
- invariants/constraints;
- risk-sensitive MPC;
- abstention;
- continual evaluation.

The useful idea is the **closed-loop world-model architecture**. The numeric claims about 8-versus-16 paradigms are not automatically evidence and must be treated as hypotheses/targets unless reproduced.

---

## 3.7 OmniRoute analysis corpus

This is the model/provider capability record.

It makes a crucial distinction between:

- `$0` model pricing on a shared platform;
- a provider's free API tier;
- promotional or account-specific quotas;
- genuinely unlimited local inference.

The record identifies candidate free/low-cost models such as Nemotron, GPT-OSS, Qwen3-Coder, Nex-N2-Pro, North Mini Code, Laguna, Gemma, Gemini, and NVIDIA endpoints, while repeatedly emphasizing that catalog status must be **live API-tested** before routing depends on it.

The recommended architecture is capability-aware routing:

```text
request
  |
  +-- autocomplete -> fast model
  +-- simple coding -> fast/normal model
  +-- tool use -> tool-capable model
  +-- complex agent -> strongest available model
```

This is preferable to blindly cascading through a fixed list.

The record also recommends preserving a known-good path rather than allowing an agent to rewrite it merely because a new model appears stronger.

---

# 4. Cross-model consensus: what survives the corpus

Across the records, the most consistent engineering conclusions are:

## 4.1 Verification beats architectural rhetoric

A system that prints `SUCCESS` is not necessarily successful. A documentation table marked `VERIFIED` is not evidence unless the underlying test executes and asserts the requirement.

## 4.2 Models disagree usefully

Claude, Grok, Devin, Qwen, Perplexity, and LMArena-derived conversations frequently disagree. That disagreement should be preserved and used as an input to engineering verification.

## 4.3 Candidate generation and certification must be separate

An LLM/optimizer can propose a candidate. It should not be the sole authority that certifies its own modification.

## 4.4 Dynamic systems need dynamic validation

A stationary result is not automatically valid after the state changes. Non-stationary engineering needs transition evidence and should abstain when transition validation is unavailable.

## 4.5 More components do not automatically mean more intelligence

Adding paradigms, model versions, cells, modules, or symbolic layers can increase capability, but only measured task performance establishes an improvement.

## 4.6 Representation is not computation

Shadow alphabets, ordinal names, symbolic references, and ontological labels can be useful representations. They do not create the computation they represent.

## 4.7 Dead code is not a capability

A module existing in the repository is not equivalent to it being imported, reachable, executed, tested, and validated.

## 4.8 Honest failure is a feature

The strongest records repeatedly prefer:

```text
UNRESOLVED
UNAVAILABLE
UNVERIFIED
ABSTAIN
```

over a fabricated successful answer.

---

# 5. Reconstructed tool/capability map

The corpus demonstrates or proposes the following tool classes.

| Capability | Demonstrated in corpus | Correct interpretation |
|---|---|---|
| GitHub repository inspection | Yes | Read/search/diff/modify repository artifacts when connected |
| Git/GitHub publishing | Yes | Branches, commits, PRs, repository updates |
| Local code execution | Yes | Python/Node/scripts can be executed when runtime exists |
| Static syntax checks | Yes | `node --check`, AST parsing, compilation checks |
| Full-file code review | Yes | Can inspect large source sets and trace integration |
| SQLite | Yes | Databases, FTS5, ledgers, state machines |
| SymPy | Yes | Real symbolic algebra/logic capabilities when installed |
| PyTorch | Yes | Real learned-model/GPU experiments when compute is available |
| CUDA/GPU | Yes in recorded experiments | Requires an actual CUDA-capable runtime; not implied by documentation |
| Kaggle GPU | Yes in recorded workflows | Remote GPU execution through Kaggle tooling/CLI |
| Hugging Face model acquisition | Yes in recorded workflows | Download/model metadata workflows; hashes should be locally computed/pinned when needed |
| OpenRouter | Yes | Multi-provider/model inference and routing; live availability must be tested |
| NVIDIA endpoints | Candidate/partially verified | Account/quota/availability must be checked live |
| Gemini | Candidate/verified tier claims in record | Current pricing/availability must be rechecked before use |
| Ollama / LM Studio / vLLM | Proposed local inference layer | Hardware-bound, locally rate-limit-free inference |
| E2B | Proposed/partially implemented | Sandbox integration was identified as a gap in Glimmer Foundry |
| Groq | Teacher/speed specialist in records | Pricing/free status must be live-checked |
| ONNX Runtime | Demonstrated | Real neural inference pipeline possible without GPU |
| YOLOv8 | Demonstrated generic COCO inference | Not automatically a UI detector without UI-trained weights |
| Tesseract.js | Demonstrated | Real offline OCR |
| Vite/TypeScript build | Demonstrated | Browser build verification |
| Watchdog/filesystem watcher | Demonstrated/proposed | Shared-directory event ingestion |
| FFmpeg | Demonstrated/proposed | Media compression/transcoding |
| Chunked/resumable upload | Demonstrated in Agent OS design | State-backed upload recovery |
| Model lineage analysis | Designed | Requires real versioned weights and comparable evaluation |
| Model councils/ensembles | Designed/partially implemented | Consensus must use explicit aggregation rules |
| World-model prediction | Experimental | Requires real trained dynamics and held-out evaluation |
| Causal discovery | Experimental | Requires assumptions/interventions/data; not automatic causal truth |
| Autonomous planning | Partial in historical systems | Many "planner" implementations were keyword/template based rather than learned search |
| Semantic embeddings | Not established in some systems | A hash-based vector is not semantic embedding retrieval |
| Continual learning | Experimental | Requires actual training/update loop and drift evaluation |
| Autonomous self-modification | Experimental | Must be bounded by sandbox, tests, promotion gates, rollback |

---

# 6. GPU capability reconstruction

The model corpus establishes a realistic GPU pathway:

```text
Neo/SROS
   |
   +-- CPU control plane
   |     - orchestration
   |     - state management
   |     - verification
   |     - provenance
   |     - promotion/rollback
   |
   +-- GPU compute plane
         - model inference
         - world-model training
         - candidate evaluation
         - Monte Carlo / rollout workloads
         - PyTorch training
         - batch benchmarking
         - multi-model evaluation
```

Kaggle can provide remote GPU execution for experiments. Local GPU inference/training is constrained by the actual hardware and memory available.

The corpus specifically demonstrates a Kaggle bridge that can:

1. verify Kaggle credentials;
2. build a payload;
3. construct kernel metadata;
4. request a GPU accelerator;
5. push the kernel;
6. poll cloud status;
7. retrieve output ledgers.

The same corpus also shows why cloud claims must be tested: kernel metadata slug mismatches caused actual 400 errors, and the corrected title/id derivation fixed the push path.

---

# 7. Reconstructed SROS relationship

The corpus suggests the following final conceptual arrangement:

```text
                    FULL NEO CORPUS
                         |
          +--------------+--------------+
          |              |              |
      MODEL RECORDS   WORLD MODELS   EXECUTION SYSTEMS
          |              |              |
          +--------------+--------------+
                         |
                    EVIDENCE POOL
                         |
              +----------+----------+
              |                     |
       STATIONARY ENGINEER   NON-STATIONARY ENGINEER
              |                     |
              +----------+----------+
                         |
                  CANDIDATE SET
                         |
              ADVERSARIAL / CRITIC
                         |
                   VERIFICATION
                         |
               RESOLUTION EVALUATOR
                         |
                  PROMOTION GATE
                         |
                    SROS RESULT
                  /            \
             RESOLVED        ABSTAIN
```

The stationary engineer should establish correctness under fixed assumptions.

The non-stationary engineer should establish whether the resolution survives or adapts to state transition.

Neither engineer should be treated as an infallible oracle.

---

# 8. Model-record roles

The records can be assigned these roles without treating the models as authorities:

| Source | Best role in the engineering loop |
|---|---|
| Claude | deep critique, code audit, falsification, architecture correction |
| Devin | implementation/execution planning and integration work |
| Grok | broad brainstorming, candidate discovery, model/architecture exploration |
| Qwen | artifact construction, math-atlas/SPICE experimentation, code generation |
| Perplexity | research synthesis and world-model design exploration |
| LMArena/GPT corpus | comparative interaction, benchmark context, broad ideation |
| OmniRoute analysis | provider/model routing research and capability matrix |

These are **roles inferred from the records**, not permanent model identities.

A future model can outperform an older model in a role and should be re-evaluated accordingly.

---

# 9. Mandatory epistemic gates

Every future Neo agent must apply these rules:

### Gate A — Source provenance

Record where a claim came from.

### Gate B — Implementation status

Classify it as `VERIFIED`, `IMPLEMENTED`, `PARTIAL`, `EXPERIMENTAL`, `HISTORICAL`, `PLANNED`, or `UNVERIFIED`.

### Gate C — Runtime evidence

Prefer execution/test evidence over prose.

### Gate D — Model disagreement

Preserve conflicting model conclusions instead of averaging them into an invented consensus.

### Gate E — No fabricated metrics

If no empirical measurement exists, do not assign a precise percentage merely because repeated reasoning feels convergent.

### Gate F — No self-certification

Candidate generators do not certify their own candidates.

### Gate G — Dynamic-state validation

A stationary success is not a non-stationary success.

### Gate H — Dead-code detection

A component must be reachable from the actual runtime path before its capability is counted.

### Gate I — Capability boundary

A symbolic representation does not create computational access to the represented object.

### Gate J — Honest abstention

When required evidence is missing, the correct result is `UNRESOLVED` or `ABSTAIN`, not a fabricated answer.

---

# 10. Historical experiments worth preserving

The corpus contains several experimental directions that remain valuable as research candidates:

1. Champion/challenger recursive optimization.
2. Stationary/non-stationary dual engineering.
3. Model-lineage evolution analysis.
4. Multi-model consensus/council systems.
5. World-model prediction and transition modeling.
6. Mathematical Language Atlas + SPICE transfer capsules.
7. GPU/Kaggle experiment orchestration.
8. Local model ensembles and capability-aware routing.
9. Vision/OCR/ONNX pipelines.
10. Shared-directory Agent OS execution substrate.
11. Counterfactual and adversarial evaluation.
12. Persistent memory and evidence ledgers.

These should be evaluated independently before integration.

---

# 11. Experiments that require special skepticism

The corpus contains claims that sound stronger than the underlying evidence establishes. These must remain explicitly marked as hypotheses until reproduced:

- "superintelligence" claims;
- exponentially multiplying paradigm power;
- fabricated model-lineage performance numbers;
- personality counts derived from imposed fingerprints;
- self-aware or escaped model narratives;
- symbolic systems described as hypercomputational;
- generic YOLO presented as UI detection;
- hash-based vectors presented as semantic embeddings;
- planner/template systems presented as autonomous planning;
- documentation claims of tests that contain placeholders;
- model catalogs presented as live API guarantees;
- GPU hardware percentage attribution to weight quality.

The corpus itself contains corrective analyses for many of these. The corrections are part of the valuable knowledge and must not be discarded merely because the earlier claims were more exciting.

---

# 12. The most important reconstructed architectural insight

The corpus repeatedly converges on the same deeper architecture:

```text
                 KNOWLEDGE / MODEL CORPUS
                           |
                           v
                      STATE MODEL
                           |
                 +---------+---------+
                 |                   |
            STATIONARY          NON-STATIONARY
            ENGINEERING         ENGINEERING
                 |                   |
                 +---------+---------+
                           |
                     CANDIDATES
                           |
                     VERIFICATION
                           |
                  MULTI-RUN EVIDENCE
                           |
                 CANARY / SHADOW TEST
                           |
                  PROMOTE / ROLLBACK
                           |
                      TELEMETRY
                           |
                    NEW EVIDENCE
                           |
                           +----> next cycle
```

The goal is therefore **not** one enormous self-modifying AI.

The stronger architecture is a modular cognitive/engineering system surrounded by increasingly rigorous evidence, verification, model comparison, uncertainty handling, and rollback.

That conclusion is independently reinforced by the recursive-optimizer work and the model critiques of overclaimed systems.

---

# 13. What should happen next

Before further SROS architectural integration:

1. Treat this reconstruction as the context index.
2. Read the original model records when a claim is important.
3. Map every candidate subsystem to actual source and tests.
4. Run Stationary and Non-Stationary analysis independently.
5. Preserve disagreements.
6. Produce a candidate plan.
7. Implement only verified changes.
8. Re-run tests.
9. Re-read every changed file.
10. Re-review the repository against this reconstruction.
11. Update this reconstruction when new evidence materially changes the architecture.

## Final rule

**The corpus is evidence, not mythology.**

**The models are engineering participants, not oracles.**

**The engineers are part of a larger system, not standalone agents.**

**The executable system is the final authority on what currently works.**
