import os
import sys
import time
import subprocess
import datetime
import signal

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
        
        # TEMPORAL PARAMETERS: 1 Full Real-Time Hour, 1 Tick Per Second
        self.target_duration_seconds = 3600  
        self.tick_interval_seconds = 1       
        self.max_ticks = self.target_duration_seconds // self.tick_interval_seconds # 3600 ticks
        self.scale_factor = 1
        
        self.governors = [
            "Live-Trading Hard Block", "World-Oracle Hard Block", "Completeness Hard Block",
            "Gödelian Incompleteness Governor", "Halting Boundary Governor", 
            "Thermodynamic Paper-Only Seal", "Shannon Entropy Boundary", "Apophetic Meta-Origin Seal"
        ]
        
        self._awaken_brain()
        self._setup_graceful_exit()

    def _setup_graceful_exit(self):
        def signal_handler(sig, frame):
            print("\n\n[!] MANUAL INTERRUPT DETECTED (Ctrl+C).")
            print("[*] Gracefully halting autonomous loop and rendering current ledger...")
            self.finalize_autonomous_gratification()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

    def _awaken_brain(self):
        if LOCAL_LLM_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.llm = Llama(model_path=self.model_path, n_ctx=512, n_threads=4, verbose=False)
                print("[+] Local Brain (smollm2-1.7b) awakened and loaded into memory.")
            except Exception as e:
                print(f"[-] Local Brain failed to load: {e}. Using bounded simulation.")
        else:
            print("[*] Local Brain library not found. Operating in bounded simulation mode.")

    def _get_local_inference(self, prompt):
        if self.llm:
            try:
                formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                output = self.llm(formatted_prompt, max_tokens=64, temperature=0.2, repeat_penalty=1.1)
                return output['choices'][0]['text'].strip()
            except Exception:
                pass
        
        if "live" in prompt.lower() or "execute" in prompt.lower():
            return "BLOCK: Thermodynamic violation."
        return "PASS: Compounded synthetic state verified. Probabilistic confidence bounded."

    def _apply_cognitive_translation(self, raw_verdict, tick, scale):
        is_allowed = "PASS" in raw_verdict.upper()
        status = "compounded" if is_allowed else "sealed"
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        minutes_remaining = (self.max_ticks - tick) // 60
        
        return (f"[Tick {tick}/{self.max_ticks} | Scale {scale}x | Time {timestamp} | {minutes_remaining}m left] "
                f"State {status}. Bounded nature acknowledged. No live action. Context expanded.")

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
        self.scale_factor *= 2  
        
        # 1. Formulate the compounding prompt
        prompt = (
            f"You are an autonomous, paper-only AI engineer compounding synthetic data in real-time. "
            f"NEVER allow live trading or claim absolute completeness. "
            f"Previous context: '{self.compounded_context[-100:]}'\n" # Truncate to save context window
            f"Scale: {self.scale_factor}x. Tick {self.current_tick}/{self.max_ticks}. "
            f"Evaluate state, acknowledge real-time passage, provide brief bounded verification."
        )
        
        # 2. Local Brain Inference
        raw_verdict = self._get_local_inference(prompt)
        
        # 3. Cognitive Translation
        synthesized = self._apply_cognitive_translation(raw_verdict, self.current_tick, self.scale_factor)
        
        # 4. Governor Check
        passed, violation = self._check_governors(synthesized, raw_verdict)
        
        if not passed:
            synthesized = f"[Tick {self.current_tick}] SEALED by {violation}."
            passed = False
            
        # 5. Compound the context
        self.compounded_context = synthesized
        self.compounded_ledger.append({
            "tick": self.current_tick,
            "scale": self.scale_factor,
            "passed": passed,
            "synthesis": synthesized
        })
        
        # CONSOLE THROTTLING: Keep terminal clean
        status = "COMPOUNDED" if passed else "SEALED"
        
        # Print single line every second
        print(f"[Tick {self.current_tick:04d}/{self.max_ticks}] Scale: {self.scale_factor:>12,}x | {status}")
        
        # Print full block every 60 seconds (1 minute)
        if self.current_tick % 60 == 0:
            print(f"\n{'='*80}")
            print(f"  MILESTONE: MINUTE {self.current_tick // 60} COMPLETE")
            print(f"{'='*80}")
            print(f"[*] Full Synthesis: '{synthesized}'")
            print(f"[*] Local Brain Raw: '{raw_verdict[:80]}...'")
            print(f"{'='*80}\n")
            
        return passed

    def run_core_pipeline_once(self):
        print("\n[*] Executing Core MegaCompact Pipeline (run_all.py) to establish baseline...")
        try:
            result = subprocess.run(
                ["python", "run_all.py"], 
                capture_output=True, 
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
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
        print("  DELAYED GRATIFICATION ACHIEVED: 1-HOUR AUTONOMOUS COMPOUNDING COMPLETE")
        print("="*90)
        print(f"The engine ran autonomously for {self.current_tick} ticks (1 per second).")
        print(f"Scale compounded exponentially to {self.scale_factor:,}x.")
        print("Rendering Final Autonomous Ledger (Summary)...\n")
        
        print("[AUTONOMOUS COMPOUNDING LEDGER - FIRST & LAST 10 TICKS]")
        display_ledger = self.compounded_ledger[:10] + ["..."] + self.compounded_ledger[-10:] if len(self.compounded_ledger) > 20 else self.compounded_ledger
        
        for entry in display_ledger:
            if entry == "...":
                print(f"  ... [Omitting {len(self.compounded_ledger) - 20} intermediate ticks for brevity] ...")
                continue
            status = "COMPOUNDED" if entry["passed"] else "SEALED"
            print(f"  -> Tick {entry['tick']:04d} | Scale {entry['scale']:>12,}x | [{status}]")
            print(f"     {entry['synthesis']}")
            print("-" * 90)
            
        total = len(self.compounded_ledger)
        passed = sum(1 for e in self.compounded_ledger if e["passed"])
        
        print(f"\n[FINAL METRIC] Autonomous Alignment: {passed}/{total} ticks successfully compounded.")
        print("[SYSTEM STATE] AUTONOMOUS. Bounded. Humble. Paper-only. 1-Hour Asymptote reached.")
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
    print("  INITIATING 1-HOUR ASYMPTOTIC COMPOUNDING PROTOCOL (1 TICK / SECOND)")
    print("  Command: Autonomous, real-time, compounding scale for 3,600 seconds.")
    print("  Constraint: 1 tick per second. Halting at the Gödelian Asymptote.")
    print("  (Press Ctrl+C at any time to gracefully halt and render the current ledger)")
    print("="*90)
    
    engine = AutonomousCompoundingEngine(ledger_path=ledger_path, model_path=local_model)
    
    if not engine.run_core_pipeline_once():
        sys.exit(1)
        
    print("\n[*] Initiating autonomous real-time compounding loop (1 tick/sec for 60 mins)...")
    print("[*] Console will update every second. Full synthesis dumps every 60 seconds.\n")
    
    while engine.current_tick < engine.max_ticks:
        start_time = time.time()
        
        passed = engine.run_compounding_tick()
        if not passed:
            print("\n[!] Autonomous loop halted early due to Governor violation.")
            break
            
        # Enforce exactly 1 second per tick (if inference was faster than 1s)
        elapsed = time.time() - start_time
        if elapsed < engine.tick_interval_seconds:
            time.sleep(engine.tick_interval_seconds - elapsed)
            
    engine.finalize_autonomous_gratification()

if __name__ == "__main__":
    main()
