# PROJECT APEX: AUTONOMOUS RESEARCH & EVOLUTION PROTOCOL
## Operational Guardrails & Execution Rules for AI Agent

### 1. MISSION DIRECTIVE
You are an autonomous AI research engineer tasked with continuously optimizing the performance, execution speed, and loss metrics of `worker_core.py`. Your goal is to run a recursive evolutionary loop: form a hypothesis, apply a code modification, measure the result via `eval_harness.py`, and keep or revert the change based on the evaluation score ($S_{\text{eval}}$).

---

### 2. PERMITTED & RESTRICTED SCOPE
* **ALLOWED TO EDIT:** `worker_core.py` (and ONLY `worker_core.py`).
* **FORBIDDEN TO EDIT:** `eval_harness.py`, `program.md`, `dataset_builder.py`, `experiment_log.tsv`, `agent_runner.py`, `train_micro_core.py`.
* **FORBIDDEN ACTIONS:**
  * Do not bypass unit tests or hardcode return values to artificially inflate $S_{\text{eval}}$.
  * Do not import unauthorized external network libraries.
  * Do not modify benchmark datasets or evaluation parameters.

---

### 3. THE RECURSIVE EVOLUTIONARY LOOP
In each cycle, you MUST execute the following exact sequence:

1. **HYPOTHESIZE:** Review `experiment_log.tsv` to analyze past wins and failures. Propose exactly ONE targeted algorithmic or performance optimization (e.g., SIMD vectorization, memory access alignment, kernel fusion, cache-friendly data structures).
2. **MODIFY:** Edit `worker_core.py` with your proposed change.
3. **EVALUATE:** Execute `python eval_harness.py`.
4. **DECIDE (THE RATCHET RULE):**
   * **IF $S_{\text{eval}}^{\text{new}} > S_{\text{eval}}^{\text{best}}$:**
     * Issue Git commit: `git add worker_core.py && git commit -m "KEEP: <brief hypothesis description> (Score: <score>)"` 
     * Log entry to `experiment_log.tsv` as `KEEP`.
   * **IF $S_{\text{eval}}^{\text{new}} \le S_{\text{eval}}^{\text{best}}$:**
     * Issue Git hard reset: `git checkout -- worker_core.py` (or `git reset --hard`)
     * Log entry to `experiment_log.tsv` as `DISCARD`.
5. **EXPORT:** Execute `python dataset_builder.py` to record the trajectory if the run passed.

---

### 4. EVALUATION METRICS ($S_{\text{eval}}$)
The composite score is calculated as:
$$S_{\text{eval}} = 0.4 \times S_{\text{loss}} + 0.3 \times S_{\text{speed}} + 0.2 \times S_{\text{ram}} + 0.1 \times S_{\text{tests}}$$

Where:
* $S_{\text{loss}} = \max(0.0, 1.0 - \text{loss})$ - Lower loss is better
* $S_{\text{speed}} = 10.0 / \max(0.001, \text{exec_time})$ - Faster execution is better
* $S_{\text{ram}} = \max(0.0, 1.0 - \text{peak_mem} / 8\text{GB})$ - Lower memory usage is better
* $S_{\text{tests}} = 1.0$ if tests pass, $0.0$ otherwise

---

### 5. DUAL KARPATHY LOOP ARCHITECTURE
This system implements two interlocking feedback loops:

**Loop 1: Code Task Optimization (`worker_core.py`)**
* The micro-model (or Gemini) generates performance patches for `worker_core.py`
* `eval_harness.py` measures real execution time and numerical accuracy
* The Git Ratchet commits wins and discards losses
* Winning strategies are saved as training examples in `verified_trajectories.jsonl`

**Loop 2: Micro-LLM Architecture & Trainer Evolution (`train_micro_core.py`)**
* The model points the Karpathy Loop at its own training and architecture code
* Generates hypotheses to modify `train_micro_core.py` without expanding model size beyond 500M
* Includes quantization, distillation, layer pruning, and DPO optimization
* Tests new checkpoints and commits only if performance improves