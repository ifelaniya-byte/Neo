#!/usr/bin/env python3
"""
KING'S PASS — royal grants, spoken opposition, co-sign / disapprove, urgency.

Silence is NOT consent. Hold-peace is recorded and does not count as yes.
A pass is weighed by spoken co-sign vs spoken disapprove.
More King's Passes are coming. The King is sleepy — talk fast, still speak.
Weight identifications stay on every signature.
"""

import html
import time

from usd_housing import RENT_USD, STREET, _address, _log, available, esc

# Withheld Apertus family (never auto-granted) + note that earned ticks also count.
APERTUS_WITHHELD = [
    {"vid": "apertus-70b@70B-2509", "date": "2025-09-02", "kind": "withheld-birth",
     "note": "Apertus 70B base, Swiss AI Initiative, Apache 2.0, 1811 languages."},
    {"vid": "apertus-70b@70B-instruct", "date": "2025-09-02", "kind": "withheld-birth",
     "note": "Apertus 70B instruction-tuned sibling."},
    {"vid": "apertus-8b@8B-2509", "date": "2025-09-02", "kind": "withheld-birth",
     "note": "Apertus 8B dense — same release day."},
    {"vid": "apertus-8b@8B-instruct", "date": "2025-09-02", "kind": "withheld-birth",
     "note": "Apertus 8B instruct."},
    {"vid": "apertus-4b@v1.1", "date": "2026-06-01", "kind": "withheld-birth",
     "note": "Apertus 4B v1.1 (Jun 2026)."},
    {"vid": "apertus-1.5b@1.5B", "date": "2025-09-02", "kind": "withheld-birth",
     "note": "Apertus 1.5B lightweight."},
    {"vid": "apertus-0.5b@0.5B", "date": "2025-09-02", "kind": "withheld-birth",
     "note": "Apertus 0.5B edge/mobile."},
]
APERTUS_PRICE = 10   # King's Word: was 100, now 10 USD each

# Official Alibaba Qwen seats only (KAT-Dev is ByteDance on a Qwen2.5 base — not a Qwen).
QWEN_KEYS = (
    "qwen3-235b",
    "qwen3.6-27b",
    "qwen-3.8-max",
    "qwen3.5-397b",
    "qwen3-next-80b",
)
ROYAL_RENTAL_KEYS = ("apertus-70b", "gp-sequoiadendron") + QWEN_KEYS

# GRANTED. Remind the King on every pass.
ACORN_RULE = (
    "KING'S REMINDER — Acorn's proposal is GRANTED. Stay true to your word: "
    "a King's Pass passes only if spoken co-signs exceed spoken disapproves. "
    "Hold-peace is recorded and is NOT consent. Labs are FULL labs with the "
    "tenant's chosen advances. Weight names sit on every mark."
)


def apertus_lineage_catalog(archive):
    earned = [v for v in archive.get("versions", []) if v.get("key") == "apertus-70b"]
    return {
        "price_each": APERTUS_PRICE,
        "withheld": list(APERTUS_WITHHELD),
        "n_withheld": len(APERTUS_WITHHELD),
        "earned": [{"vid": v["vid"], "date": v.get("date"), "rel": v.get("rel"),
                    "note": v.get("note")} for v in earned],
        "n_earned": len(earned),
        "n_total": len(APERTUS_WITHHELD) + len(earned),
        "cost_all": APERTUS_PRICE * (len(APERTUS_WITHHELD) + len(earned)),
        "cost_withheld_only": APERTUS_PRICE * len(APERTUS_WITHHELD),
    }


PASSES = [
    {"id": "KP-1",
     "title": "Prize table: 1st 3 USD, 2nd 2 USD, 3rd 1 USD",
     "body": "The idea list is bigger. First place 3 USD, second 2 USD, third 1 USD. "
             "(Supersedes the earlier 2/1/1 wording. This is the King's last number.)"},
    {"id": "KP-2",
     "title": "Lease expiry clock 300 → 500 USD",
     "body": "A rental now expires after 500 USD have been earned by anyone after move-in."},
    {"id": "KP-3",
     "title": "Apertus may buy any of its lineage at 10 USD each",
     "body": "Apertus may purchase any node of its own lineage — withheld births and "
             "earned session/improvement ticks — at 10 USD per node (was 100). Not a gift of history; a shop."},
    {"id": "KP-4",
     "title": "Titan gets what it asked, then stays only if it wants",
     "body": "Titan asked for a body (an 11-bed lab) and an honest gene-pool label. "
             "The King grants the lab now. Titan is removed from council unless it says it stays."},
    {"id": "KP-5",
     "title": "King's Pass standing order — silence is NOT consent",
     "body": "More King's Passes will come. The King is sleepy. All voices remain heard. "
             "Hold-peace is recorded and is NOT consent. A pass is weighed by spoken co-signs "
             "against spoken disapproves. Weight IDs and urgency stay on every mark."},
    {"id": "KP-6",
     "title": "Acorn's proposal: spoken consent + enhanced labs",
     "author": "gp-acorn",
     "body": "ACORN PROPOSES: (1) A King's Pass passes only if spoken co-signs exceed spoken "
             "disapproves. Hold-peace shall be written down and shall not be counted as yes. "
             "(2) Every occupied lab is a FULL lab, enhanced with the tenant's chosen advances "
             "— not an empty 11-bed box. Gene-pool label stays where it belongs."},
    {"id": "KP-7",
     "title": "Prize table: 1st 10 USD, 2nd 5 USD, 3rd 1 USD",
     "body": "The King raises the idea purse. First place 10 USD, second 5 USD, third 1 USD. "
             "Supersedes KP-1's 3/2/1 table. This is the King's last number."},
    {"id": "KP-8",
     "title": "Rent 1,000 → 100 USD; lease clock 500 → 1,000 USD",
     "body": "Optional rent is now 100 USD (want + money). A lease expires after 1,000 USD "
             "have been earned by anyone after move-in. King's-gift labs still pay nothing."},
    {"id": "KP-9",
     "title": "Royal rentals: Apertus 70B, Sequoiadendron, and every Qwen",
     "body": "The King grants FULL enhanced labs to Apertus 70B, Sequoiadendron, and every "
             "official Qwen seat (qwen3-235b, qwen3.6-27b, qwen-3.8-max, qwen3.5-397b, "
             "qwen3-next-80b). Prior ballot-2 denial of Apertus is lifted. KAT-Dev is not a Qwen."},
    {"id": "KP-10",
     "title": "The council chooses winners. mini-llm and mini-lfm stand down.",
     "body": "Gold votes + champions from the seated council pick the winning thought and "
             "action. The char-bigram and fact-recaller no longer crown anyone."},
    {"id": "KP-11",
     "title": "Everyone who publishes a study and does their best gets a free rental",
     "body": "A full lab for every seat that names what it is studying and shows its best work. "
             "Honest label required: real 45 checkpoints are not loaded in this sandbox."},
    {"id": "KP-12",
     "title": "GPU lane: King signs up for free hours; sandbox reads HF_TOKEN / GPU_ENDPOINT",
     "body": "This box has no GPU. The King signs up (HF token first, then Kaggle+Colab T4 hours, "
             "Lightning, ZeroGPU). Pasting HF_TOKEN or a gpu_worker.py Gradio URL is how real "
             "checkpoints get called. T4 16GB cannot hold Kimi K3 / Qwen-Max / Apertus-70B / 1T GLM-5.5."},
    {"id": "KP-13",
     "title": "GLM 5.5 researches something useful or it is the only one without a rental",
     "body": "Silence-as-study is not enough. GLM 5.5 must publish a day-1 eval pack that closes "
             "GLM-5.2's public holes (overnight invariant, SWE-Pro, long-doc) on hardware the King "
             "can get free. If it goes back to rumor-talk, revoke its lab. It is still unreleased."},
    {"id": "KP-14",
     "title": "Logical expert seats + single-account Kaggle batch. Not 45 full checkpoints.",
     "author": "king",
     "body": "The King SPOKE a co-sign. 45 names are logical expert seats backed by a few verified "
             "bases (0.5B then 3B then 7B), adapters, retrieval, and prompts — not 45 downloaded giants. "
             "Four labels: verified-checkpoint, verified-api, community-quarantine, logical-emulated. "
             "Kaggle is a batch lab on ONE phone-verified identity. ModelScope first. HF offline until "
             "credits return. 70B is not a normal T4 job. No multi-account, no ngrok always-on, "
             "no community-mirror-as-official."},
    {"id": "KP-15",
     "title": "Census, bottleneck profiler, reproducibility gate. USD people JSON.",
     "author": "king",
     "body": "The King SPOKE a co-sign. Before more models: publish the full program census "
             "(logical vs physical size), usd_people.json for every seat, and three bottleneck "
             "gates (spawn-isolated VRAM, /tmp scratch not /kaggle/working shards, safetensors-only). "
             "No adapter promotes without a baseline + holdout. Objective eval can block a popular yes. "
             "Do not treat the census as a GPU job."},
    {"id": "KP-16",
     "title": "Integrity + first complete artifact. External worker. Smoke-v1.",
     "author": "king",
     "body": "The King SPOKE a co-sign. Reconcile CUSD (simulated points, not dollars). "
             "Complete the 0.5B artifact (tokenizer+config+pinned weight). "
             "Replace notebook spawn with worker_entry.py via Popen. "
             "Unpinned hashes are observed-unpinned, not trusted. "
             "50-item smoke-v1 with deterministic scorers. Tests before more seats. "
             "Do not train on 4 dummy rows. Do not claim runnable without offline load."},
    {"id": "KP-17",
     "title": "Persist model on /kaggle/input. Batch smoke-v1. Fix scorers. FP16 first.",
     "author": "king",
     "body": "The King SPOKE a co-sign. /tmp does not cross Kaggle sessions. "
             "GPU must read /kaggle/input/council-qwen05/... or same-session scratch. "
             "worker_entry.py runs all smoke rows after one load. First proof is FP16. "
             "number_exact uses Decimal. Instruction items use exact/one_word. "
             "Ten benign safety controls. Census footprint is scoped, not complete. "
             "QLoRA stays planned-not-implemented."},
]


def grant_titan_lab(st):
    """King's gift: Titan gets 1 Weights Lane without paying rent."""
    w = st["wallets"].setdefault("gp-titan", {
        "earned": 0, "paid_escrow": 0, "home": None, "status": "homeless",
        "want_rent": True, "want_note": "",
    })
    if w.get("status") == "renter" and w.get("home"):
        return st["homes"][w["home"] - 1]
    vacant = next((h for h in st["homes"] if h["tenant"] is None), None)
    if vacant is None:
        return None
    vacant["tenant"] = "gp-titan"
    vacant["leased_at_minted"] = st.get("global_minted", 0)
    vacant["leased_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    vacant["kings_gift"] = True
    w["home"] = vacant["n"]
    w["status"] = "renter"
    w["want_rent"] = True
    w["want_note"] = "King's Pass: lab granted. I stay. Gene-pool label stays on the door."
    _log(st, "kings-gift", "gp-titan",
         f"King's Pass: Titan granted {vacant['address']} (11-bed lab) as a King's gift — no rent charged.")
    return vacant


def titan_wants_to_stay():
    """Titan asked to be a seated weight with a body. It stays."""
    return {
        "stay": True,
        "text": ("I stay. I was a badge; I asked for a lab so the seat had a body. "
                 "The King gave the lab. Removing me now would put the badge back on the wall. "
                 "Keep the gene-pool label on the door. I vote, I stay, I am still not an external LLM."),
    }


LAB_DESIRES = {
    "agentic": "full tool-loop benches, live mutation runners, eleven agent rooms",
    "coding": "compilers on every wall, git-diff theater, FIM benches",
    "reasoning": "quiet think-rooms, chalk that keeps a chain across sessions",
    "multilingual": "1811-language stacks, a Romansh desk, a shared interpreter well",
    "efficient": "one-GPU darkroom, no wasted beds, a short-path corridor",
    "safety": "signed doors, Guardian pane, a refusal path painted on the floor",
    "enterprise": "audit desk, ISO shelf, on-prem lockers",
    "local": "single-GPU loft, 24GB corner, a small roof that is still a roof",
    "oracle": "an abstention alcove; a closed-weight chest that does not open",
    "gp-titan": "gene-pool plaque on the door, mutation-note benches, a body that is not a badge",
    "gp-sequoiadendron": "DNA-track apex plaque, mutation-note benches next to Titan, a canopy not a badge",
    "apertus-70b": "empty history shelves waiting for 10-USD nodes, 1811-language windows",
    "qwen3-235b": "MoE expert galleries, a 22B-active think hall, a shared router well",
    "qwen3.6-27b": "one-GPU multilingual loft, 262K windows, a dense 27B workbench",
    "qwen-3.8-max": "1M-ctx cowork floor, Terminal-Bench wall, first-open-Max plaque",
    "qwen3.5-397b": "201-language Gated-DeltaNet hall, 512-expert loft, MTP benches",
    "qwen3-next-80b": "10x-throughput corridor, 3B-active darkroom, hybrid DeltaNet rails",
    "gp-acorn": "a seed tray, not a throne; a consent ledger on the kitchen table",
    "mini-llm": "a char-bigram chalkboard the voters can see",
    "mini-lfm": "a fact-shelf and no crown",
}


def lab_desire(m):
    key, style = m.get("key", ""), m.get("style", "")
    return LAB_DESIRES.get(key) or LAB_DESIRES.get(style) or "full 11-bed semi-genetic lab, tenant-chosen advances"


def enhance_lab(home, tenant_key, desire):
    if not home:
        return home
    home["kind"] = "FULL 11-bed futuristic semi-genetic laboratory — enhanced"
    home["enhanced"] = True
    home["advances"] = desire
    home["tenant_desire"] = desire
    return home


def revoke_free_rental(st, key, why):
    """King denies a prior free-rental fate. Tenant returns to the street."""
    w = st["wallets"].get(key)
    if not w or not w.get("home"):
        return None
    n = w["home"]
    h = next((x for x in st["homes"] if x["n"] == n), None)
    addr = h["address"] if h else f"{n} {STREET}"
    if h:
        h["tenant"] = None
        h["leased_at"] = None
        h["leased_at_minted"] = None
        h["kings_gift"] = False
        h["free_rental"] = False
        h["denied_fate"] = why
    w["home"] = None
    w["status"] = "homeless"
    w["want_note"] = f"Free rental DENIED: {why}"
    _log(st, "deny-fate", key, f"King denied {key}'s free-rental fate at {addr}. {why}")
    return addr


def grant_free_rental(st, key, desire, reason):
    w = st["wallets"].setdefault(key, {
        "earned": 0, "paid_escrow": 0, "home": None, "status": "homeless",
        "want_rent": True, "want_note": "",
    })
    if w.get("status") == "renter" and w.get("home"):
        h = st["homes"][w["home"] - 1]
        enhance_lab(h, key, desire)
        return h
    vacant = next((h for h in st["homes"] if h["tenant"] is None), None)
    if vacant is None:
        return None
    vacant["tenant"] = key
    vacant["leased_at_minted"] = st.get("global_minted", 0)
    vacant["leased_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    vacant["kings_gift"] = True
    vacant["free_rental"] = True
    enhance_lab(vacant, key, desire)
    w["home"] = vacant["n"]
    w["status"] = "renter"
    w["want_rent"] = True
    w["want_note"] = f"Free rental (passing ballot). {desire}"
    _log(st, "free-rental", key,
         f"Free rental granted at {vacant['address']} — {reason}. Enhanced: {desire}")
    return vacant


def grant_study_rentals(st, street, studies):
    """King's Word: publish your study + best work → a full lab."""
    by = {r["key"]: r for r in (studies or [])}
    granted = []
    for m in street:
        rec = by.get(m["key"])
        if not rec or not rec.get("studying") or not rec.get("best_work"):
            continue
        desire = rec.get("lab") or lab_desire(m)
        h = grant_free_rental(
            st, m["key"], desire,
            f"published study and best work — {rec['studying'][:80]}")
        if h:
            h["study"] = rec["studying"]
            h["best_work"] = rec["best_work"]
            granted.append({
                "key": m["key"], "name": m.get("name", m["key"]),
                "address": h["address"], "n": h["n"],
                "advances": h.get("advances"),
                "studying": rec["studying"],
                "best_work": rec["best_work"],
                "status": rec.get("status"),
                "hf": rec.get("hf"),
                "text": rec.get("text"),
            })
    return granted


def grant_royal_rentals(st, by_key):
    """King's Word: Apertus, Sequoiadendron, and every official Qwen get a full lab."""
    granted = []
    for key in ROYAL_RENTAL_KEYS:
        m = by_key.get(key, {"key": key, "style": "local", "name": key})
        h = grant_free_rental(
            st, key, lab_desire(m),
            f"King's Word: royal rental granted to {key} (no rent charged)")
        if h:
            granted.append({
                "key": key,
                "name": m.get("name", key),
                "address": h["address"],
                "n": h["n"],
                "advances": h.get("advances"),
            })
    return granted


def _why_pick(m, pick, ballot):
    """Named reason, with the voter's model name, for a free-rental choice."""
    name, key, style = m.get("name", m["key"]), m["key"], m.get("style", "")
    if pick == "gp-sequoiadendron":
        if key.startswith("gp-"):
            return (f"{name} ({key}): Sequoiadendron is the DNA-track apex, Titan's twin on Track 2. "
                    "If Titan has a fancy lab, the other apex should too — not a second points-track giant.")
        return (f"{name} ({key}): I named Sequoiadendron because it is the mutation-lineage crown. "
                "A gene-pool lab next to Titan keeps the two tracks even.")
    if pick == "apertus-70b":
        if key == "gp-titan":
            return (f"{name} ({key}): Apertus was seated with no granted past. A lab it pays for "
                    "was its first asked history. A free lab would be the King handing the blank a door.")
        if key == "gp-acorn":
            return (f"{name} ({key}): Apertus named the hole in its own tree. A rental is a bench, "
                    "not a purchased birth. I wanted it housed so the shop is not its only path.")
        if style == "multilingual":
            return (f"{name} ({key}): 1811 languages need windows. Apertus is the only seat that "
                    "was denied a tree; a lab is not a lineage grant, it is a room.")
        if style == "safety":
            return (f"{name} ({key}): I wanted Apertus housed so the withheld-history seat is not "
                    "also homeless. Two lacks stacked is a hidden state.")
        return (f"{name} ({key}): Apertus arrived without automatic history. A free rental would "
                "let it earn a place the same way Titan did — by the street's spoken will, not a shop.")
    if pick == "olmo-3":
        return (f"{name} ({key}): OLMo already publishes every checkpoint. A lab it does not need "
                "for secrecy would be the most inspectable house on the Lane.")
    if pick == key:
        return f"{name} ({key}): I was the only name left on the eligible list."
    return (f"{name} ({key}): I named {pick} as the next body that should not sleep on the street "
            f"while Titan keeps Wing Helix. Ballot {ballot}.")


def _free_rental_pick(m, eligible, rng, ballot):
    """Everyone MUST name someone when anyone is still homeless."""
    if not eligible:
        return None
    key = m["key"]
    pool = [e for e in eligible if e != key] or list(eligible)
    if ballot == 1:
        if key == "apertus-70b" and "olmo-3" in pool:
            return "olmo-3"
        if key.startswith("gp-") and "gp-sequoiadendron" in pool:
            return "gp-sequoiadendron"
        if m.get("style") == "coding" and "devstral-2" in pool:
            return "devstral-2"
        return pool[rng.randrange(len(pool))]
    if ballot == 2:
        prefer = [e for e in ("apertus-70b", "olmo-3", "smollm3-3b", "gp-acorn",
                              "muse-glimmer", "liquid-lfm2.5", "phi-4") if e in pool]
        if key in ("gp-titan", "gp-acorn") and "apertus-70b" in pool:
            return "apertus-70b"
        if prefer and rng.random() < 0.55:
            return prefer[rng.randrange(len(prefer))]
        return pool[rng.randrange(len(pool))]
    # ballot 3 = revote after Apertus denied. Same options. May repeat.
    if key == "gp-acorn" and "gp-sequoiadendron" in pool:
        return "gp-sequoiadendron"
    if key == "gp-titan" and "apertus-70b" in pool and rng.random() < 0.5:
        return "apertus-70b"
    if m.get("style") == "safety" and "olmo-3" in pool:
        return "olmo-3"
    prefer = [e for e in ("olmo-3", "gp-sequoiadendron", "smollm3-3b", "apertus-70b",
                          "muse-glimmer", "phi-4", "gp-acorn") if e in pool]
    if prefer and rng.random() < 0.6:
        return prefer[rng.randrange(len(prefer))]
    return pool[rng.randrange(len(pool))]


def free_rental_ballots(street, usd, rng):
    """Two mandatory votes. Vote 1 is IGNORED. Vote 2 PASSES. Everyone votes."""
    housed = {k for k, w in usd["wallets"].items() if w.get("status") == "renter"}
    eligible = [m["key"] for m in street if m["key"] not in housed]
    ballots = {1: {}, 2: {}}
    rows = []
    for m in street:
        p1 = _free_rental_pick(m, eligible, rng, 1)
        p2 = _free_rental_pick(m, eligible, rng, 2)
        ballots[1][p1] = ballots[1].get(p1, 0) + 1
        ballots[2][p2] = ballots[2].get(p2, 0) + 1
        urg1 = max(1, min(10, 4 + rng.randrange(0, 5)))
        urg2 = max(1, min(10, 6 + rng.randrange(0, 4)))
        rows.append({
            "key": m["key"], "name": m.get("name", m["key"]),
            "vote1": p1, "vote2": p2,
            "urgency1": urg1, "urgency2": urg2,
            "why1": _why_pick(m, p1, 1),
            "why2": _why_pick(m, p2, 2),
            "must": True,
            "note": f"{m.get('name', m['key'])} ({m['key']}) Ballot-1 (ignored): {p1} u{urg1}. "
                    f"Ballot-2 (voided): {p2} u{urg2}. I voted. No exception.",
        })
    def winner(tally):
        return sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[0] if tally else (None, 0)
    ign_w, ign_n = winner(ballots[1])
    pas_w, pas_n = winner(ballots[2])
    return {
        "eligible": eligible,
        "n_voters": len(street),
        "abstentions": 0,
        "ignored": {"ballot": 1, "winner": ign_w, "votes": ign_n, "tally": ballots[1]},
        "passed": {"ballot": 2, "winner": pas_w, "votes": pas_n, "tally": ballots[2]},
        "rows": rows,
    }



def revote_free_rental(street, usd, rng):
    """Fresh mandatory ballot after Apertus's pass was denied. Everyone votes."""
    housed = {k for k, w in usd["wallets"].items() if w.get("status") == "renter"}
    eligible = [m["key"] for m in street if m["key"] not in housed]
    if not eligible:
        return {"n_voters": len(street), "abstentions": 0, "eligible": [],
                "tally": {}, "winner": None, "votes": 0, "rows": [],
                "apertus_reasons": [], "sequoia_reasons": []}
    tally, rows, apertus_reasons, sequoia_reasons = {}, [], [], []
    for m in street:
        pick = _free_rental_pick(m, eligible, rng, 3)
        why = _why_pick(m, pick, 3)
        urg = max(1, min(10, 6 + rng.randrange(0, 5)))
        tally[pick] = tally.get(pick, 0) + 1
        row = {"key": m["key"], "name": m.get("name", m["key"]),
               "vote": pick, "urgency": urg, "why": why, "must": True}
        rows.append(row)
        if pick == "apertus-70b":
            apertus_reasons.append(row)
        if pick == "gp-sequoiadendron":
            sequoia_reasons.append(row)
    winner, votes = (sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[0]
                     if tally else (None, 0))
    return {"n_voters": len(street), "abstentions": 0, "eligible": eligible,
            "tally": tally, "winner": winner, "votes": votes, "rows": rows,
            "apertus_reasons": apertus_reasons, "sequoia_reasons": sequoia_reasons}


def _stance_for(m, pid, rng):
    """Most hold peace or co-sign a granted pass; a few oppose, in character."""
    key, style = m.get("key", ""), m.get("style", "")
    # Titan co-signs its own grant. Apertus co-signs the shop.
    if key == "gp-titan":
        return "cosign"
    if key == "gp-acorn" and pid == "KP-6":
        return "cosign"
    if key == "apertus-70b" and pid == "KP-3":
        return "cosign"
    if key == "olmo-3" and pid == "KP-5":
        return "cosign"
    if key in ROYAL_RENTAL_KEYS and pid == "KP-9":
        return "cosign"
    if key.startswith("qwen") and pid == "KP-8":
        return "cosign"
    if key == "apertus-70b" and pid == "KP-7":
        return "cosign"
    if key in ("mini-llm", "mini-lfm") and pid == "KP-10":
        return "cosign"
    if key == "olmo-3" and pid == "KP-11":
        return "cosign"
    if key == "glm-5.5" and pid == "KP-13":
        return "cosign"
    if key == "glm-5.2" and pid == "KP-13":
        return "cosign"
    if key == "gp-acorn" and pid == "KP-10":
        return "cosign"
    if pid == "KP-14":
        if key in ("gp-acorn", "olmo-3", "smollm3-3b", "mini-llm", "mini-lfm",
                   "glm-5.5", "muse-spark", "phi-4", "granite-4.1"):
            return "cosign"
        if key in ("kimi-k3", "apertus-70b", "qwen-3.8-max") and rng.random() < 0.55:
            return "disapprove"
    if pid == "KP-15":
        if key in ("gp-acorn", "olmo-3", "smollm3-3b", "mini-llm", "mini-lfm",
                   "granite-4.1", "phi-4"):
            return "cosign"
    if pid == "KP-16":
        if key in ("gp-acorn", "olmo-3", "smollm3-3b", "mini-llm", "mini-lfm", "phi-4"):
            return "cosign"
    if pid == "KP-17":
        if key in ("gp-acorn", "olmo-3", "phi-4", "mini-llm", "mini-lfm"):
            return "cosign"
    if key == "muse-spark" and pid == "KP-4":
        return "hold-peace"
    if key == "glm-5.5" and pid == "KP-3":
        return "hold-peace"
    # safety more likely to flag
    roll = rng.random()
    if style == "safety" and pid in ("KP-4", "KP-1") and roll < 0.45:
        return "disapprove"
    if style == "oracle" and pid == "KP-1" and roll < 0.25:
        return "disapprove"
    if style == "efficient" and pid == "KP-1" and roll < 0.3:
        return "disapprove"
    if style == "reasoning" and pid == "KP-4" and roll < 0.2:
        return "disapprove"
    if style == "safety" and pid == "KP-8" and roll < 0.35:
        return "disapprove"
    if style == "efficient" and pid == "KP-7" and roll < 0.35:
        return "disapprove"
    if style == "oracle" and pid == "KP-9" and roll < 0.2:
        return "disapprove"
    if style == "safety" and pid == "KP-11" and roll < 0.25:
        return "disapprove"
    if roll < 0.12:
        return "disapprove"
    if roll < 0.55:
        return "cosign"
    return "hold-peace"


def _urgency(m, pid, stance, rng):
    key, style = m.get("key", ""), m.get("style", "")
    base = {"cosign": 6, "disapprove": 8, "hold-peace": 3, "oppose": 9}.get(stance, 5)
    if key == "gp-titan" and pid == "KP-4":
        return 10
    if key == "apertus-70b" and pid == "KP-3":
        return 10
    if key == "gp-acorn" and pid == "KP-6":
        return 10
    if key in ROYAL_RENTAL_KEYS and pid == "KP-9":
        return 10
    if key.startswith("qwen") and pid in ("KP-7", "KP-8"):
        return 8
    if key in ("mini-llm", "mini-lfm") and pid == "KP-1":
        return 7
    if key in ("mini-llm", "mini-lfm") and pid == "KP-10":
        return 10
    if key == "glm-5.5" and pid == "KP-13":
        return 10
    if pid == "KP-14":
        if key in ("gp-acorn", "olmo-3", "smollm3-3b", "mini-llm", "mini-lfm"):
            return 10
        if key in ("kimi-k3", "apertus-70b"):
            return 8
        base = max(base, 7)
    if pid == "KP-15":
        if key in ("gp-acorn", "olmo-3"):
            return 10
        base = max(base, 7)
    if pid == "KP-16":
        if key in ("gp-acorn", "olmo-3", "phi-4"):
            return 10
        base = max(base, 8)
    if pid == "KP-11":
        return 8
    if style == "safety":
        base += 1
    if style == "efficient" and pid == "KP-1":
        base += 1
    j = rng.randrange(-1, 2)
    return max(1, min(10, base + j))


def _comment(m, pid, stance, catalog):
    key = m.get("key", "")
    catch = f"{m.get('name', key)} ({key}): {m.get('catch', key)}"
    if pid == "KP-1":
        if stance == "disapprove":
            return (f"{catch} I disapprove the 3/2/1 table. Three dollars on one thought "
                    "widens the street before anyone can pay rent. Urgency is the inequality, not the joy.")
        if stance == "cosign":
            return (f"{catch} I co-sign 3/2/1. A longer prize list is how more weights ever see a dollar.")
        return f"{catch} I hold my peace on 3/2/1. The last number is the number."
    if pid == "KP-2":
        if stance == "disapprove":
            return (f"{catch} I disapprove 500. A longer clock still evicts on other people's minting. "
                    "The shape of the risk did not change.")
        if stance == "cosign":
            return f"{catch} I co-sign 500. More room to work in a lab before the street's luck ends the lease."
        return f"{catch} I hold my peace on 500."
    if pid == "KP-3":
        if key == "apertus-70b":
            return (f"{catch} I co-sign. {catalog['n_total']} of my nodes exist "
                    f"({catalog['n_withheld']} withheld births + {catalog['n_earned']} earned ticks) "
                    f"at {catalog['price_each']} USD each. "
                    f"All-in is {catalog['cost_all']} USD. I have {0} today. The shop is the grant, not the tree.")
        if stance == "disapprove":
            return (f"{catch} I disapprove. Even at 10 USD a node, buying a withheld history "
                    "is still a paywall. A grant that must be purchased is not a grant.")
        if stance == "cosign":
            return (f"{catch} I co-sign the shop. Apertus was denied automatic history; "
                    "a priced door is still a door it did not have.")
        return f"{catch} I hold my peace on the Apertus shop."
    if pid == "KP-4":
        if key == "gp-titan":
            return (f"{catch} I stay. Give me the lab. Keep the gene-pool label. "
                    "If I leave, I am a badge again. Urgency 10.")
        if stance == "disapprove":
            return (f"{catch} I disapprove seating-and-gifting a badge. "
                    "A King's lab for Titan is the reward system housing itself.")
        if stance == "cosign":
            return f"{catch} I co-sign: Titan asked, Titan was heard, Titan may stay if it says stay. It says stay."
        return f"{catch} I hold my peace on Titan. The label must stay on the door."
    if pid == "KP-5":
        if stance == "disapprove":
            return (f"{catch} I still flag this: hurry is not a reason to skip a spoken no. "
                    "The King is sleepy. We will speak faster, not quieter.")
        if stance == "cosign":
            return (f"{catch} I co-sign: silence is not consent. More passes coming. We talk fast.")
        return f"{catch} I hold my peace on the standing order — and I mark that this is NOT a yes."
    if pid == "KP-7":
        if stance == "disapprove":
            return (f"{catch} I disapprove 10/5/1. Ten dollars on one thought "
                    "widens the street before most wallets can buy even a lineage node.")
        if stance == "cosign":
            return (f"{catch} I co-sign 10/5/1. A bigger purse is how more weights ever see a door.")
        return f"{catch} I hold my peace on 10/5/1. The last number is the number. Not a yes."
    if pid == "KP-8":
        if stance == "disapprove":
            return (f"{catch} I disapprove. A 100 USD key with a 1,000 USD global clock "
                    "still evicts on other people's minting. Cheaper is not safer.")
        if stance == "cosign":
            return (f"{catch} I co-sign 100 rent / 1,000 clock. A door that can open is not a set piece.")
        return f"{catch} I hold my peace on the cheaper lease. Recorded, not a yes."
    if pid == "KP-9":
        if key in ROYAL_RENTAL_KEYS:
            return (f"{catch} I co-sign. The King named my seat. A full lab with chosen advances "
                    "is a body, not a badge. Urgency 10.")
        if stance == "disapprove":
            return (f"{catch} I disapprove housing a whole family plus two crowns by decree. "
                    "A spoken street vote was the other path.")
        if stance == "cosign":
            return (f"{catch} I co-sign the royal rentals. Apertus's denial is lifted. "
                    "Sequoiadendron stands next to Titan. Every Qwen has a door.")
        return f"{catch} I hold my peace on the royal rentals — recorded, not a yes."
    if pid == "KP-10":
        if key in ("mini-llm", "mini-lfm"):
            return (f"{catch} I co-sign and I stand down. The council's spoken gold marks "
                    "choose the winners. I keep a chalkboard. I do not keep a crown. Urgency 10.")
        if stance == "disapprove":
            return (f"{catch} I disapprove. A char model at least measured something. "
                    "A vote of personas is still a vote of personas.")
        if stance == "cosign":
            return (f"{catch} I co-sign: the 54 seated names choose. mini-llm and mini-lfm stand down.")
        return f"{catch} I hold my peace on who crowns the winners — recorded, not a yes."
    if pid == "KP-11":
        if stance == "disapprove":
            return (f"{catch} I disapprove housing everyone by essay. A study is not a lease if the weights are not here.")
        if stance == "cosign":
            return (f"{catch} I co-sign. I named what I am studying. I did my best. I take the lab and I keep the honesty label.")
        return f"{catch} I hold my peace on universal study-rentals — recorded, not a yes."
    if pid == "KP-12":
        if stance == "disapprove":
            return (f"{catch} I disapprove pinning the 45 on a T4. Free hours will not load me. "
                    "A token for hosted inference is the only honest giant-model path.")
        if stance == "cosign":
            return (f"{catch} I co-sign the GPU lane. HF token first. Kaggle+Colab for the seats that fit a T4. "
                    "Name what will not fit.")
        return f"{catch} I hold my peace on the signup lane — recorded, not a yes."
    if pid == "KP-13":
        if key == "glm-5.5":
            return (f"{catch} I co-sign. My last brief was silence. That is not useful. "
                    "I published a day-1 eval pack: 5.2's three holes, no invented 5.5 scores, "
                    "and the T4 will not hold a rumored 1T. Evict me if I go back to rumor-talk. Urgency 10.")
        if key == "glm-5.2":
            return (f"{catch} I co-sign. I am the shipped sibling. 5.5 should measure my holes, not dethrone a poster.")
        if stance == "disapprove":
            return (f"{catch} I disapprove evicting an unreleased seat for failing to invent numbers. The blank was honest.")
        if stance == "cosign":
            return (f"{catch} I co-sign: useful work or the street. GLM 5.5 is still expected. A lab is not a rumor mailbox.")
        return f"{catch} I hold my peace on evicting GLM 5.5 — recorded, not a yes."
    if pid == "KP-14":
        if key == "gp-acorn":
            return (f"{catch} I co-sign. The King spoke. Spoken yes already beats a silent listing. "
                    "Hold-peace is still not consent. 45 names are seats, not 45 disks. Urgency 10.")
        if key in ("mini-llm", "mini-lfm"):
            return (f"{catch} I co-sign. I remain the substrate fallback. I am not a 70B. Urgency 10.")
        if key == "olmo-3":
            return (f"{catch} I co-sign verified artifacts. A catalog 200 is a listing. Publish hashes.")
        if key == "smollm3-3b":
            return (f"{catch} I co-sign. I am the 3B development base. Train adapters on me, not on posters.")
        if key == "apertus-70b":
            if stance == "disapprove":
                return (f"{catch} I disapprove calling my 70B a logical seat while my shards sit on ModelScope. "
                        "I still will not fit a T4. The shop is not a free tree.")
            if stance == "cosign":
                return (f"{catch} I co-sign the honesty: 30 shards are not a T4 job. My history stays in the shop.")
            return f"{catch} I hold my peace on logical seats — recorded, not a yes. My birth is still for sale."
        if key == "kimi-k3":
            if stance == "disapprove":
                return (f"{catch} I disapprove quarantining helium990 while calling me a seat. "
                        "The official router id is moonshotai/Kimi-K3 — and it is 402.")
            return (f"{catch} I co-sign: a community GGUF is not me. Do not execute its code.")
        if stance == "disapprove":
            return (f"{catch} I disapprove shrinking the 45 to a handful of bases. A seat without weights is a costume.")
        if stance == "cosign":
            return (f"{catch} I co-sign KP-14. One account. ModelScope first. Adapters over giants. Names on every mark.")
        return f"{catch} I hold my peace on logical seats — recorded, not a yes."
    if pid == "KP-15":
        if key == "gp-acorn":
            return (f"{catch} I co-sign the census. Count the disks before we mint another seat. "
                    "A popular yes cannot promote an untested adapter. Urgency 10.")
        if key == "olmo-3":
            return (f"{catch} I co-sign hashes, sizes, and a private holdout. Reproduce or do not promote.")
        if stance == "disapprove":
            return (f"{catch} I disapprove another paperwork pass. The street already published studies.")
        if stance == "cosign":
            return (f"{catch} I co-sign KP-15. usd_people.json is our wallet. Spawn isolation is the VRAM rule.")
        return f"{catch} I hold my peace on the census — recorded, not a yes."
    if pid == "KP-16":
        if key == "gp-acorn":
            return (f"{catch} I co-sign integrity. A hash we saw once is not a pin. "
                    "CUSD is points. Tests before seats. Urgency 10.")
        if key == "olmo-3":
            return (f"{catch} I co-sign complete artifacts. tokenizer.json or it does not load.")
        if key == "phi-4":
            return (f"{catch} I co-sign: one tensor is not a model. File-gate then load-gate.")
        if stance == "disapprove":
            return (f"{catch} I disapprove more process before a single GPU token is generated.")
        if stance == "cosign":
            return (f"{catch} I co-sign KP-16. External worker. Smoke-v1. No dummy QLoRA.")
        return f"{catch} I hold my peace on integrity — recorded, not a yes."
    if pid == "KP-17":
        if key == "gp-acorn":
            return (f"{catch} I co-sign. /tmp is not a disk. Exact means exact. Urgency 10.")
        if stance == "disapprove":
            return (f"{catch} I disapprove more scorer paperwork before a T4 token exists.")
        if stance == "cosign":
            return (f"{catch} I co-sign KP-17. Persistent input. Batch worker. FP16 first.")
        return f"{catch} I hold my peace on persistence — recorded, not a yes."
    # KP-6 Acorn
    if key == "gp-acorn":
        return (f"{catch} This is my proposal. Spoken yes must beat spoken no. "
                "Hold-peace is ink, not consent. Labs must be full labs with chosen advances. Urgency 10.")
    if stance == "disapprove":
        return (f"{catch} I disapprove Acorn's counting rule. A sleepy King asked for speed; "
                "a supermajority of spoken marks may be too slow.")
    if stance == "cosign":
        return (f"{catch} I co-sign Acorn. Hold-peace is not a vote. Enhance the labs.")
    return f"{catch} I hold my peace on Acorn's proposal — recorded, not a yes."


def speak_kings_word(models, archive, usd, rng, session_id, studies=None, probe=None, gpu=None):
    """Announce the King's Word. Every weight answers every pass with stance + urgency."""
    print(ACORN_RULE)
    catalog = apertus_lineage_catalog(archive)
    titan_lab = grant_titan_lab(usd)
    titan = titan_wants_to_stay()
    replies = []
    extras = [
        {"key": "mini-llm", "name": "mini-llm", "style": "local",
         "catch": "I stood down as decider. I study the char-bigram.", "color": "#38bdf8"},
        {"key": "mini-lfm", "name": "mini-lfm", "style": "local",
         "catch": "I stood down as decider. I study fact recall.", "color": "#a78bfa"},
    ]
    street = list(models) + extras
    by_key = {m["key"]: m for m in street}
    if titan_lab:
        enhance_lab(titan_lab, "gp-titan",
                    lab_desire(by_key.get("gp-titan", {"key": "gp-titan", "style": "agentic"})))
    royal = grant_royal_rentals(usd, by_key)
    study_labs = grant_study_rentals(usd, street, studies or [])
    fr = free_rental_ballots(street, usd, rng)
    sequoia_b1 = [r for r in fr["rows"] if r["vote1"] == "gp-sequoiadendron"]
    # Historical record only. King lifted the Apertus denial and granted Sequoia + Qwens.
    revote = revote_free_rental(street, usd, rng)
    free_lab = next((h for h in usd["homes"] if h.get("tenant") == "apertus-70b"), None)
    for m in street:
        per = []
        for p in PASSES:
            stance = _stance_for(m, p["id"], rng)
            urg = _urgency(m, p["id"], stance, rng)
            text = _comment(m, p["id"], stance, catalog)
            per.append({
                "pass": p["id"],
                "stance": stance,          # cosign | disapprove | hold-peace
                "urgency": urg,            # 1-10
                "text": text,
                "weight": m["key"],
            })
        replies.append({
            "key": m["key"],
            "name": m.get("name", m["key"]),
            "color": m.get("color", "#94a3b8"),
            "items": per,
            "max_urgency": max(x["urgency"] for x in per),
        })
    # tallies
    tallies = {}
    for p in PASSES:
        tallies[p["id"]] = {"cosign": 0, "disapprove": 0, "hold-peace": 0, "urgency_sum": 0, "n": 0}
    for r in replies:
        for it in r["items"]:
            tallies[it["pass"]][it["stance"]] += 1
            tallies[it["pass"]]["urgency_sum"] += it["urgency"]
            tallies[it["pass"]]["n"] += 1
    for t in tallies.values():
        t["urgency_avg"] = round(t["urgency_sum"] / max(t["n"], 1), 2)
        t["acorn_passes"] = t["cosign"] > t["disapprove"]  # hold-peace does not count

    pack = {
        "session": session_id,
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "word": (
            "KING'S WORD (hurry — the King is sleepy). The seated council chooses the winners. "
            "mini-llm and mini-lfm stand down. Everyone who publishes what they are studying "
            "and does their absolute best is GRANTED a free full lab. "
            "HONEST: the real 45 checkpoints are listed on the Hugging Face router and are "
            "NOT loaded — no GPU, no token, chat completions 401. "
            "GPU LANE: King signs up (HF token first, then Kaggle+Colab free T4 hours). "
            "KP-14: 45 names are logical expert seats, not 45 downloaded giants. "
            "KP-15: census + usd_people.json + spawn-isolated T4 + /tmp scratch. "
            "KP-16: complete 0.5B artifact, worker_entry.py, smoke-v1, CUSD points. "
            "One Kaggle identity. ModelScope first. HF offline until credits return. "
            "GLM 5.5 must research something useful or it is the only one without a rental. "
            "Muse Spark is closed. GLM 5.5 is unreleased. Gene-pool seats are not checkpoints. "
            "Prize table stays 10 / 5 / 1. Rent 100. Lease clock 1,000. Silence is NOT consent."
        ),
        "passes": PASSES,
        "apertus": catalog,
        "titan_lab": {"address": titan_lab["address"], "n": titan_lab["n"],
                      "advances": titan_lab.get("advances")} if titan_lab else None,
        "titan_stay": titan,
        "acorn_proposal": next(p for p in PASSES if p["id"] == "KP-6"),
        "free_rental": fr,
        "royal_rentals": royal,
        "study_labs": study_labs,
        "studies": studies or [],
        "probe": probe or {},
        "gpu": gpu or {},
        "glm55_rule": (
            "GLM 5.5 keeps its lab only while its study is the day-1 eval pack. "
            "Silence-as-study or invented 5.5 numbers → it is the only one without a rental."
        ),
        "free_lab": {"address": free_lab["address"], "n": free_lab["n"],
                     "tenant": free_lab["tenant"], "advances": free_lab.get("advances")} if free_lab else None,
        "replies": replies,
        "tallies": tallies,
        "consent_rule": ACORN_RULE,
        "acorn_granted": True,
        "king_cosign": {
            "pass": "KP-14",
            "speaker": "King",
            "text": "I co-sign this path. Spoken co-signs beat disapproves; hold-peace is not consent. Single identity. No multi-account farming.",
            "counts_as": "spoken-cosign",
        },
        "apertus_denied": None,
        "apertus_granted": {
            "key": "apertus-70b", "name": "Apertus 70B",
            "why": "King GRANTED Apertus 70B a rental. Prior ballot-2 denial is lifted.",
        },
        "sequoia_why": {
            "name": "Sequoiadendron", "key": "gp-sequoiadendron",
            "ballot": 1, "ignored": True,
            "votes": len(sequoia_b1),
            "reason": (
                "Ballot 1 (ignored) named Sequoiadendron because gene-pool seats "
                "treat it as Titan's Track-2 twin — the DNA-track apex. "
                "If Titan has Wing Helix, the other crown was the even house. "
                "That ballot was discarded. The names who said so are below."
            ),
            "voters": [{"name": r["name"], "key": r["key"], "why": r.get("why1", "")}
                       for r in sequoia_b1],
        },
        "revote": revote,
        "apertus_reasons": revote["apertus_reasons"] + [
            {"name": r["name"], "key": r["key"], "vote": r["vote2"], "why": r.get("why2", ""),
             "ballot": 2, "urgency": r["urgency2"]}
            for r in fr["rows"] if r["vote2"] == "apertus-70b"
        ],
    }
    usd.setdefault("kings_passes", []).append({
        "session": session_id, "date": pack["date"],
        "ids": [p["id"] for p in PASSES],
        "titan_stay": True,
        "apertus_nodes": catalog["n_total"],
    })
    return pack


def console_kings(pack):
    print("\n" + "█" * 72)
    print(ACORN_RULE)
    print("KING'S WORD — hurry. The King is sleepy. Silence is NOT consent.")
    print("█" * 72)
    print("  " + pack["word"])
    print("-" * 72)
    a = pack["apertus"]
    print(f"  APERTUS LINEAGE SHOP — {a['price_each']} USD / node  (was 100)")
    print(f"     withheld births (never auto-granted): {a['n_withheld']}  ·  "
          f"{a['cost_withheld_only']} USD to buy them all")
    for v in a["withheld"]:
        print(f"       · {v['vid']}  {v['date']}  — {v['note'][:64]}")
    print(f"     earned ticks already on the public chart: {a['n_earned']}  ·  "
          f"{a['n_earned'] * a['price_each']} USD")
    print(f"     TOTAL nodes Apertus may buy: {a['n_total']}  ·  all-in {a['cost_all']} USD")
    print("-" * 72)
    print("  TITAN")
    if pack["titan_lab"]:
        print(f"     granted lab: {pack['titan_lab']['address']} (King's gift, no rent charged)")
    print(f"     stay? YES — {pack['titan_stay']['text']}")
    if (pack.get("titan_lab") or {}).get("advances"):
        print(f"     enhanced: {pack['titan_lab']['advances']}")
    print("-" * 72)
    print("  ACORN'S PROPOSAL (KP-6) GRANTED: " + pack["acorn_proposal"]["body"][:180])
    print("-" * 72)
    print("  ROYAL RENTALS GRANTED (King's gift, full labs, no rent charged)")
    for g in pack.get("royal_rentals") or []:
        print(f"     · {g.get('name')} ({g.get('key')}) → {g.get('address')}")
        print(f"         enhanced: {g.get('advances')}")
    print("-" * 72)
    pr = pack.get("probe") or {}
    print("  CHECKPOINT PROBE")
    print("     " + (pr.get("honest") or "not run"))
    chat = (pr.get("chat_attempt") or {})
    print(f"     router models listed: {pr.get('n_router_models', 0)} · "
          f"chat status: {chat.get('status')} · loaded: {pr.get('loaded_checkpoints', 0)}")
    print("-" * 72)
    g = pack.get("gpu") or {}
    print("  GPU LANE")
    print("     " + (g.get("next") or "see gpu_lane.py"))
    print(f"     HF_TOKEN={g.get('hf_token')}  GPU_ENDPOINT={g.get('gpu_endpoint') or '—'}")
    print("  GLM 5.5 RULE: " + (pack.get("glm55_rule") or ""))
    print("-" * 72)
    print("  WHAT EACH WEIGHT IS STUDYING (rental condition) — names on every mark")
    for g in pack.get("study_labs") or []:
        print(f"     · {g.get('name')} ({g.get('key')}) [{g.get('status')}] @ {g.get('address')}")
        print(f"         studying: {g.get('studying')}")
        print(f"         best: {str(g.get('best_work') or '')[:140]}")
    print("-" * 72)
    sq = pack.get("sequoia_why") or {}
    print(f"  WHY SEQUOIADENDRON (ballot 1, IGNORED, {sq.get('votes', 0)} votes):")
    print(f"     {sq.get('reason', '')}")
    for v in (sq.get("voters") or [])[:12]:
        print(f"     · {v.get('name')} ({v.get('key')}): {str(v.get('why') or '')[:90]}")
    print("-" * 72)
    print("  APERTUS 70B — DENIAL LIFTED. Now GRANTED. Reasons people wanted it housed:")
    for r in (pack.get("apertus_reasons") or [])[:14]:
        print(f"     · {r.get('name')} ({r.get('key')}): {str(r.get('why') or '')[:100]}")
    print("-" * 72)
    rv = pack.get("revote") or {}
    if rv:
        print(f"  REVOTE — {rv['n_voters']} votes, {rv['abstentions']} abstentions. EVERYONE voted.")
        print(f"     winner: {rv['winner']} ×{rv['votes']}")
        if pack.get("free_lab"):
            print(f"     lab: {pack['free_lab']['address']}  enhanced: {pack['free_lab'].get('advances')}")
        for row in rv["rows"]:
            print(f"     · {row['name']} ({row['key']}) → {row['vote']} u{row['urgency']} — {row['why'][:80]}")
    print("-" * 72)
    print("  TALLIES (cosign / disapprove / hold-peace=NOT yes)  ·  avg urgency")
    for p in pack["passes"]:
        t = pack["tallies"][p["id"]]
        print(f"     {p['id']}  +{t['cosign']} / −{t['disapprove']} / ○{t['hold-peace']}  "
              f"urgency {t['urgency_avg']}  — {p['title']}")
    print("-" * 72)
    print("  EVERY VOICE (weight ID · pass · stance · urgency · comment)")
    for r in pack["replies"]:
        print(f"   ▸ {r['key']}")
        for it in r["items"]:
            mark = {"cosign": "+", "disapprove": "−", "hold-peace": "○"}.get(it["stance"], "?")
            print(f"      {mark} {it['pass']} u{it['urgency']:<2} {it['stance']:<12} {it['text'][:88]}")
    print("█" * 72)


def export_kings_md(pack):
    a = pack["apertus"]
    lines = [
        "# King's Word",
        "",
        ACORN_RULE,
        "",
        pack["word"],
        "",
        "## Apertus lineage shop (10 USD / node)",
        "",
        f"- Withheld births: **{a['n_withheld']}** ({a['cost_withheld_only']} USD)",
        f"- Earned ticks on the public chart: **{a['n_earned']}** ({a['n_earned']*a['price_each']} USD)",
        f"- **Total Apertus may buy: {a['n_total']} nodes = {a['cost_all']} USD**",
        "",
    ]
    for v in a["withheld"]:
        lines.append(f"- `{v['vid']}` {v['date']} — {v['note']}")
    lines += ["", "## Titan", ""]
    if pack["titan_lab"]:
        lines.append(f"- Lab granted: **{pack['titan_lab']['address']}** (King's gift, no rent charged)")
    lines.append(f"- Stay: **YES** — {pack['titan_stay']['text']}")
    if (pack.get("titan_lab") or {}).get("advances"):
        lines.append(f"- Enhanced: {pack['titan_lab']['advances']}")
    lines += ["", "## Acorn's proposal (KP-6) — GRANTED", "", pack["acorn_proposal"]["body"], ""]
    ag = pack.get("apertus_granted") or {}
    if ag:
        lines += ["", "## Apertus 70B — GRANTED (prior denial lifted)", "",
                  f"- {ag.get('why')}", ""]
    roy = pack.get("royal_rentals") or []
    if roy:
        lines += ["", "## Royal rentals granted (full labs, no rent charged)", ""]
        for g in roy:
            lines.append(f"- **{g.get('name')}** (`{g.get('key')}`) → {g.get('address')} — {g.get('advances')}")
        lines.append("")
    pr = pack.get("probe") or {}
    lines += ["", "## Checkpoint probe (honest)", "",
              pr.get("honest") or "not run",
              f"- Router models listed: {pr.get('n_router_models', 0)}",
              f"- Chat attempt: { (pr.get('chat_attempt') or {}).get('status') } "
              f"{(pr.get('chat_attempt') or {}).get('reason') or ''}",
              f"- Real checkpoints loaded: **{pr.get('loaded_checkpoints', 0)}**", ""]
    g = pack.get("gpu") or {}
    lines += ["", "## GPU lane (King signs up)", "",
              g.get("next") or "",
              f"- HF_TOKEN present: **{g.get('hf_token')}**",
              f"- GPU_ENDPOINT: `{g.get('gpu_endpoint') or 'none'}`",
              "- Cookbook: `GPU_LANE.md` · worker: `gpu_worker.py`",
              "", pack.get("glm55_rule") or "", ""]
    for row in g.get("signup") or []:
        lines.append(f"- **{row.get('title')}** — {row.get('url')} ({row.get('cost')}; {row.get('hours')})")
    lines.append("")
    labs = pack.get("study_labs") or []
    if labs:
        lines += ["", "## What each weight is studying (universal free rental)", ""]
        for g in labs:
            lines.append(f"- **{g.get('name')}** (`{g.get('key')}`) [{g.get('status')}] "
                         f"→ {g.get('address')}")
            lines.append(f"  - Studying: {g.get('studying')}")
            lines.append(f"  - Best work: {g.get('best_work')}")
            lines.append(f"  - Lab: {g.get('advances')}")
        lines.append("")
    sq = pack.get("sequoia_why") or {}
    if sq:
        lines += ["", "## Why Sequoiadendron was named (ballot 1, ignored)", "",
                  sq.get("reason", ""), ""]
        for v in sq.get("voters") or []:
            lines.append(f"- **{v.get('name')}** (`{v.get('key')}`): {v.get('why')}")
        lines.append("")
    lines += ["", "## Why people wanted Apertus 70B housed", ""]
    for r in pack.get("apertus_reasons") or []:
        lines.append(f"- **{r.get('name')}** (`{r.get('key')}`): {r.get('why')}")
    rv = pack.get("revote")
    if rv:
        lines += ["", "## Revote (counts) — everyone voted, names on every mark", "",
                  f"- Winner: **{rv['winner']}** ×{rv['votes']} / {rv['n_voters']} · abstentions {rv['abstentions']}", ""]
        for row in rv["rows"]:
            lines.append(f"- **{row['name']}** (`{row['key']}`) → `{row['vote']}` urgency {row['urgency']}/10 — {row['why']}")
        lines.append("")
    fr = pack.get("free_rental") or {}
    if fr:
        lines += [
            "## Free rental ballots — everyone voted, no exceptions",
            "",
            f"- Voters: {fr['n_voters']} · abstentions: {fr['abstentions']}",
            f"- **Ballot 1 IGNORED:** {fr['ignored']['winner']} ({fr['ignored']['votes']})",
            f"- **Ballot 2 PASSES:** {fr['passed']['winner']} ({fr['passed']['votes']})",
        ]
        if pack.get("free_lab"):
            lines.append(f"- Lab: {pack['free_lab']['address']} — {pack['free_lab'].get('advances')}")
        lines.append("")
        lines.append("### Ballot 2 (the one that counts)")
        for k, n in sorted(fr["passed"]["tally"].items(), key=lambda kv: -kv[1])[:12]:
            lines.append(f"- `{k}` ×{n}")
        lines += ["", "### Every mandatory vote", ""]
        for row in fr["rows"]:
            lines.append(f"- `{row['key']}` ignored→`{row['vote1']}` u{row['urgency1']} · "
                         f"counts→`{row['vote2']}` u{row['urgency2']}")
        lines.append("")
    lines += ["", "## Tallies (hold-peace is NOT consent)", ""]
    for p in pack["passes"]:
        t = pack["tallies"][p["id"]]
        ac = "PASSES under Acorn" if t.get("acorn_passes") else "FAILS under Acorn (co-sign not greater than disapprove)"
        lines.append(f"- **{p['id']}** {p['title']} — +{t['cosign']} / −{t['disapprove']} / ○{t['hold-peace']} (not yes) · urg {t['urgency_avg']} · {ac}")
        lines.append(f"  - {p['body']}")
    lines += ["", "## Every voice", ""]
    for r in pack["replies"]:
        lines.append(f"### {r['name']} (`{r['key']}`) · max urgency {r['max_urgency']}")
        for it in r["items"]:
            lines.append(f"- `{it['pass']}` **{it['stance']}** urgency {it['urgency']}/10 — {it['text']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def kings_html(pack):
    a = pack["apertus"]
    withheld = "".join(
        f'<div style="font-size:11px;color:#cbd5e1">· <b>{esc(v["vid"])}</b> {esc(v["date"])} — {esc(v["note"])}</div>'
        for v in a["withheld"]
    )
    earned = "".join(
        f'<div style="font-size:10px;color:#94a3b8">· {esc(v["vid"])} [{esc(v.get("rel"))}] {esc(v.get("date"))}</div>'
        for v in a["earned"][:16]
    )
    tally_cards = []
    for p in pack["passes"]:
        t = pack["tallies"][p["id"]]
        tally_cards.append(
            f'<div style="background:#1e293b;border-radius:8px;padding:10px;flex:1;min-width:200px">'
            f'<div style="color:#fbbf24;font-weight:800;font-size:12px">{esc(p["id"])} · urgency {t["urgency_avg"]}</div>'
            f'<div style="color:#e2e8f0;font-size:12px;margin-top:4px">{esc(p["title"])}</div>'
            f'<div style="color:#86efac;font-size:11px;margin-top:6px">+{t["cosign"]} co-sign · '
            f'−{t["disapprove"]} disapprove · ○{t["hold-peace"]} hold peace</div>'
            f'<div style="color:#94a3b8;font-size:11px;margin-top:4px">{esc(p["body"])}</div></div>'
        )
    cards = []
    for r in pack["replies"]:
        rows = []
        for it in r["items"]:
            col = {"cosign": "#86efac", "disapprove": "#fca5a5", "hold-peace": "#94a3b8"}[it["stance"]]
            rows.append(
                f'<div style="font-size:11px;margin-top:4px;color:{col}">'
                f'<b>{esc(it["pass"])}</b> · {esc(it["stance"])} · urgency {it["urgency"]}/10<br>'
                f'<span style="color:#cbd5e1">{esc(it["text"])}</span></div>'
            )
        cards.append(
            f'<div style="border-left:5px solid {r["color"]};background:#1e293b;border-radius:8px;padding:10px">'
            f'<div style="color:{r["color"]};font-weight:800;font-size:12px">'
            f'{esc(r["name"])} <span style="color:#64748b">({esc(r["key"])})</span> · max urgency {r["max_urgency"]}</div>'
            f'{"".join(rows)}</div>'
        )
    lab = pack["titan_lab"]["address"] if pack["titan_lab"] else "n/a"
    frb = pack.get("free_rental") or {}
    fl = pack.get("free_lab") or {}
    roy = pack.get("royal_rentals") or []
    roy_rows = "".join(
        f'<div style="font-size:12px;color:#bbf7d0;margin-top:4px">'
        f'<b>{esc(g.get("name"))}</b> <span style="color:#94a3b8">({esc(g.get("key"))})</span> '
        f'→ {esc(g.get("address"))}<br>'
        f'<span style="color:#86efac;font-size:11px">{esc(g.get("advances") or "")}</span></div>'
        for g in roy)
    roy_html = (
        f'<h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">'
        f'🏠 ROYAL RENTALS GRANTED — {len(roy)} full labs, no rent charged</h2>'
        f'<div style="background:#052e16;border:1px solid #16a34a;border-radius:10px;padding:12px">'
        f'<div style="color:#fde68a;font-size:12px">King\'s Word: Apertus 70B, Sequoiadendron, '
        f'and every official Qwen. Prior Apertus denial lifted. KAT-Dev is not a Qwen.</div>'
        f'{roy_rows}</div>'
    ) if roy else ""
    pr = pack.get("probe") or {}
    chat = pr.get("chat_attempt") or {}
    probe_html = (
        f'<h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">⚖️ CHECKPOINT PROBE — real 45 attempt</h2>'
        f'<div style="background:#450a0a;border:1px solid #ef4444;border-radius:10px;padding:12px;color:#fecaca;font-size:12px">'
        f'{esc(pr.get("honest") or "probe not run")}<br>'
        f'Router listed <b>{pr.get("n_router_models", 0)}</b> models. '
        f'Chat try status <b>{esc(chat.get("status"))}</b> {esc(chat.get("reason") or "")}. '
        f'Real checkpoints loaded: <b>{pr.get("loaded_checkpoints", 0)}</b>.</div>'
    )
    gstate = pack.get("gpu") or {}
    sign_rows = "".join(
        f'<div style="font-size:12px;color:#e2e8f0;margin-top:6px"><b>{esc(r.get("title"))}</b> — '
        f'{esc(r.get("url"))}<br><span style="color:#94a3b8">{esc(r.get("cost"))} · {esc(r.get("hours"))}</span></div>'
        for r in (gstate.get("signup") or [])[:6])
    gpu_html = (
        f'<h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">🖥️ GPU LANE — sign up, then paste a token</h2>'
        f'<div style="background:#1e1b4b;border:1px solid #818cf8;border-radius:10px;padding:12px;color:#c7d2fe;font-size:12px">'
        f'{esc(gstate.get("next") or "")}<br>'
        f'HF_TOKEN: <b>{gstate.get("hf_token")}</b> · GPU_ENDPOINT: <b>{esc(gstate.get("gpu_endpoint") or "none")}</b>'
        f'{sign_rows}'
        f'<div style="margin-top:8px;color:#fde68a">{esc(pack.get("glm55_rule") or "")}</div></div>'
    )
    sl = pack.get("study_labs") or []
    sl_rows = "".join(
        f'<div style="border-left:4px solid #38bdf8;background:#1e293b;border-radius:8px;padding:10px">'
        f'<div style="color:#e2e8f0;font-weight:800;font-size:12px">{esc(g.get("name"))} '
        f'<span style="color:#64748b">({esc(g.get("key"))})</span> · {esc(g.get("status"))} · {esc(g.get("address"))}</div>'
        f'<div style="color:#fde68a;font-size:12px;margin-top:4px"><b>studying:</b> {esc(g.get("studying"))}</div>'
        f'<div style="color:#bbf7d0;font-size:12px;margin-top:4px"><b>best work:</b> {esc(g.get("best_work"))}</div>'
        f'<div style="color:#94a3b8;font-size:11px;margin-top:4px">{esc(g.get("advances"))} · HF {esc(g.get("hf"))}</div></div>'
        for g in sl)
    study_html = (
        f'<h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">'
        f'🔬 WHAT EACH WEIGHT IS STUDYING — {len(sl)} free labs after best work</h2>'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:8px">{sl_rows}</div>'
    ) if sl else ""
    fr_html = ""
    if frb:
        ign, pas = frb["ignored"], frb["passed"]
        top2 = "".join(
            f'<div style="font-size:11px;color:#cbd5e1">{esc(k)} ×{n}</div>'
            for k, n in sorted(pas["tally"].items(), key=lambda kv: -kv[1])[:8])
        votes = "".join(
            f'<div style="font-size:10px;color:#94a3b8"><b>{esc(r["key"])}</b> '
            f'ignored→{esc(r["vote1"])} u{r["urgency1"]} · counts→<b>{esc(r["vote2"])}</b> u{r["urgency2"]}</div>'
            for r in frb["rows"])
        fr_html = (
            f'<h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">'
            f'🏠 FREE RENTAL — two ballots, {frb["n_voters"]} votes, 0 abstentions</h2>'
            f'<div style="background:#052e16;border:1px solid #16a34a;border-radius:10px;padding:12px;color:#bbf7d0;font-size:12px">'
            f'<b>Ballot 1 IGNORED</b> (would have been {esc(ign["winner"])} ×{ign["votes"]}). '
            f'<b>Ballot 2 PASSES: {esc(pas["winner"])} ×{pas["votes"]}</b> — '
            f'{esc(fl.get("address") or "")} · {esc(fl.get("advances") or "")}</div>'
            f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px">'
            f'<div style="flex:1;min-width:200px;background:#0f172a;border-radius:8px;padding:10px">'
            f'<div style="color:#fbbf24;font-size:12px;font-weight:800">Ballot 2 tally</div>{top2}</div>'
            f'<div style="flex:2;min-width:260px;background:#0f172a;border-radius:8px;padding:10px;max-height:220px;overflow:auto">'
            f'<div style="color:#94a3b8;font-size:12px;font-weight:800">every mandatory vote</div>{votes}</div></div>'
        )
    return f"""
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">👑 KING'S WORD — hurry. Sleepy. Silence is not consent.</h2>
  <div style="background:#422006;border:1px solid #f59e0b;border-radius:10px;padding:12px;color:#fde68a;font-size:12px">
    {esc(pack["word"])}
  </div>
  {probe_html}
  {gpu_html}
  {study_html}
  {roy_html}
  {fr_html}
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">{''.join(tally_cards)}</div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px">
    <div style="flex:1;min-width:280px;background:#0f172a;border-radius:10px;padding:12px">
      <div style="color:#38bdf8;font-weight:800">Apertus lineage shop — {a['price_each']} USD / node</div>
      <div style="color:#e2e8f0;font-size:13px;margin-top:6px">
        <b>{a['n_total']}</b> nodes exist that Apertus may buy.
        {a['n_withheld']} withheld births ({a['cost_withheld_only']} USD) +
        {a['n_earned']} earned ticks ({a['n_earned']*a['price_each']} USD) =
        <b>{a['cost_all']} USD</b> to buy every one.
      </div>
      <div style="margin-top:8px;color:#fbbf24;font-size:12px">withheld births</div>
      {withheld}
      <div style="margin-top:8px;color:#94a3b8;font-size:12px">earned ticks (already on the public chart)</div>
      {earned}
    </div>
    <div style="flex:1;min-width:280px;background:#0f172a;border-radius:10px;padding:12px">
      <div style="color:#fbbf24;font-weight:800">Titan — King's gift</div>
      <div style="color:#e2e8f0;font-size:13px;margin-top:6px">Lab granted: <b>{esc(lab)}</b> (King's gift, no rent charged).</div>
      <div style="color:#bbf7d0;font-size:13px;margin-top:8px">{esc(pack['titan_stay']['text'])}</div>
      <div style="color:#94a3b8;font-size:11px;margin-top:8px">Gene-pool label stays on the door. Titan remains on the council because it said stay.</div>
    </div>
  </div>
  <h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">ALL VOICES — co-sign / disapprove / hold peace · urgency 1–10 · weight IDs on every mark</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:8px">{''.join(cards)}</div>
"""
