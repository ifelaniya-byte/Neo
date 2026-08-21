"""
PROJECT APEX: TRAJECTORY EXTRACTOR & DISTILLATION DATASET BUILDER
Converts verified winning worker_core edits into structured JSONL trajectories for QLoRA fine-tuning.
"""

import json
import os

LOG_FILE = "experiment_log.tsv"
OUTPUT_DATASET = "verified_trajectories.jsonl"
WORKER_FILE = "worker_core.py"

def export_trajectory():
    """Exports winning trajectories to JSONL format for micro-LLM training."""
    if not os.path.exists(LOG_FILE):
        return
        
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            return
        last_line = lines[-1].strip().split("\t")
        
    run_id, timestamp, hypothesis, score, result, commit_hash = last_line
    
    if result != "KEEP":
        print("[DATASET BUILDER] Skipping non-winning trajectory.")
        return
        
    with open(WORKER_FILE, "r") as f:
        worker_code = f.read()
        
    trajectory_entry = {
        "trajectory_id": f"apex_traj_{run_id}",
        "timestamp": timestamp,
        "instruction": "Optimize worker_core.py execution speed and loss metrics while maintaining thread safety.",
        "hypothesis": hypothesis,
        "verification_score": float(score),
        "verified_code_patch": worker_code,
        "commit_hash": commit_hash
    }
    
    with open(OUTPUT_DATASET, "a", encoding="utf-8") as f:
        f.write(json.dumps(trajectory_entry) + "\n")
        
    print(f"[DATASET BUILDER] Successfully exported winning trajectory {run_id} to {OUTPUT_DATASET}")

if __name__ == "__main__":
    export_trajectory()