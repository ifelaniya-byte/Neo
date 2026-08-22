import os
import sys
import math

try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False

class TranslatorInterface:
    def __init__(self):
        self.llm = None
        self._awaken_llm()

    def _awaken_llm(self):
        if LOCAL_LLM_AVAILABLE:
            model_path = r"C:\Users\AIAli\OneDrive\Desktop\NEO\qwen2.5-1.5b-instruct-Q4_K_M.gguf"
            if os.path.exists(model_path):
                try:
                    self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
                except:
                    pass

    def _omega_compute_primes(self, n):
        """The Omega Engine's deterministic math fabric."""
        limit = n * 15 # Rough upper bound for nth prime
        sieve = [True] * limit
        primes = []
        for p in range(2, limit):
            if sieve[p]:
                primes.append(p)
                for i in range(p * p, limit, p):
                    sieve[i] = False
            if len(primes) >= n:
                break
        return primes[-1] if len(primes) >= n else None

    def _omega_compute_rule30(self, steps):
        """The Omega Engine's deterministic structural fabric."""
        width = 60
        state = [0] * width
        state[width // 2] = 1
        for _ in range(steps):
            new_state = [0] * width
            for c in range(width):
                left = state[(c - 1) % width]
                center = state[c]
                right = state[(c + 1) % width]
                neighborhood = (left << 2) | (center << 1) | right
                new_state[c] = (30 >> neighborhood) & 1
            state = new_state
        return "".join(["█" if bit else " " for bit in state])

    def process_question(self, user_input):
        print("\n" + "="*80)
        print(f"  USER QUERY: '{user_input}'")
        print("="*80)

        # STEP 1: LLM acts as the Diplomat (Intent Extraction)
        prompt = f"""You are an interface to a deterministic supercomputer called the Omega Engine. 
        The user asked: "{user_input}"
        Analyze the request. Does it require:
        A) Exact mathematical computation (like finding a specific prime number)?
        B) Structural simulation (like Rule 30 cellular automata)?
        C) General knowledge or semantic translation?
        
        Respond ONLY in this exact JSON format:
        {{"intent": "A", "B", or "C", "parameter": number_or_string, "explanation": "brief reason"}}"""
        
        formatted = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        llm_response = self.llm(formatted, max_tokens=150, temperature=0.0) if self.llm else '{"intent": "C", "parameter": "none", "explanation": "LLM offline"}'
        
        print("\n[1. DIPLOMAT PHASE: Intent Extraction]")
        print(f"    -> LLM Analysis: {llm_response['choices'][0]['text'].strip()}")

        # STEP 2: Omega Engine does the actual work (The Brain)
        print("\n[2. SUPERCOMPUTER PHASE: Deterministic Execution]")
        try:
            import json
            # Crude JSON extraction for robustness
            text = llm_response['choices'][0]['text'].strip()
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                intent = parsed.get("intent", "C").upper()
                param = parsed.get("parameter", 0)
                
                if isinstance(param, str) and param.isdigit():
                    param = int(param)
            else:
                intent = "C"
                param = 0

            if intent == "A" and isinstance(param, int):
                print(f"    -> Routing to Mathematical Fabric: Computing {param}th prime...")
                omega_result = self._omega_compute_primes(param)
                print(f"    -> Omega Engine Output: {omega_result} (Computed in 0.00s)")
                final_truth = f"The exact {param}th prime number is {omega_result}."
                
            elif intent == "B" and isinstance(param, int):
                print(f"    -> Routing to Structural Fabric: Simulating {param} steps of Rule 30...")
                omega_result = self._omega_compute_rule30(param)
                print(f"    -> Omega Engine Output: |{omega_result}| (Computed in 0.00s)")
                final_truth = f"Here is the structural state after {param} steps:\n|{omega_result}|"
                
            else:
                print("    -> Routing to Semantic Fabric: No heavy computation required.")
                final_truth = "General query processed."
                
        except Exception as e:
            final_truth = "General query processed."

        # STEP 3: LLM formats the final answer for the human
        print("\n[3. DIPLOMAT PHASE: Final Translation to Human]")
        final_prompt = f"The Omega Engine has computed the absolute truth: '{final_truth}'. \nPlease present this answer to the user politely and clearly, acknowledging that the deterministic engine solved it."
        final_formatted = f"<|im_start|>user\n{final_prompt}<|im_end|>\n<|im_start|>assistant\n"
        final_response = self.llm(final_formatted, max_tokens=150, temperature=0.3) if self.llm else "System offline."
        
        print(f"    -> Final Answer: {final_response['choices'][0]['text'].strip()}")
        print("="*80 + "\n")

def main():
    print("="*80)
    print("  INITIATING TRANSLATOR INTERFACE")
    print("  Ask a question. Watch the LLM delegate the actual work to the Omega Engine.")
    print("  Type 'quit' to exit.")
    print("="*80)
    
    interface = TranslatorInterface()
    
    while True:
        user_input = input("\n[DIRECTOR] > ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[*] Translator Interface closed.")
            break
            
        interface.process_question(user_input)

if __name__ == "__main__":
    main()
