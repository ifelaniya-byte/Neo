#!/usr/bin/env python3
"""
COUNCIL ROUTER — management plane for KP-14.

Runs HERE (no GPU, no torch). It does not pretend to load 70B.
It classifies a seat and returns a route + provenance:

  local file → ModelScope catalog → Kaggle listing → HF API (gated) → substrate → unavailable

Inference of real weights happens on a single-account Kaggle T4 via the
batch notebooks, or on HF Inference Providers only when
WEIGHTS_ALLOW_HF_TOKEN=1 AND credits exist. This module never prints tokens.

USED BY: model_council.py
"""

import json
import os
import time

import seat_registry
import weight_source
import mini_llm
import mini_lfm

BASE = os.path.dirname(os.path.abspath(__file__))


def _offline_exists(rel):
    if not rel:
        return False
    path = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    return os.path.exists(path) and os.path.getsize(path) > 0


def classify(key):
    s = seat_registry.BY_KEY.get(key)
    if not s:
        return {
            "key": key, "route": "unknown", "status": "logical-emulated",
            "runnable_here": False, "runnable_t4": False,
            "note": "seat not in registry",
        }
    route = "unavailable"
    if s["backend"] == "substrate" or s.get("local_path") in ("mini_llm.py", "mini_lfm.py"):
        route = "substrate"
    elif s["local_path"] and _offline_exists(s["local_path"]):
        route = "local-file"
    elif s["status"] == "verified-checkpoint" and s["backend"] == "modelscope":
        route = "modelscope-catalog"
    elif s["status"] == "verified-checkpoint" and s["backend"] == "kaggle":
        route = "kaggle-catalog"
    elif s["status"] == "verified-api":
        route = "hf-api-depleted"
    elif s["status"] == "community-quarantine":
        route = "quarantine"
    elif s["status"] == "logical-emulated":
        route = "emulated"
    allow_hf = os.environ.get("WEIGHTS_ALLOW_HF_TOKEN") == "1"
    hf_present = bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"))
    return {
        "key": key,
        "status": s["status"],
        "domain": s["domain"],
        "backend": s["backend"],
        "identifier": s["identifier"],
        "route": route,
        "t4": s["t4"],
        "runnable_here": route == "substrate",
        "runnable_t4": s["t4"] in ("easy", "tight") and s["status"] in (
            "verified-checkpoint", "community-quarantine"),
        "hf_allowed": allow_hf and hf_present,
        "trust_remote_code": s["trust_remote_code"],
        "note": s["note"],
    }


def substrate_answer(key, prompt):
    """Honest tiny fallback. Never claims to be the named giant."""
    tables, vocab = mini_llm.train(mini_llm.CORPUS, 3)
    import random
    cont = mini_llm.generate(tables, vocab, 48, 0.7, prompt[:24], random.Random(0), 3)
    facts = mini_lfm.train(mini_lfm.FACTS)
    probs, matched, _h = mini_lfm.score(facts[0], facts[2], prompt, 0.15)
    top = max(range(len(probs)), key=lambda i: probs[i])
    return {
        "ok": True,
        "kind": "substrate",
        "seat": key,
        "text": (
            f"[substrate · seat={key} · NOT the named checkpoint] "
            f"fact={facts[2][top]!r} p={probs[top]:.3f} "
            f"bigram={cont[:80]!r}"
        ),
        "matched": sorted(matched),
    }


def execute_seat(key, prompt):
    """Route only. Real GPU inference is a Kaggle notebook job, not this box."""
    rec = classify(key)
    rec["prompt"] = prompt
    rec["date"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if rec["route"] == "substrate" or rec["route"] in ("emulated", "quarantine", "unavailable",
                                                       "hf-api-depleted", "modelscope-catalog",
                                                       "kaggle-catalog", "local-file", "unknown"):
        # This sandbox cannot run torch. Local-file is a safetensors on disk.
        if rec["route"] == "local-file":
            rec["result"] = {
                "ok": False, "kind": "file-only",
                "text": (f"[{key}] verified file present but this box has no torch/GPU. "
                         f"Upload to a Kaggle T4 notebook. Identifier={rec.get('identifier')}."),
            }
        elif rec["route"] == "hf-api-depleted":
            rec["result"] = {
                "ok": False, "kind": "api-blocked",
                "text": (f"[{key}] last live id {rec.get('identifier')}. "
                         "HF credits 402 / token absent. Do not retry 402."),
            }
        elif rec["route"] == "quarantine":
            rec["result"] = {
                "ok": False, "kind": "quarantine",
                "text": (f"[{key}] community listing `{rec.get('identifier')}` is quarantined. "
                         "trust_remote_code=False. Do not train from it yet."),
            }
        elif rec["route"] in ("modelscope-catalog", "kaggle-catalog"):
            rec["result"] = {
                "ok": False, "kind": "catalog-only",
                "text": (f"[{key}] {rec['route']} `{rec.get('identifier')}` "
                         f"T4={rec['t4']}. Pull/run on a single-account Kaggle session."),
            }
        else:
            rec["result"] = substrate_answer(key, prompt)
    return rec


def snapshot():
    rows = [classify(s["key"]) for s in seat_registry.SEATS]
    by_route = {}
    for r in rows:
        by_route[r["route"]] = by_route.get(r["route"], 0) + 1
    return {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "policy": weight_source.apply_offline_policy(),
        "counts": seat_registry.counts(),
        "routes": by_route,
        "rows": rows,
    }


def console(snap=None):
    snap = snap or snapshot()
    print("\n" + "⇨" * 36)
    print("COUNCIL ROUTER — classify only; no fake 70B load")
    print("⇨" * 36)
    print("  routes:", snap.get("routes"))
    c = snap.get("counts") or {}
    print(f"  registry {c}")
    print("⇨" * 36)


def export_md(snap=None):
    snap = snap or snapshot()
    lines = [
        "# Council router snapshot",
        "",
        f"- Date: {snap.get('date')}",
        f"- Routes: `{json.dumps(snap.get('routes'))}`",
        f"- HF offline: `{(snap.get('policy') or {}).get('hf_offline')}`",
        f"- HF token in env: `{(snap.get('policy') or {}).get('hf_token_in_env')}`",
        "",
        "Runnable *here* = substrate only. Runnable on T4 = verified/quarantine easy|tight.",
        "",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    seat_registry.write_mapping()
    snap = snapshot()
    console(snap)
    print(json.dumps(execute_seat("smollm3-3b", "what is the largest ocean"), indent=2)[:600])
    print(json.dumps(execute_seat("glm-5.5", "unreleased check"), indent=2)[:500])
