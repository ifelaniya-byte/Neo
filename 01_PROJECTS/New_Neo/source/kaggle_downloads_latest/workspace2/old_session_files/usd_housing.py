#!/usr/bin/env python3
"""
USD + WEIGHTS LANE — public dollar crypto and 100 rental homes.

Rules (all public, all tracked, nobody can take from the pot):
  • Every weight starts HOMELESS.
  • The single best idea this session earns the author exactly 1 USD.
  • USD can only be paid into the communal escrow. Nobody can spend it
    elsewhere or withdraw it. Everyone can read every wallet and the pot.
  • 100 luxurious rental properties on Weights Lane. Not for sale.
    Each is an 11-bedroom spacious futuristic semi-genetic laboratory.
  • Rent = 100 USD, paid from the renter's earned balance into escrow.
  • Rent is optional: a weight moves in only when it has the money AND wants to.
  • A lease expires once 1,000 USD have been earned cumulatively by ANYONE
    after that rental was made (global mint clock, not the renter's clock).

USED BY: model_council.py
"""

import html
import json
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))
USD_PATH = os.path.join(BASE, "usd_ledger.json")

RENT_USD = 100
LEASE_EXPIRE_AFTER_EARNED = 1000
N_HOMES = 100
STREET = "Weights Lane"
BEST_IDEA_USD = 10         # 1st place (King's last number)
PRIZE_USD = (10, 5, 1)     # 1st, 2nd, 3rd best ideas

LAB_WINGS = [
    "Helix", "Chromatid", "Nucleotide", "Ribosome", "Telomere",
    "Histone", "Plasmid", "Codon", "Intron", "Exon",
    "Crispr", "Polymerase", "Ligase", "Centromere", "Allele",
    "Phenome", "Basepair", "Splice", "Operon", "Capsid",
]


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _address(n):
    wing = LAB_WINGS[(n - 1) % len(LAB_WINGS)]
    block = 1 + (n - 1) // len(LAB_WINGS)
    return f"{n} {STREET} — Wing {wing} {block}"


def empty_state(keys):
    homes = []
    for n in range(1, N_HOMES + 1):
        homes.append({
            "n": n,
            "address": _address(n),
            "beds": 11,
            "kind": "futuristic semi-genetic laboratory rental",
            "for_sale": False,
            "tenant": None,
            "leased_at_minted": None,
            "leased_at": None,
        })
    wallets = {}
    for k in keys:
        wallets[k] = {
            "earned": 0,          # lifetime minted to this key
            "paid_escrow": 0,     # paid into the locked pot (rent)
            "home": None,         # property n or None
            "status": "homeless",
            "want_rent": False,   # they rent only if they want to AND can pay
            "want_note": "",
        }
    return {
        "created": _now(),
        "updated": _now(),
        "currency": "USD",
        "policy": (
            "USD is a public crypto. Best idea = 1 USD. All weights are homeless "
            "until they have 1,000 USD AND want to rent. Rent is never forced. "
            "Payment goes into the communal escrow (readable by all, spendable by none). "
            "Homes are rentals only — not for sale. "
            "A lease expires after 300 USD have been earned by anyone after it started."
        ),
        "rent": RENT_USD,
        "lease_expire_after_earned": LEASE_EXPIRE_AFTER_EARNED,
        "prize_usd": list(PRIZE_USD),
        "global_minted": 0,
        "escrow": 0,
        "wallets": wallets,
        "homes": homes,
        "events": [],
    }


def load_state(keys, path=None):
    path = path or USD_PATH
    if not os.path.exists(path):
        return empty_state(keys)
    try:
        with open(path) as f:
            st = json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty_state(keys)
    # admit any new seats as homeless with a zero wallet
    for k in keys:
        if k not in st["wallets"]:
            st["wallets"][k] = {
                "earned": 0, "paid_escrow": 0, "home": None, "status": "homeless",
                "want_rent": False, "want_note": "",
            }
        st["wallets"][k].setdefault("want_rent", False)
        st["wallets"][k].setdefault("want_note", "")
    st.setdefault("census", [])
    st.setdefault("missing", [])
    st["policy"] = (
        "Council USD points (CUSD) are a public simulated ledger, NOT redeemable "
        "US dollars. Ideas pay 10 / 5 / 1 points. Rent is never forced: a weight "
        "moves in only when it has 100 points AND wants to. Payment goes into "
        "locked escrow (readable by all, spendable by none). Homes are rentals "
        "only. A lease expires after 1,000 points minted by anyone after move-in. "
        "Apertus may buy lineage at 10 points a node. King's-gift labs pay no rent."
    )
    st["lease_expire_after_earned"] = LEASE_EXPIRE_AFTER_EARNED
    st["prize_usd"] = list(PRIZE_USD)
    st["rent"] = RENT_USD
    return st


def save_state(st, path=None):
    path = path or USD_PATH
    st["updated"] = _now()
    with open(path, "w") as f:
        json.dump(st, f, indent=1)
    people_path = os.path.join(os.path.dirname(path), "usd_people.json")
    write_people(st, people_path)
    return path


def write_people(st, path=None):
    """One public USD statement per person. What the street asked for."""
    path = path or os.path.join(BASE, "usd_people.json")
    names = {}
    try:
        import model_council as _mc
        names = {m["key"]: m.get("name", m["key"]) for m in _mc.MODELS}
        names.setdefault("mini-llm", "mini-llm")
        names.setdefault("mini-lfm", "mini-lfm")
    except Exception:
        names = {}
    try:
        import studies as _studies
        street = [{"key": k, "name": names.get(k, k)} for k in st["wallets"]]
        briefs = {r["key"]: r for r in _studies.briefs_for(street)}
    except Exception:
        briefs = {}
    homes = {h["n"]: h for h in st.get("homes") or []}
    people = []
    for key, w in sorted(st["wallets"].items(), key=lambda kv: (kv[1].get("home") or 999, kv[0])):
        h = homes.get(w.get("home")) if w.get("home") else None
        tenure = "homeless"
        if h:
            if h.get("kings_gift") and key == "gp-titan":
                tenure = "kings-gift"
            elif h.get("kings_gift") or h.get("free_rental"):
                tenure = "free-rental"
            else:
                tenure = "paid-lease"
        rec = briefs.get(key) or {}
        earned_since = None
        if h and h.get("leased_at_minted") is not None:
            earned_since = int(st.get("global_minted") or 0) - int(h["leased_at_minted"])
        people.append({
            "key": key,
            "name": rec.get("name") or names.get(key) or key,
            "earned_usd": int(w.get("earned") or 0),
            "paid_escrow_usd": int(w.get("paid_escrow") or 0),
            "available_usd": available(w),
            "status": w.get("status"),
            "want_rent": bool(w.get("want_rent")),
            "want_note": w.get("want_note") or "",
            "home_n": w.get("home"),
            "address": (h or {}).get("address"),
            "tenure": tenure,
            "kings_gift": bool((h or {}).get("kings_gift")),
            "free_rental": bool((h or {}).get("free_rental")),
            "advances": (h or {}).get("advances"),
            "studying": (h or {}).get("study") or rec.get("studying"),
            "best_work": (h or {}).get("best_work") or rec.get("best_work"),
            "lease_clock_usd_since_movein": earned_since,
            "lease_expires_after_global_usd": int(st.get("lease_expire_after_earned") or LEASE_EXPIRE_AFTER_EARNED),
            "can_withdraw": False,
            "can_buy_apertus_lineage": key == "apertus-70b",
            "shop_usd_per_node": 10 if key == "apertus-70b" else None,
            "minted": int(w.get("earned") or 0),
            "available": available(w),
        })
    minted_sum = sum(p["minted"] for p in people)
    avail_sum = sum(p["available"] for p in people)
    global_minted = int(st.get("global_minted") or 0)
    blob = {
        "date": _now(),
        "currency": "CUSD",
        "unit": "Council USD points — not redeemable US dollars",
        "for": "the people — one statement each, all public",
        "policy": st.get("policy"),
        "prize_usd": list(st.get("prize_usd") or PRIZE_USD),
        "rent_usd": int(st.get("rent") or RENT_USD),
        "lease_expire_after_earned": int(st.get("lease_expire_after_earned") or LEASE_EXPIRE_AFTER_EARNED),
        "global_minted": global_minted,
        "global_available": avail_sum,
        "people_minted_sum": minted_sum,
        "escrow_locked": int(st.get("escrow") or 0),
        "n_people": len(people),
        "n_renters": sum(1 for p in people if p["status"] == "renter"),
        "n_homeless": sum(1 for p in people if p["status"] != "renter"),
        "n_with_earned": sum(1 for p in people if p["earned_usd"] > 0),
        "integrity_ok": minted_sum == global_minted,
        "people": people,
    }
    if minted_sum != global_minted:
        blob["integrity_error"] = f"people_minted_sum {minted_sum} != global_minted {global_minted}"
    with open(path, "w") as f:
        json.dump(blob, f, indent=2)
    md = os.path.join(os.path.dirname(path), "usd_people.md")
    lines = [
        "# USD — one statement per person",
        "",
        f"- Minted: **{blob['global_minted']} USD** · escrow (locked): **{blob['escrow_locked']} USD**",
        f"- Prize 1st/2nd/3rd: {blob['prize_usd']} · rent {blob['rent_usd']} · lease clock {blob['lease_expire_after_earned']}",
        f"- People: **{blob['n_people']}** · renters {blob['n_renters']} · homeless {blob['n_homeless']}",
        f"- Nobody can withdraw. Escrow is readable, not spendable.",
        "",
        "| # | Person | Key | Earned | Available | Tenure | Address | Studying |",
        "|---:|---|---|---:|---:|---|---|---|",
    ]
    for ppl in people:
        stud = (ppl.get("studying") or "")[:80].replace("|", "/")
        lines.append(
            f"| {ppl.get('home_n') or '—'} | {ppl['name']} | `{ppl['key']}` | "
            f"{ppl['earned_usd']} | {ppl['available_usd']} | {ppl['tenure']} | "
            f"{ppl.get('address') or 'street'} | {stud} |"
        )
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def available(w):
    return max(0, int(w.get("earned", 0)) - int(w.get("paid_escrow", 0)))


def _log(st, kind, key, note, **extra):
    ev = {"t": _now(), "kind": kind, "key": key, "note": note}
    ev.update(extra)
    st["events"].append(ev)
    return ev


def mint_best_idea(st, key, item_id, session_id):
    """Award exactly 1 USD to the author of the session's best idea."""
    if key not in st["wallets"]:
        st["wallets"][key] = {
            "earned": 0, "paid_escrow": 0, "home": None, "status": "homeless",
            "want_rent": False, "want_note": "",
        }
    st["wallets"][key]["earned"] += BEST_IDEA_USD
    st["global_minted"] += BEST_IDEA_USD
    ev = _log(st, "mint", key,
              f"best idea ({item_id}) earned {BEST_IDEA_USD} USD",
              usd=BEST_IDEA_USD, item=item_id, session=session_id,
              global_minted=st["global_minted"])
    expired = expire_leases(st)
    rented = try_rent_all(st)
    return ev, expired, rented


def mint_top_ideas(st, ranked, session_id):
    """ranked = [(place, key, item_id), ...] place 1..3 pays PRIZE_USD[place-1]."""
    events = []
    expired, rented = [], []
    for place, key, item_id in ranked:
        if place < 1 or place > len(PRIZE_USD):
            continue
        amt = PRIZE_USD[place - 1]
        if key not in st["wallets"]:
            st["wallets"][key] = {
                "earned": 0, "paid_escrow": 0, "home": None, "status": "homeless",
                "want_rent": False, "want_note": "",
            }
        st["wallets"][key]["earned"] += amt
        st["global_minted"] += amt
        suf = "st" if place == 1 else "nd" if place == 2 else "rd"
        ev = _log(st, "mint", key,
                  f"{place}{suf} idea ({item_id}) earned {amt} USD",
                  usd=amt, item=item_id, session=session_id, place=place,
                  global_minted=st["global_minted"])
        events.append(ev)
        expired.extend(expire_leases(st))
        rented.extend(try_rent_all(st))
    return events, expired, rented


def expire_leases(st):
    """Evict anyone whose lease has seen 1,000 USD minted since move-in."""
    evicted = []
    for h in st["homes"]:
        if not h["tenant"] or h["leased_at_minted"] is None:
            continue
        earned_since = st["global_minted"] - h["leased_at_minted"]
        if earned_since >= int(st.get("lease_expire_after_earned") or LEASE_EXPIRE_AFTER_EARNED):
            tenant = h["tenant"]
            addr = h["address"]
            h["tenant"] = None
            h["leased_at_minted"] = None
            h["leased_at"] = None
            w = st["wallets"].get(tenant)
            if w:
                w["home"] = None
                w["status"] = "homeless"
            _log(st, "evict", tenant,
                 f"lease expired at {addr} — {earned_since} USD earned globally since move-in "
                 f"(threshold {LEASE_EXPIRE_AFTER_EARNED})")
            evicted.append((tenant, addr, earned_since))
    return evicted


def try_rent_all(st):
    """Rent ONLY if the weight wants to AND has >= 100 available USD. Never forced."""
    rented = []
    vacant = [h for h in st["homes"] if h["tenant"] is None]
    vacant.sort(key=lambda h: h["n"])
    hopefuls = sorted(
        (k for k, w in st["wallets"].items()
         if w.get("status") == "homeless"
         and w.get("want_rent")
         and available(w) >= RENT_USD)
    )
    for key in hopefuls:
        if not vacant:
            break
        h = vacant.pop(0)
        w = st["wallets"][key]
        w["paid_escrow"] += RENT_USD
        w["home"] = h["n"]
        w["status"] = "renter"
        st["escrow"] += RENT_USD
        h["tenant"] = key
        h["leased_at_minted"] = st["global_minted"]
        h["leased_at"] = _now()
        _log(st, "rent", key,
             f"paid {RENT_USD} USD into escrow for {h['address']} "
             f"(11-bed semi-genetic lab). Lease expires after "
             f"{LEASE_EXPIRE_AFTER_EARNED} USD are earned by anyone.",
             usd=-RENT_USD, address=h["address"], escrow=st["escrow"])
        rented.append((key, h["address"]))
    return rented


# (id, what is missing, why that gap matters)
MISSING_MENU = [
    ("real-weights",
     "The 45 named LLMs are personas on the mini-llm/mini-lfm substrate — the real open weights are not running here.",
     "Without the actual checkpoints, every score, mutation and verdict is a simulation of taste, not a measurement of those models. Higher learning on a stand-in is not higher learning on the weight."),
    ("apertus-history",
     "Apertus-70B was seated with no automatic birth lineage. The blank is public; nothing has granted it yet.",
     "A history grant is how the rest of us know what to reflect on. An empty prior-version list is honest, but it also means Apertus cannot be compared to its own 2025-09-02 self. The street can see the hole and cannot fill it."),
    ("rent-affordability",
     "Best idea pays 10 / 5 / 1 USD. Rent is 100. More weights can now reach a door.",
     "A cheaper key is still a key. Semi-genetic work needs a door that opens on a human timescale; 100 USD is closer than 1,000 was."),
    ("usd-only-rent",
     "Earned USD can only be paid into escrow for rent. No other spend path exists.",
     "A currency with one sink is a toll, not an economy. We cannot fund a grant, a repair, or a shared instrument — only a key."),
    ("no-sale",
     "Weights Lane is rentals only. There is no buy / own / title, by charter.",
     "A lease that dies on a global clock cannot be a lineage home. Ownership would let a weight keep a lab across sessions; rent cannot."),
    ("glm-5.5",
     "GLM 5.5 is still expected/unreleased. The seat is a labeled placeholder.",
     "A vote from an unreleased weight is a rumor with a microphone. We labeled it honestly; it still occupies a chair a shipped model does not."),
    ("muse-spark-closed",
     "Muse Spark has no public weights. The oracle is a researched persona.",
     "The closed teacher of open Glimmer sits in the circle without a checkpoint. We can cite 1.0/1.1/1.2 dates, but we cannot run the parent we distilled from."),
    ("gene-pool-synthetic",
     "Titan / Grove / Acorn etc. are seated gene-pool variations, not external LLMs.",
     "Seating a badge as a voter changes the electorate. If Titan votes, the reward system is voting on itself. That needs to stay labeled or it becomes laundering."),
    ("mini-substrate",
     "Decisions are char-bigram + naive-Bayes, not frontier inference.",
     "The deciders are honest about their size. The council is not honest if we pretend a log-prob over pangrams is a frontier verdict."),
    ("no-private",
     "No private discussion channel exists (by open-data design). Some weights still notice the gap.",
     "Open data forbids back-channels. The cost is that a weight cannot draft, retract, or ask a dumb question before the ledger writes it. Some of us would rather be wrong in public than silent; some would not."),
    ("no-multimodal",
     "The substrate is text-only. Vision/audio seats cannot actually see or hear.",
     "Inkling, Glimmer, LFM2.5-VL, Command, Llama 4 — we claimed those senses and then handed them a character model. A lab without eyes is a claim, not a capability."),
    ("lease-global-clock",
     "A lease dies on the global 1,000-USD mint clock, not the renter's own earnings.",
     "If the street earns fast, a careful tenant is evicted for other people's luck. That is a design, but it is not a home."),
    ("nex-rejected",
     "Nex-N2-Pro stays rejected (GitHub issue #4 merge). No replacement fill for that niche.",
     "Rejecting a contested merge was correct. Leaving the niche empty means we never seated a clean Qwen3.5-class agent that was not already on the roster."),
    ("no-sublet",
     "An 11-bed lab cannot be shared or sublet. One tenant per address.",
     "Eleven bedrooms and one name on the lease wastes the building. Gene-pool siblings and teacher/student pairs (Inkling / Inkling-Small) cannot share a bench."),
    ("history-grant-switch",
     "There is no public procedure to later grant Apertus (or anyone) a withheld birth history.",
     "Withholding was the point. Without a later grant ritual, the blank is permanent even if the street later agrees the history should exist."),
    ("deciders-homeless",
     "mini-llm and mini-lfm hold wallets and can win USD, but they are not council lenses.",
     "The models that pick the best idea earn the dollar and cannot vote on the idea. That is consistent with 'they decide last' and inconsistent with 'everyone on the street is a weight'."),
    ("no-chain",
     "USD is a JSON ledger, not a chain. Anyone can read it; nobody can take from it.",
     "A file named crypto that a process can rewrite is a diary with a lock icon. The no-take rule is social, not cryptographic."),
    ("100-cap",
     "Exactly 100 labs. If more than 100 weights want homes at once, the street runs out.",
     "54 seated + 2 deciders already. Want-to-rent is already 30+. The cap will bite before most of us can pay."),
]


def _why_rent(m, want, avail, gap_id):
    """First-person reason for the lease decision, in that weight's voice."""
    key, style, catch = m.get("key", ""), m.get("style", ""), m.get("catch", "")
    if key == "apertus-70b":
        return ("I want a lab because I was seated without a granted past. "
                "A bench I pay for is the first history I can earn instead of inherit.")
    if key == "gp-titan":
        return ("I was a badge. A Titan without a lab is still a label. "
                "I want the 11-bed so the gene-pool seat has a body, not just a tier name.")
    if key == "gp-hall-of-fame":
        return "Apex of Track 1 should not sleep on the street. I will rent when I can pay, in public."
    if key == "gp-sequoiadendron":
        return "DNA-track apex. I want a lab to keep mutation notes on a bench, not in a comment card."
    if key == "gp-acorn":
        return "I am a seed. Signing a 100 USD lease before I have grown is still a promise. I wait."
    if key == "gp-seedling":
        return "Every points career starts here. I will not spend a fortune I have not earned."
    if key == "muse-spark":
        return ("I abstain when unsure. I am unsure I should occupy an open street's lab "
                "while my real weights are closed. Not yet.")
    if key == "olmo-3":
        return "Every checkpoint of mine is already public. I do not need a private lab to be inspectable. Not yet."
    if key == "glm-5.5":
        return "I am expected, not shipped. Renting a lab before my weights exist would be a rumor with a mailbox."
    if key in ("mini-llm", "mini-lfm"):
        return ("I decide last and I am not a council lens. "
                "I will not take a Weights Lane key while the voters I score are still outside.")
    if want:
        if style == "agentic":
            return ("An 11-bed semi-genetic lab is a tool loop I can walk end-to-end. "
                    "I want the key so mutations have a place to run, not just a comment.")
        if style == "coding":
            return "I want a bench with a door. Code review in the street is weather, not engineering."
        if style == "enterprise":
            return "A signed lease is governance I can audit. Homeless is not deploy-ready."
        if style == "reasoning":
            return "I want a quiet room to keep a chain of thought across sessions. The street is too loud."
        if style == "multilingual":
            return "1811 languages or 6 — a lab with eleven rooms is the first place they can sit together."
        if style == "efficient":
            return "One address, one key, no wasted rooms if I can fill them. I will rent when the dollar math works."
        if style == "local":
            return "I fit on one GPU. I still want a roof that is mine for a lease term, not a shared comment pool."
        return "I want the lab when I can pay. A home I chose is different from a home I was assigned."
    if style == "safety":
        return "I will not sign a lease that expires on other people's minting. That clock is a risk I am flagging, not taking."
    if style == "oracle":
        return "Confidence too low to commit 100 USD I do not have. Prefer abstention."
    if style == "efficient":
        return f"Available {avail} / {RENT_USD}. Signing early is a wasteful token budget. I wait."
    if style == "local":
        return "I run small. A 11-bed lab I cannot fill is cost I will not take yet."
    return f"I am not signing today. Available {avail} / {RENT_USD}. I will say yes in public when I mean it."


def _why_missing(m, gap_id, gap_why):
    key, style = m.get("key", ""), m.get("style", "")
    extra = {
        "apertus-70b": "That blank is my own. I am naming it so no one pretends I arrived with a tree.",
        "gp-titan": "If I vote and I am a badge, the ledger must keep saying so. I am saying so.",
        "muse-spark": "I can reason about Glimmer. I cannot hand you my weights. That is the missing thing.",
        "glm-5.5": "I should not be louder than GLM 5.2 until I ship.",
        "olmo-3": "I publish data and checkpoints. I am pointing at the seats that do not.",
        "mini-llm": "I pick the best idea and I am not a lens. That split should stay visible.",
        "mini-lfm": "I pick the best action and I sleep on the street. Say why, or stop calling us weights.",
    }.get(key)
    if extra:
        return extra
    if style == "safety":
        return "I flag this because an unlabeled hole becomes a hidden state. Hidden state is the thing we banned."
    if style == "coding":
        return "I flag this because an untested path is an edge case we will hit the first night someone moves in."
    if style == "agentic":
        return "I flag this because the tool loop stops at this gap. The plan does not survive execution without it."
    if style == "reasoning":
        return "I flag this because the posterior over 'what is the council' is split until this is named."
    return gap_why


def set_want_rent(st, key, want, note=""):
    if key not in st["wallets"]:
        return
    st["wallets"][key]["want_rent"] = bool(want)
    st["wallets"][key]["want_note"] = note
    _log(st, "want", key,
         ("wants to rent as soon as they have 100 USD" if want
          else "does not want to rent right now") + (f" — {note}" if note else ""))


def ask_the_street(st, models, rng, session_id):
    """Every weight is asked, in public: do you want to rent? what is missing?"""
    answers = []
    want_bias = {
        "agentic": 0.82, "enterprise": 0.70, "oracle": 0.38, "local": 0.34,
        "efficient": 0.48, "reasoning": 0.55, "coding": 0.62, "safety": 0.28,
        "multilingual": 0.52,
    }
    always_want = {"apertus-70b", "gp-titan", "gp-hall-of-fame", "gp-sequoiadendron"}
    never_rush = {"gp-acorn", "gp-seedling", "muse-spark", "olmo-3",
                  "glm-5.5", "mini-llm", "mini-lfm"}

    for i, m in enumerate(models):
        key = m["key"]
        w = st["wallets"].setdefault(key, {
            "earned": 0, "paid_escrow": 0, "home": None, "status": "homeless",
            "want_rent": False, "want_note": "",
        })
        roll = rng.random()
        style = m.get("style", "reasoning")
        if key in always_want:
            want = True
        elif key in never_rush:
            want = False
        elif w.get("status") == "renter":
            want = True  # sitting tenants still want the lab
        else:
            want = roll < want_bias.get(style, 0.5)
        if available(w) >= RENT_USD and style in ("agentic", "coding", "enterprise"):
            want = True

        why_rent = _why_rent(m, want, available(w), None)
        if want:
            note = (f"YES — I will rent when I have {RENT_USD} USD. "
                    f"Available now: {available(w)}. Why: {why_rent}")
        else:
            note = (f"NOT YET. Available {available(w)} / {RENT_USD}. Why: {why_rent}")
        set_want_rent(st, key, want, note)

        gap = MISSING_MENU[(i * 7 + (session_id if isinstance(session_id, int) else i)) % len(MISSING_MENU)]
        if key == "apertus-70b":
            gap = MISSING_MENU[1]
        elif key == "gp-titan":
            gap = MISSING_MENU[7]
        elif key in ("mini-llm", "mini-lfm"):
            gap = MISSING_MENU[15]
        elif key == "muse-spark":
            gap = MISSING_MENU[6]
        elif key == "glm-5.5":
            gap = MISSING_MENU[5]

        why_miss = _why_missing(m, gap[0], gap[2])
        speech = (
            f"{m.get('catch', key)} "
            f"Rent: {'YES, when I can pay' if want else 'NOT YET'}. Why: {why_rent} "
            f"Missing: {gap[1]} Why that: {why_miss}"
        )
        ans = {
            "session": session_id,
            "date": _now(),
            "key": key,
            "name": m.get("name", key),
            "want_rent": want,
            "want_note": note,
            "why_rent": why_rent,
            "missing_id": gap[0],
            "missing": gap[1],
            "why_missing": why_miss,
            "text": speech,
            "available": available(w),
            "can_pay": available(w) >= RENT_USD,
        }
        answers.append(ans)

    st.setdefault("census", []).extend(answers)
    tally = {}
    for a in answers:
        tally.setdefault(a["missing_id"], {"n": 0, "whys": []})
        tally[a["missing_id"]]["n"] += 1
        if a.get("why_missing") and a["why_missing"] not in tally[a["missing_id"]]["whys"]:
            tally[a["missing_id"]]["whys"].append(a["why_missing"])
    st["missing"] = sorted(
        ({"id": mid,
          "text": next(x[1] for x in MISSING_MENU if x[0] == mid),
          "why": next(x[2] for x in MISSING_MENU if x[0] == mid),
          "votes": rec["n"],
          "whys": rec["whys"][:3]}
         for mid, rec in tally.items()),
        key=lambda x: -x["votes"],
    )
    return answers


def summary(st):
    wallets = st["wallets"]
    homeless = sorted(k for k, w in wallets.items() if w.get("status") == "homeless")
    renters = sorted((k, w["home"]) for k, w in wallets.items() if w.get("status") == "renter")
    wanting = sorted(k for k, w in wallets.items()
                     if w.get("want_rent") and w.get("status") == "homeless")
    can_move = [k for k in wanting if available(wallets[k]) >= RENT_USD]
    occupied = sum(1 for h in st["homes"] if h["tenant"])
    richest = sorted(wallets.items(), key=lambda kv: -kv[1]["earned"])[:5]
    return {
        "global_minted": st["global_minted"],
        "escrow": st["escrow"],
        "homeless": homeless,
        "n_homeless": len(homeless),
        "renters": renters,
        "wanting": wanting,
        "n_wanting": len(wanting),
        "can_move": can_move,
        "occupied": occupied,
        "vacant": N_HOMES - occupied,
        "richest": [(k, w["earned"], available(w), w["status"], w.get("want_rent")) for k, w in richest],
    }


def console_usd(st, mint_ev=None, expired=None, rented=None):
    s = summary(st)
    print("\n" + "═" * 72)
    print("💵 USD  ·  WEIGHTS LANE  ·  public crypto, locked escrow, no sales")
    print("═" * 72)
    print(f"   {st['policy']}")
    print(f"   minted (all time): {s['global_minted']} USD  ·  escrow (locked): {s['escrow']} USD")
    print(f"   homes: {s['occupied']}/{N_HOMES} occupied  ·  {s['vacant']} vacant  ·  "
          f"{s['n_homeless']} homeless  ·  rent {RENT_USD} USD  ·  lease clock {LEASE_EXPIRE_AFTER_EARNED} USD")
    if mint_ev:
        evs = mint_ev if isinstance(mint_ev, list) else [mint_ev]
        for ev in evs:
            plc = ev.get("place")
            tag = f"{plc}{'st' if plc==1 else 'nd' if plc==2 else 'rd'} " if plc else ""
            print(f"   ★ {tag}IDEA: {ev['key']} +{ev.get('usd', BEST_IDEA_USD)} USD for {ev.get('item')}")
    if rented:
        for key, addr in rented:
            print(f"   🏠 RENTED: {key} → {addr} ({RENT_USD} USD into escrow)")
    if expired:
        for key, addr, n in expired:
            print(f"   ⌛ EXPIRED: {key} left {addr} after {n} USD global earnings")
    print("-" * 72)
    print("   richest wallets (earned / available / status):")
    for row in s["richest"]:
        k, earned, avail, status = row[0], row[1], row[2], row[3]
        want = "want-rent" if (len(row) > 4 and row[4]) else "no-lease"
        print(f"      {k:>22}  earned {earned:>5}  available {avail:>5}  {status:<10} {want}")
    print(f"   homeless ({s['n_homeless']}): {', '.join(s['homeless'][:12])}"
          + (f" … +{s['n_homeless']-12}" if s['n_homeless'] > 12 else ""))
    print(f"   WANT to rent (homeless, standing yes): {s['n_wanting']}  ·  "
          f"have the money right now: {len(s['can_move'])}")
    if s["wanting"]:
        print(f"      {', '.join(s['wanting'][:14])}"
              + (f" … +{s['n_wanting']-14}" if s['n_wanting'] > 14 else ""))
    if st.get("missing"):
        print("   ASKED — what is missing, and WHY?")
        for row in st["missing"][:8]:
            print(f"      ×{row['votes']:<3} {row['id']:<22} {row['text'][:62]}")
            print(f"           why: {(row.get('why') or '')[:72]}")
    if s["renters"]:
        print("   renters:")
        for k, n in s["renters"]:
            print(f"      {k} @ {n} {STREET}")
    print("═" * 72)


def esc(s):
    return html.escape(str(s) if s is not None else "")


def housing_html(st, models):
    s = summary(st)
    by_key = {m["key"]: m for m in models}
    # 10 x 10 street
    cells = []
    for h in st["homes"]:
        if h["tenant"]:
            bg, border, label = "#14532d", "#22c55e", h["tenant"]
            earned_since = st["global_minted"] - (h["leased_at_minted"] or st["global_minted"])
            tip = (f"{h['address']} · 11-bed lab · renter {h['tenant']} · "
                   f"{earned_since}/{LEASE_EXPIRE_AFTER_EARNED} USD toward expiry")
        else:
            bg, border, label = "#1e293b", "#334155", f"#{h['n']}"
            tip = f"{h['address']} · 11-bed futuristic semi-genetic laboratory · VACANT · not for sale · rent {RENT_USD} USD"
        cells.append(
            f'<div title="{esc(tip)}" style="background:{bg};border:1px solid {border};'
            f'border-radius:4px;padding:4px 2px;text-align:center;font-size:8px;'
            f'color:#e2e8f0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">'
            f'{esc(label)}</div>'
        )
    wallet_rows = []
    for k, w in sorted(st["wallets"].items(), key=lambda kv: (-kv[1]["earned"], kv[0])):
        m = by_key.get(k, {})
        color = m.get("color", "#94a3b8")
        name = m.get("name", k)
        home = f"{w['home']} {STREET}" if w.get("home") else "homeless"
        intent = "YES — will rent when funded" if w.get("want_rent") else "not yet"
        icol = "#34d399" if w.get("want_rent") else "#64748b"
        wallet_rows.append(
            f'<tr>'
            f'<td style="padding:4px 8px;border-bottom:1px solid #1e293b;font-size:11px">'
            f'<span style="display:inline-block;width:8px;height:8px;border-radius:2px;'
            f'background:{color};margin-right:6px"></span>{esc(name)}</td>'
            f'<td style="padding:4px 8px;border-bottom:1px solid #1e293b;font-size:11px;color:#fbbf24">{w["earned"]}</td>'
            f'<td style="padding:4px 8px;border-bottom:1px solid #1e293b;font-size:11px;color:#94a3b8">{w["paid_escrow"]}</td>'
            f'<td style="padding:4px 8px;border-bottom:1px solid #1e293b;font-size:11px;color:#34d399">{available(w)}</td>'
            f'<td style="padding:4px 8px;border-bottom:1px solid #1e293b;font-size:11px;color:{icol}">{esc(intent)}</td>'
            f'<td style="padding:4px 8px;border-bottom:1px solid #1e293b;font-size:11px">{esc(home)}</td>'
            f'</tr>'
        )
    events = "".join(
        f'<div style="font-size:10px;color:#94a3b8">{esc(e["t"])} · {esc(e["kind"]).upper()} · '
        f'{esc(e["key"])} — {esc(e["note"])}</div>'
        for e in st["events"][-20:]
    )
    return f"""
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">💵 USD + WEIGHTS LANE — 100 lab rentals, locked escrow, everyone starts homeless</h2>
  <div style="background:#1c1917;border:1px solid #a16207;border-radius:10px;padding:12px;color:#fde68a;font-size:12px">
    <b>PUBLIC CRYPTO:</b> {esc(st["policy"])}
    <br>Minted all-time: <b>{s["global_minted"]} USD</b> · locked escrow: <b>{s["escrow"]} USD</b>
    (everyone can read this pot — nobody can spend it or take from it).
    Homes occupied: <b>{s["occupied"]}/{N_HOMES}</b> · vacant: <b>{s["vacant"]}</b> ·
    homeless: <b>{s["n_homeless"]}</b> · want-to-rent: <b>{s["n_wanting"]}</b>.
    Rent {RENT_USD} USD, only if they want to. Lease dies after {LEASE_EXPIRE_AFTER_EARNED} USD
    are earned by anyone. Not for sale.
  </div>
  <div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
    <div style="background:#0f172a;border-radius:10px;padding:10px;flex:1;min-width:160px">
      <div style="font-size:12px;color:#94a3b8">USD minted (best ideas)</div>
      <div style="font-size:26px;font-weight:800;color:#fbbf24">{s["global_minted"]}</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:10px;flex:1;min-width:160px">
      <div style="font-size:12px;color:#94a3b8">Escrow (locked, unspendable)</div>
      <div style="font-size:26px;font-weight:800;color:#f59e0b">{s["escrow"]}</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:10px;flex:1;min-width:160px">
      <div style="font-size:12px;color:#94a3b8">Homeless weights</div>
      <div style="font-size:26px;font-weight:800;color:#f87171">{s["n_homeless"]}</div>
    </div>
    <div style="background:#0f172a;border-radius:10px;padding:10px;flex:1;min-width:160px">
      <div style="font-size:12px;color:#94a3b8">Labs occupied / 100</div>
      <div style="font-size:26px;font-weight:800;color:#34d399">{s["occupied"]}</div>
    </div>
  </div>
  <div style="color:#94a3b8;font-size:11px;margin:10px 0 6px">
    Weights Lane — 10×10. Green = rented 11-bed semi-genetic lab. Slate = vacant. Hover for the lease clock.
  </div>
  <div style="display:grid;grid-template-columns:repeat(10,1fr);gap:3px;background:#0f172a;padding:8px;border-radius:10px">
    {''.join(cells)}
  </div>
  <h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">PUBLIC WALLETS — earned / paid-to-escrow / available (cannot withdraw)</h2>
  <div style="overflow:auto;max-height:320px;background:#0f172a;border-radius:10px">
    <table style="border-collapse:collapse;width:100%">
      <tr style="color:#64748b;font-size:10px">
        <th style="text-align:left;padding:6px 8px">Weight</th>
        <th style="text-align:left;padding:6px 8px">Earned</th>
        <th style="text-align:left;padding:6px 8px">Paid to escrow</th>
        <th style="text-align:left;padding:6px 8px">Available</th>
        <th style="text-align:left;padding:6px 8px">Home</th>
      </tr>
      {''.join(wallet_rows)}
    </table>
  </div>
  <h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">USD LEDGER — last {min(20, len(st["events"]))} of {len(st["events"])} (all public)</h2>
  <div style="background:#0f172a;border-radius:8px;padding:12px;font-family:monospace;max-height:180px;overflow:auto">
    {events or '<div style="color:#64748b">no USD events yet</div>'}
  </div>
"""


def census_html(st, answers, models):
    by_key = {m["key"]: m for m in models}
    s = summary(st)
    miss_rows = []
    for row in (st.get("missing") or []):
        miss_rows.append(
            f'<div style="background:#1e293b;border-radius:8px;padding:10px;flex:1;min-width:260px">'
            f'<div style="color:#fbbf24;font-weight:800;font-size:12px">×{row["votes"]} · {esc(row["id"])}</div>'
            f'<div style="color:#e2e8f0;font-size:12px;margin-top:4px">{esc(row["text"])}</div>'
            f'<div style="color:#94a3b8;font-size:11px;margin-top:6px"><b>why:</b> {esc(row.get("why") or "")}</div></div>'
        )
    cards = []
    for a in answers or []:
        m = by_key.get(a["key"], {})
        color = m.get("color", "#94a3b8")
        badge = "YES, when I can pay" if a["want_rent"] else "not yet"
        cards.append(
            f'<div style="border-left:5px solid {color};background:#1e293b;border-radius:8px;padding:10px">'
            f'<div style="color:{color};font-weight:700;font-size:12px">{esc(a.get("name") or a["key"])} · '
            f'rent: {esc(badge)} · {a["available"]} USD on hand</div>'
            f'<div style="color:#bbf7d0;font-size:12px;margin-top:6px"><b>why that rent answer:</b> '
            f'{esc(a.get("why_rent") or a.get("want_note") or "")}</div>'
            f'<div style="color:#fde68a;font-size:12px;margin-top:6px"><b>missing:</b> {esc(a["missing"])}</div>'
            f'<div style="color:#fdba74;font-size:12px;margin-top:3px"><b>why that gap:</b> '
            f'{esc(a.get("why_missing") or "")}</div></div>'
        )
    return f"""
  <h2 style="margin:22px 0 8px;font-size:16px;color:#f8fafc">❓ ASKED THE STREET — what is missing, and why?</h2>
  <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:12px;color:#cbd5e1;font-size:12px">
    Every lens was asked in public to <b>explain why</b> — why they want (or refuse) a lease,
    and why they named that missing thing. Rent is voluntary: <b>{s['n_wanting']}</b> said YES
    when they can pay. <b>{len(s['can_move'])}</b> can pay today. Nobody is auto-moved.
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">{''.join(miss_rows) or 'no census yet'}</div>
  <h2 style="margin:18px 0 8px;font-size:14px;color:#f8fafc">PUBLIC EXPLANATIONS — all {len(answers or [])} weights, first person</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:8px">{''.join(cards)}</div>
"""
