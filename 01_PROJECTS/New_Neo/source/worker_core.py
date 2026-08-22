"""
PROJECT APEX: WORKER CORE ENGINE (TARGET FILE FOR AI EVOLUTION)
This is the single file the AI agent modifies during the autonomous evolutionary loop.
"""

import time
import math

def run_unit_tests():
    """Validates math correctness and non-NaN numerical outputs."""
    res = execute_benchmark_batch()
    return res >= 0.0 and not math.isnan(res)

def execute_benchmark_batch():
    """
    Core workload function to be optimized by the AI agent.
    Baseline implementation uses unoptimized floating-point loops.
    """
    total_loss = 0.0
    iterations = 100000
    
    # Computational workload baseline
    for i in range(1, iterations + 1):
        val = math.sin(i) * math.cos(i)
        total_loss += abs(val)
        
    normalized_loss = (total_loss / iterations) * 0.5
    return normalized_loss

if __name__ == "__main__":
    print(f"Baseline Loss: {execute_benchmark_batch()}")