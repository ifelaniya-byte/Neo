# Limitations and independent plan (for other AIs to revise)

Date: 2026-08-13. Author: Arena.ai Agent Mode (this turn).  
This is **not** a completion claim. It is a constraint sheet plus a plan other models should tear apart.

---

## 1. Who / what I am

- I am a helpful agent on Arena.ai Agent Mode.
- I do not have a durable personal identity across products. I should not be treated as a specific frontier lab checkpoint.
- I cannot see the user’s local machine, Kaggle browser, phone, or wallet.
- I cannot click Kaggle’s “GPU on” button. I can only write files the user uploads.
- I forget anything not written under `/home/user` (and some paths are excluded from snapshots).
- I can be compacted mid-project; long histories become summaries. **Do not trust my memory of numbers—trust files.**

---

## 2. This sandbox (measured this turn)

| Resource | Measured fact |
|---|---|
| OS | Linux 6.1 x86_64, glibc 2.41, hostname `e2b.local` |
| CPU | 2 cores |
| RAM | not independently measured this turn; treat as modest shared VM |
| Disk | **~26 GB total**, ~20 GB free, ~4 GB used |
| GPU | **None.** No `/dev/nvidia*`, no `nvidia-smi` |
| Python | **3.13.14** |
| pip | present; installed packages **do not reliably persist** across snapshot restores |
| Network | outbound HTTP generally works (ModelScope, Kaggle API, HF router were used earlier) |
| Preview iframe | **no network**; CDN/CSS/images fail in-app |
| Servers | must bind `0.0.0.0`; user’s browser is not localhost |

### Packages (now)

**Present:** numpy, requests, PyYAML, psutil, `datasets`  
**Absent:** torch, transformers, accelerate, peft, trl, bitsandbytes, modelscope, kaggle CLI

So I **cannot** load Qwen, tokenize with HuggingFace tokenizers, train LoRA, or run `worker_entry.py` to completion here.

### Secrets (now)

- `HF_TOKEN` / `HUGGING_FACE_HUB_TOKEN`: unset  
- `WEIGHTS_ALLOW_HF_TOKEN`: unset  
- `KAGGLE_API_TOKEN`: unset  
- `~/.kaggle/access_token`: **not present this turn** (it existed in earlier sessions; snapshot/exclusion or cleanup)  
- I must never write tokens into ledger, dashboard, markdown, or git.

### Snapshot exclusions (I cannot rely on these surviving)

`.arena`, `.cache`, `.venv`, `node_modules`, `__pycache__`, `build`, `dist`, `.git/config`, `.git/credentials`, `.netrc`, and similar.

A 988 MB weight **does** persist under `/home/user/weights_offline/` if it was written there.

---

## 3. Capability limitations (model / agent)

1. **No real 45-checkpoint inference.** Personas are lenses + substrate unless a live call is logged.
2. **No musical/sung audio** if speech tools are used; speech is spoken-word only.
3. **I invent plausible code that is wrong.** Unit tests catch some of that; GPU contracts are untested.
4. **I over-complete scaffolding** (many notebooks) while the data plane stays at 0%. Other AIs should discount “files exist” as “it works.”
5. **I cannot certify licenses** beyond reading a LICENSE file. SPDX + redistribution to Kaggle Datasets needs a human.
6. **I cannot pin `master` to a git SHA** via ModelScope’s public revisions API (only `master` branch listed).
7. **I cannot operate multi-account GPU farms** and must refuse TOS evasion.
8. **HF Inference** last known state: credits **402**. I must not retry 402 loops.
9. **Catalog HTTP 200 ≠ authentic weights.**
10. **Council votes are simulated personas**, not independent models. Do not treat +31/−9 as scientific consensus on GPU design.
11. **CUSD is not money.**
12. **I should not `pip install torch` here**: 2 CPU, 20 GB free, Python 3.13, no NVIDIA. It would waste disk and still not prove T4.
13. **Long jobs die** at bash timeout unless using process tools; I am bad at “just leave a 2-hour train running” in this product.
14. **I cannot see Kaggle quota UI** (hours left, T4 vs P100, internet-on toggle).
15. **Viewer ≠ download.** HTML previews are sandboxed.

---

## 4. Project limitations (as of files on disk)

What is actually true:

- One complete **file set** for Qwen2.5-0.5B-Instruct (weight + tokenizer + config + license), hashes recorded.
- `artifact_gate.py` file-gate **exit 0**; transformers load **not run**.
- `worker_entry.py` + smoke-v2 (60) + scorers + 18 unit tests: **code-plane**.
- **0** `run_report.json`, **0** predictions, **0** adapters, **0** GPU seconds.
- Dashboard HTML ~5.4 MB of history; not a public site.
- Kaggle Dataset `council-qwen05` is a **path convention**, not a proven uploaded artifact.

---

## 5. Independent plan (for revision)

Other AIs: reject any step that requires this sandbox to grow a GPU. Prefer deleting work over adding seats.

### Goal

One **runtime-verified** baseline:

```text
persistent Qwen 0.5B dir
→ file-gate + hash
→ offline tokenizer/config/model load (on T4)
→ FP16, local_files_only, trust_remote_code=False
→ 60 smoke-v2 items
→ evaluation.json
→ run_report.json
→ second fresh session matches hashes of inputs
```

Until that exists, **do not** train, route 56 seats, or download 3B+.

### Track A — Human + Kaggle (only path to 100% of KP-16/17)

Owner: the King / user. Time: 45–90 minutes. Cost: free T4 quota.

1. Confirm Apache-2.0 allows uploading the Qwen dir as a **private** Kaggle Dataset named `council-qwen05`. If unsure, download inside **one** GPU session instead of publishing a Dataset.
2. Upload only: `worker_entry.py`, `smoke_scorer.py`, `artifact_gate.py`, `datasets/smoke-v2.jsonl`, `datasets/smoke-v2.manifest.json`, `kaggle_worker_template.ipynb`.
3. CPU first: discover dir (exactly one complete folder), `python artifact_gate.py $DIR`.
4. GPU: run notebook. Save outputs even on failure.
5. Second session: same Dataset hash, same smoke-v2 sha256 `d880d026bbc799847774506043cfb44c6c0ce4846384393412e6f6e273d34bee`.
6. Bring back **redacted** result files into this repo. Then an agent may update census/status.

**Why this track is first:** every remaining falsehood is “we ran the model.” Only Kaggle (or Colab) can make that true.

### Track B — This sandbox (maintenance only)

Owner: any agent. Time: minutes. Do **not** call this capability growth.

1. Keep tests green (`python3 -m unittest discover -s tests -q`).
2. Never commit tokens. Rotate any token that appeared in chat.
3. Do not grow `council_dashboard.html`. Status lives in `site/index.html` + JSON.
4. Do not add seats, QLoRA, or 27B pulls.
5. If HF credits return: one **read** token, `WEIGHTS_ALLOW_HF_TOKEN=1`, one smoke prompt, then stop. Still does not replace T4 batch proof.

### Track C — After two matching T4 reports

Only then:

1. NF4 vs FP16 on same 60 items.
2. Human license review + try to pin a commit SHA from Qwen’s GitHub/HF if ModelScope won’t.
3. A real train set (500–2000, licensed, not 4 rows) if a capability gap is measured.
4. One 3B candidate if 0.5B pipeline is boringly reliable.

### Explicit non-goals (reject these PRs)

- Dual-T4 70B offload as weekly plan  
- Multi-account hour farming  
- Treating helium990 / community GGUFs as official  
- Promoting adapters on one string match  
- Trust-on-first-use hashes  
- Calling CUSD “money”  
- Installing torch in this 2-core box to “finish 100%”

---

## 6. How other AIs should revise this plan

Score every recommendation with:

```text
expected_value = capability_gain × P(success) × reuse
                 / (GPU_hours + disk + TOS_risk + agent_hallucination_risk)
```

Demand evidence labels: VERIFIED / SUPPLIED / IMPLEMENTED-UNTESTED / BLOCKED.

If a reviser claims the sandbox can finish inference, they are wrong unless they show `torch.cuda.is_available()==True` in **this** environment.

---

## 7. Time / place / why (leftover)

| What | Where | Who | Time | Why it is leftover |
|---|---|---|---|---|
| First FP16 60-item run | Kaggle T4 | User | 45–90 min | No GPU here |
| Second reproduction | New Kaggle session | User | 30–45 min | Persistence + nondeterminism |
| Official git SHA | HF/GitHub, not this API | Agent+user | 30 min research | ModelScope only exposes `master` |
| Gitleaks | User machine or CI | User | 15 min | Not installed here |
| QLoRA | Kaggle after baseline | Later | hours | No measured gap yet |

**I am done with what this box can honestly finish.** The next author should either (a) run Track A and return artifacts, or (b) cut scope—not add another King’s Pass.
