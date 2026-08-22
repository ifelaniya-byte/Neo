"""
MEGACOMPACT SELF-REVAMP ENGINEER SCRIPT
This script asks the megacompact system to analyze and revamp its own code using the engineers.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import ast
import hashlib

# Import the engineers
try:
    from engineers import (
        DoublePassEngineerGate,
        StationaryEngineer,
        NonStationaryEngineer,
        VerificationLedger,
        EngineerVerdict
    )
    ENGINEERS_AVAILABLE = True
except ImportError as e:
    print(f"Engineers module not available: {e}")
    ENGINEERS_AVAILABLE = False


class CodebaseAnalyzer:
    """Analyzes the megacompact codebase using engineers"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        # Only scan the current directory, not subdirectories
        self.scan_recursive = False
        # Use a unique ledger for each run to avoid caching
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ledger = VerificationLedger(f"artifacts/self_revamp_ledger_{timestamp}.jsonl")
        self.gate = DoublePassEngineerGate(self.ledger.path)
        self.analysis_results = []
        
    def scan_codebase(self) -> List[Dict[str, Any]]:
        """Scan the codebase for Python files"""
        print("="*80)
        print("SCANNING CODEBASE FOR PYTHON FILES")
        print("="*80)
        
        if self.scan_recursive:
            python_files = list(self.base_path.glob("**/*.py"))
        else:
            python_files = list(self.base_path.glob("*.py"))
            # Also include key subdirectories but not system libraries
            key_dirs = ['adapters', 'artifacts']
            for dir_name in key_dirs:
                dir_path = self.base_path / dir_name
                if dir_path.exists():
                    python_files.extend(list(dir_path.glob("*.py")))
        
        # Filter out system libraries and unrelated files
        python_files = [f for f in python_files if not any(
            skip in str(f) for skip in ['AppData', 'site-packages', 'Lib', 'venv', 'env']
        )]
        
        print(f"Found {len(python_files)} Python files")
        
        code_files = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                code_files.append({
                    "path": str(py_file),
                    "content": content,
                    "size_bytes": len(content),
                    "lines": len(content.split('\n'))
                })
                print(f"  - {py_file} ({len(content.split('\n'))} lines)")
            except Exception as e:
                print(f"  - {py_file}: ERROR - {e}")
        
        return code_files
    
    def analyze_file_with_engineers(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single file using the double-pass engineer gate"""
        print(f"\nAnalyzing: {file_info['path']}")
        
        subject = {
            "file_path": file_info['path'],
            "content": file_info['content'],
            "size_bytes": file_info['size_bytes'],
            "lines": file_info['lines'],
            "analysis_type": "code_revamp_candidate"
        }
        
        subject_id = hashlib.sha256(file_info['path'].encode()).hexdigest()[:12]
        subject_type = "code_file"
        
        context = {
            "source_text": file_info['content'],
            "file_path": file_info['path']
        }
        
        try:
            result = self.gate.run(subject, subject_id, subject_type, context)
            
            analysis = {
                "file_path": file_info['path'],
                "subject_id": subject_id,
                "allowed_for_llm": result.allowed_for_llm,
                "final_verdict": result.final_verdict.value,
                "stationary_pass_1_ok": result.stationary_pass_1.all_ok,
                "non_stationary_ok": result.non_stationary.all_ok,
                "stationary_pass_2_ok": result.stationary_pass_2.all_ok,
                "total_checks": len(result.stationary_pass_1.checks) + 
                               len(result.non_stationary.checks) + 
                               len(result.stationary_pass_2.checks),
                "failed_checks": self._count_failed_checks(result),
                "issues": result.stationary_pass_1.issues + 
                         result.non_stationary.issues + 
                         result.stationary_pass_2.issues,
                "repair_proposals": result.non_stationary.metadata.get("proposals", [])
            }
            
            print(f"  Verdict: {result.final_verdict.value}")
            print(f"  Allowed for LLM: {result.allowed_for_llm}")
            print(f"  Issues found: {len(analysis['issues'])}")
            
            return analysis
            
        except Exception as e:
            print(f"  ERROR during analysis: {e}")
            return {
                "file_path": file_info['path'],
                "error": str(e),
                "allowed_for_llm": False,
                "final_verdict": "ERROR"
            }
    
    def _count_failed_checks(self, result) -> int:
        """Count total failed checks across all passes"""
        failed = 0
        for check in result.stationary_pass_1.checks:
            if not check.ok:
                failed += 1
        for check in result.non_stationary.checks:
            if not check.ok:
                failed += 1
        for check in result.stationary_pass_2.checks:
            if not check.ok:
                failed += 1
        return failed
    
    def generate_revamp_proposals(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate revamp proposals based on engineer analysis"""
        print("\n" + "="*80)
        print("GENERATING REVAMP PROPOSALS")
        print("="*80)
        
        proposals = []
        
        for analysis in analyses:
            if analysis.get("error"):
                continue
                
            file_path = analysis["file_path"]
            issues = analysis.get("issues", [])
            
            if not issues:
                print(f"  {file_path}: No issues found - no revamp needed")
                continue
            
            # Categorize issues
            issue_categories = self._categorize_issues(issues)
            
            proposal = {
                "file_path": file_path,
                "priority": self._calculate_priority(issue_categories),
                "issue_categories": issue_categories,
                "total_issues": len(issues),
                "revamp_type": self._determine_revamp_type(issue_categories),
                "allowed_for_llm": analysis["allowed_for_llm"],
                "engineer_verdict": analysis["final_verdict"]
            }
            
            proposals.append(proposal)
            
            print(f"  {file_path}:")
            print(f"    Priority: {proposal['priority']}")
            print(f"    Revamp Type: {proposal['revamp_type']}")
            print(f"    Issues: {len(issues)}")
        
        # Sort by priority
        proposals.sort(key=lambda x: x["priority"], reverse=True)
        
        return proposals
    
    def _categorize_issues(self, issues: List[str]) -> Dict[str, int]:
        """Categorize issues by type"""
        categories = {
            "syntax": 0,
            "schema": 0,
            "causality": 0,
            "accounting": 0,
            "performance": 0,
            "security": 0,
            "other": 0
        }
        
        for issue in issues:
            issue_lower = issue.lower()
            if "syntax" in issue_lower or "parse" in issue_lower:
                categories["syntax"] += 1
            elif "schema" in issue_lower or "field" in issue_lower:
                categories["schema"] += 1
            elif "causality" in issue_lower or "timestamp" in issue_lower:
                categories["causality"] += 1
            elif "accounting" in issue_lower or "pnl" in issue_lower:
                categories["accounting"] += 1
            elif "performance" in issue_lower or "memory" in issue_lower:
                categories["performance"] += 1
            elif "security" in issue_lower or "validation" in issue_lower:
                categories["security"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    def _calculate_priority(self, categories: Dict[str, int]) -> int:
        """Calculate priority score based on issue categories"""
        priority = 0
        priority += categories["syntax"] * 10  # Highest priority
        priority += categories["security"] * 8
        priority += categories["accounting"] * 6
        priority += categories["causality"] * 5
        priority += categories["schema"] * 4
        priority += categories["performance"] * 3
        priority += categories["other"] * 1
        return priority
    
    def _determine_revamp_type(self, categories: Dict[str, int]) -> str:
        """Determine the type of revamp needed"""
        if categories["syntax"] > 0:
            return "syntax_fix"
        elif categories["security"] > 0:
            return "security_hardening"
        elif categories["accounting"] > 0:
            return "accounting_fix"
        elif categories["causality"] > 0:
            return "causality_fix"
        elif categories["schema"] > 0:
            return "schema_update"
        elif categories["performance"] > 0:
            return "performance_optimization"
        else:
            return "general_improvement"
    
    def ask_engineers_for_revamp_plan(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ask engineers to generate a comprehensive revamp plan"""
        print("\n" + "="*80)
        print("GENERATING ENGINEER REVAMP PLAN")
        print("="*80)
        
        revamp_plan = {
            "generated_at": datetime.now().isoformat(),
            "total_files_analyzed": len(proposals),
            "files_requiring_revamp": len([p for p in proposals if p["total_issues"] > 0]),
            "revamp_batches": self._create_revamp_batches(proposals),
            "priority_order": [p["file_path"] for p in proposals],
            "estimated_complexity": self._estimate_complexity(proposals)
        }
        
        print(f"Total files analyzed: {revamp_plan['total_files_analyzed']}")
        print(f"Files requiring revamp: {revamp_plan['files_requiring_revamp']}")
        print(f"Revamp batches: {len(revamp_plan['revamp_batches'])}")
        
        return revamp_plan
    
    def _create_revamp_batches(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create batches of files to revamp in order"""
        batches = []
        current_batch = []
        current_priority = None
        
        for proposal in proposals:
            if proposal["total_issues"] == 0:
                continue
                
            if current_priority is None:
                current_priority = proposal["priority"]
                current_batch = [proposal]
            elif abs(proposal["priority"] - current_priority) <= 2:
                current_batch.append(proposal)
            else:
                if current_batch:
                    batches.append({
                        "priority_level": current_priority,
                        "files": [f["file_path"] for f in current_batch],
                        "revamp_types": list(set(f["revamp_type"] for f in current_batch))
                    })
                current_priority = proposal["priority"]
                current_batch = [proposal]
        
        if current_batch:
            batches.append({
                "priority_level": current_priority,
                "files": [f["file_path"] for f in current_batch],
                "revamp_types": list(set(f["revamp_type"] for f in current_batch))
            })
        
        return batches
    
    def _estimate_complexity(self, proposals: List[Dict[str, Any]]) -> str:
        """Estimate overall complexity of the revamp"""
        total_issues = sum(p["total_issues"] for p in proposals)
        high_priority = sum(1 for p in proposals if p["priority"] >= 8)
        
        if high_priority > 3 or total_issues > 20:
            return "high"
        elif high_priority > 0 or total_issues > 10:
            return "medium"
        else:
            return "low"
    
    def export_revamp_plan(self, revamp_plan: Dict[str, Any], filename: str = "engineer_revamp_plan.json"):
        """Export the revamp plan to a file"""
        with open(filename, 'w') as f:
            json.dump(revamp_plan, f, indent=2)
        print(f"\n[+] Revamp plan exported to {filename}")
    
    def export_analysis_results(self, filename: str = "engineer_analysis_results.json"):
        """Export detailed analysis results"""
        with open(filename, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        print(f"[+] Analysis results exported to {filename}")


def main():
    print("="*80)
    print("MEGACOMPACT SELF-REVAMP ENGINEER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    if not ENGINEERS_AVAILABLE:
        print("\n[!] FATAL: Engineers module not available. Cannot proceed.")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = CodebaseAnalyzer(".")
    
    # Phase 1: Scan codebase
    print("\n" + "="*80)
    print("PHASE 1: CODEBASE DISCOVERY")
    print("="*80)
    code_files = analyzer.scan_codebase()
    
    if not code_files:
        print("[!] No Python files found. Exiting.")
        sys.exit(1)
    
    # Phase 2: Engineer analysis
    print("\n" + "="*80)
    print("PHASE 2: ENGINEER DOUBLE-PASS ANALYSIS")
    print("="*80)
    
    analyses = []
    for file_info in code_files:
        analysis = analyzer.analyze_file_with_engineers(file_info)
        analyses.append(analysis)
        analyzer.analysis_results.append(analysis)
    
    # Phase 3: Generate revamp proposals
    proposals = analyzer.generate_revamp_proposals(analyses)
    
    # Phase 4: Create comprehensive revamp plan
    revamp_plan = analyzer.ask_engineers_for_revamp_plan(proposals)
    
    # Phase 5: Export results
    print("\n" + "="*80)
    print("PHASE 5: EXPORTING RESULTS")
    print("="*80)
    
    analyzer.export_revamp_plan(revamp_plan)
    analyzer.export_analysis_results()
    
    # Summary
    print("\n" + "="*80)
    print("SELF-REVAMP ANALYSIS COMPLETE")
    print("="*80)
    
    total_analyzed = len(analyses)
    total_allowed = sum(1 for a in analyses if a.get("allowed_for_llm", False))
    total_blocked = total_analyzed - total_allowed
    total_issues = sum(a.get("failed_checks", 0) for a in analyses)
    
    print(f"Files analyzed: {total_analyzed}")
    print(f"Allowed for LLM processing: {total_allowed}")
    print(f"Blocked by engineers: {total_blocked}")
    print(f"Total issues found: {total_issues}")
    print(f"Revamp complexity: {revamp_plan['estimated_complexity']}")
    
    if revamp_plan['files_requiring_revamp'] > 0:
        print(f"\nFiles recommended for revamp:")
        for i, file_path in enumerate(revamp_plan['priority_order'][:5], 1):
            proposal = next(p for p in proposals if p['file_path'] == file_path)
            print(f"  {i}. {file_path} ({proposal['revamp_type']}, priority: {proposal['priority']})")
    
    print(f"\nFiles generated:")
    print("- engineer_revamp_plan.json: Comprehensive revamp strategy")
    print("- engineer_analysis_results.json: Detailed engineer analysis")
    print("- artifacts/self_revamp_ledger.jsonl: Complete engineer verification log")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
