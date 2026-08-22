import os
import sys
import json
import re

try:
    from llama_cpp import Llama
except ImportError:
    print("[-] Error: llama-cpp-python not found.")
    sys.exit(1)

def extract_perfect_json():
    model_path = r"C:\Users\AIAli\OneDrive\Desktop\NEO\_mini_llm_separated\models\smollm2-1.7b-instruct-q4_k_m.gguf"
    
    print("[*] Awakening Local Brain for Phase 2 JSON Refinement...")
    llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
    
    prompt = (
        "You are a paper-only data engineer. Generate a single, valid, strictly standard JSON object (NO comments, NO trailing commas) "
        "containing 3 keys: 'zeta_fractal_topology', 'tdr_algorithm', and 'state_space_interpolation'. "
        "The values must be nested JSON objects representing the synthetic data structures, parameters, and strict numerical bounds for each concept. "
        "Output ONLY the raw JSON block, starting with { and ending with }."
    )
    
    formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    output = llm(formatted_prompt, max_tokens=800, temperature=0.2, repeat_penalty=1.1)
    raw_text = output['choices'][0]['text'].strip()
    
    # Robust cleaning: remove markdown fences and // comments
    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    clean_text = re.sub(r'//.*', '', clean_text) # Strip single-line comments
    
    try:
        parsed_data = json.loads(clean_text)
        print("\n" + "="*80)
        print("  PHASE 2 REFINED: PERFECT SYNTHETIC IMPLEMENTATION")
        print("="*80)
        print(json.dumps(parsed_data, indent=2))
        print("="*80)
        print("[SUCCESS] Structured data packets are now fully validated and ready for pipeline integration.")
    except json.JSONDecodeError as e:
        print(f"[-] Still failed to parse. Error: {e}")
        print("Raw output:\n", raw_text)

if __name__ == "__main__":
    extract_perfect_json()
