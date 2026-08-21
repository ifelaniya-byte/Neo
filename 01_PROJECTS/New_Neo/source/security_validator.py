"""
PROJECT APEX: SECURITY & VALIDATION LAYER
Validates code changes for security, correctness, and safety.
Prevents malicious or dangerous modifications.
"""

import ast
import re
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class SecurityLevel(Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    RISKY = "RISKY"
    DANGEROUS = "DANGEROUS"

class ValidationType(Enum):
    SYNTAX = "SYNTAX"
    SECURITY = "SECURITY"
    CORRECTNESS = "CORRECTNESS"
    PERFORMANCE = "PERFORMANCE"
    DEPENDENCY = "DEPENDENCY"

@dataclass
class ValidationIssue:
    issue_type: ValidationType
    severity: SecurityLevel
    description: str
    line_number: int
    code_snippet: str
    recommendation: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ValidationReport:
    overall_status: SecurityLevel
    issues: List[ValidationIssue]
    validation_time: float
    code_hash: str
    passed_checks: int
    failed_checks: int
    
    def to_dict(self):
        return asdict(self)

class SecurityValidator:
    """
    Comprehensive security and validation system for code changes.
    Prevents dangerous modifications while allowing safe optimizations.
    """
    
    def __init__(self):
        self.validation_history = []
        self.blocked_patterns = self._initialize_blocked_patterns()
        self.safe_imports = self._initialize_safe_imports()
    
    def _initialize_blocked_patterns(self) -> List[Dict]:
        """Initialize patterns that are explicitly blocked."""
        return [
            {
                'pattern': r'eval\s*\(',
                'description': 'Use of eval() function',
                'severity': SecurityLevel.DANGEROUS,
                'recommendation': 'Avoid eval() - use safer alternatives'
            },
            {
                'pattern': r'exec\s*\(',
                'description': 'Use of exec() function',
                'severity': SecurityLevel.DANGEROUS,
                'recommendation': 'Avoid exec() - use safer alternatives'
            },
            {
                'pattern': r'__import__\s*\(',
                'description': 'Use of __import__() function',
                'severity': SecurityLevel.RISKY,
                'recommendation': 'Use standard import statements'
            },
            {
                'pattern': r'open\s*\([^)]*["\']w["\']',
                'description': 'File write operation',
                'severity': SecurityLevel.WARNING,
                'recommendation': 'Ensure file writes are controlled and necessary'
            },
            {
                'pattern': r'subprocess\.(call|run|Popen)\s*\(',
                'description': 'Subprocess execution',
                'severity': SecurityLevel.RISKY,
                'recommendation': 'Validate all subprocess commands and inputs'
            },
            {
                'pattern': r'os\.system\s*\(',
                'description': 'OS system command execution',
                'severity': SecurityLevel.DANGEROUS,
                'recommendation': 'Use subprocess with proper validation instead'
            },
            {
                'pattern': r'socket\.',
                'description': 'Network socket operations',
                'severity': SecurityLevel.WARNING,
                'recommendation': 'Ensure network operations are controlled'
            },
            {
                'pattern': r'input\s*\(',
                'description': 'User input without validation',
                'severity': SecurityLevel.WARNING,
                'recommendation': 'Always validate and sanitize user input'
            }
        ]
    
    def _initialize_safe_imports(self) -> List[str]:
        """Initialize list of safe import modules."""
        return [
            'math', 'time', 'random', 'statistics',
            'collections', 'itertools', 'functools',
            'numpy', 'pandas',  # Data processing
            'torch', 'tensorflow',  # ML frameworks
            'transformers',  # NLP
            'psutil',  # System monitoring
            'json', 'csv', 'pickle'  # Data formats
        ]
    
    def validate_code(self, code: str, context: Dict = None) -> ValidationReport:
        """
        Perform comprehensive validation of code changes.
        Returns detailed validation report.
        """
        if context is None:
            context = {}
        
        start_time = time.time()
        issues = []
        passed_checks = 0
        failed_checks = 0
        
        # 1. Syntax validation
        syntax_issues = self._validate_syntax(code)
        if syntax_issues:
            issues.extend(syntax_issues)
            failed_checks += len(syntax_issues)
        else:
            passed_checks += 1
        
        # 2. Security validation
        security_issues = self._validate_security(code)
        if security_issues:
            issues.extend(security_issues)
            failed_checks += len(security_issues)
        else:
            passed_checks += 1
        
        # 3. Import validation
        import_issues = self._validate_imports(code)
        if import_issues:
            issues.extend(import_issues)
            failed_checks += len(import_issues)
        else:
            passed_checks += 1
        
        # 4. Code pattern validation
        pattern_issues = self._validate_patterns(code)
        if pattern_issues:
            issues.extend(pattern_issues)
            failed_checks += len(pattern_issues)
        else:
            passed_checks += 1
        
        # 5. Performance validation
        performance_issues = self._validate_performance(code)
        if performance_issues:
            issues.extend(performance_issues)
            failed_checks += len(performance_issues)
        else:
            passed_checks += 1
        
        # Determine overall status
        overall_status = self._determine_overall_status(issues)
        
        # Generate code hash
        code_hash = self._generate_code_hash(code)
        
        validation_time = time.time() - start_time
        
        report = ValidationReport(
            overall_status=overall_status,
            issues=issues,
            validation_time=validation_time,
            code_hash=code_hash,
            passed_checks=passed_checks,
            failed_checks=failed_checks
        )
        
        self.validation_history.append(report)
        return report
    
    def _validate_syntax(self, code: str) -> List[ValidationIssue]:
        """Validate Python syntax."""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(ValidationIssue(
                issue_type=ValidationType.SYNTAX,
                severity=SecurityLevel.DANGEROUS,
                description=f"Syntax error: {e.msg}",
                line_number=e.lineno or 0,
                code_snippet=code.split('\n')[e.lineno - 1] if e.lineno else "",
                recommendation="Fix syntax error before proceeding"
            ))
        
        return issues
    
    def _validate_security(self, code: str) -> List[ValidationIssue]:
        """Validate against security vulnerabilities."""
        issues = []
        lines = code.split('\n')
        
        for blocked in self.blocked_patterns:
            pattern = blocked['pattern']
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(ValidationIssue(
                        issue_type=ValidationType.SECURITY,
                        severity=blocked['severity'],
                        description=blocked['description'],
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation=blocked['recommendation']
                    ))
        
        return issues
    
    def _validate_imports(self, code: str) -> List[ValidationIssue]:
        """Validate import statements for safety."""
        issues = []
        lines = code.split('\n')
        
        # Extract import statements
        import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
        
        for line_num, line in enumerate(lines, 1):
            match = re.match(import_pattern, line.strip())
            if match:
                module = match.group(1) or match.group(2)
                base_module = module.split('.')[0]
                
                if base_module not in self.safe_imports:
                    issues.append(ValidationIssue(
                        issue_type=ValidationType.DEPENDENCY,
                        severity=SecurityLevel.WARNING,
                        description=f"Potentially unsafe import: {module}",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation=f"Validate that {module} is safe and necessary"
                    ))
        
        return issues
    
    def _validate_patterns(self, code: str) -> List[ValidationIssue]:
        """Validate code patterns for potential issues."""
        issues = []
        lines = code.split('\n')
        
        # Check for hardcoded credentials
        credential_pattern = r'(password|secret|key|token)\s*=\s*["\'][^"\']{8,}["\']'
        for line_num, line in enumerate(lines, 1):
            if re.search(credential_pattern, line, re.IGNORECASE):
                issues.append(ValidationIssue(
                    issue_type=ValidationType.SECURITY,
                    severity=SecurityLevel.DANGEROUS,
                    description="Potential hardcoded credential detected",
                    line_number=line_num,
                    code_snippet=line.strip(),
                    recommendation="Use environment variables or configuration files"
                ))
        
        # Check for infinite loops
        loop_pattern = r'while\s+True\s*:'
        for line_num, line in enumerate(lines, 1):
            if re.search(loop_pattern, line):
                # Check if there's a break statement
                context_start = max(0, line_num - 1)
                context_end = min(len(lines), line_num + 10)
                context = '\n'.join(lines[context_start:context_end])
                
                if 'break' not in context:
                    issues.append(ValidationIssue(
                        issue_type=ValidationType.CORRECTNESS,
                        severity=SecurityLevel.WARNING,
                        description="Potential infinite loop detected",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation="Ensure loop has exit condition"
                    ))
        
        return issues
    
    def _validate_performance(self, code: str) -> List[ValidationIssue]:
        """Validate code for potential performance issues."""
        issues = []
        lines = code.split('\n')
        
        # Check for nested loops
        nesting_level = 0
        for line_num, line in enumerate(lines, 1):
            if re.search(r'\b(for|while)\s+', line):
                nesting_level += 1
                if nesting_level > 3:
                    issues.append(ValidationIssue(
                        issue_type=ValidationType.PERFORMANCE,
                        severity=SecurityLevel.WARNING,
                        description=f"Deep nesting detected (level {nesting_level})",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation="Consider refactoring to reduce complexity"
                    ))
            elif line.strip() and not line.strip().startswith('#'):
                # Reset nesting on non-indented line
                if not line.startswith(' ') and not line.startswith('\t'):
                    nesting_level = 0
        
        return issues
    
    def _determine_overall_status(self, issues: List[ValidationIssue]) -> SecurityLevel:
        """Determine overall security status based on issues."""
        if not issues:
            return SecurityLevel.SAFE
        
        severities = [issue.severity for issue in issues]
        
        if SecurityLevel.DANGEROUS in severities:
            return SecurityLevel.DANGEROUS
        elif SecurityLevel.RISKY in severities:
            return SecurityLevel.RISKY
        elif SecurityLevel.WARNING in severities:
            return SecurityLevel.WARNING
        else:
            return SecurityLevel.SAFE
    
    def _generate_code_hash(self, code: str) -> str:
        """Generate hash of code for tracking."""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()[:16]
    
    def get_validation_summary(self) -> Dict:
        """Get summary of validation history."""
        if not self.validation_history:
            return {}
        
        total_validations = len(self.validation_history)
        safe_count = sum(1 for r in self.validation_history if r.overall_status == SecurityLevel.SAFE)
        warning_count = sum(1 for r in self.validation_history if r.overall_status == SecurityLevel.WARNING)
        risky_count = sum(1 for r in self.validation_history if r.overall_status == SecurityLevel.RISKY)
        dangerous_count = sum(1 for r in self.validation_history if r.overall_status == SecurityLevel.DANGEROUS)
        
        return {
            'total_validations': total_validations,
            'safe_validations': safe_count,
            'warning_validations': warning_count,
            'risky_validations': risky_count,
            'dangerous_validations': dangerous_count,
            'safe_rate': safe_count / total_validations if total_validations > 0 else 0
        }
    
    def is_safe_to_apply(self, validation_report: ValidationReport) -> bool:
        """
        Determine if code changes are safe to apply based on validation report.
        """
        return validation_report.overall_status in [SecurityLevel.SAFE, SecurityLevel.WARNING]