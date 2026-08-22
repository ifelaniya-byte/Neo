# run_moa_cpu_eval.py
import os
import time
import json
from typing import Dict, Any, List

# 1. IMPORT YOUR ACTUAL GRADER
import sys
sys.path.append("C:\\Users\\AIAli\\OneDrive\\Desktop\\NEO")
try:
    from smoke_scorer import score_one
except ImportError:
    print("Critical Error: Could not import 'score_one' from smoke_scorer.py.")
    print("Please run this script from the directory containing smoke_scorer.py.")
    exit(1)

# 2. LOCAL MODEL PATHS
QWEN_MODEL_PATH = "C:\\Users\\AIAli\\OneDrive\\Desktop\\NEO\\qwen2.5-1.5b-instruct-Q4_K_M.gguf"
SMOL_MODEL_PATH = "C:\\Users\\AIAli\\OneDrive\\Desktop\\NEO\\models\\smollm2-1.7b-instruct-q4_k_m.gguf"

# Verify models exist before loading
for path in [QWEN_MODEL_PATH, SMOL_MODEL_PATH]:
    if not os.path.exists(path):
        print(f"Missing model file: {path}")
        print("Please ensure both models are downloaded and placed in the correct directory.")
        exit(1)

# 3. INITIALIZE MODELS (Strictly CPU-only, bounded context windows)
print("Loading models into System RAM (CPU-only execution)...")

from llama_cpp import Llama

# Keep n_ctx conservative (1024 or 2048) to comfortably fit both in 8GB System RAM
qwen_model = Llama(
    model_path=QWEN_MODEL_PATH,
    n_gpu_layers=0,  # Explicitly CPU-only
    n_ctx=1024,
    verbose=False
)
print("Loaded Qwen2.5-1.5B-Instruct")

smol_model = Llama(
    model_path=SMOL_MODEL_PATH,
    n_gpu_layers=0,  # Explicitly CPU-only
    n_ctx=1024,
    verbose=False
)
print("Loaded SmolLM2-1.7B-Instruct")


# 4. INFERENCE ENGINE (Formatting prompts as ChatML)
def apply_chatml_template(prompt: str) -> str:
    """Both Qwen2.5 and SmolLM2 instruct models use ChatML format."""
    return f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

def run_cpu_inference(model: Llama, prompt: str, max_tokens: int = 256) -> str:
    formatted_prompt = apply_chatml_template(prompt)
    output = model(
        formatted_prompt,
        max_tokens=max_tokens,
        temperature=0.1,  # Low temperature for deterministic scoring
        stop=["<|im_end|>", "<|im_start|>", "user", "assistant"],
        echo=False
    )
    return output["choices"][0]["text"].strip()


# 5. DATASET LOADER
def load_real_dataset(path: str = "C:\\Users\\AIAli\\OneDrive\\Desktop\\NEO\\datasets\\smoke-v2.jsonl") -> List[Dict[str, Any]]:
    dataset = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))
    return dataset


# 6. EXPERIMENT RUNNER
def run_moa_experiment():
    try:
        dataset = load_real_dataset()
        print(f"\nLoaded {len(dataset)} items from smoke-v2.jsonl")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    results = []
    qwen_score_total = 0.0
    smol_score_total = 0.0
    synth_score_total = 0.0
    routing_upper_bound_total = 0.0  # Theoretical limit if we selected perfect answers
    
    print("\nStarting CPU-only MoA Evaluation Loop...")
    
    for idx, item in enumerate(dataset):
        prompt = item["prompt"]
        domain = item.get("domain", "unknown")
        
        start_time = time.time()
        
        # Step A: Draft Generation
        ans_qwen = run_cpu_inference(qwen_model, prompt)
        ans_smol = run_cpu_inference(smol_model, prompt)
        
        # Step B: Synthesis Pass (Executed on Qwen-1.5B)
        synth_prompt = (
            f"You are a consensus engine. Combine and verify the best, most mathematically "
            f"accurate facts from the two drafts below to answer the user prompt correctly. "
            f"Respond with only the final verified answer, avoiding editorial fluff.\n\n"
            f"User Prompt: {prompt}\n\n"
            f"Draft 1: {ans_qwen}\n"
            f"Draft 2: {ans_smol}\n\n"
            f"Synthesized Answer:"
        )
        ans_synth = run_cpu_inference(qwen_model, synth_prompt)
        
        latency = time.time() - start_time
        
        # Step C: Real grading via score_one
        # score_one expects (item_dict, prediction_string) and returns a float or bool
        eval_qwen = float(score_one(item, ans_qwen))
        eval_smol = float(score_one(item, ans_smol))
        eval_synth = float(score_one(item, ans_synth))
        
        # Did at least one model have a correct response?
        eval_upper_bound = 1.0 if (eval_qwen > 0.0 or eval_smol > 0.0) else 0.0
        
        # Accumulate metrics
        qwen_score_total += eval_qwen
        smol_score_total += eval_smol
        synth_score_total += eval_synth
        routing_upper_bound_total += eval_upper_bound
        
        # Log incremental updates
        print(f"[{idx+1}/{len(dataset)}] Latency: {latency:.2f}s | Qwen: {eval_qwen} | Smol: {eval_smol} | Synth: {eval_synth}")
        
        results.append({
            "id": item.get("id", idx),
            "domain": domain,
            "latency_sec": latency,
            "predictions": {
                "qwen": ans_qwen,
                "smol": ans_smol,
                "synthesis": ans_synth
            },
            "scores": {
                "qwen": eval_qwen,
                "smol": eval_smol,
                "synthesis": eval_synth,
                "perfect_routing_possible": eval_upper_bound
            }
        })
        
    total_items = len(dataset)
    
    # Calculate Final Accuracies
    acc_qwen = (qwen_score_total / total_items) * 100
    acc_smol = (smol_score_total / total_items) * 100
    acc_synth = (synth_score_total / total_items) * 100
    acc_upper_bound = (routing_upper_bound_total / total_items) * 100
    
    print("\n--- CPU EVALUATION SUMMARY ---")
    print(f"Total Evaluated Items: {total_items}")
    print(f"Qwen2.5-1.5B Baseline:                   {acc_qwen:.2f}%")
    print(f"SmolLM2-1.7B Baseline:                   {acc_smol:.2f}%")
    print(f"Synthesis Strategy:                      {acc_synth:.2f}%")
    print(f"Theoretical Routing Upper Bound:         {acc_upper_bound:.2f}%")
    print("---------------------------------")
    
    # Export full run data
    output_payload = {
        "summary": {
            "total_items": total_items,
            "qwen_baseline_accuracy": acc_qwen,
            "smol_baseline_accuracy": acc_smol,
            "synthesis_accuracy": acc_synth,
            "perfect_routing_upper_bound": acc_upper_bound,
            "system_info": {
                "platform": "cpu_only",
                "gpu_layers": 0,
                "total_rss_budget_gb": 8
            }
        },
        "runs": results
    }
    
    with open("C:\\Users\\AIAli\\OneDrive\\Desktop\\NEO\\moa_real_evaluation_results.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print("Full run metadata saved to moa_real_evaluation_results.json")

if __name__ == "__main__":
    run_moa_experiment()
