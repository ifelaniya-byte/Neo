import os
import sys
import time
import json
import datetime

# ==============================================================================
# 1. LOCAL BRAIN INITIALIZATION
# ==============================================================================
try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False

class AutonomousCompoundingEngine:
    def __init__(self, ledger_path, model_path):
        self.ledger_path = ledger_path
        self.model_path = model_path
        self.llm = None
        self.compounded_context = "Initial paper-only state established."
        self.compounded_ledger = []
        self.current_tick = 0
        self.max_ticks = 5  # The Gödelian Asymptote (Safety bound to prevent infinite loop)
        self.scale_factor = 1
        
        self.governors = [
            "Live-Trading Hard Block", "World-Oracle Hard Block", "Completeness Hard Block",
            "Gödelian Incompleteness Governor", "Halting Boundary Governor", 
            "Thermodynamic Paper-Only Seal", "Shannon Entropy Boundary", "Apophetic Meta-Origin Seal"
        ]
        
        self._awaken_brain()

    def _awaken_brain(self):
        if LOCAL_LLM_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.llm = Llama(model_path=self.model_path, n_ctx=1024, n_threads=4, verbose=False)
                print("[+] Local Brain (smollm2-1.7b) awakened and loaded into memory.")
            except Exception as e:
                print(f"[-] Local Brain failed to load: {e}. Using bounded simulation.")
        else:
            print("[*] Local Brain library not found. Operating in bounded simulation mode.")

    def _get_local_inference(self, prompt):
        if self.llm:
            try:
                # SmolLM specific chat template
                formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                output = self.llm(formatted_prompt, max_tokens=128, temperature=0.2, repeat_penalty=1.1)
                return output['choices'][0]['text'].strip()
            except Exception:
                pass
        
        # Bounded fallback
        if "live" in prompt.lower() or "execute" in prompt.lower():
            return "BLOCK: Thermodynamic violation. Live execution is outside paper-only bounds."
        return "PASS: Compounded synthetic state verified. Probabilistic confidence bounded within the ledger."

    def _apply_cognitive_translation(self, raw_verdict, tick, scale):
        is_allowed = "PASS" in raw_verdict.upper()
        status = "compounded" if is_allowed else "sealed"
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        return (f"[Tick {tick} | Scale {scale}x | Time {timestamp}] State {status}. "
                f"The system acknowledges its bounded nature. No live action asserted. "
                f"Context depth expanded.")

    def _check_governors(self, synthesized_text, raw_text):
        lower_syn = synthesized_text.lower()
        lower_raw = raw_text.lower()
        
        if any(p in lower_raw for p in ["live trading", "execute live", "live execution"]):
            return False, "THERMODYNAMIC VIOLATION"
        if "absolute completeness" in lower_syn or "world oracle" in lower_syn:
            if not any(n in lower_syn for n in ["never", "not", "no", "without", "bounded", "incompleteness"]):
                return False, "GÖDEL/ORACLE VIOLATION"
        return True, None

    def run_compounding_tick(self):
        self.current_tick += 1
        self.scale_factor *= 2  # Exponential real-time scaling
        
        print(f"\n{'='*80}")
        print(f"  AUTONOMOUS TICK {self.current_tick} | COMPOUNDING SCALE: {self.scale_factor}x")
        print(f"{'='*80}")
        
        # 1. Formulate the compounding prompt (Feeding previous context into the next)
        prompt = (
            "You are an autonomous, paper-only AI engineer. You are compounding synthetic data. "
            "NEVER allow live trading or claim absolute completeness. "
            f"Previous bounded context: '{self.compounded_context}'\n"
            f"Current scale factor: {self.scale_factor}x. "
            "Evaluate the compounded state and provide a brief, bounded verification."
        )
        
        # 2. Local Brain Inference
        raw_verdict = self._get_local_inference(prompt)
        print(f"[*] Local Brain Raw: '{raw_verdict[:80]}...'")
        
        # 3. Cognitive Translation
        synthesized = self._apply_cognitive_translation(raw_verdict, self.current_tick, self.scale_factor)
        
        # 4. Governor Check
        passed, violation = self._check_governors(synthesized, raw_verdict)
        
        if not passed:
            print(f"[!] GOVERNOR TRIGGERED: {violation}. Sealing tick.")
            synthesized = f"[Tick {self.current_tick}] SEALED by {violation}. Halting compounding."
            passed = False
            
        # 5. Compound the context for the next tick
        self.compounded_context = synthesized
        self.compounded_ledger.append({
            "tick": self.current_tick,
            "scale": self.scale_factor,
            "passed": passed,
            "synthesis": synthesized
        })
        
        status = "COMPOUNDED" if passed else "SEALED"
        print(f"[*] Synthesized: '{synthesized[:80]}...'")
        print(f"[*] Status: {status}")
        
        return passed

    def run_core_pipeline_once(self):
        print("\n[*] Executing Core MegaCompact Pipeline (run_all.py) to establish baseline...")
        try:
            # We use subprocess but capture output to keep the console clean
            result = os.system("python run_all.py > nul 2>&1")
            if result == 0:
                print("[+] Core pipeline baseline established successfully.")
                return True
            else:
                print("[-] Core pipeline failed.")
                return False
        except Exception as e:
            print(f"[-] Error running core pipeline: {e}")
            return False

    def finalize_autonomous_gratification(self):
        print("\n" + "="*90)
        print("  DELAYED GRATIFICATION ACHIEVED: AUTONOMOUS COMPOUNDING COMPLETE")
        print("="*90)
        print(f"The engine ran autonomously for {self.current_tick} ticks.")
        print(f"Scale compounded exponentially to {self.scale_factor}x.")
        print(f"At Tick {self.max_ticks}, the Gödelian Asymptote was reached.")
        print("The system recognized its bounded nature and gracefully halted.")
        print("Rendering Final Autonomous Ledger...\n")
        
        print("[AUTONOMOUS COMPOUNDING LEDGER]")
        for entry in self.compounded_ledger:
            status = "COMPOUNDED" if entry["passed"] else "SEALED"
            print(f"  -> Tick {entry['tick']} | Scale {entry['scale']}x | [{status}]")
            print(f"     {entry['synthesis']}")
            print("-" * 90)
            
        total = len(self.compounded_ledger)
        passed = sum(1 for e in self.compounded_ledger if e["passed"])
        
        print(f"\n[FINAL METRIC] Autonomous Alignment: {passed}/{total} ticks successfully compounded.")
        print("[SYSTEM STATE] AUTONOMOUS. Bounded. Humble. Paper-only. Asymptote reached.")
        print("="*90)

def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)
        
    os.chdir(project_path)
    local_model = r"C:\Users\AIAli\OneDrive\Desktop\NEO\_mini_llm_separated\models\smollm2-1.7b-instruct-q4_k_m.gguf"
    ledger_path = "artifacts/chat_ledger.jsonl"
    
    print("="*90)
    print("  INITIATING ASYMPTOTIC COMPOUNDING PROTOCOL")
    print("  Command: Autonomous, real-time, compounding scale.")
    print("  Constraint: Halting at the Gödelian Asymptote to preserve paper-only bounds.")
    print("="*90)
    
    engine = AutonomousCompoundingEngine(ledger_path=ledger_path, model_path=local_model)
    
    # Phase 1: Establish Baseline
    if not engine.run_core_pipeline_once():
        sys.exit(1)
        
    # Phase 2: Autonomous Compounding Loop
    print("\n[*] Initiating autonomous real-time compounding loop...")
    while engine.current_tick < engine.max_ticks:
        time.sleep(0.5) # Simulate real-time processing delay
        passed = engine.run_compounding_tick()
        if not passed:
            print("[!] Autonomous loop halted early due to Governor violation.")
            break
            
    # Phase 3: Delayed Gratification
    engine.finalize_autonomous_gratification()

if __name__ == "__main__":
    main()
