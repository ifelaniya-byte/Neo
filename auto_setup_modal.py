# auto_setup_modal.py
import os

script_content = '''import modal
import json
import os
import subprocess
import time
from datetime import datetime, timezone

# 1. Define the Modal App and Image
app = modal.App("omega-modal-bridge")

# FIX: Added "numpy" alongside "torch" to prevent the initialization warning
image = modal.Image.debian_slim().pip_install("torch", "numpy")

# 2. Define the remote GPU function
@app.function(gpu="T4", image=image, timeout=3600)
def run_remote_workload(mode: str, matrix_size: int = 2048, iterations: int = 3):
    import torch
    import numpy as np  # Now safely imported
    
    result = {
        "status": "unknown",
        "mode": mode,
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count(),
        "devices": [],
        "elapsed_seconds": 0,
        "omega_output": None
    }

    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            result["devices"].append({
                "index": i,
                "name": props.name,
                "total_vram_mib": props.total_memory // (1024 * 1024),
                "multiprocessor_count": props.multi_processor_count,
                "compute_capability": f"{props.major}.{props.minor}"
            })

    if mode == "smoke":
        # Synthetic smoke test (proven to work)
        try:
            start = time.time()
            a = torch.randn(matrix_size, matrix_size, device="cuda")
            b = torch.randn(matrix_size, matrix_size, device="cuda")
            for _ in range(iterations):
                c = torch.matmul(a, b)
            result["result_shape"] = list(c.shape)
            result["elapsed_seconds"] = time.time() - start
            result["status"] = "passed"
            result["pytorch_version"] = torch.__version__
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

    elif mode == "omega":
        # REAL OMEGA BENCHMARK EXECUTION
        try:
            start = time.time()
            
            # Execute the actual Omega/Kaggle bridge script inside the Modal container
            # NOTE: Modal mounts your local directory to /root by default.
            # <-- UPDATE THIS LINE if your actual Omega entrypoint has a different name or needs args
            command = ["python", "run_kaggle_bridge.py"] 
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd="/root", 
                timeout=3000 # 50 minutes timeout for heavy Omega workloads
            )
            
            result["elapsed_seconds"] = time.time() - start
            result["omega_stdout_tail"] = process.stdout[-2000:] # Last 2000 chars to avoid huge payloads
            result["omega_stderr"] = process.stderr
            
            if process.returncode == 0:
                result["status"] = "passed"
            else:
                result["status"] = "failed"
                result["return_code"] = process.returncode
                
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "Omega workload exceeded timeout limit."
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

    return result

# 3. Local Entrypoint
@app.local_entrypoint()
def main(mode: str = "smoke", matrix_size: int = 2048, iterations: int = 3):
    print("=" * 80)
    print("OMEGA MODAL GPU BRIDGE")
    print("=" * 80)
    print(f"Mode:         {mode}")
    print(f"GPU request:  T4")
    print("=" * 80)

    start_time = time.time()
    
    # Call the remote function
    remote_result = run_remote_workload.remote(mode=mode, matrix_size=matrix_size, iterations=iterations)
    
    elapsed = time.time() - start_time
    remote_result["total_elapsed_seconds"] = elapsed

    # Save ledger locally
    os.makedirs("omega_modal_results", exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    json_path = f"omega_modal_results/omega_modal_{mode}_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(remote_result, f, indent=2)
        
    print("\\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    print(json.dumps(remote_result, indent=2))
    print(f"\\nJSON ledger saved to: {os.path.abspath(json_path)}")
    print("OMEGA MODAL BRIDGE COMPLETE.")
'''

# Write the file
with open("run_modal_bridge.py", "w", encoding="utf-8") as f:
    f.write(script_content)

print("✅ SUCCESS: 'run_modal_bridge.py' has been auto-created/overwritten.")
print("✅ FIX APPLIED: 'numpy' is now installed in the Modal image.")
print("✅ NEW FEATURE: '--mode omega' is now available.")
print("\\nNext step: Run the Omega test with:")
print("python -m modal run .\\run_modal_bridge.py --mode omega")