#!/usr/bin/env python3
"""
KP-16 — complete offline artifact gate.

A single .safetensors is not a runnable model. Required:
  weight verified AND config AND tokenizer files AND license recorded.

transformers load is attempted only if the package exists.
This sandbox typically has no transformers — then we report file-gate only.
"""

import hashlib
import json
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))
QWEN_DIR = os.path.join(
    BASE, "weights_offline", "modelscope", "Qwen__Qwen2.5-0.5B-Instruct")
REQUIRED = (
    "model.safetensors",
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "generation_config.json",
    "vocab.json",
    "merges.txt",
    "LICENSE",
)
_MANIFEST = os.path.join(BASE, "registry", "qwen25_05b_manifest.json")


def _load_pins():
    pins = {
        "model.safetensors": {
            "bytes": 988097824,
            "sha256": "fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe",
        },
    }
    try:
        man = json.load(open(_MANIFEST, encoding="utf-8"))
        for name, meta in (man.get("files") or {}).items():
            if meta.get("sha256") and meta.get("bytes"):
                pins[name] = {"bytes": meta["bytes"], "sha256": meta["sha256"]}
        return pins, man
    except Exception:
        return pins, None


PINNED, MANIFEST = _load_pins()


def sha256_file(path):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def verify_offline_artifact(model_dir=None):
    root = model_dir or QWEN_DIR
    rec = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_dir": os.path.relpath(root, BASE) if os.path.isabs(root) else root,
        "exists": os.path.isdir(root),
        "files": {},
        "required_ok": False,
        "weight_pinned_ok": False,
        "config_json_ok": False,
        "tokenizer_files_ok": False,
        "transformers_available": False,
        "config_load_ok": None,
        "tokenizer_load_ok": None,
        "runnable_offline": False,
        "errors": [],
        "status": "incomplete",
    }
    if not rec["exists"]:
        rec["errors"].append("model directory missing")
        rec["status"] = "absent"
        return rec
    for fn in sorted(os.listdir(root)):
        path = os.path.join(root, fn)
        if not os.path.isfile(path):
            continue
        digest, size = sha256_file(path)
        pin = PINNED.get(fn)
        row = {"bytes": size, "sha256": digest, "pinned": bool(pin)}
        if pin:
            row["pin_match"] = digest == pin["sha256"] and size == pin["bytes"]
            if not row["pin_match"]:
                rec["errors"].append(f"pin mismatch {fn}")
        rec["files"][fn] = row
    missing = [r for r in REQUIRED if r not in rec["files"]]
    rec["missing_required"] = missing
    rec["required_ok"] = not missing
    rec["weight_pinned_ok"] = bool(
        rec["files"].get("model.safetensors", {}).get("pin_match"))
    rec["config_json_ok"] = "config.json" in rec["files"]
    rec["tokenizer_files_ok"] = all(
        f in rec["files"] for f in ("tokenizer.json", "tokenizer_config.json",
                                    "vocab.json", "merges.txt"))
    try:
        with open(os.path.join(root, "config.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        rec["model_type"] = cfg.get("model_type")
        rec["architectures"] = cfg.get("architectures")
        rec["vocab_size"] = cfg.get("vocab_size")
        rec["license_file"] = "LICENSE" in rec["files"]
    except Exception as e:
        rec["errors"].append(f"config parse: {e}")
        rec["config_json_ok"] = False

    rec["tokenizer_offline_safe"] = False
    tcfg_path = os.path.join(root, "tokenizer_config.json")
    if os.path.isfile(tcfg_path):
        with open(tcfg_path, encoding="utf-8") as fh:
            tcfg = json.load(fh)
        blob = json.dumps(tcfg)
        remote = ("http://" in blob.lower()) or ("https://" in blob.lower()) \
            or ("huggingface.co" in blob.lower())
        rec["tokenizer_class"] = tcfg.get("tokenizer_class")
        rec["chat_template_embedded"] = isinstance(tcfg.get("chat_template"), str) \
            and len(tcfg.get("chat_template") or "") > 20
        rec["tokenizer_auto_map"] = tcfg.get("auto_map")
        rec["tokenizer_remote_refs"] = remote
        rec["tokenizer_offline_safe"] = (
            rec["chat_template_embedded"]
            and not remote
            and not tcfg.get("auto_map")
            and tcfg.get("tokenizer_class") in ("Qwen2Tokenizer", "PreTrainedTokenizer",
                                                "PreTrainedTokenizerFast", "Qwen2TokenizerFast")
        )
        if not rec["tokenizer_offline_safe"]:
            rec["errors"].append("tokenizer_config not offline-safe")

    try:
        import transformers  # noqa: F401
        rec["transformers_available"] = True
        from transformers import AutoConfig, AutoTokenizer
        try:
            c = AutoConfig.from_pretrained(
                root, local_files_only=True, trust_remote_code=False)
            rec["config_load_ok"] = True
            rec["model_type"] = getattr(c, "model_type", rec.get("model_type"))
        except Exception as e:
            rec["config_load_ok"] = False
            rec["errors"].append(f"config load: {type(e).__name__}: {e}")
        try:
            tok = AutoTokenizer.from_pretrained(
                root, local_files_only=True, trust_remote_code=False)
            rec["tokenizer_load_ok"] = True
            rec["tokenizer_class"] = type(tok).__name__
            rec["tokenizer_len"] = len(tok)
        except Exception as e:
            rec["tokenizer_load_ok"] = False
            rec["errors"].append(f"tokenizer load: {type(e).__name__}: {e}")
    except ImportError:
        rec["transformers_available"] = False
        rec["errors"].append(
            "transformers not installed here — file-gate only, load unproven")

    rec["manifest_files_pinned"] = all(
        rec["files"].get(name, {}).get("pin_match") for name in REQUIRED
        if name in PINNED)
    rec["official_revision"] = (MANIFEST or {}).get("revision")
    rec["source"] = (MANIFEST or {}).get("source")
    rec["license"] = (MANIFEST or {}).get("license")
    rec["authenticity"] = {
        "weight_pinned": rec["weight_pinned_ok"],
        "full_manifest_pinned": rec["manifest_files_pinned"],
        "official_revision_pinned": rec["official_revision"] not in (None, "master"),
        "license_recorded": bool(rec.get("license_file")),
        "runtime_verified": False,
    }
    rec["runnable_offline"] = (
        rec["required_ok"] and rec["weight_pinned_ok"]
        and rec["config_json_ok"] and rec["tokenizer_files_ok"]
        and rec.get("config_load_ok") is True
        and rec.get("tokenizer_load_ok") is True
    )
    if rec["runnable_offline"]:
        rec["status"] = "runnable-offline"
    elif rec["required_ok"] and rec["weight_pinned_ok"]:
        rec["status"] = "files-complete-load-unproven"
    elif rec["weight_pinned_ok"]:
        rec["status"] = "weight-only"
    else:
        rec["status"] = "incomplete"
    return rec


def console(rec):
    print("\n" + "◆" * 72)
    print("ARTIFACT GATE — complete offline check")
    print("◆" * 72)
    print(f"  dir: {rec.get('model_dir')}")
    print(f"  status: {rec.get('status')}")
    print(f"  required_ok={rec.get('required_ok')}  pin={rec.get('weight_pinned_ok')}  "
          f"tok_files={rec.get('tokenizer_files_ok')}")
    print(f"  transformers={rec.get('transformers_available')}  "
          f"config_load={rec.get('config_load_ok')}  tok_load={rec.get('tokenizer_load_ok')}")
    print(f"  runnable_offline={rec.get('runnable_offline')}")
    for e in rec.get("errors") or []:
        print("  ERR", e)
    print("◆" * 72)


def find_complete_model_dir(root):
    """Exactly one directory containing required files, or raise."""
    need = {
        "model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json",
    }
    root = os.path.abspath(root)
    candidates = []
    if os.path.isdir(root) and all(os.path.isfile(os.path.join(root, n)) for n in need):
        candidates.append(root)
    if os.path.isdir(root):
        for dirpath, _dns, fns in os.walk(root):
            if all(n in fns for n in need) and dirpath not in candidates:
                candidates.append(dirpath)
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one complete model directory under {root}; found {candidates}")
    return candidates[0]


if __name__ == "__main__":
    import sys
    model_dir = sys.argv[1] if len(sys.argv) > 1 else None
    rec = verify_offline_artifact(model_dir)
    os.makedirs(os.path.join(BASE, "registry"), exist_ok=True)
    path = os.path.join(BASE, "registry", "artifact_gate.json")
    with open(path, "w") as f:
        json.dump(rec, f, indent=2)
    console(rec)
    print("wrote", path)
    if not rec.get("required_ok") or not rec.get("weight_pinned_ok"):
        raise SystemExit(1)
    if rec.get("tokenizer_offline_safe") is False:
        raise SystemExit(1)
