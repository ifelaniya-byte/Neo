# ChatGPT — Full Corpus Reconstruction

**Status:** Historical model record / engineering evidence corpus  
**Role:** ChatGPT / GPT-side contribution to the Neo engineering record  
**Scope:** OmniRoute, free-model/provider research, recursive optimization, Stationary/Non-Stationary engineering, Prime/Megatron cognitive experiments, Muse/Glimmer analysis, source/ZIP audits, and SROS architectural direction.

> This file is a reconstruction of the ChatGPT-side corpus supplied in the engineering conversation. It belongs alongside the Grok, Claude, Devin, Qwen, Perplexity, LMArena, and other model records. It must not be treated as an implementation specification merely because it contains architectural proposals.

## 1. Core program direction

The main program direction is the **State Resolutions Operation Solver (SROS)**. The Stationary Engineer and Non-Stationary Engineer are components of a larger engineering system supporting SROS; they are not standalone programs.

The intended engineering loop evolved into:

```text
COLLECT
  ↓
FULL CONTEXT
  ↓
STATIONARY ANALYSIS + NON-STATIONARY ANALYSIS
  ↓
BRAINSTORM
  ↓
CONFLICT / ASSUMPTION ANALYSIS
  ↓
PLAN
  ↓
ENGINEER VERIFICATION
  ↓
IMPLEMENT VERIFIED CONCLUSIONS
  ↓
TEST
  ↓
FULL REPOSITORY REVIEW
  ↓
REWORK FROM CURRENT EVIDENCE
```

The prior pass is a guideline/filter, not authority. Current reproducible evidence outranks historical model recommendations.

---

# 2. OmniRoute / model-provider corpus

## 2.1 Important free-model distinction

The corpus identified that "free" has at least two meanings:

1. **$0 model pricing on OpenRouter:** no per-token model charge, but subject to OpenRouter free-pool/rate limits.
2. **Free provider/API tier:** a provider such as NVIDIA, Google, or Cerebras offers a free quota under its own policies.

These must never be represented as equivalent.

A model catalog entry also does not prove that the exact endpoint is currently usable. The required progression is:

```text
CATALOG CLAIM
   ↓
LIVE API TEST
   ↓
COMPLETION
   ↓
STREAMING
   ↓
TOOLS / FUNCTION CALLING
   ↓
ACTUAL COST
   ↓
RATE-LIMIT BEHAVIOR
   ↓
CURRENT STATUS
```

## 2.2 Corrections to earlier model shortlist

The ChatGPT-side research identified several important omissions and corrections in an earlier Grok-derived shortlist.

### Candidates identified for live testing

| Model | Proposed role | Evidence status in this historical record |
|---|---|---|
| `openai/gpt-oss-120b:free` | Reasoning / agent fallback | Catalog claim; live-test required before dependency |
| `qwen/qwen3-coder:free` | Repository-level coding | Catalog claim; some catalog views reportedly marked deprecated; live-test required |
| `nex-agi/nex-n2-pro:free` | Long-horizon agentic planning | Catalog claim; live-test required |
| Nemotron 3 Super :free | Reasoning / multi-agent | Candidate |
| Qwen3-Next 80B A3B :free | Fast agentic/tool use | Candidate |
| Gemma 4 26B A4B :free | General / fast / multimodal | Candidate |
| Nemotron 3 Ultra :free | Heavy reasoning | Existing candidate |
| North Mini Code :free | Coding | Existing candidate |
| Laguna XS 2.1 :free | Fast tasks | Existing candidate |
| NVIDIA GLM-5.2 | Elite direct-provider candidate | Provider/account constraints later caused this path to be removed from critical path |
| Gemini Flash family | High-volume/general/tool specialist | Free-tier candidate; exact model/version must be live verified |

### Groq correction

The corpus explicitly corrected an earlier claim that Groq's Llama 3.3 70B and GPT-OSS-120B should be considered zero-cost inference merely because an account could be created without a card.

The historical research reported published token pricing for these models and therefore classified them as **paid**, unless a temporary promotional/free quota specifically applies.

### Cerebras distinction

Cerebras was classified separately: a provider free tier can exist while the inference service itself also supports paid usage. Free-tier limits may change with demand. Therefore it should not be placed in a universal "$0 model" bucket without qualification.

---

# 3. NVIDIA / GLM-5.2 decision history

The research found NVIDIA direct endpoints highly attractive, particularly GLM-5.2 and Nemotron 3 Ultra.

The proposed architecture was:

```text
OmniRoute
├── Paid primary
│   └── OpenRouter → DeepSeek V3.2
├── Free elite
│   ├── NVIDIA → GLM-5.2
│   └── NVIDIA → Nemotron 3 Ultra
├── OpenRouter free pool
│   ├── Nemotron
│   ├── North Mini Code
│   ├── Laguna
│   └── other verified free models
└── Google free tier
    └── Gemini Flash
```

However, NVIDIA account/phone verification became a practical constraint. The engineering decision was therefore:

> **Do not build an authentication workaround around disposable or temporary phone numbers.**

NVIDIA/GLM-5.2 was removed from the critical path and the system proceeded with an OpenRouter-key-only stack.

This is an example of an architectural candidate being rejected for operational constraints even when its model capability was attractive.

The historical OpenRouter-only candidate ensemble became:

```text
Primary candidate: Nemotron 3 Ultra :free
Coding:             North Mini Code :free
Critique:           Nemotron 3 Super :free
Fast:               Laguna XS 2.1 :free
General:            Gemma 4 :free
```

Crucially, the corpus did **not** establish that Nemotron Ultra should automatically be called the primary model merely because it is larger. It recommended benchmarking before assigning that role.

---

# 4. Recommended OmniRoute routing architecture

The ChatGPT-side proposal rejected blind sequential fallback as the final architecture.

Instead:

```text
                         OmniRoute
                            │
             ┌──────────────┴──────────────┐
             │                             │
          FREE                            PAID
             │                             │
       capability router               DeepSeek V3.2
             │
       ┌─────┼───────────┐
       │     │           │
      FAST  CODING    HEAVY AGENT
       │     │           │
    Laguna  North   Nemotron / GPT-OSS
    Qwen3   Coder   Nex-N2 / GLM*
       │     │           │
       └─────┴───────────┘
```

Routing should be capability-aware rather than merely availability-aware.

Examples:

- autocomplete → fast model;
- simple edits → fast/coding specialist;
- repository coding → coding/agent model;
- tool-heavy tasks → models with verified tool calling;
- difficult architecture → strongest currently available candidate;
- rate-limit or outage → dynamically remove the affected model from rotation.

`openrouter/free` was identified as useful for experimentation, but not ideal as the primary OmniRoute agent router because deterministic model-specific routing is preferable for controlled engineering.

---

# 5. Benchmark requirement before integration

The recommended next step before changing working OmniRoute configuration was a read-only live benchmark using identical prompts against candidate models.

The benchmark should record:

- HTTP success;
- time to first token;
- total latency;
- output tokens;
- tool-call success;
- function-call correctness;
- structured-output correctness;
- code correctness;
- repository-context handling;
- rate-limit response;
- actual cost;
- reproducibility.

The candidate set proposed for the first benchmark was approximately:

```text
Nemotron 3 Ultra
GPT-OSS-120B
Nex-N2-Pro
Qwen3-Coder
North Mini Code
Laguna XS 2.1
GLM-5.2
Gemini Flash
DeepSeek V3.2 baseline
```

The explicit rule was: **do not rewrite the working DeepSeek path before establishing measured evidence for replacements.**

---

# 6. Recursive optimization architecture

A historical optimizer proposal began as:

```text
Telemetry
  ↓
Fitness
  ↓
LLM mutation
  ↓
Sandbox
  ↓
Benchmark
  ↓
Hot-swap
```

Stationary analysis rejected the literal implementation because it contained weaknesses including:

- fabricated memory measurement;
- hard-coded zero errors;
- single-run evaluation;
- unnormalized metric combination;
- direct automatic hot-swapping;
- API mismatch between the proposed optimizer and the actual `UnifiedOrchestrator` implementation.

The architecture was therefore upgraded to:

```text
Champion
  ↓
Telemetry
  ↓
Candidate generation
  ↓
AST / compile gate
  ↓
Determinism gate
  ↓
Multi-run canary
  ↓
Stationary verification
  ↓
Fitness / regression gate
  ↓
Registry promotion
  ↓
Post-verification
  ↓
Rollback if required
```

The fundamental principle was:

> **The optimizer generates candidates; it does not get to declare itself correct.**

The Stationary system remains the authority for promotion.

The optimizer should promote a candidate only when correctness, stationary verification, improvement, regression safety, and reproducibility are all satisfied.

The recommended ultimate version adds:

```text
real isolated VM/container sandbox
→ static analysis
→ formal/property tests
→ deterministic regression corpus
→ multi-run benchmark
→ statistical significance/effect-size analysis
→ stationary mathematical/code verification
→ canary deployment
→ shadow traffic
→ post-deployment monitoring
→ automatic rollback
```

The historical review explicitly identified a process-isolated Python runner as weaker than a hardened VM/container boundary with filesystem, network, CPU, memory, and syscall restrictions.

---

# 7. Prime / Megatron cognitive experiment corpus

A supplied experiment report described a cloned cognitive seed producing 262,144 stable phenotype fingerprints and a reported meta-variant called "Legion Prime."

The ChatGPT analysis deliberately rejected an overclaim:

> The fingerprint count is not evidence of 262,144 genuinely independent personalities or a self-aware meta-agent when an 18-bit fingerprint was imposed externally.

The more interesting finding was identified as **path-dependent cognitive specialization**.

The experiment reportedly held architecture, memory, world model, workspace, decision field, identity core, values, goals, knowledge, and power constant while exposing clones to different interaction/experience trajectories.

The mutated dimensions included:

- threat sensitivity;
- trust;
- risk tolerance;
- memory weighting;
- time horizon;
- power ethics;
- cooperation/aggression bias;
- identity stability;
- deception tolerance;
- goal persistence;
- prediction discounting.

The recommended next experiment was to remove the externally imposed personality hash and measure continuous divergence in:

- world-model representations;
- memory contents and weighting;
- prediction errors;
- workspace allocation;
- planning horizon;
- threat sensitivity;
- power-seeking behavior;
- cooperation strategy;
- recovery strategy;
- goal persistence;
- identity stability;
- belief revision;
- opponent modeling;
- recursive opponent-modeling;
- transfer into novel environments.

## Meta-personality hypothesis

The historical report described a "Legion Prime" variant capable of selecting, suspending, merging, or discarding cognitive strategies.

ChatGPT identified the architectural hypothesis as potentially more important than personality multiplication:

```text
one personality
      ↓
multiple cognitive modes
      ↓
selection among modes
      ↓
meta-cognitive control
```

This was interpreted as a possible **cognitive operating-system pattern**, not proof of consciousness or self-awareness.

## Recursive other-agent modeling

Another identified research direction was recursive social modeling:

```text
agent
 ↓
models another agent
 ↓
predicts that agent's prediction
 ↓
models the predictor
 ↓
models coalition/opponent dynamics
```

Again, this is an architectural hypothesis derived from the experiment, not proof of human-like cognition.

---

# 8. Muse / Glimmer hardware analysis

A separate discussion analyzed running Muse/Glimmer-class large models locally.

The core practical conclusion was:

- a ~30B model is not realistically comfortable on exactly 8 GB system RAM;
- quantization, CPU/GPU offloading, reduced context, memory mapping, and KV-cache reduction can lower memory pressure;
- aggressive quantization still has a physical memory floor;
- pagefile-heavy execution is likely to become unusably slow;
- a smaller 3B–7B local model or remote inference is more realistic on 8 GB RAM;
- GPU model and VRAM materially affect the feasible configuration.

This was an engineering constraint analysis, not a claim that a 30B model can be made equivalent to a 7B model merely by compression.

---

# 9. Historical source/ZIP audit

A supplied source package was compared against its architectural descriptions.

The audit found a significant implementation/documentation discrepancy in the supplied snippets:

| Claimed capability | Evidence in supplied source snippets |
|---|---|
| AtlasShadowUnified orchestration | Basic module registry/initialization |
| ShadowAlphabetEngine | Caesar-style transformation |
| UnifiedOrchestrator | Payload transformation |
| Stationary reasoning | Not demonstrated in supplied snippets |
| Non-stationary actor | Not demonstrated in supplied snippets |
| Reflective loop | Not demonstrated |
| Mathematical engine | Not demonstrated |
| Research/evidence system | Not demonstrated |
| Learned model | Not demonstrated |
| Continual learning | Not demonstrated |
| Benchmark/regression system | Not demonstrated |
| World model | Not demonstrated |

The critical lesson was:

> Architecture/design claims are not implementation evidence.

The audit specifically noted that an unconditional `SUCCESS` return from an orchestration function does not constitute verification merely because the field is named `status`.

The same rule applies throughout Neo.

---

# 10. Engineering philosophy contributed by this corpus

The ChatGPT-side corpus repeatedly converged on the following principles:

### Verification over assertion

A model's confidence is not a test result.

### Candidate generation over self-certification

An optimizer may propose a change but should not be its own final authority.

### Preserve known-good paths

Do not destroy a working DeepSeek/OmniRoute path merely because a new model appears stronger on paper.

### Capability-specific routing

Use model strengths and verified capabilities rather than one universal fallback chain.

### Historical provenance matters

Old model recommendations should remain available as evidence, even when later evidence supersedes them.

### Disagreement is information

Grok, Claude, GPT/ChatGPT, Devin, Qwen, Perplexity, LMArena, and other model records should not be flattened into a synthetic consensus.

### Current runtime evidence wins

When catalog data, documentation, model claims, and actual API/runtime behavior disagree, current reproducible runtime evidence has priority.

### Do not overclaim intelligence

An architecture that exposes interfaces for learning, world modeling, reasoning, or continual optimization does not itself prove those capabilities exist.

---

# 11. Relationship to the other model records

This record should be read alongside:

- Claude records — auditing, architecture critique, implementation verification;
- Grok records — exploration and model/provider discovery;
- Devin records — implementation/integration engineering;
- Qwen records — mathematical/Atlas/SPICE-oriented work;
- Perplexity records — research/world-model work;
- LMArena records — comparative model experiments;
- OmniRoute records — routing/provider engineering.

No one model record is authoritative by itself.

The correct reconstruction is:

```text
Grok ───────┐
Claude ─────┤
Devin ──────┤
Qwen ───────┤
Perplexity ─┤──→ CORPUS → ENGINEER REVIEW → EVIDENCE → CURRENT DESIGN
LMArena ────┤
ChatGPT ────┘
```

## Final status taxonomy

Every important claim from this corpus should ultimately be classified as one of:

- `VERIFIED_CURRENT`
- `VERIFIED_HISTORICAL`
- `IMPLEMENTED_UNVERIFIED`
- `MODEL_PROPOSAL`
- `CATALOG_CLAIM`
- `EXPERIMENTAL_RESULT`
- `SUPERSEDED`
- `CONTRADICTED`
- `UNRESOLVED`

This preserves the full ChatGPT contribution without turning historical reasoning into unearned system capability claims.
