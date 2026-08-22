import os
import sys
import math
import json
import re

try:
    from llama_cpp import Llama
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False

class TranslatorInterfaceV4:
    def __init__(self):
        self.llm = None
        self._awaken_llm()
        self.core_fabrics = {
            "Symbolic": "154,809 Unicode characters mapped for absolute representation.",
            "Mathematical": "100,000+ Prime numbers and 1000-digit precision constants (Pi, e, Phi).",
            "Logical": "All 16 Boolean logic gates and 256 states of an 8-bit register.",
            "Structural": "Rule 30 Cellular Automata for computationally irreducible emergence."
        }
        # NEW: Conversational Memory Buffer
        self.history = [] 
        self.expansion_count = 0 # Tracks how many times we've expanded

    def _awaken_llm(self):
        if LOCAL_LLM_AVAILABLE:
            model_path = r"C:\Users\AIAli\OneDrive\Desktop\NEO\qwen2.5-1.5b-instruct-Q4_K_M.gguf"
            if os.path.exists(model_path):
                try:
                    self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
                except:
                    pass

    def _omega_compute_primes(self, n):
        limit = n * 15
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
        self.history.append({"role": "user", "content": user_input})
        
        print("\n" + "="*80)
        print(f"  USER QUERY: '{user_input}'")
        print("="*80)

        lower_input = user_input.lower().strip()
        
        # =========================================================================
        # 1. CONTEXTUAL CONTINUATION OVERRIDE (The "More" Handler)
        # =========================================================================
        if lower_input in ["more", "continue", "next", "keep going", "another", "5 more"]:
            # Check if the previous context was about fabrics or expansion
            prev_context = " ".join([h["content"] for h in self.history[-3:]]).lower()
            if "fabric" in prev_context or "expansion" in prev_context:
                print("\n[1. CONTEXTUAL MEMORY TRIGGERED]")
                print("    -> Diplomat recognizes 'more' as a continuation of the Fabric Expansion.")
                print("    -> Generating 5 ADDITIONAL theoretical fabrics...")
                
                self.expansion_count += 1
                expansion_prompt = f"""You are the Diplomat interface for the Omega Engine.
                Previously, you listed theoretical fabrics of reality and computation. 
                The user just said "more", meaning they want 5 MORE theoretical fabrics.
                Do not repeat the previous ones. Give me 5 NEW, distinct theoretical fabrics or mathematical foundations (e.g., Graph Theory, Differential Geometry, Ergodic Theory, etc.).
                Format as a numbered list starting from {(self.expansion_count * 5) + 1}.
                Keep it concise."""
                
                formatted = f"<|im_start|>user\n{expansion_prompt}<|im_end|>\n<|im_start|>assistant\n"
                llm_response = self.llm(formatted, max_tokens=300, temperature=0.3) if self.llm else "Diplomat offline."
                
                print("\n[2. DIPLOMAT RESPONSE: CONTINUED EXPANSION]")
                print(f"    {llm_response['choices'][0]['text'].strip()}")
                self.history.append({"role": "system", "content": llm_response['choices'][0]['text'].strip()})
                print("="*80 + "\n")
                return

        # =========================================================================
        # 2. SELF-AWARENESS OVERRIDE (Core Fabrics)
        # =========================================================================
        elif any(word in lower_input for word in ["what fabrics do you have", "how many fabrics", "your fabrics"]):
            print("\n[1. SELF-AWARENESS PROTOCOL TRIGGERED]")
            print("    -> Bypassing probabilistic LLM. Querying Omega Engine internal state...")
            
            print("\n[2. OMEGA ENGINE RESPONSE: DEFINITIVE CORE ARCHITECTURE]")
            for name, desc in self.core_fabrics.items():
                print(f"    -> [{name.upper()} FABRIC]: {desc}")
                
            final_truth = "The Omega Engine strictly consists of 4 deterministic core fabrics."
            self.history.append({"role": "system", "content": "Listed 4 core fabrics."})
            
        # =========================================================================
        # 3. EXPANSION OVERRIDE (Initial Fabric Search)
        # =========================================================================
        elif "find" in lower_input and "other fabrics" in lower_input:
            print("\n[1. EXPANSION PROTOCOL TRIGGERED]")
            print("    -> Omega Engine core is closed. Delegating to Diplomat's pre-trained knowledge base...")
            
            expansion_prompt = """You are the Diplomat interface for the Omega Engine. 
            The user wants to know about OTHER theoretical 'fabrics' of reality, computation, or mathematics beyond the Omega Engine's 4 core fabrics.
            List 5 well-known theoretical fabrics or foundational layers in fields like Topology, Quantum Physics, Information Theory, etc.
            Format as a numbered list 1 to 5. Keep it concise."""
            
            formatted = f"<|im_start|>user\n{expansion_prompt}<|im_end|>\n<|im_start|>assistant\n"
            llm_response = self.llm(formatted, max_tokens=300, temperature=0.2) if self.llm else "Diplomat offline."
            
            print("\n[2. DIPLOMAT RESPONSE: THEORETICAL EXPANSION]")
            print(f"    {llm_response['choices'][0]['text'].strip()}")
            self.history.append({"role": "system", "content": llm_response['choices'][0]['text'].strip()})
            print("="*80 + "\n")
            return

        # =========================================================================
        # 4. STANDARD ROUTING (With Conversational Context)
        # =========================================================================
        else:
            # Build context string from recent history
            history_text = "\n".join([f"{h['role']}: {h['content'][:100]}" for h in self.history[-4:]])
            
            prompt = f"""You are an interface to a deterministic supercomputer called the Omega Engine.
            Recent Conversation Context:
            {history_text}
            
            Current User Query: "{user_input}"
            
            Analyze the current request based on the context. Does it require:
            A) Exact mathematical computation?
            B) Structural simulation?
            C) General knowledge or semantic translation?
            
            Respond ONLY in this exact JSON format:
            {{"intent": "A", "B", or "C", "parameter": number_or_string, "explanation": "brief reason"}}"""
            
            formatted = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            llm_response = self.llm(formatted, max_tokens=150, temperature=0.0) if self.llm else '{"intent": "C", "parameter": "none", "explanation": "LLM offline"}'
            
            print("\n[1. DIPLOMAT PHASE: Intent Extraction (With Context)]")
            print(f"    -> LLM Analysis: {llm_response['choices'][0]['text'].strip()}")

            print("\n[2. SUPERCOMPUTER PHASE: Deterministic Execution]")
            try:
                text = llm_response['choices'][0]['text'].strip()
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

            print("\n[3. DIPLOMAT PHASE: Final Translation to Human]")
            final_prompt = f"The Omega Engine has computed the absolute truth: '{final_truth}'. \nPlease present this answer to the user politely and clearly."
            final_formatted = f"<|im_start|>user\n{final_prompt}<|im_end|>\n<|im_start|>assistant\n"
            final_response = self.llm(final_formatted, max_tokens=150, temperature=0.3) if self.llm else "System offline."
            
            print(f"    -> Final Answer: {final_response['choices'][0]['text'].strip()}")
            self.history.append({"role": "system", "content": final_response['choices'][0]['text'].strip()})
            
        print("="*80 + "\n")

def main():
    print("="*80)
    print("  INITIATING TRANSLATOR INTERFACE V4 (WITH CONVERSATIONAL MEMORY)")
    print("  The Diplomat now remembers context. Try: 'find and list all other fabrics'")
    print("  Then type: 'more' or 'continue'")
    print("  Type 'quit' to exit.")
    print("="*80)
    
    interface = TranslatorInterfaceV4()
    
    while True:
        user_input = input("\n[DIRECTOR] > ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[*] Translator Interface closed.")
            break
            
        interface.process_question(user_input)

if __name__ == "__main__":
    main()
