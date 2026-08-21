import os
import sys
import json
import time
import shutil
import subprocess
import re
import datetime


class KaggleBridgeController:
    def __init__(self):
        self.kaggle_username = "deemmany"
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.slug_name = f"omega-engine-unlimited-{timestamp}"
        self.slug = f"{self.kaggle_username}/{self.slug_name}"
        self.payload_dir = "kaggle_omega_payload"
        self.output_dir = "kaggle_extracted_ledgers"

    def verify_environment(self):
        print("=" * 80)
        print("  INITIATING KAGGLE BRIDGE CONTROLLER (V18 - SCHEMA-FIXED)")
        print("=" * 80)

        token_path = os.path.expanduser(r"~\.kaggle\access_token")
        if not os.path.exists(token_path):
            token_path = os.path.expanduser(r"~\.kaggle\kaggle.json")
            if not os.path.exists(token_path):
                print("\n[!] FATAL: Kaggle credentials not found")
                sys.exit(1)

        print("[+] Kaggle CLI token verified.")
        print(f"[+] Targeting Kaggle account: {self.kaggle_username}")
        print(f"[+] Unlimited slug: {self.slug}")

    def build_payload(self):
        print("\n[*] Phase 1: Building Cloud Payload...")

        if os.path.exists(self.payload_dir):
            shutil.rmtree(self.payload_dir)
        os.makedirs(self.payload_dir)

        title = self.slug_name.replace("-", " ").title()

        # FIX: removed "machine_shape" — not a documented kernel-metadata.json field.
        # Kaggle's schema validator on SaveKernel rejects unknown keys, which is the
        # most likely cause of the original 400 Bad Request. Accelerator selection
        # is handled separately via the --accelerator CLI flag in push_and_poll().
        metadata = {
            "id": self.slug,
            "title": title,
            "code_file": "omega_dual_gpu.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": False,
            "enable_gpu": True,
            "enable_internet": False,
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": [],
            "model_sources": []
        }

        with open(os.path.join(self.payload_dir, "kernel-metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        compute_script = r'''
import torch
import time
import pandas as pd
import threading
import gc
import os

class DualGPUHyperMaximizer:
    def __init__(self):
        self.num_gpus = torch.cuda.device_count()
        self.base_width = 10_000
        self.base_steps = 10_000
        self.max_iterations = 30
        self.ledger = []
        self.csv_path = "/kaggle/working/omega_ledger.csv"

    def stress_gpu(self, device_id, width, steps, results_dict):
        torch.cuda.set_device(device_id)
        device = f"cuda:{device_id}"
        dummy_hog = None
        state = None
        try:
            # Fixed-size memory pressure tensor (~2.8GB on int8). Does not scale
            # with width/steps — it is a constant background load, not part of
            # the iteration's own memory growth curve.
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
                "status": "ok",
                "sro": sro,
                "elapsed": elapsed,
                "cells": total_cells,
                "target_met": elapsed <= 1.0
            }
        except torch.cuda.OutOfMemoryError as e:
            # FIX: OOM in a worker thread previously died silently — the main
            # thread only checked "if not results" (zero results), so a partial
            # failure (1-of-2 GPUs) would continue and produce a misleading
            # ledger row. Now every OOM is recorded explicitly.
            results_dict[device_id] = {
                "status": "oom",
                "error": str(e),
                "sro": 0,
                "elapsed": 0,
                "cells": 0,
                "target_met": False
            }
        finally:
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
            # FIX: original scaled BOTH width and steps by multiplier, so total
            # work (width * steps) grew as multiplier^2 -- effectively 4x per
            # iteration despite "multiplier *= 2". That made iteration ~11
            # already represent ~10^14 cell updates, far beyond any realistic
            # runtime or Kaggle session limit. Now only width scales; steps
            # stays fixed, so total work grows linearly with multiplier (true
            # 2x per iteration, matching the "exponential loop" naming).
            width = self.base_width * multiplier
            steps = self.base_steps
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

            oom_gpus = [gid for gid, r in results.items() if r.get("status") == "oom"]
            ok_results = [r for r in results.values() if r.get("status") == "ok"]

            if oom_gpus:
                print(f"  -> OOM on GPU(s): {oom_gpus}. Stopping further scaling.")
                self.ledger.append({
                    "iteration": i,
                    "scale": multiplier,
                    "cells": 0,
                    "sro_per_sec": 0,
                    "time_sec": 0,
                    "target_met": False,
                    "status": "oom"
                })
                self._checkpoint()
                break

            total_elapsed = max(r["elapsed"] for r in ok_results)
            total_cells = sum(r["cells"] for r in ok_results)
            total_sro = sum(r["sro"] for r in ok_results)

            self.ledger.append({
                "iteration": i,
                "scale": multiplier,
                "cells": total_cells,
                "sro_per_sec": total_sro,
                "time_sec": round(total_elapsed, 4),
                "target_met": total_elapsed <= 1.0,
                "status": "ok"
            })
            print(f"  -> Time: {total_elapsed:.4f}s | SRO: {total_sro:,.0f}/sec")

            # FIX: checkpoint after every iteration so a killed/timed-out kernel
            # still leaves partial results on disk instead of losing everything
            # (the original only wrote the CSV after the full loop returned).
            self._checkpoint()

            multiplier *= 2
            gc.collect()
            torch.cuda.empty_cache()

    def _checkpoint(self):
        pd.DataFrame(self.ledger).to_csv(self.csv_path, index=False)

if __name__ == "__main__":
    engine = DualGPUHyperMaximizer()
    engine.run_exponential_loop()
    df = pd.DataFrame(engine.ledger)
    df.to_csv(engine.csv_path, index=False)
    print("\nLEDGER SAVED TO CLOUD.")
    print(df.to_string(index=False))
'''
        with open(os.path.join(self.payload_dir, "omega_dual_gpu.py"), "w", encoding="utf-8") as f:
            f.write(compute_script)

        print("[+] Payload built successfully.")
        print(f"    id            : {self.slug}")
        print(f"    title         : {title}")
        print(f"    accelerator   : NvidiaTeslaT4 (set via CLI flag, not metadata)")
        print(f"    max_iterations: 30 (checkpointed every iteration)")

    def push_and_poll(self):
        print("\n[*] Phase 2: Pushing to Kaggle via CLI...")
        try:
            result = subprocess.run(
                ["kaggle", "kernels", "push", "-p", self.payload_dir, "--accelerator", "NvidiaTeslaT4"],
                capture_output=True,
                text=True,
                check=True
            )
            print("[+] Push successful. Run initiated in the cloud.")
            print(result.stdout)

            match = re.search(r"kaggle\.com/code/([^/\s]+)/([^/\s]+)", result.stdout)
            if match:
                owner, slug_name = match.group(1), match.group(2)
                self.slug = f"{owner}/{slug_name}"
                print(f"[*] Resolved actual kernel slug: {self.slug}")
            else:
                print("[!] Could not parse kernel URL - using constructed slug")
                print("    Raw output:", result.stdout)

        except subprocess.CalledProcessError as e:
            print("\n[!] FATAL ERROR during push:")
            print("    STDOUT:", e.stdout)
            print("    STDERR:", e.stderr)
            sys.exit(1)

        print("\n[*] Phase 3: Polling for completion (this may take longer)...")
        final_status = "running"
        while True:
            try:
                status_result = subprocess.run(
                    ["kaggle", "kernels", "status", self.slug],
                    capture_output=True,
                    text=True,
                    check=True
                )
                status_line = status_result.stdout.strip().lower()
                print(f"    -> Cloud Status: {status_line}")

                if any(x in status_line for x in ("complete", "error", "cancel", "failed")):
                    final_status = status_line
                    break
                time.sleep(20)
            except subprocess.CalledProcessError as e:
                print(f"    -> Polling error: {e.stderr.strip()[:200]}. Retrying...")
                time.sleep(20)
            except Exception as e:
                print(f"    -> Polling error: {e}. Retrying...")
                time.sleep(20)

        return final_status

    def extract_results(self, final_status):
        print(f"\n[*] Phase 4: Extracting results (Final Status: {final_status})...")
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

        try:
            subprocess.run(
                ["kaggle", "kernels", "output", self.slug, "-p", self.output_dir],
                capture_output=True,
                text=True,
                check=True
            )
            csv_path = os.path.join(self.output_dir, "omega_ledger.csv")

            if os.path.exists(csv_path):
                print(f"[+] SUCCESS: Ledger extracted to {csv_path}")
                print("\n" + "=" * 80)
                print("  RUN COMPLETE - CLOUD LEDGER RETRIEVED")
                print("=" * 80)
                import csv
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        print(" | ".join(row))
            else:
                print("[!] Run finished but omega_ledger.csv was not found.")
                print("    Files present:", os.listdir(self.output_dir))
        except subprocess.CalledProcessError as e:
            print(f"[!] Error extracting output: {e.stderr}")
        except Exception as e:
            print(f"[!] Error extracting output: {e}")


def main():
    controller = KaggleBridgeController()
    controller.verify_environment()
    controller.build_payload()
    final_status = controller.push_and_poll()
    controller.extract_results(final_status)


if __name__ == "__main__":
    main()
