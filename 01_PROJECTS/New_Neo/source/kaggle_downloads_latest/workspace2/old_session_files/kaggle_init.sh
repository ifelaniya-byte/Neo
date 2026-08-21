#!/bin/bash
# KP-16/17 — same-session layout. /tmp DOES NOT persist across Kaggle sessions.
set -euo pipefail
echo "Initializing control-plane layout (no secrets)."
mkdir -p /kaggle/working/registry /kaggle/working/datasets /kaggle/working/runs
for f in mapping.json worker_entry.py smoke_scorer.py artifact_gate.py evaluate_and_promote.py; do
  if [ -f "$f" ]; then
    cp -f "$f" /kaggle/working/
  fi
done
if [ -d registry ]; then cp -r registry/. /kaggle/working/registry/; fi
if [ -d datasets ]; then cp -r datasets/. /kaggle/working/datasets/; fi

echo "Persistent model path (attach a Dataset if license allows):"
echo "  /kaggle/input/council-qwen05/Qwen__Qwen2.5-0.5B-Instruct"
echo "Same-session scratch only:"
echo "  /tmp/modelscope_cache   (dies when the session dies)"
echo "GPU request.model must point at /kaggle/input/... or a path filled in THIS session."
echo "done"
