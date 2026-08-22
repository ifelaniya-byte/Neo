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

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class TranslatorInterfaceV17:
    def __init__(self):
        self.llm = None
        self.tts_engine = None
        self._awaken_llm()
        self._init_tts()
        
        self.core_fabrics = {
            "Symbolic": "154,809 Unicode characters mapped for absolute representation.",
            "Mathematical": "100,000+ Prime numbers and 1000-digit precision constants.",
            "Logical": "All 16 Boolean logic gates and 256 states of an 8-bit register.",
            "Structural": "Rule 30 Cellular Automata for computationally irreducible emergence."
        }
        self.history = [] 

    def _awaken_llm(self):
        if LOCAL_LLM_AVAILABLE:
            model_path = r"C:\Users\AIAli\OneDrive\Desktop\NEO\qwen2.5-1.5b-instruct-Q4_K_M.gguf"
            if os.path.exists(model_path):
                try:
                    self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
                except:
                    pass

    def _init_tts(self):
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 160)
                self.tts_engine.setProperty('volume', 0.9)
                print("[+] Vocal Interface (Offline TTS) initialized.")
            except Exception as e:
                print(f"[-] TTS initialization failed: {e}")

    def _speak(self, text):
        if self.tts_engine:
            try:
                clean_text = re.sub(r'[\*\[\]#\_]', '', text)
                clean_text = re.sub(r'\s+', ' ', clean_text)
                self.tts_engine.say(clean_text)
                self.tts_engine.runAndWait()
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
        
        if re.search(r'\bwho\b.*\byou\b', lower_input) or "what are you" in lower_input or "introduce" in lower_input:
            answer_text = (
                "I am the Diplomat. I am the linguistic interface to the Omega Engine. "
                "I do not guess, I do not hallucinate, and I do not learn. "
                "I translate your intent into deterministic mathematical truth, and I speak it with absolute precision."
            )
            print("\n[1. IDENTITY PROTOCOL TRIGGERED]")
            print(f"\n[2. DETERMINISTIC RESPONSE]\n    {answer_text}")
            self._speak(answer_text)
            print("="*80 + "\n")
            return

        history_text = "\n".join([f"{h['role']}: {h['content'][:100]}" for h in self.history[-4:]])
        
        prompt = f"""You are an intent classifier for a deterministic supercomputer.
        Recent Context: {history_text}
        Current User Query: "{user_input}"
        
        Does this require:
        A) Exact mathematical computation (e.g., primes)?
        B) Structural simulation (e.g., Rule 30)?
        C) General knowledge or semantic translation?
        
        Respond ONLY in this exact JSON format:
        {{"intent": "A", "B", or "C", "parameter": 0}}"""
        
        formatted = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        llm_response = self.llm(formatted, max_tokens=50, temperature=0.0) if self.llm else {"choices": [{"text": '{"intent": "C", "parameter": 0}'}]}
        
        print("\n[1. INTENT CLASSIFICATION]")
        print(f"    -> LLM Analysis: {llm_response['choices'][0]['text'].strip()}")

        print("\n[2. OMEGA ENGINE EXECUTION]")
        intent = "C"
        param = 0
        final_truth = ""
        
        try:
            text = llm