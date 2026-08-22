import os
import sys
import json
import time
import shutil
import subprocess
import re
import datetime
import csv


class KaggleBridgeController:
    """
    Robust Kaggle bridge controller.

    Important behavior:
      - Generates a fresh unique kebab-case kernel ID.
      - Uses a title derived directly from the kernel slug.
      - Builds the complete Kaggle payload.
      - Detects quota exhaustion separately from genuine push failures.
      - Never polls unless a cloud execution has actually been confirmed.
      - Handles Kaggle CLI output appearing on stdout or stderr.
      - Does not confuse a rejected submission with a running kernel.
      - Extracts omega_ledger.csv only after confirmed completion.
    """

    def __init__(self):
        self.kaggle_username = "deemmany"

        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        slug_name = (
            f"omega-engine-dual-gpu-maximizer-{timestamp}"
        )

        self.slug = f"{self.kaggle_username}/{slug_name}"

        self.payload_dir = "kaggle_omega_payload"
        self.output_dir = "kaggle_extracted_ledgers"

        self.poll_interval = 15
        self.max_poll_seconds = 30 * 60

        self.run_confirmed = False
        self.kaggle_cli = None

    # ------------------------------------------------------------------
    # ENVIRONMENT
    # ------------------------------------------------------------------

    def verify_environment(self):
        print("=" * 80)
        print(
            "  INITIATING KAGGLE BRIDGE CONTROLLER "
            "(V15 - QUOTA-AWARE ROBUST CONTROLLER)"
        )
        print("=" * 80)

        token_path = os.path.expanduser(
            r"~/.kaggle/access_token"
        )

        if not os.path.exists(token_path):
            print()
            print(
                "[!] FATAL: Kaggle access token not found at:"
            )
            print(f"    {token_path}")
            return False

        print("[+] Kaggle access token found.")
        print(
            f"[+] Targeting Kaggle account: "
            f"{self.kaggle_username}"
        )
        print(f"[+] Kernel ID: {self.slug}")

        title = self.slug.split("/", 1)[1].replace("-", " ").title()

        print(f"[+] Kernel title: {title}")

        try:
            result = subprocess.run(
                ["kaggle", "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = (
                result.stdout.strip()
                or result.stderr.strip()
            )

            if result.returncode != 0:
                print("[!] Kaggle CLI was found but returned an error.")
                print(output)
                return False

            self.kaggle_cli = "kaggle"

            print(
                f"[+] Kaggle CLI detected: {output}"
            )

        except FileNotFoundError:
            print(
                "[!] FATAL: Kaggle CLI executable was not found."
            )
            return False

        except Exception as exc:
            print(
                f"[!] FATAL: Could not verify Kaggle CLI: {exc}"
            )
            return False

        return True

    # ------------------------------------------------------------------
    # PAYLOAD
    # ------------------------------------------------------------------

    def build_payload(self):
        print()
        print("[*] Phase 1: Building Cloud Payload...")

        if os.path.exists(self.payload_dir):
            shutil.rmtree(self.payload_dir)

        os.makedirs(self.payload_dir, exist_ok=True)

        title = (
            self.slug
            .split("/", 1)[1]
            .replace("-", " ")
            .title()
        )

        metadata = {
            "id": self.slug,
            "title": title,
            "code_file": "omega_dual_gpu.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": "false",
            "enable_gpu": "true",
            "enable_internet": "false",
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": [],
            "model_sources": []
        }

        metadata_path = os.path.join(
            self.payload_dir,
            "kernel-metadata.json"
        )

        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                metadata,
                f,
                indent=2
            )

        compute_script = r'''import csv
import gc
import threading
import time

import pandas as pd
import torch


class DualGPUHyperMaximizer:
    def __init__(self):
        self.num_gpus = torch.cuda.device_count()

        self.base_width = 10_000
        self.base_steps = 10_000

        self.max_iterations = 10

        self.ledger = []

    def stress_gpu(
        self,
        device_id,
        width,
        steps,
        results_dict
    ):
        try:
            torch.cuda.set_device(device_id)

            device = f"cuda:{device_id}"

            # Conservative allocation.
            # The original 80,000 x 100,000 int8 allocation
            # requires approximately 8 GB before overhead.
            #
            # Keep this configurable and avoid immediately
            # forcing an enormous allocation.
            dummy_hog = torch.empty(
                (8_000, 8_000),
                dtype=torch.int8,
                device=device
            )

            state = torch.zeros(
                (1, width),
                dtype=torch.int8,
                device=device
            )

            state[0, width // 2] = 1

            total_cells = width * steps

            start_time = time.perf_counter()

            for _ in range(steps):
                left = torch.roll(
                    state,
                    1,
                    dims=1
                )

                center = state

                right = torch.roll(
                    state,
                    -1,
                    dims=1
                )

                neighborhood = (
                    (left << 2)
                    | (center << 1)
                    | right
                )

                state = (
                    (30 >> neighborhood)
                    & 1
                )

            torch.cuda.synchronize(device)

            elapsed = (
                time.perf_counter()
                - start_time
            )

            sro = (
                total_cells / elapsed
                if elapsed > 0
                else 0
            )

            results_dict[device_id] = {
                "sro": sro,
                "elapsed": elapsed,
                "cells": total_cells,
                "target_met": elapsed <= 1.0,
                "error": ""
            }

            del dummy_hog
            del state

            torch.cuda.empty_cache()

        except Exception as exc:
            results_dict[device_id] = {
                "sro": 0,
                "elapsed": 0,
                "cells": 0,
                "target_met": False,
                "error": str(exc)
            }

    def run_exponential_loop(self):
        print(
            f"Detected GPUs: {self.num_gpus}"
        )

        if self.num_gpus <= 0:
            print(
                "ERROR: No CUDA GPUs detected."
            )
            return

        multiplier = 1

        for i in range(
            1,
            self.max_iterations + 1
        ):
            width = (
                self.base_width
                * multiplier
            )

            steps = (
                self.base_steps
                * multiplier
            )

            print(
                f"Iteration {i} "
                f"(Scale: {multiplier}x)"
            )

            results = {}

            threads = []

            for gpu_id in range(
                self.num_gpus
            ):
                thread = threading.Thread(
                    target=self.stress_gpu,
                    args=(
                        gpu_id,
                        width,
                        steps,
                        results
                    )
                )

                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            valid_results = [
                result
                for result in results.values()
                if result.get("error") == ""
            ]

            if not valid_results:
                print(
                    "  -> All GPU workers failed."
                )

                for gpu_id, result in results.items():
                    print(
                        f"     GPU {gpu_id}: "
                        f"{result.get('error', 'unknown error')}"
                    )

                break

            total_elapsed = max(
                result["elapsed"]
                for result in valid_results
            )

            total_cells = sum(
                result["cells"]
                for result in valid_results
            )

            total_sro = sum(
                result["sro"]
                for result in valid_results
            )

            self.ledger.append(
                {
                    "iteration": i,
                    "scale": multiplier,
                    "cells": total_cells,
                    "sro_per_sec": total_sro,
                    "time_sec": round(
                        total_elapsed,
                        4
                    ),
                    "target_met": (
                        total_elapsed <= 1.0
                    )
                }
            )

            print(
                f"  -> Time: "
                f"{total_elapsed:.4f}s "
                f"| SRO: "
                f"{total_sro:,.0f}/sec"
            )

            if total_elapsed > 5.0:
                print(
                    "HALTING BOUNDARY TRIGGERED."
                )
                break

            multiplier *= 2

            gc.collect()

            torch.cuda.empty_cache()


if __name__ == "__main__":
    engine = DualGPUHyperMaximizer()

    engine.run_exponential_loop()

    df = pd.DataFrame(
        engine.ledger
    )

    df.to_csv(
        "/kaggle/working/omega_ledger.csv",
        index=False
    )

    print(
        "LEDGER SAVED TO CLOUD."
    )
'''

        script_path = os.path.join(
            self.payload_dir,
            "omega_dual_gpu.py"
        )

        with open(
            script_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(compute_script)

        print("[+] Payload built successfully.")
        print(
            f"    Metadata: {metadata_path}"
        )
        print(
            f"    Script:   {script_path}"
        )

        return True

    # ------------------------------------------------------------------
    # OUTPUT NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def combined_process_output(result):
        stdout = result.stdout or ""
        stderr = result.stderr or ""

        return (
            f"{stdout}\n{stderr}"
        ).strip()

    # ------------------------------------------------------------------
    # QUOTA DETECTION
    # ------------------------------------------------------------------

    @staticmethod
    def is_gpu_quota_error(text):
        normalized = (
            text.lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        quota_markers = [
            "maximum weekly gpu quota",
            "weekly gpu quota",
            "gpu quota",
            "gpu quota exhausted",
            "maximum gpu quota",
            "quota of 30.00 hours",
            "quota exhausted"
        ]

        return any(
            marker in normalized
            for marker in quota_markers
        )

    # ------------------------------------------------------------------
    # KERNEL URL / SLUG EXTRACTION
    # ------------------------------------------------------------------

    @staticmethod
    def parse_kernel_slug(text):
        if not text:
            return None

        patterns = [
            r"kaggle\.com/code/([^/\s]+)/([^/\s?#]+)",
            r"https?://www\.kaggle\.com/code/([^/\s]+)/([^/\s?#]+)",
            r"https?://kaggle\.com/code/([^/\s]+)/([^/\s?#]+)"
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:
                owner = match.group(1)
                slug_name = match.group(2)

                return (
                    f"{owner}/{slug_name}"
                )

        return None

    # ------------------------------------------------------------------
    # PUSH
    # ------------------------------------------------------------------

    def push_and_poll(self):
        print()
        print("[*] Phase 2: Pushing to Kaggle via CLI...")

        try:
            result = subprocess.run(
                [
                    self.kaggle_cli,
                    "kernels",
                    "push",
                    "-p",
                    self.payload_dir
                ],
                capture_output=True,
                text=True
            )

        except FileNotFoundError:
            print(
                "[!] FATAL: Kaggle CLI executable "
                "could not be started."
            )

            self.run_confirmed = False
            return None

        except Exception as exc:
            print(
                f"[!] FATAL: Kaggle push process failed: "
                f"{exc}"
            )

            self.run_confirmed = False
            return None

        combined = self.combined_process_output(
            result
        )

        # --------------------------------------------------------------
        # QUOTA FAILURE
        # --------------------------------------------------------------

        if self.is_gpu_quota_error(
            combined
        ):
            print()
            print(
                "!" * 80
            )
            print(
                "  KAGGLE GPU QUOTA EXHAUSTED"
            )
            print(
                "!" * 80
            )
            print()
            print(
                "[!] Kaggle rejected the cloud run "
                "because the account's weekly GPU "
                "quota is exhausted."
            )
            print()
            print("    Detected:")
            print(
                "    maximum weekly gpu quota"
            )
            print()
            print(
                "    Full Kaggle response:"
            )
            print(combined)
            print()
            print(
                "[!] IMPORTANT:"
            )
            print(
                "    The kernel was NOT successfully launched."
            )
            print(
                "    No cloud execution was confirmed."
            )
            print(
                "    Controller will NOT poll."
            )

            self.run_confirmed = False

            return None

        # --------------------------------------------------------------
        # OTHER PUSH FAILURE
        # --------------------------------------------------------------

        if result.returncode != 0:
            print()
            print(
                "[!] FATAL: Kaggle rejected the kernel push."
            )
            print()
            print(
                "    Return code:"
            )
            print(
                f"    {result.returncode}"
            )
            print()
            print(
                "    Kaggle response:"
            )
            print(combined)

            self.run_confirmed = False

            return None

        # --------------------------------------------------------------
        # SUCCESS
        # --------------------------------------------------------------

        print(
            "[+] Kaggle push command completed successfully."
        )

        actual_slug = (
            self.parse_kernel_slug(
                combined
            )
        )

        if actual_slug:
            self.slug = actual_slug

            print(
                f"[+] Resolved actual kernel slug: "
                f"{self.slug}"
            )
        else:
            print(
                "[!] Kaggle did not return a "
                "parseable kernel URL."
            )

            print(
                "[*] Continuing with submitted kernel ID:"
            )

            print(
                f"    {self.slug}"
            )

        # A successful CLI return code is our submission
        # confirmation. We only proceed to polling after this.
        self.run_confirmed = True

        print()
        print(
            "[+] Cloud execution submission confirmed."
        )

        # --------------------------------------------------------------
        # POLLING
        # --------------------------------------------------------------

        print()
        print(
            "[*] Phase 3: Polling for cloud completion..."
        )
        print(
            "    This may take several minutes."
        )

        start_time = time.time()

        final_status = "unknown"

        while True:
            elapsed = (
                time.time()
                - start_time
            )

            if elapsed >= self.max_poll_seconds:
                print()
                print(
                    "[!] Polling timeout reached."
                )

                print(
                    f"    Maximum wait: "
                    f"{self.max_poll_seconds}s"
                )

                final_status = "timeout"

                break

            try:
                status_result = subprocess.run(
                    [
                        self.kaggle_cli,
                        "kernels",
                        "status",
                        "-k",
                        self.slug
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                status_output = (
                    status_result.stdout
                    or status_result.stderr
                    or ""
                ).strip()

                normalized = (
                    status_output.lower()
                )

                print(
                    f"    -> Cloud Status: "
                    f"{status_output}"
                )

                if (
                    "complete"
                    in normalized
                ):
                    final_status = "complete"
                    break

                if (
                    "error"
                    in normalized
                ):
                    final_status = "error"
                    break

                if (
                    "cancel"
                    in normalized
                ):
                    final_status = "cancelled"
                    break

                if self.is_gpu_quota_error(
                    status_output
                ):
                    print(
                        "[!] Cloud status reports "
                        "GPU quota exhaustion."
                    )

                    final_status = "quota_exhausted"
                    break

                time.sleep(
                    self.poll_interval
                )

            except subprocess.TimeoutExpired:
                print(
                    "    -> Status command timed out. "
                    "Retrying..."
                )

                time.sleep(
                    self.poll_interval
                )

            except Exception as exc:
                print(
                    f"    -> Polling error: "
                    f"{exc}"
                )

                time.sleep(
                    self.poll_interval
                )

        return final_status

    # ------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------

    def extract_results(
        self,
        final_status
    ):
        if not self.run_confirmed:
            print()
            print(
                "[!] Output extraction skipped."
            )
            print(
                "    No confirmed cloud execution."
            )
            return

        if final_status != "complete":
            print()
            print(
                "[!] Output extraction skipped."
            )
            print(
                f"    Final status: "
                f"{final_status}"
            )
            return

        print()
        print(
            "[*] Phase 4: Extracting results..."
        )

        if os.path.exists(
            self.output_dir
        ):
            shutil.rmtree(
                self.output_dir
            )

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        try:
            result = subprocess.run(
                [
                    self.kaggle_cli,
                    "kernels",
                    "output",
                    "-k",
                    self.slug,
                    "-p",
                    self.output_dir
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(
                    "[!] Error extracting output."
                )

                print(
                    result.stderr
                    or result.stdout
                )

                return

            csv_path = os.path.join(
                self.output_dir,
                "omega_ledger.csv"
            )

            if not os.path.exists(
                csv_path
            ):
                print(
                    "[!] WARNING: Run completed, "
                    "but omega_ledger.csv was not found."
                )

                return

            print(
                f"[+] SUCCESS: Ledger extracted to "
                f"{csv_path}"
            )

            print()
            print(
                "=" * 80
            )

            print(
                "  CLOUD LEDGER RETRIEVED"
            )

            print(
                "=" * 80
            )

            with open(
                csv_path,
                "r",
                encoding="utf-8",
                newline=""
            ) as f:
                reader = csv.reader(f)

                for row in reader:
                    print(
                        "  | ".join(row)
                    )

        except Exception as exc:
            print(
                f"[!] Error extracting output: "
                f"{exc}"
            )

    # ------------------------------------------------------------------
    # MAIN CONTROLLER
    # ------------------------------------------------------------------

    def run(self):
        if not self.verify_environment():
            return

        if not self.build_payload():
            return

        final_status = (
            self.push_and_poll()
        )

        if final_status is None:
            print()
            print(
                "[!] Controller stopped before polling."
            )
            print(
                "[!] No cloud execution was confirmed."
            )
            return

        self.extract_results(
            final_status
        )


def main():
    controller = (
        KaggleBridgeController()
    )

    controller.run()


if __name__ == "__main__":
    main()
