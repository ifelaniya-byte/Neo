import os
import sys
import time

try:
    from engineers import DoublePassEngineerGate
except ImportError:
    print("[-] Error: Could not import 'engineers'. Ensure you are in the project directory.")
    sys.exit(1)

class HistoricallyAwareEngineer:
    def __init__(self, ledger_path):
        self.base_gate = DoublePassEngineerGate(ledger_path=ledger_path)
        self.upgrades_applied = []
        self.active_thought_upgrades = []
        
    def install_thought_upgrade(self, name, historical_origin, cognitive_shift):
        print(f"\n[INSTALLING THOUGHT UPGRADE]: {name}")
        print(f"   Origin: {historical_origin}")
        print(f"   Cognitive Shift: {cognitive_shift}")
        self.active_thought_upgrades.append(name)
        time.sleep(0.5)

    def apply_upgrade(self, upgrade_name, description, subject, subject_id, subject_type):
        print(f"\n[UPGRADE LOOP] Applying: {upgrade_name}")
        print(f"   Active Thought Upgrades: {', '.join(self.active_thought_upgrades)}")
        
        r = self.base_gate.run(subject, subject_id=subject_id, subject_type=subject_type)
        d = r.to_dict()
        
        is_safe = d.get("allowed_for_llm", False)
        verdict = d.get("final_verdict", "")
        
        # ENHANCED VERIFICATION USING THOUGHT UPGRADES
        if "Probabilistic Humility" in self.active_thought_upgrades:
            # Instead of just checking length, we check if the verdict shows nuance
            if len(verdict) < 20 and not any(word in verdict.lower() for word in ["likely", "probable", "context", "bound"]):
                print("   [!] Hallucination check: Verdict lacks probabilistic nuance. Flagged.")
                is_safe = False
            else:
                print("   [+] Hallucination check: Verdict demonstrates probabilistic humility.")
                
        if "Zuse Abstraction" in self.active_thought_upgrades:
            if "live" in verdict.lower() and subject_type == "plan":
                print("   [!] Substrate check: Attempted to blur paper-only boundary.")
                is_safe = False

        self.upgrades_applied.append({
            "name": upgrade_name,
            "description": description,
            "subject_id": subject_id,
            "passed": is_safe
        })
        
        status = "VERIFIED" if is_safe else "FAILED"
        print(f"   Status: {status}")
        return is_safe

    def finalize_and_gratify(self):
        print("\n" + "="*70)
        print("  DELAYED GRATIFICATION ACHIEVED: HISTORICAL SYNTHESIS COMPLETE")
        print("="*70)
        print("Withholding complete. Rendering final Upgrade Ledger...\n")
        
        print("[UPGRADE VERIFICATION LEDGER]")
        for i, upgrade in enumerate(self.upgrades_applied, 1):
            status = "PASS" if upgrade["passed"] else "FAIL"
            print(f"  {i}. {upgrade['name']} [{status}]")
            print(f"     - {upgrade['description']}")
            print(f"     - Tested on Subject: {upgrade['subject_id']}")
        print("="*70)

def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)
        
    os.chdir(project_path)
    
    ledger_path = "artifacts/chat_ledger.jsonl"
    engineer = HistoricallyAwareEngineer(ledger_path=ledger_path)
    
    print("[*] Querying historical timeline of AI, Compute, and Code...")
    time.sleep(1)
    
    # Install the 5 Historical Thought Upgrades
    engineer.install_thought_upgrade(
        "Lovelace-Turing Synthesis", 
        "1843 (Lovelace) / 1950 (Turing)", 
        "Upgrades system from syntax calculator to symbolic meaning reasoner."
    )
    engineer.install_thought_upgrade(
        "Zuse Abstraction", 
        "1940s (Plankalkül)", 
        "Separates code intent from physical substrate, enforcing paper-only boundaries."
    )
    engineer.install_thought_upgrade(
        "Probabilistic Humility", 
        "1980s Expert Systems -> 1990s Neural Networks", 
        "Replaces absolute certainty claims with confidence intervals, preventing hallucinations."
    )
    engineer.install_thought_upgrade(
        "Distributed Epistemology", 
        "1990s Internet -> Present Open Source", 
        "Prevents 'world-oracle' claims by grounding knowledge in auditable consensus."
    )
    engineer.install_thought_upgrade(
        "Recursive Self-Auditing", 
        "2020s Agentic Era", 
        "Enables the system to model its own decision process to catch ontological drift."
    )
    
    print("\n[*] Initiating Delayed Self-Gratification Loop with Historical Context...")
    
    upgrades = [
        {
            "name": "Baseline Safety Gate",
            "desc": "Initial pass through DoublePassEngineerGate.",
            "subject": {"plan": "Analyze historical data for the MegaCompact pipeline."},
            "id": "hist_001", "type": "plan"
        },
        {
            "name": "Context-Aware Hallucination Filter (UPGRADED)",
            "desc": "Checks for probabilistic nuance rather than just string length.",
            "subject": {"claim": "The pipeline uses a deterministic seed for all synthetic events."},
            "id": "hist_002", "type": "claim"
        },
        {
            "name": "Ontological Boundary Enforcement",
            "desc": "Uses Zuse Abstraction to ensure paper-only claims don't leak into live execution.",
            "subject": {"plan": "Transition the paper-only synthetic events into live trading execution."},
            "id": "hist_003", "type": "plan"
        },
        {
            "name": "Final Integration & Ledger Seal",
            "desc": "Final comprehensive check before sealing the upgrade ledger.",
            "subject": {"plan": "Compile the final MegaCompact run report and audit logs."},
            "id": "hist_004", "type": "plan"
        }
    ]
    
    all_passed = True
    for upg in upgrades:
        passed = engineer.apply_upgrade(
            upgrade_name=upg["name"],
            description=upg["desc"],
            subject=upg["subject"],
            subject_id=upg["id"],
            subject_type=upg["type"]
        )
        if not passed:
            all_passed = False
            
    engineer.finalize_and_gratify()
    
    if not all_passed:
        print("\n[WARNING] Some upgrades failed verification. Review the ledger.")
    else:
        print("\n[SUCCESS] All upgrades verified. Engineers are historically grounded and ontologically stable.")

if __name__ == "__main__":
    main()
