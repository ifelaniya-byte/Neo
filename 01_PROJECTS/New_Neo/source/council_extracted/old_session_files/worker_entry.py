#!/usr/bin/env python3
"""
Isolated GPU worker. External .py via Popen. Exit 0 only on success.

Default: FP16, no device_map, local_files_only=True, trust_remote_code=False.
Benchmark mode REQUIRES smoke_scorer. Persist model at /kaggle/input/...
"""

import json
import os
import sys
import time
import traceback
from pathlib import Path

try:
    import smoke_scorer
    SCORER_IMPORT_ERROR = None
except Exception as exc:
    smoke_scorer = None
    SCORER_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"


def atomic_json(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2), encoding="utf-8")
    os.replace(temp, path)


def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _pad_id(tokenizer):
    pad = tokenizer.pad_token_id
    if pad is None:
        pad = tokenizer.eos_token_id
    if pad is None:
        raise RuntimeError("tokenizer has neither pad_token_id nor eos_token_id")
    return pad


def _render(tokenizer, prompt):
    messages = [{"role": "user", "content": prompt}]
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
    return prompt


def _generate(model, tokenizer, prompt, request):
    import torch
    rendered = _render(tokenizer, prompt)
    inputs = tokenizer(
        rendered, return_tensors="pt", truncation=True,
        max_length=request.get("max_input_tokens", 1024),
    )
    inputs = {k: v.to("cuda:0") for k, v in inputs.items()}
    input_tokens = int(inputs["input_ids"].shape[-1])
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            max_new_tokens=request.get("max_new_tokens", 64),
            do_sample=False,
            pad_token_id=_pad_id(tokenizer),
            eos_token_id=tokenizer.eos_token_id,
        )
    torch.cuda.synchronize()
    infer_s = time.perf_counter() - t0
    completion_ids = generated[0, input_tokens:]
    completion = tokenizer.decode(completion_ids, skip_special_tokens=True).strip()
    return {
        "completion": completion,
        "input_tokens": input_tokens,
        "output_tokens": int(completion_ids.shape[-1]),
        "inference_seconds": round(infer_s, 4),
    }


def main():
    request_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    request = json.loads(request_path.read_text(encoding="utf-8"))
    result = {
        "schema_version": 3,
        "ok": False,
        "model": request.get("model"),
        "dtype": request.get("dtype", "float16"),
        "quantization": request.get("quantization", "none"),
        "started_at": time.time(),
        "local_files_only": bool(request.get("local_files_only", True)),
        "scorer_import_error": SCORER_IMPORT_ERROR,
        "persist_note": "Prefer /kaggle/input/... ; /tmp is same-session only.",
    }
    succeeded = False
    try:
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable — this worker is for a T4 session")

        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        result["versions"] = {
            "python": sys.version.split()[0],
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        }
        try:
            import accelerate
            result["versions"]["accelerate"] = accelerate.__version__
        except Exception:
            result["versions"]["accelerate"] = None
        result["gpu"] = {
            "name": torch.cuda.get_device_name(0),
            "n": torch.cuda.device_count(),
            "total_bytes": torch.cuda.get_device_properties(0).total_memory,
        }

        load_start = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(
            request["model"],
            local_files_only=request.get("local_files_only", True),
            trust_remote_code=False,
        )
        # First proof: FP16 without device_map / Accelerate.
        model = AutoModelForCausalLM.from_pretrained(
            request["model"],
            local_files_only=request.get("local_files_only", True),
            trust_remote_code=False,
            use_safetensors=True,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        )
        if request.get("quantization") == "nf4":
            raise RuntimeError("NF4 is a later experiment; first proof must be FP16")
        model.to("cuda:0")
        model.eval()
        result["load_seconds"] = round(time.perf_counter() - load_start, 3)
        result["load_path"] = "fp16-no-device-map"

        bench = request.get("benchmark_path")
        if bench:
            if smoke_scorer is None:
                raise RuntimeError(
                    "benchmark requested but smoke_scorer could not be imported: "
                    + str(SCORER_IMPORT_ERROR))
            items = []
            with open(bench, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line))
            smoke_scorer.validate_benchmark(items)
            pred_path = Path(request.get(
                "output_predictions_path",
                str(output_path).replace(".json", "_predictions.jsonl")))
            if pred_path.exists():
                pred_path.unlink()
            predictions = {}
            infer_total = 0.0
            completed = 0
            failed = 0
            for it in items:
                try:
                    one = _generate(model, tokenizer, it["prompt"], request)
                    infer_total += one["inference_seconds"]
                    rec = {
                        "id": it["id"],
                        "ok": True,
                        "domain": it.get("domain"),
                        "completion": one["completion"],
                        "input_tokens": one["input_tokens"],
                        "output_tokens": one["output_tokens"],
                        "inference_seconds": one["inference_seconds"],
                    }
                    predictions[it["id"]] = one["completion"]
                    completed += 1
                except torch.cuda.OutOfMemoryError:
                    raise
                except Exception as exc:
                    rec = {
                        "id": it["id"],
                        "ok": False,
                        "domain": it.get("domain"),
                        "completion": "",
                        "error": {"type": type(exc).__name__, "message": str(exc)[:500]},
                    }
                    predictions[it["id"]] = ""
                    failed += 1
                append_jsonl(pred_path, rec)
            ev = smoke_scorer.score_run(predictions, items)
            if ev is None:
                raise RuntimeError("evaluation missing after benchmark")
            result.update({
                "ok": True,
                "mode": "benchmark",
                "benchmark_items_attempted": len(items),
                "predictions_written": len(predictions),
                "prediction_failures": failed,
                "prediction_ok": completed,
                "predictions_path": pred_path.name,
                "inference_seconds": round(infer_total, 4),
                "evaluation": ev,
                "peak_allocated_bytes": int(torch.cuda.max_memory_allocated(0)),
                "peak_reserved_bytes": int(torch.cuda.max_memory_reserved(0)),
            })
            succeeded = True
        else:
            one = _generate(model, tokenizer, request["prompt"], request)
            result.update({
                "ok": True,
                "mode": "single",
                **one,
                "tokens_per_second": (
                    round(one["output_tokens"] / one["inference_seconds"], 3)
                    if one["inference_seconds"] else None),
                "peak_allocated_bytes": int(torch.cuda.max_memory_allocated(0)),
                "peak_reserved_bytes": int(torch.cuda.max_memory_reserved(0)),
            })
            succeeded = True
    except Exception as exc:
        result["ok"] = False
        result["error"] = {
            "type": type(exc).__name__,
            "message": str(exc)[:1000],
            "trace_tail": traceback.format_exc()[-2000:],
        }
        succeeded = False
    finally:
        result["finished_at"] = time.time()
        result["wall_seconds"] = round(result["finished_at"] - result["started_at"], 3)
        atomic_json(output_path, result)
    return succeeded


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("usage: worker_entry.py REQUEST.json RESULT.json\n")
        raise SystemExit(2)
    raise SystemExit(0 if main() else 1)
