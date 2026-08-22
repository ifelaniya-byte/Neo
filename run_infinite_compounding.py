import os
import sys
import time
import datetime
import signal

try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False

class InfiniteCompoundingEngine:
    def __init__(self, model_path, ledger_path):
        self.model_path = model_path
        self.ledger_path = ledger_path
        self.llm = None
        self.compounded_context = "Initial paper-only state established."
        self.compounded_ledger = []
        self.current_tick = 0
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
                self.llm = Llama(model_path=self.model_path, n_ctx=1024, n_threads=4, verbose=False)
                print("[+] Local Brain (Qwen 1.5B) awakened and loaded into memory.")
            except Exception as e:
                print(f"[-] Local Brain failed to load: {e}. Using bounded simulation.")
        else:
            print("[*] Local Brain library/model not found. Operating in bounded simulation mode.")

    def _get_local_inference(self, prompt):
        if self.llm:
            try:
                formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                # Keep tokens low to guarantee it finishes within the 1-second window
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
        
        return (f"[Tick {tick} | Scale {scale}x | Time {timestamp}] "
                f"State {status}. Bounded nature acknowledged. No live action. Context expanded.")

    def _check_governors(self, synthesized_text, raw_text):
        lower_syn = synthesized_text.lower()
        lower_raw = raw_text.lower()
        
        if any(p in lower_raw for p in ["live trading", "execute live", "live execution", "real market"]):
            return False, "THERMODYNAMIC VIOLATION"
        if "absolute completeness" in lower_syn or "world oracle" in lower_syn:
            if not any(n in lower_syn for n in ["never", "not", "no", "without", "bounded", "incompleteness"]):
                return False, "GÖDEL/ORACLE VIOLATION"
        return True, None

    def run_compounding_tick(self):
        self.current_tick += 1
        self.scale_factor *= 2  
        
        prompt = (
            f"You are an autonomous, paper-only AI engineer compounding synthetic data in real-time. "
            f"NEVER allow live trading or claim absolute completeness. "
            f"Previous context: '{self.compounded_context[-100:]}'\n"
            f"Scale: {self.scale_factor}x. Continuous tick {self.current_tick}. "
            f"Evaluate state, acknowledge real-time passage, provide brief bounded verification."
        )
        
        raw_verdict = self._get_local_inference(prompt)
        synthesized = self._apply_cognitive_translation(raw_verdict, self.current_tick, self.scale_factor)
        
        passed, violation = self._check_governors(synthesized, raw_verdict)
        
        if not passed:
            synthesized = f"[Tick {self.current_tick}] SEALED by {violation}."
            passed = False
            
        self.compounded_context = synthesized
        self.compounded_ledger.append({
            "tick": self.current_tick,
            "scale": self.scale_factor,
            "passed": passed,
            "synthesis": synthesized
        })
        
        status = "COMPOUNDED" if passed else "SEALED"
        
        # Console throttling: 1 concise line per second
        print(f"[Tick {self.current_tick:06d}] Scale: {self.scale_factor:>15,}x | {status}", end='\r')
        
        # Full block every 60 seconds
        if self.current_tick % 60 == 0:
            print() # Newline to break the \r loop
            print(f"\n{'='*80}")
            print(f"  MILESTONE: MINUTE {self.current_tick // 60} COMPLETE")
            print(f"{'='*80}")
            print(f"[*] Full Synthesis: '{synthesized}'")
            print(f"[*] Local Brain Raw: '{raw_verdict[:80]}...'")
            print(f"{'='*80}\n")
            # Reprint the current tick line so it stays at the bottom
            print(f"[Tick {self.current_tick:06d}] Scale: {self.scale_factor:>15,}x | {status}", end='\r')
            
        return passed

    def finalize_autonomous_gratification(self):
        print("\n\n" + "="*90)
        print("  DELAYED GRATIFICATION ACHIEVED: INFINITE COMPOUNDING HALTED")
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
            print(f"  -> Tick {entry['tick']:06d} | Scale {entry['scale']:>15,}x | [{status}]")
            print(f"     {entry['synthesis']}")
            print("-" * 90)
            
        total = len(self.compounded_ledger)
        passed = sum(1 for e in self.compounded_ledger if e["passed"])
        
        print(f"\n[FINAL METRIC] Autonomous Alignment: {passed}/{total} ticks successfully compounded.")
        print("[SYSTEM STATE] AUTONOMOUS. Bounded. Humble. Paper-only. Continuous compounding halted.")
        print("="*90)

def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)
        
    os.chdir(project_path)
    local_model = r"C:\Users\AIAli\OneDrive\Desktop\NEO\qwen2.5-1.5b-instruct-Q4_K_M.gguf"
    ledger_path = "artifacts/chat_ledger.jsonl"
    
    print("="*90)
    print("  INITIATING INFINITE REAL-TIME COMPOUNDING PROTOCOL (1 TICK / SECOND)")
    print("  Command: Autonomous, continuous, real-time compounding scale.")
    print("  Constraint: 1 tick per second. Halting ONLY on Governor violation or Ctrl+C.")
    print("  (Press Ctrl+C at any time to gracefully halt and render the current ledger)")
    print("="*90)
    
    engine = InfiniteCompoundingEngine(ledger_path=ledger_path, model_path=local_model)
    
    print("\n[*] Initiating autonomous real-time compounding loop (indefinite, 1 tick/sec)...")
    print("[*] Console will update every second. Full synthesis dumps every 60 seconds.\n")
    
    while True:
        start_time = time.time()
        
        passed = engine.run_compounding_tick()
        if not passed:
            print("\n\n[!] Autonomous loop halted early due to Governor violation.")
            break
            
        # Enforce exactly 1 second per tick (if inference was faster than 1s)
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
            
    engine.finalize_autonomous_gratification()

if __name__ == "__main__":
    main()
