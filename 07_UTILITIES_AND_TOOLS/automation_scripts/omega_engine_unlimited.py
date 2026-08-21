
import torch
import time
import pandas as pd
import threading
import gc

class DualGPUHyperMaximizer:
    def __init__(self):
        self.num_gpus = torch.cuda.device_count()
        self.base_width = 10_000
        self.base_steps = 10_000
        self.max_iterations = 30          # much higher
        self.ledger = []

    def stress_gpu(self, device_id, width, steps, results_dict):
        torch.cuda.set_device(device_id)
        device = f"cuda:{device_id}"
        # Memory hog – large but still safe for T4
        dummy_hog = torch.empty((50_000, 60_000), dtype=torch.int8, device=device)
        state = torch.zeros((1, width), dtype=torch.int8, device=device)
        state[0, width // 2] = 1
        total_cells = width * steps
        start_time = time.perf_counter()
        for _ in range(steps):
            left = torch.roll(state, 1, dims=1)
            center = state
            right = torch.roll(state, -1, dims=1)
            neighborhood = (left << 2) | (center << 1) | right
            state = (30 >> neighborhood) & 1
        torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - start_time
        sro = total_cells / elapsed if elapsed > 0 else 0
        results_dict[device_id] = {
            "sro": sro,
            "elapsed": elapsed,
            "cells": total_cells,
            "target_met": elapsed <= 1.0
        }
        del dummy_hog, state
        torch.cuda.empty_cache()

    def run_exponential_loop(self):
        print(f"Detected GPUs: {self.num_gpus}")
        if self.num_gpus > 0:
            print(f"GPU name: {torch.cuda.get_device_name(0)}")
        else:
            print("WARNING: No CUDA devices found. Exiting.")
            return

        multiplier = 1
        for i in range(1, self.max_iterations + 1):
            width = self.base_width * multiplier
            steps = self.base_steps * multiplier
            print(f"\n=== Iteration {i} | Scale {multiplier}x | width={width} steps={steps} ===")
            results = {}
            threads = []
            for gpu_id in range(self.num_gpus):
                t = threading.Thread(
                    target=self.stress_gpu,
                    args=(gpu_id, width, steps, results)
                )
                threads.append(t)
                t.start()
            for t in threads:
                t.join()

            if not results:
                print("ERROR: No results collected. Stopping.")
                break

            total_elapsed = max(r["elapsed"] for r in results.values())
            total_cells = sum(r["cells"] for r in results.values())
            total_sro = sum(r["sro"] for r in results.values())

            self.ledger.append({
                "iteration": i,
                "scale": multiplier,
                "cells": total_cells,
                "sro_per_sec": total_sro,
                "time_sec": round(total_elapsed, 4),
                "target_met": total_elapsed <= 1.0
            })
            print(f"  -> Time: {total_elapsed:.4f}s | SRO: {total_sro:,.0f}/sec")

            # NO HALT BOUNDARY – keep going until OOM or max_iterations
            multiplier *= 2
            gc.collect()
            torch.cuda.empty_cache()

if __name__ == "__main__":
    engine = DualGPUHyperMaximizer()
    engine.run_exponential_loop()
    df = pd.DataFrame(engine.ledger)
    df.to_csv("/kaggle/working/omega_ledger.csv", index=False)
    print("\nLEDGER SAVED TO CLOUD.")
    print(df.to_string(index=False))
