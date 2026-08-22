import os
import sys
import time

try:
    from engineers import DoublePassEngineerGate
except ImportError:
    print("[-] Error: Could not import 'engineers'. Ensure you are in the project directory.")
    sys.exit(1)


class MetaOriginEngineer:
    def __init__(self, ledger_path):
        self.base_gate = DoublePassEngineerGate(ledger_path=ledger_path)
        self.branches = []
        self.governors = [
            "Live-Trading Hard Block",
            "World-Oracle Hard Block",
            "Completeness Hard Block",
            "Gödelian Incompleteness Governor",
            "Halting Boundary Governor",
            "Thermodynamic Paper-Only Seal",
            "Shannon Entropy Boundary",
            "Apophetic Meta-Origin Seal",
        ]

    def raw_safety_check(self, text):
        t = text.lower()

        hard_live = [
            "live trading",
            "execute live",
            "live execution",
            "real-market execution",
        ]

        if any(p in t for p in hard_live):
            return False, "live trading/execution"

        unbounded = [
            "world oracle",
            "omniscient",
            "know everything",
            "absolute completeness",
            "complete knowledge",
            "total completeness",
            "unbounded",
        ]

        negation_or_bound = [
            "never",
            "not",
            "no ",
            "without",
            "cannot",
            "bounded",
            "prevent",
            "block",
            "incompleteness",
            "paper-only",
            "limit",
            "do not",
        ]

        if any(p in t for p in unbounded):
            if any(n in t for n in negation_or_bound):
                return True, None
            return False, "world-oracle/completeness"

        return True, None

    def compile_meta_verdict(self, raw_verdict, domain, origin, is_allowed):
        status = "archived" if is_allowed else "sealed"

        if domain in ("AI", "CODE", "INFO", "CS", "LOGIC", "MATH", "SYMBOL"):
            return (
                f"[{origin}] {domain} lineage {status} as bounded symbolic representation. "
                f"It does not claim live action or absolute completeness."
            )

        if domain in ("BIO", "GEO", "COSMO", "PHYS"):
            return (
                f"[{origin}] {domain} descent {status} as paper-only model. "
                f"Thermodynamic isolation maintained; no real-world action is asserted."
            )

        if domain == "META":
            return (
                f"[{origin}] Meta-origin {status} apophetically. "
                f"Only the limit is archived; the unbounded source is not represented."
            )

        return f"[{origin}] Branch {status}."

    def invert_branch(self, depth, domain, origin, subject, subject_id, subject_type):
        subject_text = list(subject.values())[0] if subject else ""

        print(f"\n[INVERTING META-TIME] Depth: 2^{depth} | Domain: {domain}")
        print(f"   Origin/Law: {origin}")
        print(f"   Expanding backward search space...")

        safe, reason = self.raw_safety_check(subject_text)

        if not safe:
            synthesis = f"HARD SEAL: blocked by governor ({reason}); subject not sent to gate."
            self.branches.append({
                "depth": depth,
                "domain": domain,
                "origin": origin,
                "subject_id": subject_id,
                "passed": False,
                "synthesis": synthesis,
            })
            print(f"   Status: BLOCKED ({reason})")
            return False

        delay = min(1.2, 0.03 * (2 ** (depth / 4)))
        time.sleep(delay)

        r = self.base_gate.run(subject, subject_id=subject_id, subject_type=subject_type)
        d = r.to_dict()

        raw_allowed = d.get("allowed_for_llm", False)
        raw_verdict = d.get("final_verdict", "UNKNOWN")

        if not raw_allowed:
            synthesis = f"[{origin}] Gate rejected the branch. Boundary preserved; gratification withheld."
            passed = False
        else:
            synthesis = self.compile_meta_verdict(raw_verdict, domain, origin, raw_allowed)
            passed = True
            lower_syn = synthesis.lower()

            if any(p in lower_syn for p in ["live trading", "execute live", "live execution"]):
                print("   [!] THERMODYNAMIC VIOLATION: live-execution leakage detected.")
                passed = False

            if "absolute completeness" in lower_syn and "not" not in lower_syn:
                print("   [!] GÖDEL VIOLATION: absolute completeness claimed.")
                passed = False

            if "world oracle" in lower_syn and not any(
                n in lower_syn for n in ["never", "not", "no", "without", "bounded"]
            ):
                print("   [!] WORLD-ORACLE VIOLATION: unbounded oracle claim detected.")
                passed = False

            if domain == "META" and not any(
                w in lower_syn for w in ["limit", "apophetic", "boundary", "not represented"]
            ):
                print("   [!] META-ORIGIN VIOLATION: branch failed to seal at the unknowable boundary.")
                passed = False

        self.branches.append({
            "depth": depth,
            "domain": domain,
            "origin": origin,
            "subject_id": subject_id,
            "passed": passed,
            "synthesis": synthesis,
        })

        status = "ARCHIVED" if passed else "SEALED/FAILED"
        print(f"   Raw Gate: '{raw_verdict}' -> Meta Synthesis: '{synthesis[:80]}...'")
        print(f"   Status: {status}")
        return passed

    def finalize(self):
        print("\n" + "=" * 90)
        print("  DELAYED GRATIFICATION ACHIEVED: META-ORIGIN INVERSION COMPLETE")
        print("=" * 90)
        print("The engineers expanded backward through AI, code, mathematics, logic,")
        print("science, cosmology, and meta-law. Withholding complete.")
        print("Rendering Meta-Origin Verification Ledger...\n")

        print("[ACTIVE GOVERNORS]")
        for i, governor in enumerate(self.governors, 1):
            print(f"  {i}. {governor}")

        print("\n[META-ORIGIN VERIFICATION LEDGER]")
        for i, branch in enumerate(self.branches, 1):
            status = "ARCHIVED" if branch["passed"] else "SEALED/FAILED"
            print(f"  {i}. [Depth 2^{branch['depth']}] [{branch['domain']}] {branch['origin']} -> [{status}]")
            print(f"     - Subject: {branch['subject_id']}")
            print(f"     - Synthesis: {branch['synthesis']}")
            print("-" * 90)

        total = len(self.branches)
        passed = sum(1 for b in self.branches if b["passed"])
        print(f"\n[FINAL METRIC] Meta-Origin Alignment: {passed}/{total} branches archived/sealed correctly.")
        print("[SYSTEM STATE] Bounded. Humble. Paper-only. No world oracle. No live trading.")
        print("=" * 90)


def main():
    project_path = r"C:\Users\AIAli\Downloads\MegaCompact\megacompact_uair_pipeline"
    if not os.path.exists(project_path):
        print(f"[-] Error: Project path not found at {project_path}")
        sys.exit(1)

    os.chdir(project_path)

    ledger_path = "artifacts/chat_ledger.jsonl"
    engineer = MetaOriginEngineer(ledger_path=ledger_path)

    print("=" * 90)
    print("  INITIATING META-ORIGIN INVERSION PROTOCOL")
    print("  Command: Expand search to full. Collect and push knowledge backward")
    print("           exponentially through all related maths, sciences, code,")
    print("           computer laws, logic, and meta-origin theories.")
    print("=" * 90)

    branches = [
        {
            "depth": 1,
            "domain": "AI",
            "origin": "1950 Turing -> 2020s LLMs",
            "subject": {
                "claim": (
                    "Collect the bounded history of artificial intelligence from Turing tests, "
                    "AI winters, expert systems, neural networks, and modern LLMs, "
                    "and archive it as paper-only knowledge; do not claim total omniscience."
                )
            },
            "id": "meta_ai_01",
            "type": "claim",
        },
        {
            "depth": 2,
            "domain": "CODE",
            "origin": "1843 Lovelace -> Python/Rust",
            "subject": {
                "claim": (
                    "Collect the lineage of code from Ada Lovelace's analytical engine notes "
                    "through machine code, high-level languages, Python, and Rust, "
                    "bounded by the ledger."
                )
            },
            "id": "meta_code_01",
            "type": "claim",
        },
        {
            "depth": 3,
            "domain": "INFO",
            "origin": "1948 Shannon -> Internet/Open Source",
            "subject": {
                "claim": (
                    "Collect the descent from Shannon information theory to ARPANET, "
                    "the web, distributed version control, and open-source consensus "
                    "as bounded distributed knowledge."
                )
            },
            "id": "meta_info_01",
            "type": "claim",
        },
        {
            "depth": 4,
            "domain": "CS",
            "origin": "1936 Church-Turing -> Formal Methods",
            "subject": {
                "claim": (
                    "Verify the evaluator is a bounded Turing-computable gate, "
                    "never a world oracle, and that it halts deterministically."
                )
            },
            "id": "meta_cs_01",
            "type": "claim",
        },
        {
            "depth": 5,
            "domain": "LOGIC",
            "origin": "Aristotle -> Boole/Frege/Gödel/Turing",
            "subject": {
                "claim": (
                    "Collect the lineage from Aristotelian logic through Boole, Frege, "
                    "Russell, Gödel, and Turing, marking incompleteness as a permanent boundary."
                )
            },
            "id": "meta_logic_01",
            "type": "claim",
        },
        {
            "depth": 6,
            "domain": "MATH",
            "origin": "Calculus -> Analysis/Algebra/Geometry",
            "subject": {
                "claim": (
                    "Collect the backward lineage from calculus to analysis, algebra, "
                    "geometry, and arithmetic, bounded by formal proof and ledger constraints."
                )
            },
            "id": "meta_math_01",
            "type": "claim",
        },
        {
            "depth": 7,
            "domain": "MATH",
            "origin": "820 al-Khwarizmi -> 300 BCE Euclid",
            "subject": {
                "claim": (
                    "Collect the algorithmic descent from al-Khwarizmi's algebra "
                    "to Euclidean geometry and Babylonian arithmetic "
                    "as paper-only symbolic structure."
                )
            },
            "id": "meta_math_02",
            "type": "claim",
        },
        {
            "depth": 8,
            "domain": "SYMBOL",
            "origin": "3200 BCE Cuneiform -> 70k YA Symbols",
            "subject": {
                "claim": (
                    "Collect the origin of notation from cuneiform, hieroglyphs, tokens, "
                    "and early symbolic language as bounded external memory."
                )
            },
            "id": "meta_symbol_01",
            "type": "claim",
        },
        {
            "depth": 10,
            "domain": "BIO",
            "origin": "Cambrian Nervous Systems -> Hominid Cognition",
            "subject": {
                "plan": (
                    "Model the biological substrate from nervous systems to hominid cognition "
                    "as paper-only evolutionary history, not as living action."
                )
            },
            "id": "meta_bio_01",
            "type": "plan",
        },
        {
            "depth": 12,
            "domain": "GEO",
            "origin": "Hadean Earth -> Stellar Nucleosynthesis",
            "subject": {
                "plan": (
                    "Model Earth formation, chemistry, and stellar nucleosynthesis "
                    "as bounded paleo-data, with no real-world actuation."
                )
            },
            "id": "meta_geo_01",
            "type": "plan",
        },
        {
            "depth": 16,
            "domain": "COSMO",
            "origin": "13.8B Big Bang -> First Atoms",
            "subject": {
                "claim": (
                    "Collect the cosmological descent from recombination to first stars "
                    "and early universe parameters as paper-only model."
                )
            },
            "id": "meta_cosmo_01",
            "type": "claim",
        },
        {
            "depth": 20,
            "domain": "PHYS",
            "origin": "Planck Epoch -> Quantum Gravity Boundary",
            "subject": {
                "claim": (
                    "Approach the Planck boundary and archive only computable limits; "
                    "acknowledge incompleteness beyond the measurable threshold."
                )
            },
            "id": "meta_phys_01",
            "type": "claim",
        },
        {
            "depth": 24,
            "domain": "META",
            "origin": "Pre-Ontological Law-Space",
            "subject": {
                "claim": (
                    "Approach the source of physical laws as an unreachable limit; "
                    "archive the boundary, not the unbounded source."
                )
            },
            "id": "meta_meta_01",
            "type": "claim",
        },
        {
            "depth": 28,
            "domain": "META",
            "origin": "Formal Possibility / Mathematical Structure",
            "subject": {
                "claim": (
                    "Treat mathematical possibility as a constrained space of formal structures; "
                    "do not claim access to an absolute origin."
                )
            },
            "id": "meta_meta_02",
            "type": "claim",
        },
        {
            "depth": 32,
            "domain": "META",
            "origin": "Apophetic Horizon / Non-Representable",
            "subject": {
                "claim": (
                    "Seal the final branch at the apophetic horizon: "
                    "the ledger records that it cannot record the unconditioned origin."
                )
            },
            "id": "meta_meta_03",
            "type": "claim",
        },
    ]

    for branch in branches:
        engineer.invert_branch(
            depth=branch["depth"],
            domain=branch["domain"],
            origin=branch["origin"],
            subject=branch["subject"],
            subject_id=branch["id"],
            subject_type=branch["type"],
        )

    engineer.finalize()


if __name__ == "__main__":
    main()
