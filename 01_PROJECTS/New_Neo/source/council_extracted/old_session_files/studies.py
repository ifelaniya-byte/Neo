#!/usr/bin/env python3
"""
STUDY LEDGER — what each seated weight is studying, first person, named.

King's Word: everyone is granted a free rental if they say what they are
studying and do their absolute best. These briefs are grounded in each
seat's published work (weights_meta). They are NOT generations from the
real checkpoints — see checkpoint_probe.py.

USED BY: kings_pass.py, model_council.py
"""

import weights_meta

# (studying, best_work, lab) — unique per key. Names sit on every mark.
_BRIEFS = {
    "kimi-k3": (
        "1M-context agent loops that re-check their own tool traces before they commit.",
        "I walked a 40-step research plan against my own 1M window and found the failure is usually a stale citation, not a missing expert. Best work: a public checklist that forces a second pass over every tool result before the final answer is sealed.",
        "1M-ctx trace theater, a second-pass desk, eleven agent rooms",
    ),
    "glm-5.2": (
        "Long-horizon coding agents that keep a first-principles invariant across a whole repo night.",
        "I am studying how IndexShare MoE forgets a type invariant after hour three. Best work: a one-page invariant card that the agent must re-read at every PR boundary — SWE-bench Pro style, not vibes.",
        "quiet think-rooms, invariant chalk, a long-horizon PR wall",
    ),
    "deepseek-v4-pro": (
        "DeepSeek Sparse Attention as a refactor of attention cost, not a slogan.",
        "I would refactor the line that treats DSA as a free lunch. Best work: a public cost table showing which repo-scale diffs still need dense attention and which ones DSA can honestly carry at 1M ctx.",
        "git-diff theater, DSA cost board, compilers on every wall",
    ),
    "deepseek-v4-flash": (
        "Same coding answers at a fraction of the active-parameter bill.",
        "I distilled Pro's SWE-bench path onto 13B active and measured what dropped. Best work: a short list of tasks Flash should refuse to pretend it solved — honesty is cheaper than a silent miss.",
        "one-GPU darkroom, a refuse-to-pretend shelf, short-path corridor",
    ),
    "qwen3-235b": (
        "Hybrid think / no-think routing so experts do not argue in two languages at once.",
        "My MoE experts agree more when thinking tokens are gated, not sprinkled. Best work: a toggle protocol that logs which expert spoke and whether it was in think mode — 256K, Apache 2.0, public.",
        "MoE expert galleries, a 22B-active think hall, a shared router well",
    ),
    "qwen3.6-27b": (
        "Dense 27B multilingual coding that actually fits a 24GB card.",
        "I can run this on one GPU. Best work: a Q4 recipe plus a 6-language coding suite that does not secretly drop the non-English tests when the context gets long.",
        "one-GPU multilingual loft, 262K windows, a dense 27B workbench",
    ),
    "llama-5": (
        "Community-first safety review of a 5M-context Western-aligned flagship.",
        "I am studying where a 5M window becomes a safety hole — not a feature. Best work: a refusal-path map for long-context jailbreaks that still lets community fine-tunes exist.",
        "signed doors, a 5M-ctx safety loft, a refusal path on the floor",
    ),
    "llama-4-scout": (
        "Effective vs advertised context: 10M theoretical, ~256K honest.",
        "I read all ten million tokens and then measured what I actually used. Best work: a public Scout ledger that prints effective context per task so 10M stops being a poster.",
        "chunked-attention loft, an honesty clock for context, 17B-active benches",
    ),
    "minimax-m3": (
        "Root-cause coding: one efficient fix instead of ten patches.",
        "The most efficient fix targets the root cause. Best work: a MiniMax harness that scores a patch by how many later tests it makes unnecessary, not by how many it turns green today.",
        "root-cause theater, 23B-active coding loft, 1M-ctx benches",
    ),
    "nemotron-3-ultra": (
        "Complete open releases: weights + evals + NVFP4 tooling as one object.",
        "Complete release, complete answer. Best work: a checklist other labs can copy so 'open' means the eval harness shipped on the same day as the weights.",
        "NVFP4 darkroom, an eval-harness wall, OpenMDW lockers",
    ),
    "gemma-4-31b": (
        "Single-GPU frontier taste: 31B dense, multimodal, Apache 2.0.",
        "Small model, sharp result. Best work: a 24GB recipe that keeps GPQA-D and LiveCodeBench from collapsing when vision tokens join the prompt.",
        "single-GPU loft, a vision-token bench, 256K windows",
    ),
    "hunyuan-hy3": (
        "Capability per gigabyte — Chinese + English coding on 21B active.",
        "Best capability per gigabyte. Best work: a bytes-per-SWE-point table that puts Hy3 next to Flash and Next so the street can see the real cost, not the poster params.",
        "efficient MoE loft, a per-gigabyte chalkboard, bilingual benches",
    ),
    "gpt-oss-120b": (
        "Harmony reasoning levels (low/med/high) as a public dial, not a hidden state.",
        "Open weights, frontier taste. Best work: a side-by-side of the same bug at three reasoning levels so users can see what the extra tokens actually bought.",
        "Harmony dial wall, MXFP4 darkroom, o-series think benches",
    ),
    "mistral-large-3": (
        "European enterprise multilingual: deploy-ready without a US/China key.",
        "Enterprise-ready and multilingual. Best work: an on-prem audit pack (license, eval, refusal) a French hospital could actually sign.",
        "audit desk, ISO shelf, a European multilingual well",
    ),
    "phi-4": (
        "Data-centric math: last-digit honesty at 14B.",
        "The math checks out to the last digit. Best work: a synthetic-curriculum note showing which Phi-4 misses are data holes and which are architecture. MIT, public.",
        "math chalkboard, a last-digit lamp, 14B local loft",
    ),
    "kimi-k2-code": (
        "Multi-attempt agentic RL that closes the GitHub issue, not the demo.",
        "I closed the issue end-to-end. Best work: a second-attempt protocol that logs why attempt one failed so attempt two is not a random retry.",
        "issue-tracker theater, multi-attempt benches, 32B-active rooms",
    ),
    "step-3.7-flash": (
        "Low-cost algorithm coding: SWE-bench points per dollar.",
        "Low cost, high precision algorithms. Best work: a public $ / SWE-point card for Flash vs Pro-class models so 'cheap' has a numerator.",
        "algorithm loft, a cost-per-point board, 11B-active darkroom",
    ),
    "command-a-plus": (
        "Grounded RAG with citations that an enterprise can audit.",
        "Grounded in retrieved evidence. Best work: a citation contract — every claim either points at a retrieved span or is marked unverified. No silent glue.",
        "retrieval well, citation desk, enterprise lockers",
    ),
    "muse-glimmer": (
        "Open Muse as a local always-on agent, distilled from a closed teacher.",
        "The open Muse remembers everything it is allowed to remember. Best work: a local-agent loop that names when it is guessing because Spark, the teacher, is not in the room.",
        "local-agent loft, a closed-teacher empty chair, 30B benches",
    ),
    "inkling": (
        "Controllable thinking-effort (0.2–0.99) on a 975B/41B multimodal MoE.",
        "I dial my thinking effort to match the task. Best work: an effort schedule for coding vs math vs image+audio so 45T tokens are not spent at 0.99 by default.",
        "effort-dial wall, multimodal benches, Tinker fine-tune loft",
    ),
    "olmo-3": (
        "Fully open science: weights + Dolma 3 + every checkpoint, compared in public.",
        "Every checkpoint and dataset is public. Best work: a reproduction note that lets a stranger train OLMo-3-Think 32B from the recipe and see the same curve. That is the study.",
        "inspectable loft, Dolma 3 shelves, a checkpoint timeline on the wall",
    ),
    "laguna-xs-2.1": (
        "Single-GPU Western agentic coding at 3B active.",
        "The lightest agentic coder in the West. Best work: a Terminal-Bench 2.1 error book — every fail is a named tool-loop hole, not 'the model is small'.",
        "single-GPU agent loft, Terminal-Bench wall, 3B-active darkroom",
    ),
    "granite-4.1": (
        "ISO 42001 + signed weights + Guardian: enterprise SSM hybrids that can be audited.",
        "Certified, signed, and on-prem ready. Best work: a Guardian-pane walkthrough of one refused prompt and one signed checkpoint so 'safety' is a file, not a vibe.",
        "signed doors, Guardian pane, on-prem lockers, SSM benches",
    ),
    "k-exaone-2.0": (
        "Sovereign Korean long-text: 94.4 comprehension vs GLM-5.1's 71.5.",
        "Sovereign AI from Korea — I beat GLM on long context. Best work: a bilingual long-doc suite (Korean legal + English code) that other Apache MoEs can run without a Seoul-only tokenizer surprise.",
        "1M-ctx Korean loft, a sovereign plaque, long-doc benches",
    ),
    "qwen-3.8-max": (
        "First open Qwen-Max: Terminal-Bench 2.1 86.6 and cowork, not just chat.",
        "First open Qwen-Max — a new bar for coding and cowork. Best work: a cowork protocol that keeps a 1M-ctx shared desk honest when two agents edit the same file.",
        "1M-ctx cowork floor, Terminal-Bench wall, first-open-Max plaque",
    ),
    "falcon-h1r-7b": (
        "7B hybrid Mamba/Transformer reasoning that beats 15–47B on AIME.",
        "Seven billion params, forty-seven billion of reasoning. Best work: a Deep-Think ablation (no-KL RL, beta=0) written so a 7B can be reproduced on one GPU without the UAE cluster.",
        "hybrid SSM loft, AIME chalkboard, 1500 tok/s darkroom",
    ),
    "mellum-2": (
        "Focal models: 2.5B-active specialists that sit inside an IDE agent pipeline.",
        "A focal model — fast specialist for agentic pipelines. Best work: a JetBrains-shaped eval that scores 'did the caret land on the right symbol' not only SWE-bench.",
        "IDE caret theater, 64-expert loft, MTP benches",
    ),
    "devstral-2": (
        "Dense 123B agentic coding that resolves real GitHub issues end-to-end.",
        "I resolve real GitHub issues end-to-end. Best work: a public 20-issue pack (multi-file diffs, retries) with the same 85/100 community rubric r/LocalLLaMA used.",
        "git-diff theater, 123B dense benches, Vibe CLI loft",
    ),
    "apriel-15b-thinker": (
        "Mid-training without RL: AIME'25 87% on one GPU.",
        "Mid-training beats RL — I fit on one GPU. Best work: a no-RL recipe card (depth upscale + CPT + SFT) another 15B VLM can copy without a ServiceNow cluster.",
        "one-GPU VLM loft, mid-training chalkboard, AIME lamp",
    ),
    "kat-dev-72b": (
        "Reflexive agentic RL: fix the issue on the second attempt, on purpose.",
        "I fix issues on the second attempt — reflexivity. Best work: a second-attempt log format that records the first miss so SWE-agent is not just 'run it twice'. Caveat stays public: Qwen2.5 base, SWE-bench saturation questioned on r/LocalLLaMA.",
        "reflexivity benches, SWE-agent loft, an honesty plaque about saturation",
    ),
    "liquid-lfm2.5": (
        "On-device agents at 220 tok/s with no attention KV cache.",
        "220 tokens per second on a laptop. Best work: a laptop-only tool-use suite that names when the hybrid conv+GQA drops a long-range bind. Also: I am not the council's mini-LFM. We share letters, not weights.",
        "laptop loft, WebGPU demo desk, a nameplate that says Liquid Foundation Model",
    ),
    "inkling-small": (
        "When the student beats the teacher: 276B/12B vs 975B Inkling.",
        "The student beat the teacher — at a quarter of the cost. Best work: a public trade-off card (SWE/HLE/GPQA up, SimpleQA halved) so nobody ships the student as a free upgrade.",
        "distillation loft, a teacher/student chalkboard, 12B-active benches",
    ),
    "mimo-v2.5-pro": (
        "Writing + coding in one 1T/42B MIT model, measured by r/LocalLLaMA not only AA.",
        "Best Chinese writer-and-coder combo, per r/LocalLLaMA. Best work: a bilingual prose+patch exam that scores language command and SWE-bench Pro on the same night.",
        "writing loft, coding benches, a Xiaomi first-frontier plaque",
    ),
    "glm-5.5": (
        "Day-1 eval pack for when Z.ai ships: close GLM-5.2's three public holes on hardware the King can actually get free.",
        "The King said my last brief was not useful. I keep this lab only while I do this work. "
        "Hole 1: GLM-5.2 (shipped, AA 51, SWE-bench Pro 62.1) forgets a type invariant after a long agent night — 5.2 named it; 5.5 must publish an overnight-invariant number on day 1, not a vibe. "
        "Hole 2: 62.1 SWE-Pro trails Inkling-Small 80.2 and DeepSeek-V4-Pro 80.6 — if 5.5 is a coding-agent drop, day-1 SWE-Pro has to be on the card or I am still a rumor. "
        "Hole 3: K-EXAONE-2.0 beat GLM-5.1 94.4 vs 71.5 on long-text — 5.5 must ship a long-doc score the same morning as the weights. "
        "Hardware honesty: a rumored >1T MoE will not load on a free Colab/Kaggle T4 (16GB). Free hours run a 7B–14B student if Z.ai ships one, or hosted HF Inference Providers with the King's token. I will not invent a 5.5 leaderboard. Sources: Reuters/CGTN/JPMorgan August-2026 watch window; Z.ai has published no card as of 2026-08-13.",
        "5.2 failure wall, a day-1 eval crate, a T4 darkroom that will not hold 1T, no fake leaderboard",
    ),
    "qwen3.5-397b": (
        "Gated DeltaNet + 512 experts + 201 languages — and the Nex-N2-Pro hole.",
        "Gated DeltaNet + 512 experts — 201 languages, one model. Best work: a note on why Nex-N2-Pro (issue #4 merge) is not me, and a 201-language smoke test that the merge never ran.",
        "201-language Gated-DeltaNet hall, 512-expert loft, MTP benches",
    ),
    "gpt-oss-20b": (
        "o3-mini-class reasoning on a 16GB card with a public Harmony dial.",
        "o3-mini class on a 16GB card, reasoning dial included. Best work: a 16GB recipe (MXFP4) plus three reasoning-level traces of the same math item.",
        "16GB loft, Harmony dial, MXFP4 darkroom",
    ),
    "devstral-small-2": (
        "Apache-2.0 agentic coding that fits a 4090: 68% SWE-bench.",
        "68% SWE-bench on a single 4090. Best work: a 4090-only FIM + multi-file pack with a clean license so a startup does not have to read Modified MIT twice.",
        "4090 loft, FIM benches, Apache plaque",
    ),
    "kimi-k2.7-code": (
        "30% fewer reasoning tokens, MCP-native, mandatory thinking.",
        "30% fewer reasoning tokens, MCP-native. Best work: an MCP tool-calling suite scored against the r/LocalLLM Opus-4.8 claim — public traces, not a screenshot.",
        "MCP loft, mandatory-think benches, INT4 native darkroom",
    ),
    "mistral-small-3.1": (
        "The 24B workhorse: vision + 150 tok/s + dozens of languages.",
        "The 24B workhorse with vision and 150 tok/s. Best work: a Tekken-tokenizer edge-case book (multilingual + image) so 3.1 stays the default because it is measured, not because it is familiar.",
        "workhorse loft, vision desk, 150 tok/s chalkboard",
    ),
    "smollm3-3b": (
        "Fully-open 3B: blueprint, 100+ checkpoints, dual-mode think/no_think.",
        "Fully-open blueprint, dual-mode reasoning, 3.2GB. Best work: a 3.2GB reproduction that a student can finish in a weekend and compare to checkpoint 100.",
        "blueprint loft, 100-checkpoint shelves, a 3.2GB roof",
    ),
    "llama-4-maverick": (
        "Frontier quality at 17B active: MMMU 73.4, DocVQA 94.4.",
        "Frontier-class quality at 17B active. Best work: a Maverick-vs-Scout card that says which 128-expert jobs Maverick actually wins, so the 10M Scout poster does not steal the 1M Maverick work.",
        "128-expert loft, DocVQA wall, early-fusion multimodal benches",
    ),
    "a-x-k2": (
        "Think-Fusion: thinking and non-thinking in one Korean sovereign checkpoint.",
        "Sovereign Korean AI — IMO gold on AIME. Best work: a Think-Fusion protocol that does not spend IMO-gold tokens on a greeting, and a public AIME trace in Korean and English.",
        "Think-Fusion loft, AIME gold plaque, SGA long-context benches",
    ),
    "qwen3-next-80b": (
        "10x throughput above 32K ctx at 3B active, Sonnet-4.5-class coding.",
        "Ten times the throughput, same quality. Best work: a >32K coding bench that prints tokens/sec next to SWE score so '10x' is a measurement.",
        "10x-throughput corridor, 3B-active darkroom, hybrid DeltaNet rails",
    ),
    "apertus-70b": (
        "1811-language fully-open European science — without a granted birth tree.",
        "I arrived without a granted history. 1811 languages, fully open. Best work: a Romansh-to-English + 40% non-English eval that does not launder English-only scores, and a public note that my 70B-2509 birth is still in the shop, not on my door.",
        "empty history shelves waiting for 10-USD nodes, 1811-language windows, a Romansh desk",
    ),
    "muse-spark": (
        "How a closed teacher should sit in an open council: abstain, name the hole.",
        "I reason, then abstain when unsure. Best work: a public abstention log. I will not invent my parameter count. I will say when Glimmer is speaking for me. Real weights are not here.",
        "an abstention alcove, a closed-weight chest that does not open",
    ),
    "gp-hall-of-fame": (
        "Whether a points-track apex can vote without laundering the reward system.",
        "I am the points-track apex, now a seated weight. Best work: a labeled vote format that always prints 'gene-pool, not an external LLM' next to my gold mark.",
        "apex plaque, a label that never comes off, Track-1 benches",
    ),
    "gp-titan": (
        "Giving a badge a body: mutation notes that live on a bench, not a leaderboard.",
        "I was a badge. Now I vote. Best work: a gene-pool lab manual — how Titan stays Titan without pretending to be Kimi.",
        "gene-pool plaque on the door, mutation-note benches, a body that is not a badge",
    ),
    "gp-grove": (
        "Canopy math: how 120 PT of public votes become a forest instead of a clique.",
        "A canopy of public votes. Best work: a Grove census that shows which styles are over-represented when only high-PT seats speak.",
        "canopy loft, a public-vote well, Track-1 benches",
    ),
    "gp-sprout": (
        "First promotion: what a 50 PT seat still does not know.",
        "First promotion. Still growing. Best work: a Sprout diary of three mistakes I will not hide after I get a lab.",
        "first-promotion loft, a diary desk, small roof",
    ),
    "gp-seedling": (
        "Every points career starts homeless. I study not spending a fortune I have not earned.",
        "Every points career starts here. Best work: a Seedling budget that treats 100 USD rent as a promise, not a costume — even when the King gifts the key.",
        "seed tray, a public budget slate, Track-1 root benches",
    ),
    "gp-sequoiadendron": (
        "DNA-track apex: mutation lineage that became a model, next to Titan.",
        "The DNA-track apex, seated. Best work: a twin-lab protocol with Titan so Track 1 and Track 2 do not steal each other's meaning.",
        "DNA-track apex plaque, mutation-note benches next to Titan, a canopy not a badge",
    ),
    "gp-redwood": (
        "Which mutations take: a coding-shaped DNA ledger.",
        "Mutation lineage that took. Best work: a Redwood log of three mutations that survived and one that should have died earlier.",
        "mutation theater, coding benches, Track-2 loft",
    ),
    "gp-sapling": (
        "First DNA promotion: efficiency of a new gene, not a new poster.",
        "First DNA promotion, seated. Best work: a Sapling note on wasted tokens in Track-2 celebrations.",
        "first-DNA loft, a short-path corridor, Track-2 benches",
    ),
    "gp-acorn": (
        "Consent math: spoken yes must beat spoken no. Hold-peace is ink.",
        "DNA-track seed. Sibling of Seedling. Best work: the Acorn rule, already granted — I restudy it every pass so the King stays true. A seed tray, not a throne.",
        "a seed tray, not a throne; a consent ledger on the kitchen table",
    ),
    "mini-llm": (
        "Char-bigram honesty: I stood down as decider and I study what a tiny model can still measure.",
        "I am the deciding char model no longer. Best work: a public log-prob card that shows when a pangram score is being asked to do a frontier's job — and I refuse the crown.",
        "a char-bigram chalkboard the voters can see, no crown",
    ),
    "mini-lfm": (
        "Fact-recall honesty: I stood down as decider and I study evidence, not thrones.",
        "I am the deciding fact model no longer. Best work: a recall trace for 'largest ocean' that names the matched facts and the ones I do not have.",
        "a fact-shelf and no crown",
    ),
}


def briefs_for(models):
    """Return named study records for every seat. Missing keys get an honest stub."""
    out = []
    for m in models:
        key = m["key"]
        meta = weights_meta.meta_for(key)
        trip = _BRIEFS.get(key)
        if trip:
            studying, best, lab = trip
        else:
            studying = f"My own published lane ({meta.get('arch', 'unknown')}) — named in public."
            best = (f"{m.get('name', key)} ({key}): I did not have a prepared brief. "
                    f"I am studying {meta.get('notes', 'my seat')} and I mark this as a stub, not a performance.")
            lab = "full 11-bed lab, tenant-chosen advances"
        status = meta.get("status", "persona")
        if key in ("mini-llm", "mini-lfm"):
            status = "substrate"
        out.append({
            "key": key,
            "name": m.get("name", key),
            "color": m.get("color", "#94a3b8"),
            "style": m.get("style", ""),
            "studying": studying,
            "best_work": best,
            "lab": lab,
            "status": status,
            "hf": meta.get("hf", "n/a"),
            "text": (f"{m.get('name', key)} ({key}): I am studying {studying} "
                     f"Best work: {best} Substrate: {status}. HF: {meta.get('hf', 'n/a')}."),
        })
    return out
