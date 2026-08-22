"""
PROJECT APEX: EVALUATION HARNESS & SERE-X SANDBOX GATE
Runs candidate worker_core.py code, tracks resource usage, calculates S_eval,
and outputs deterministic evaluation metrics.
"""

import sys
import time
import os
import psutil

# Enforce thread safety & process locks
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

W_LOSS = 0.4
W_SPEED = 0.3
W_RAM = 0.2
W_TESTS = 0.1

BASELINE_TIME = 10.0
BASELINE_LOSS = 1.0

def run_sere_x_benchmark():
    """Executes benchmark evaluation with resource tracking."""
    print("[SERE-X GATE] Executing benchmark evaluation...")
    start_mem = psutil.virtual_memory().used
    
    start_time = time.time()
    try:
        import worker_core
        import importlib
        importlib.reload(worker_core)
        
        test_passed = worker_core.run_unit_tests()
        loss = worker_core.execute_benchmark_batch()
        
    except Exception as e:
        print(f"[SERE-X GATE] EXECUTION ERROR: {e}")
        return 0.0, 1.0, 999.0, False
        
    exec_time = time.time() - start_time
    peak_mem = psutil.virtual_memory().used - start_mem
    mem_headroom = max(0.0, 1.0 - (peak_mem / (8 * 1024 * 1024 * 1024)))
    
    loss_score = max(0.0, 1.0 - loss)
    speed_score = BASELINE_TIME / max(0.001, exec_time)
    test_score = 1.0 if test_passed else 0.0
    
    s_eval = (W_LOSS * loss_score) + (W_SPEED * speed_score) + (W_RAM * mem_headroom) + (W_TESTS * test_score)
    
    print(f"--- BENCHMARK METRICS ---")
    print(f"Exec Time : {exec_time:.6f}s")
    print(f"Final Loss: {loss:.6f}")
    print(f"Unit Tests: {'PASSED' if test_passed else 'FAILED'}")
    print(f"S_EVAL    : {s_eval:.6f}")
    
    return s_eval, loss, exec_time, test_passed

if __name__ == "__main__":
    score, loss, duration, passed = run_sere_x_benchmark()
    with open(".latest_score", "w") as f:
        f.write(f"{score:.6f}")