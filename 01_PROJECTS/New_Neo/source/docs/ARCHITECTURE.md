# PROJECT APEX: Complete Architecture Documentation

## Overview

Project APEX implements a revolutionary **closed-loop self-refactoring and compressive evolution protocol** that enables a micro-LLM (≤500M parameters) to continuously optimize its own codebase, distill its own weights, and improve its execution runtime.

---

## The Dual Karpathy Loop Architecture

The system operates across three interlocking feedback loops:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE DUAL KARPATHY LOOP                                       │
│                                                                                              │
│   ┌───────────────────────────┐    Generates Code    ┌───────────────────────────────────┐   │
│   │   Gemini 2.0 / 0.5B Base  ├─────────────────────►│ worker_core.py Execution Engine   │   │
│   └─────────────┬─────────────┘                      └─────────────────┬─────────────────┘   │
│                 │                                                      │                     │
│                 │ Farms Trajectories                                   │ Evaluates Score     │
│                 ▼                                                      ▼                     │
│   ┌───────────────────────────┐    Fine-Tunes        ┌───────────────────────────────────┐   │
│   │ verified_trajectories.jsonl│─────────────────────►│  train_micro_core.py (Trainer)    │   │
│   └───────────────────────────┘                      └─────────────────┬─────────────────┘   │
│                                                                        │                     │
│                                                       Evolves Trainer  │ (Karpathy Loop #2)  │
│                                                       & Architecture   ▼                     │
│                                                      ┌───────────────────────────────────┐   │
│                                                      │ APEX-NANO-135M / 0.5B Micro-LLM   │   │
│                                                      └───────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Loop 1: Code Task Optimization (`worker_core.py`)

### Purpose
Optimize computational performance through iterative code refinement.

### Process Flow
1. **Generation:** The micro-model (or Gemini) generates performance patches for `worker_core.py`
2. **Evaluation:** `eval_harness.py` measures real execution time and numerical accuracy
3. **Selection:** The Git Ratchet commits wins and discards losses
4. **Collection:** Winning strategies are saved as training examples in `verified_trajectories.jsonl`

### Key Components

#### `worker_core.py`
- **Target file** for autonomous optimization
- Contains computational workload (baseline: mathematical loop operations)
- Must maintain function signatures: `run_unit_tests()`, `execute_benchmark_batch()`
- Can be modified for any computational optimization task

#### `eval_harness.py`
- **SERE-X Sandbox Gate** for safe code execution
- Calculates composite score: $S_{\text{eval}} = 0.4 \times S_{\text{loss}} + 0.3 \times S_{\text{speed}} + 0.2 \times S_{\text{ram}} + 0.1 \times S_{\text{tests}}$
- Tracks resource usage (memory, execution time)
- Enforces thread safety via environment variables

#### `agent_runner.py`
- **Outer execution harness** orchestrating the evolutionary loop
- Pre-configured with Gemini 2.0 Flash API integration
- Implements Git Ratchet mechanism for version control
- Exports winning trajectories via `dataset_builder.py`

---

## Loop 2: Micro-LLM Architecture & Trainer Evolution (`train_micro_core.py`)

### Purpose
Enable the micro-LLM to optimize its own training and architecture while respecting the 500M parameter ceiling.

### Self-Refinement Strategies

#### 1. Quantization & Distillation
- Precision reduction: FP16 → INT8 → 4-bit NormalFloat (NF4)
- Maintains reasoning capability while maximizing tokens-per-second
- Enables deployment on resource-constrained hardware

#### 2. Layer & Attention Pruning
- Identifies and removes underperforming transformer heads
- Strips redundant layers to shrink parameter density
- Preserves reasoning score through careful selection criteria

#### 3. Direct Preference Optimization (DPO)
- Aligns micro-model on *why* winning code worked
- Learns from *why* discarded code failed
- Creates preference pairs from trajectory data

### Process Flow
1. **Hypothesis Generation:** Agent proposes modifications to `train_micro_core.py`
2. **Training Execution:** Modified trainer produces new checkpoint
3. **Validation:** `eval_harness.py` tests new checkpoint performance
4. **Selection:** Git commits if performance improves, rolls back otherwise

---

## Component Specifications

### 1. `program.md` - Master Protocol
- Defines mission directive and scope constraints
- Specifies permitted and forbidden actions
- Documents the recursive evolutionary loop sequence
- Provides evaluation metric formulas

### 2. `worker_core.py` - Target Engine
- **Current Baseline:** Unoptimized floating-point mathematical loop
- **Function Signatures:**
  - `run_unit_tests()`: Validates correctness and non-NaN outputs
  - `execute_benchmark_batch()`: Core computational workload
- **Optimization Targets:** SIMD vectorization, memory alignment, cache optimization

### 3. `eval_harness.py` - Benchmark Gate
- **Thread Safety:** Enforces single-threaded execution
- **Resource Tracking:** Monitors memory usage and execution time
- **Scoring System:** Multi-objective optimization balance
- **Safety:** Isolates execution to prevent system damage

### 4. `experiment_log.tsv` - Audit Trail
- **Columns:** Run_ID, Timestamp, Hypothesis, S_eval, Result, Commit_Hash
- **Purpose:** Complete history of optimization attempts
- **Analysis:** Enables pattern recognition and strategy refinement

### 5. `dataset_builder.py` - Trajectory Extractor
- **Input:** `experiment_log.tsv` and current `worker_core.py`
- **Output:** `verified_trajectories.jsonl` (structured training data)
- **Format:** JSONL with trajectory metadata and code patches

### 6. `train_micro_core.py` - Distillation Engine
- **Base Model:** HuggingFaceTB/SmolLM2-135M-Instruct
- **Parameter Limit:** 500M (strictly enforced)
- **Training Objective:** Instruction tuning on optimization trajectories
- **Output:** `./apex_nano_final` (compressed local model)

### 7. `setup_env.py` - System Bootstrapper
- **Git Initialization:** Sets up version control infrastructure
- **Dependency Management:** Verifies and installs required packages
- **Baseline Setup:** Seeds experiment log with initial metrics

---

## Data Flow Diagram

```
┌─────────────────┐
│  Gemini API     │
│  (Cloud LLM)    │
└────────┬────────┘
         │ 1. Generate Code
         ▼
┌─────────────────┐
│ agent_runner.py │◄───────────────────────────────────────────┐
└────────┬────────┘                                            │
         │ 2. Write worker_core.py                            │
         ▼                                                     │
┌─────────────────┐     3. Execute    ┌─────────────────┐     │
│ worker_core.py  │──────────────────►│ eval_harness.py │     │
└─────────────────┘                   └────────┬────────┘     │
         │ 4. Read Code                       │ 5. Score     │
         └─────────────────────────────────────┘              │
         │ 6. Git Decision (KEEP/DISCARD)                      │
         ▼                                                     │
┌─────────────────┐     7. Export     ┌─────────────────┐     │
│ Git Repository  │──────────────────►│dataset_builder   │     │
└─────────────────┘                   └────────┬────────┘     │
         │                                     │ 8. JSONL     │
         │                                     ▼              │
         │                          ┌─────────────────┐        │
         │                          │verified_traject-│        │
         └──────────────────────────│ories.jsonl     │◄───────┘
                                    └────────┬────────┘
                                             │ 9. Training Data
                                             ▼
                                    ┌─────────────────┐
                                    │train_micro_core │
                                    │    .py          │
                                    └────────┬────────┘
                                             │ 10. Fine-tune
                                             ▼
                                    ┌─────────────────┐
                                    │ apex_nano_final │
                                    │  (Local Model)  │
                                    └─────────────────┘
```

---

## Performance Characteristics

### Expected Improvements
- **Execution Speed:** 2-10x faster through iterative optimization
- **Memory Efficiency:** Reduced footprint via algorithmic improvements
- **Model Compression:** 50-70% size reduction through quantization
- **Inference Speed:** 100+ steps/minute on local hardware

### Convergence Behavior
- **Initial Phase:** Rapid improvements from low-hanging optimizations
- **Middle Phase:** Slower but steady gains from algorithmic refinements
- **Final Phase:** Convergence to optimal implementation with minor tweaks

---

## Security & Safety Mechanisms

### 1. Code Isolation
- All code execution contained within `eval_harness.py` sandbox
- Thread limits prevent resource exhaustion
- Memory caps prevent system instability

### 2. Git Ratchet
- Every change is version-controlled and reversible
- Failed optimizations automatically rolled back
- Complete audit trail of all modifications

### 3. Parameter Limits
- Hard ceiling at 500M parameters for micro-LLM
- Verification checks before training execution
- Prevents uncontrolled model growth

### 4. Network Restrictions
- No unauthorized external library imports
- API calls limited to configured endpoints
- Local execution capability for offline operation

---

## Extension Points

### Custom Workloads
Replace `worker_core.py` with your computational task while maintaining:
- `run_unit_tests()` function signature
- `execute_benchmark_batch()` function signature
- Mathematical correctness validation

### Alternative Models
Modify `train_micro_core.py` to use different base models:
- Qwen2.5-0.5B for larger capacity
- DistilGPT-2 for faster training
- Custom fine-tuned models for domain specificity

### Evaluation Metrics
Adjust weights in `eval_harness.py` to prioritize:
- Speed over accuracy (increase W_SPEED)
- Memory efficiency (increase W_RAM)
- Test reliability (increase W_TESTS)

---

## Deployment Scenarios

### Cloud-Based Optimization
- Use Gemini 2.0 Flash for rapid initial iteration
- Leverage unlimited cloud resources for trajectory farming
- Transition to local model for cost efficiency

### Local-Only Operation
- Train micro-LLM on cloud-farmed trajectories
- Deploy locally for offline optimization
- Maintain full autonomy without external dependencies

### Hybrid Approach
- Use cloud for complex architectural changes
- Use local model for incremental improvements
- Balance cost, speed, and quality

---

## Monitoring & Debugging

### Real-Time Metrics
Console output provides:
- Current iteration and best score
- Hypothesis descriptions
- Benchmark results
- Git commit status

### Post-Analysis
- `experiment_log.tsv`: Complete optimization history
- `verified_trajectories.jsonl`: Training data quality
- Git history: Detailed code evolution
- Model checkpoints: Performance progression

### Common Issues
- **Score Plateaus:** Consider changing optimization strategy
- **Memory Issues:** Reduce iteration count or optimize memory usage
- **API Failures:** Switch to local LLM or check network connectivity
- **Git Conflicts:** Ensure clean repository state before execution

---

## Future Enhancements

### Planned Features
- Multi-objective optimization with Pareto fronts
- Distributed training for larger trajectory datasets
- Neural architecture search for automated model design
- Transfer learning from domain-specific codebases

### Research Directions
- Meta-learning of optimization strategies
- Causal reasoning for code modification impact
- Self-supervised trajectory quality assessment
- Cross-domain knowledge transfer

---

## Conclusion

Project APEX represents a significant advancement in autonomous software optimization, combining:
- **Karpathy Loop principles** for iterative improvement
- **Micro-LLM technology** for local, efficient execution
- **Git Ratchet mechanisms** for safe, reversible evolution
- **Comprehensive evaluation** for multi-objective optimization

The system enables continuous, autonomous code improvement while maintaining strict safety constraints and providing complete auditability of the optimization process.