"""Deterministic verifier — the only authority for promotions."""

from __future__ import annotations

import os
import re
from typing import Any, Optional


def verify_solution_numpy(weights, input_vec) -> float:
    """Simple deterministic score for simulation mode."""
    import numpy as np
    prediction = np.tanh(np.dot(input_vec, weights))
    return float(np.mean(prediction > 0))


def verify_output_text(output_text: str, expected_answer: str | None = None) -> bool:
    """
    Conservative text verifier used by the online daemon.
    Does NOT execute generated code — only structural + optional exact match.
    """
    if not output_text or not isinstance(output_text, str):
        return False
    text = output_text.strip()
    if len(text) < 8 or len(text) > 2000:
        return False

    has_marker = bool(
        re.search(r"(SOLUTION:|ANSWER:|Final Answer:)", text, re.IGNORECASE)
    )
    if not has_marker:
        return False

    if expected_answer is not None:
        # Extract after the last marker and compare loosely
        parts = re.split(r"(?:SOLUTION:|ANSWER:|Final Answer:)", text, flags=re.IGNORECASE)
        if len(parts) < 2:
            return False
        extracted = parts[-1].strip()
        # Normalize whitespace / case for numeric or short answers
        norm_ext = re.sub(r"\s+", " ", extracted).strip().lower()
        norm_exp = re.sub(r"\s+", " ", str(expected_answer)).strip().lower()
        return norm_exp in norm_ext or norm_ext == norm_exp

    return True


def score_group(texts: list[str], expected: str | None = None) -> list[float]:
    """Return binary or soft scores for a group of completions (GRPO)."""
    return [1.0 if verify_output_text(t, expected) else 0.0 for t in texts]


class E2BSandboxVerifier:
    """
    E2B sandbox verifier for safe code execution.
    Uses isolated cloud micro-VMs to execute generated code patches.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("E2B_API_KEY", "")
        self.sandbox = None
        self._available = False
        
        if self.api_key and self.api_key != "mock_e2b_token":
            try:
                from e2b_code_interpreter import Sandbox
                self.Sandbox = Sandbox
                self._available = True
            except ImportError:
                print("[E2B] e2b_code_interpreter not installed - falling back to text-only verification")
    
    def is_available(self) -> bool:
        return self._available
    
    def verify_code_patch(self, code_patch: str, test_suite_path: str = "") -> dict:
        """
        Execute code patch in isolated E2B sandbox and return verification results.
        
        Args:
            code_patch: Generated Python code to verify
            test_suite_path: Optional path to test suite to run
            
        Returns:
            dict with stdout, stderr, exit_code, and passed status
        """
        if not self._available:
            return {
                "stdout": "",
                "stderr": "E2B sandbox not available - using text-only verification",
                "exit_code": -1,
                "passed": False,
                "method": "fallback"
            }
        
        try:
            with self.Sandbox(api_key=self.api_key) as sandbox:
                # Write the generated patch to the sandbox environment
                sandbox.files.write("/workspace/patch.py", code_patch)
                
                # Execute the code
                if test_suite_path:
                    # If test suite provided, run pytest
                    result = sandbox.commands.run(f"pytest {test_suite_path}")
                else:
                    # Just execute the patch directly
                    result = sandbox.commands.run("python /workspace/patch.py")
                
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "passed": result.exit_code == 0,
                    "method": "e2b_sandbox"
                }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"E2B sandbox error: {str(e)}",
                "exit_code": -1,
                "passed": False,
                "method": "error"
            }
    
    def verify_with_timeout(self, code_patch: str, timeout_sec: int = 30) -> dict:
        """
        Execute code with timeout protection.
        """
        if not self._available:
            return self.verify_code_patch(code_patch)
        
        try:
            with self.Sandbox(api_key=self.api_key, timeout=timeout_sec) as sandbox:
                sandbox.files.write("/workspace/patch.py", code_patch)
                result = sandbox.commands.run("python /workspace/patch.py", timeout=timeout_sec)
                
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "passed": result.exit_code == 0,
                    "method": "e2b_sandbox"
                }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"E2B timeout or error: {str(e)}",
                "exit_code": -1,
                "passed": False,
                "method": "timeout"
            }


def verify_with_safety_fallback(
    code_patch: str, 
    text_output: str, 
    expected: Optional[str] = None,
    e2b_api_key: Optional[str] = None
) -> dict:
    """
    Multi-layer verification: try E2B sandbox first, fall back to text verification.
    
    Args:
        code_patch: Generated code to execute in sandbox
        text_output: Text output for fallback verification
        expected: Expected answer for text verification
        e2b_api_key: Optional E2B API key
        
    Returns:
        dict with verification results and method used
    """
    # Try E2B sandbox first
    verifier = E2BSandboxVerifier(e2b_api_key)
    if verifier.is_available():
        sandbox_result = verifier.verify_code_patch(code_patch)
        if sandbox_result["passed"]:
            return {
                **sandbox_result,
                "method": "e2b_sandbox",
                "fallback_used": False
            }
    
    # Fall back to text verification
    text_passed = verify_output_text(text_output, expected)
    return {
        "stdout": text_output,
        "stderr": "Used text-only verification (E2B unavailable or failed)",
        "exit_code": 0 if text_passed else 1,
        "passed": text_passed,
        "method": "text_fallback",
        "fallback_used": True
    }
