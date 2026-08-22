#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "=== VERIFY ALL ==="
python -m tests.test_accuracy
python -m tests.test_karpathy_loop
python -m src.lab --mode simulation --cycles 5 --cadence 0
python -m src.growing_assistant learn
echo "=== ALL GREEN ==="
