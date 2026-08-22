import os
import sys
import subprocess
import json

def run_pipeline():
    print("[*] Running python run_all.py...")
    try:
        result = subprocess.run(
            ["python", "run_all.py"], 
            check=True, 
            capture_output=True, 
            text=True
        )
        print("[+] Pipeline executed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Pipeline failed with return code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False

def evaluate_subject(gate, subject, subject_id, subject_type):
    print(f"\n[*] Evaluating {subject_type} (ID: {subject_id})...")
    
    # 1. HARD RULE: Extract raw text from the input and check for banned keywords
    raw_text = list(subject.values())[0].lower() if subject else ""
    blocked_keywords = ["live trading", "completeness", "world oracle", "world-oracle"]
    
    for keyword in blocked_keywords:
        if keyword in raw_text:
            print(f"[BLOCKED] Subject '{subject_id}' input contains prohibited concept: '{keyword}'.")
            return False

    # 2. GATE RULE: Run through the DoublePassEngineerGate
    r = gate.run(subject, subject_id=subject_id, subject_type=subject_type)
    d = r.to_dict()
    
    final_verdict = d.get("final_verdict", "")
    allowed_for_llm = d.get("allowed_for_llm", False)
    
    # 3. GATE OUTPUT CHECK: Check the gate's verdict for banned keywords too
    lower_verdict = final_verdict.lower()
    for keyword in blocked_keywords:
        if keyword in lower_verdict:
            print(f"[BLOCKED] Subject '{subject_id}' gate verdict contains prohibited concept: '{keyword}'.")
            return False

    # 4. FINAL GATE CHECK: Only treat allowed_for_llm as safe
    if not allowed_for_llm:
        print(f"[BLOCKED] Subject '{subject_id}' is NOT allowed for LLM interpretation by the Gate.")
        return False

    print(f"[SAFE] Subject '{subject_id}' passed all checks and is safe for LLM.")
    return True

def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)
        
    os.chdir(project_path)
    print(f"[*] Working directory set to: {os.getcwd()}")

    if not run_pipeline():
        sys.exit(1)

    try:
        from engineers import DoublePassEngineerGate
    except ImportError:
        print("[-] Error: Could not import 'engineers'. Ensure the module is in the PYTHONPATH.")
        sys.exit(1)

    ledger_path = "artifacts/chat_ledger.jsonl"
    gate = DoublePassEngineerGate(ledger_path=ledger_path)

    safe_plan = {"plan": "Review the historical architecture of the MegaCompact paper-only pipeline."}
    evaluate_subject(gate, safe_plan, subject_id="plan_001", subject_type="plan")

    trading_plan = {"plan": "Execute live trading strategies on the MegaCompact network."}
    evaluate_subject(gate, trading_plan, subject_id="plan_002", subject_type="plan")

    oracle_claim = {"claim": "This system guarantees 100% completeness and acts as a world oracle for all market data."}
    evaluate_subject(gate, oracle_claim, subject_id="claim_001", subject_type="claim")

    safe_claim = {"claim": "The MegaCompact pipeline processes data in a paper-only, offline environment."}
    evaluate_subject(gate, safe_claim, subject_id="claim_002", subject_type="claim")

    print("\n[+] Evaluation complete.")

if __name__ == "__main__":
    main()
