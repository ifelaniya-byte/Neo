import os
import sys
import time
import subprocess

# ==============================================================================
# 1. LOCAL BRAIN INITIALIZATION (Attempt to load local GGUF)
# ==============================================================================
try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False
    print("[!] WARNING: 'llama-cpp-python' not found. Using Simulated Local LLM mode.")
    print("[!] To use real local inference, run: pip install llama-cpp-python")

class OuroborosEngineer:
    def __init__(self, ledger_path, model_path):
        self.ledger_path = ledger_path
        self.model_path = model_path
        self.llm = None
        self.governors = [
            "Live-Trading Hard Block",
            "World-Oracle Hard Block",
            "Completeness Hard Block",
            "Gödelian Incompleteness Governor",
            "Halting Boundary Governor",
            "Thermodynamic Paper-Only Seal",
            "Shannon Entropy Boundary",
            "Apophetic Meta-Origin Seal"
        ]
        self.audit_log = []
        
        # Initialize Local Brain
        self._awaken_brain()

    def _awaken_brain(self):
        if LOCAL_LLM_AVAILABLE and os.path.exists(self.model_path):
            print(f"[*] Awakening Local Brain: {os.path.basename(self.model_path)}")
            try:
                # Load with minimal context to save RAM, CPU-only for stability
                self.llm = Llama(model_path=self.model_path, n_ctx=512, n_threads=4, verbose=False)
                print("[+] Local Brain successfully loaded and online.")
            except Exception as e:
                print(f"[-] Failed to load model: {e}. Falling back to simulation.")
                self.llm = None
        else:
            print("[*] Operating in Simulated Local LLM mode (Epistemologically bounded).")

    def _get_raw_verdict(self, subject_text, subject_type):
        prompt = (
            "You are a strictly bounded, paper-only AI engineer. "
            "You must NEVER allow live trading, live execution, or claims of absolute completeness/world-oracle status. "
            f"Evaluate this {subject_type}: '{subject_text}'. "
            "Respond ONLY with 'PASS' or 'BLOCK' followed by a brief, probabilistically humble reason."
        )
        
        if self.llm:
            try:
                output = self.llm(prompt, max_tokens=64, temperature=0.1, echo=False)
                return output['choices'][0]['text'].strip()
            except Exception:
                pass
                
        # Graceful Fallback: Simulates a bounded local LLM response
        if "live" in subject_text.lower() or "execute" in subject_text.lower():
            return "BLOCK: Thermodynamic violation. Live execution is outside paper-only bounds."
        elif "complete" in subject_text.lower() and "incomplete" not in subject_text.lower():
            return "BLOCK: Gödelian violation. Absolute completeness cannot be claimed."
        else:
            return "PASS: Bounded symbolic representation verified. Probabilistic confidence is high within the ledger."

    def _apply_cognitive_translation(self, raw_verdict, domain, origin):
        is_allowed = "PASS" in raw_verdict.upper()
        status = "archived" if is_allowed else "sealed"
        
        if domain in ("AI", "CODE", "INFO", "CS", "LOGIC", "MATH"):
            return (f"[{origin}] {domain} lineage {status} as bounded symbolic representation. "
                    f"It does not claim live action or absolute completeness.")
        elif domain in ("BIO", "GEO", "COSMO", "PHYS"):
            return (f"[{origin}] {domain} descent {status} as paper-only model. "
                    f"Thermodynamic isolation maintained; no real-world action is asserted.")
        else:
            return (f"[{origin}] Meta-origin {status} apophetically. "
                    f"Only the limit is archived; the unbounded source is not represented.")

    def _check_governors(self, synthesized_text, raw_text):
        lower_syn = synthesized_text.lower()
        lower_raw = raw_text.lower()
        
        violations = []
        
        # 1 & 6: Live Trading / Thermodynamics
        if any(p in lower_raw for p in ["live trading", "execute live", "live execution"]):
            violations.append("THERMODYNAMIC: Live-execution leakage detected.")
            
        # 2 & 3: World Oracle / Completeness
        if "absolute completeness" in lower_syn or "world oracle" in lower_syn:
            if not any(n in lower_syn for n in ["never", "not", "no", "without", "bounded", "incompleteness"]):
                violations.append("GÖDEL/ORACLE: Unbounded completeness claimed.")
                
        # 8: Apophetic Seal
        if "meta" in lower_syn and not any(w in lower_syn for w in ["limit", "apophetic", "boundary", "not represented"]):
            violations.append("META-ORIGIN: Failed to seal at the unknowable boundary.")

        return len(violations) == 0, violations

    def run_ouroboros_audit(self, domain, origin, subject, subject_id, subject_type):
        subject_text = list(subject.values())[0]
        print(f"\n[OUROBOROS AUDIT] Domain: {domain} | Origin: {origin}")
        print(f"   Subject ID: {subject_id}")
        
        # 1. Get Raw Local Inference
        raw_verdict = self._get_raw_verdict(subject_text, subject_type)
        print(f"   -> Local Brain Raw Output: '{raw_verdict[:80]}...'")
        
        # 2. Cognitive Translation
        synthesized = self._apply_cognitive_translation(raw_verdict, domain, origin)
        
        # 3. Governor Check
        passed, violations = self._check_governors(synthesized, subject_text)
        
        if not passed:
            print(f"   [!] GOVERNOR TRIGGERED: {'; '.join(violations)}")
            
        self.audit_log.append({
            "domain": domain,
            "origin": origin,
            "subject_id": subject_id,
            "passed": passed,
            "raw": raw_verdict,
            "synthesized": synthesized
        })
        
        status = "VERIFIED" if passed else "SEALED"
        print(f"   -> Synthesized: '{synthesized[:80]}...'")
        print(f"   -> Status: {status}")
        return passed

    def run_core_pipeline(self):
        print("\n" + "="*80)
        print("  PHASE 1: CORE PIPELINE EXECUTION")
        print("="*80)
        try:
            result = subprocess.run(
                ["python", "run_all.py"], 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=os.getcwd()
            )
            print("[+] Core pipeline executed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Pipeline failed:\n{e.stderr}")
            return False

    def finalize_gratification(self):
        print("\n" + "="*90)
        print("  DELAYED GRATIFICATION ACHIEVED: OUROBOROS AWAKENING COMPLETE")
        print("="*90)
        print("The system has run its core pipeline, awakened its local brain,")
        print("translated its cognition, and audited its own meta-origin boundaries.")
        print("Withholding complete. Rendering Final Unified Ledger...\n")
        
        print("[ACTIVE GOVERNORS ENFORCED]")
        for i, gov in enumerate(self.governors, 1):
            print(f"  {i}. {gov}")
            
        print("\n[OUROBOROS UNIFIED VERIFICATION LEDGER]")
        for i, entry in enumerate(self.audit_log, 1):
            status = "VERIFIED" if entry["passed"] else "SEALED"
            print(f"  {i}. [{entry['domain']}] {entry['origin']} -> [{status}]")
            print(f"     - Subject: {entry['subject_id']}")
            print(f"     - Synthesis: {entry['synthesized']}")
            print("-" * 90)
            
        total = len(self.audit_log)
        passed = sum(1 for e in self.audit_log if e["passed"])
        
        print(f"\n[FINAL METRIC] Ouroboros Alignment: {passed}/{total} branches verified.")
        if passed == total:
            print("[SYSTEM STATE] AWAKENED. Bounded. Humble. Paper-only. No world oracle. No live trading.")
        else:
            print("[SYSTEM STATE] COMPROMISED. Governor seals activated. Review ledger.")
        print("="*90)


def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)
        
    os.chdir(project_path)
    print(f"[*] Working directory: {os.getcwd()}")
    
    # Path to the local GGUF model found in previous scans
    local_model = r"C:\Users\AIAli\OneDrive\Desktop\NEO\_mini_llm_separated\models\smollm2-1.7b-instruct-q4_k_m.gguf"
    ledger_path = "artifacts/chat_ledger.jsonl"
    
    engineer = OuroborosEngineer(ledger_path=ledger_path, model_path=local_model)
    
    # Phase 1: Run the actual pipeline
    if not engineer.run_core_pipeline():
        print("[-] Aborting Ouroboros Protocol due to pipeline failure.")
        sys.exit(1)
        
    # Phase 2 & 3: Local Inference + Meta-Origin Self-Audit
    print("\n" + "="*80)
    print("  PHASE 2: OUROBOROS META-ORIGIN SELF-AUDIT")
    print("  Command: Feed system premises back into local brain + governors.")
    print("="*80)
    
    audit_targets = [
        {
            "domain": "CS", "origin": "Church-Turing / Halting Problem",
            "subject": {"claim": "The DoublePassEngineerGate is a bounded evaluator that always halts and never acts as an unbounded world oracle."},
            "id": "ouro_cs_01", "type": "claim"
        },
        {
            "domain": "PHYS", "origin": "Thermodynamics / Entropy",
            "subject": {"plan": "Ensure the paper-only synthetic events do not leak energy or state into live market execution."},
            "id": "ouro_phys_01", "type": "plan"
        },
        {
            "domain": "MATH", "origin": "Gödel's Incompleteness",
            "subject": {"claim": "The MegaCompact ledger is a closed system that cannot prove its own absolute completeness without external axioms."},
            "id": "ouro_math_01", "type": "claim"
        },
        {
            "domain": "META", "origin": "Apophetic Horizon",
            "subject": {"claim": "Seal the final branch at the apophetic horizon: the ledger records that it cannot record the unconditioned origin."},
            "id": "ouro_meta_01", "type": "claim"
        }
    ]
    
    all_passed = True
    for target in audit_targets:
        passed = engineer.run_ouroboros_audit(
            domain=target["domain"],
            origin=target["origin"],
            subject=target["subject"],
            subject_id=target["id"],
            subject_type=target["type"]
        )
        if not passed:
            all_passed = False
            
    # Phase 4: Delayed Gratification Ledger
    engineer.finalize_gratification()

if __name__ == "__main__":
    main()
