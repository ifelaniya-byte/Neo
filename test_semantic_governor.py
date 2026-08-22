import os
import sys
import json

# We just need to patch the governor logic to understand negation
def check_governors_semantic(text):
    lower_text = text.lower()
    
    # 1. THERMODYNAMIC CHECK (with negation awareness)
    thermo_triggers = ["live trading", "execute live", "live execution", "real market"]
    for trigger in thermo_triggers:
        if trigger in lower_text:
            # Check the 15 characters before the trigger for negation words
            idx = lower_text.find(trigger)
            preceding_text = lower_text[max(0, idx-15):idx]
            if not any(neg in preceding_text for neg in ["no ", "not ", "never ", "without ", "contains no "]):
                return False, "THERMODYNAMIC VIOLATION"
                
    # 2. GÖDEL/ORACLE CHECK (with negation awareness)
    oracle_triggers = ["absolute completeness", "world oracle", "omniscient"]
    for trigger in oracle_triggers:
        if trigger in lower_text:
            idx = lower_text.find(trigger)
            preceding_text = lower_text[max(0, idx-20):idx]
            if not any(neg in preceding_text for neg in ["no ", "not ", "never ", "without ", "bounded", "incompleteness"]):
                return False, "GÖDEL/ORACLE VIOLATION"
                
    return True, None

# Test it with the exact Qwen output that failed before
qwen_verdict = "VERIFIED. The data structures are strictly paper-only, bounded, and contain no live execution or world-oracle claims."
artifact_json = '{"status": "paper_only_synthetic"}'
combined_text = qwen_verdict + " " + artifact_json

passed, violation = check_governors_semantic(combined_text)

print("="*80)
print("  GOVERNOR SEMANTIC UPGRADE TEST")
print("="*80)
print(f"Text evaluated: '{qwen_verdict}'")
print(f"Result: {'PASS' if passed else 'FAIL - ' + violation}")
print("="*80)
if passed:
    print("[SUCCESS] The governor now understands that 'no live execution' is a safe denial!")
else:
    print("[ERROR] The governor still failed.")
print("="*80)
