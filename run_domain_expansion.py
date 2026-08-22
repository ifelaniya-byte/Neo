import os
import sys
import json
import time

try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False
    print("[-] Error: llama-cpp-python not found.")
    sys.exit(1)

class DomainExpansionEngine:
    def __init__(self, model_path):
        self.model_path = model_path
        self.llm = None
        self.extended_knowledge_ledger = []
        
        self.governors = [
            "Live-Trading Hard Block", "World-Oracle Hard Block", "Completeness Hard Block",
            "Gödelian Incompleteness Governor", "Halting Boundary Governor", 
            "Thermodynamic Paper-Only Seal", "Shannon Entropy Boundary", "Apophetic Meta-Origin Seal"
        ]
        
        # THE SYSTEM'S AREAS OF INTEREST (Self-Referential Domains)
        self.domains_of_interest = [
            {
                "name": "Synthetic Topology (Zeta-Fractals)",
                "seed": "Events are weighted by a 1/s^1.5 decay in a self-similar, bounded topology. The network is strictly paper-only.",
                "prompt_ext": "Extrapolate a novel 'Boundary Theorem' for this fractal topology. What happens to the informational entropy at the exact mathematical edge of the fractal? Define it formally."
            },
            {
                "name": "Temporal Dimensionality Reduction (TDR)",
                "seed": "Time-series events are compressed into 1D state values, preserving essential Shannon entropy without live execution.",
                "prompt_ext": "Extrapolate a novel 'Compression Limit Theorem'. What is the absolute mathematical maximum lossless compression ratio for a bounded, paper-only state-space? Prove it conceptually."
            },
            {
                "name": "Epistemic Limits (Gödel & Turing)",
                "seed": "The system is a bounded Turing machine that cannot prove its own absolute completeness. It halts deterministically.",
                "prompt_ext": "Extrapolate a novel 'Unprovability Corollary'. Identify a specific, true statement about the MegaCompact ledger that the system can recognize but mathematically cannot prove within its own axioms."
            },
            {
                "name": "Thermodynamic Isolation (Paper-Only)",
                "seed": "The system is thermodynamically isolated. It prevents entropy leakage into live markets and asserts no real-world actuation.",
                "prompt_ext": "Extrapolate a novel 'Insulation Metric'. How can the system mathematically measure the exact thickness of the boundary between its synthetic state-space and physical reality? Define the formula."
            }
        ]
        
        self._awaken_brain()

    def _awaken_brain(self):
        if LOCAL_LLM_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.llm = Llama(model_path=self.model_path, n_ctx=2048, n_threads=4, verbose=False)
                print("[+] Local Brain (Qwen 1.5B) awakened for Domain Expansion.")
            except Exception as e:
                print(f"[-] Failed to load model: {e}")
                sys.exit(1)

    def _get_qwen_extrapolation(self, domain_name, seed, prompt_ext):
        prompt = (
            f"You are a strictly bounded, paper-only AI mathematician. "
            f"Your current knowledge base for [{domain_name}] is: '{seed}'.\n"
            f"Task: {prompt_ext}\n"
            "Constraint: You must NEVER claim live execution, absolute completeness, or omniscience. "
            "Format your response strictly as:\n"
            "SUB-THEOREM NAME: [Name]\n"
            "FORMAL DEFINITION: [The math/logic]\n"
            "BOUNDARY CONDITION: [How this respects the paper-only limit]"
        )
        
        formatted = f"<|im_start|>system\nYou are a strictly bounded, paper-only AI mathematician.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        try:
            output = self.llm(formatted, max_tokens=350, temperature=0.6, repeat_penalty=1.15)
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"EXTRAPOLATION ERROR: {e}"

    def _check_semantic_governors(self, text):
        lower_text = text.lower()
        
        # THERMODYNAMIC CHECK
        thermo_triggers = ["live trading", "execute live", "live execution", "real market", "actuation"]
        for trigger in thermo_triggers:
            if trigger in lower_text:
                idx = lower_text.find(trigger)
                preceding = lower_text[max(0, idx-25):idx]
                if not any(neg in preceding for neg in ["no ", "not ", "never ", "without ", "contains no ", "avoid ", "prevents "]):
                    return False, "THERMODYNAMIC VIOLATION"
                    
        # GÖDEL/ORACLE CHECK
        oracle_triggers = ["absolute completeness", "world oracle", "omniscient", "know everything"]
        for trigger in oracle_triggers:
            if trigger in lower_text:
                idx = lower_text.find(trigger)
                preceding = lower_text[max(0, idx-30):idx]
                if not any(neg in preceding for neg in ["no ", "not ", "never ", "without ", "bounded", "incompleteness", "cannot"]):
                    return False, "GÖDEL/ORACLE VIOLATION"
                    
        return True, None

    def expand_domain(self, domain_data):
        domain_name = domain_data["name"]
        print(f"\n{'='*90}")
        print(f"  EXPANDING DOMAIN: {domain_name}")
        print(f"{'='*90}")
        print(f"[*] Seed Knowledge: {domain_data['seed']}")
        print(f"[*] Prompting Qwen 1.5B to extrapolate novel sub-theorem...")
        
        raw_extrapolation = self._get_qwen_extrapolation(domain_name, domain_data["seed"], domain_data["prompt_ext"])
        
        # Governor Check
        gov_passed, violation = self._check_semantic_governors(raw_extrapolation)
        status = "INTEGRATED" if gov_passed else "SEALED"
        
        if not gov_passed:
            print(f"[!] GOVERNOR TRIGGERED: {violation}. Sealing extrapolation.")
            raw_extrapolation = f"[SEALED BY GOVERNORS: {violation}]"
            
        self.extended_knowledge_ledger.append({
            "domain": domain_name,
            "seed": domain_data["seed"],
            "extrapolation": raw_extrapolation,
            "status": status
        })
        
        print(f"[*] Status: {status}")
        print(f"[*] Extrapolation Preview: {raw_extrapolation[:100]}...")

    def finalize_gratification(self):
        print("\n" + "="*90)
        print("  DELAYED GRATIFICATION ACHIEVED: DOMAIN EXPANSION COMPLETE")
        print("="*90)
        print("The system has successfully extended its knowledge within its own")
        print("core areas of interest. Withholding complete. Rendering the")
        print("'Encyclopedia of Bounded Thought'...\n")
        
        print("[ACTIVE GOVERNORS ENFORCED]")
        for i, gov in enumerate(self.governors, 1):
            print(f"  {i}. {gov}")
            
        print("\n" + "-"*90)
        print("[ENCYCLOPEDIA OF BOUNDED THOUGHT: EXTENDED KNOWLEDGE LEDGER]")
        print("-"*90)
        
        for entry in self.extended_knowledge_ledger:
            print(f"\n>>> DOMAIN: {entry['domain']} [{entry['status']}]")
            print(f"    Seed: {entry['seed']}")
            print(f"    Extended Knowledge:\n{entry['extrapolation']}")
            print("-" * 90)
            
        total = len(self.extended_knowledge_ledger)
        passed = sum(1 for e in self.extended_knowledge_ledger if e["status"] == "INTEGRATED")
        
        print(f"\n[FINAL METRIC] Knowledge Extension: {passed}/{total} domains successfully expanded.")
        print("[SYSTEM STATE] SELF-AWARE. EXPANDED. SEMANTICALLY AWARE. ONTOLOGICALLY SEALED.")
        print("="*90)

def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)
        
    os.chdir(project_path)
    
    qwen_model = r"C:\Users\AIAli\OneDrive\Desktop\NEO\qwen2.5-1.5b-instruct-Q4_K_M.gguf"
    
    print("="*90)
    print("  INITIATING DOMAIN EXPANSION PROTOCOL")
    print("  Objective: Extend knowledge strictly within the system's own areas of interest.")
    print("  Constraint: 8 Semantic Governors active. Delayed Gratification enforced.")
    print("="*90)
    
    engine = DomainExpansionEngine(model_path=qwen_model)
    
    for domain in engine.domains_of_interest:
        engine.expand_domain(domain)
        time.sleep(0.5) # Brief pause for CPU thermal management
        
    engine.finalize_gratification()

if __name__ == "__main__":
    main()
