#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

MODE="${1:-simulation}"

if [[ "$MODE" == "simulation" ]]; then
  python -m src.lab --mode simulation --cycles "${CYCLES:-20}" --cadence "${CADENCE:-2.0}"
elif [[ "$MODE" == "server" ]]; then
  uvicorn src.server:app --host 0.0.0.0 --port "${PORT:-8000}"
elif [[ "$MODE" == "agent" ]]; then
  shift
  python -m src.micro_agent "$@"
else
  echo "Usage: ./run.sh [simulation|server|agent] ..."
  exit 1
fi
