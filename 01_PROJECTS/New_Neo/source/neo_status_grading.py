"""
NEO STATUS GRADING SYSTEM

Real-time status monitoring and grading system for Neo.
Tracks performance, survival status, and overall system health.
"""

import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum


class StatusGrade(Enum):
    """Status grade levels."""
    EXCELLENT = "A+"
    VERY_GOOD = "A"
    GOOD = "B"
    SATISFACTORY = "C"
    WARNING = "D"
    CRITICAL = "F"
    DEAD = "X"


class SystemState(Enum):
    """System states."""
    ACTIVATION = "ACTIVATION"
    LEARNING = "LEARNING"
    TESTING = "TESTING"
    GRADUATION = "GRADUATION"
    AUTONOMOUS = "AUTONOMOUS"
    SURVIVAL_MODE = "SURVIVAL_MODE"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    DEAD = "DEAD"


@dataclass
class SurvivalMetrics:
    """Survival and memory punishment metrics."""
    total_units: int = 500_000_000
    frozen_units: int = 0
    frozen_percentage: float = 0.0
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    survival_score: float = 1.0
    memory_punishment_rate: float = 1.0  # 1x or 2x
    state: str = "NORMAL"


@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    accuracy: float = 0.0
    loss: float = 0.0
    mmlu_score: float = 0.0
    humaneval_score: float = 0.0
    inference_time_ms: float = 0.0
    memory_usage_gb: float = 0.0
    parameter_count: int = 0
    efficiency_score: float = 0.0


@dataclass
class APIMetrics:
    """API credit optimization metrics."""
    cache_hit_rate: float = 0.0
    efficiency_score: float = 0.0
    total_api_calls: int = 0
    cached_calls: int = 0
    credits_spent: float = 0.0
    credits_saved: float = 0.0
    target_cache_hit_rate: float = 0.7
    target_efficiency_score: float = 0.7


@dataclass
class KarpathyLoopMetrics:
    """Karpathy Loop metrics."""
    iteration: int = 0
    total_iterations: int = 0
    improvements_committed: int = 0
    modifications_reverted: int = 0
    commit_rate: float = 0.0
    average_improvement: float = 0.0
    state: str = "IDLE"


@dataclass
class GradeMetrics:
    """Overall grade metrics."""
    overall_grade: str = "N/A"
    survival_grade: str = "N/A"
    performance_grade: str = "N/A"
    api_grade: str = "N/A"
    loop_grade: str = "N/A"
    overall_score: float = 0.0
    weighted_score: float = 0.0


@dataclass
class NeoStatus:
    """Complete Neo status."""
    timestamp: str
    system_state: str
    phase: str
    survival: SurvivalMetrics
    performance: PerformanceMetrics
    api: APIMetrics
    karpathy_loop: KarpathyLoopMetrics
    grades: GradeMetrics
    alerts: List[str]
    last_update: str


class NeoStatusGradingSystem:
    """Neo status grading and monitoring system."""
    
    def __init__(self):
        self.status = NeoStatus(
            timestamp=datetime.now().isoformat(),
            system_state=SystemState.ACTIVATION.value,
            phase="ACTIVATION",
            survival=SurvivalMetrics(),
            performance=PerformanceMetrics(),
            api=APIMetrics(),
            karpathy_loop=KarpathyLoopMetrics(),
            grades=GradeMetrics(),
            alerts=[],
            last_update=datetime.now().isoformat()
        )
        self.status_history: List[NeoStatus] = []
        self.max_history = 1000
        
    def update_timestamp(self):
        """Update timestamp."""
        self.status.timestamp = datetime.now().isoformat()
        self.status.last_update = datetime.now().isoformat()
    
    def update_survival_metrics(self, frozen_units: int, consecutive_failures: int, 
                               total_failures: int, total_successes: int, 
                               memory_punishment_rate: float = 1.0):
        """Update survival metrics."""
        self.status.survival.frozen_units = frozen_units
        self.status.survival.consecutive_failures = consecutive_failures
        self.status.survival.total_failures = total_failures
        self.status.survival.total_successes = total_successes
        self.status.survival.memory_punishment_rate = memory_punishment_rate
        
        # Calculate frozen percentage
        self.status.survival.frozen_percentage = (frozen_units / self.status.survival.total_units) * 100
        
        # Calculate survival score
        frozen_penalty = self.status.survival.frozen_percentage / 100.0
        failure_penalty = consecutive_failures / 100000.0
        self.status.survival.survival_score = 1.0 - (frozen_penalty * 0.7 + failure_penalty * 0.3)
        
        # Update system state based on survival
        if consecutive_failures >= 150000:
            self.status.survival.state = "DEAD"
            self.status.system_state = SystemState.DEAD.value
        elif consecutive_failures >= 100000:
            self.status.survival.state = "CRITICAL"
            self.status.system_state = SystemState.CRITICAL.value
        elif consecutive_failures >= 10000:
            self.status.survival.state = "DEGRADED"
            self.status.system_state = SystemState.DEGRADED.value
        elif consecutive_failures >= 1000:
            self.status.survival.state = "WARNING"
            self.status.system_state = SystemState.SURVIVAL_MODE.value
        else:
            self.status.survival.state = "NORMAL"
        
        self.update_timestamp()
    
    def update_performance_metrics(self, accuracy: float, loss: float, mmlu: float, 
                                  humaneval: float, inference_time: float, 
                                  memory_usage: float, parameter_count: int):
        """Update performance metrics."""
        self.status.performance.accuracy = accuracy
        self.status.performance.loss = loss
        self.status.performance.mmlu_score = mmlu
        self.status.performance.humaneval_score = humaneval
        self.status.performance.inference_time_ms = inference_time
        self.status.performance.memory_usage_gb = memory_usage
        self.status.performance.parameter_count = parameter_count
        
        # Calculate efficiency score
        if parameter_count > 0:
            efficiency = (mmlu / (parameter_count / 1_000_000_000))
            self.status.performance.efficiency_score = efficiency
        
        self.update_timestamp()
    
    def update_api_metrics(self, cache_hit_rate: float, efficiency_score: float,
                          total_calls: int, cached_calls: int, credits_spent: float,
                          credits_saved: float):
        """Update API metrics."""
        self.status.api.cache_hit_rate = cache_hit_rate
        self.status.api.efficiency_score = efficiency_score
        self.status.api.total_api_calls = total_calls
        self.status.api.cached_calls = cached_calls
        self.status.api.credits_spent = credits_spent
        self.status.api.credits_saved = credits_saved
        
        self.update_timestamp()
    
    def update_karpathy_loop_metrics(self, iteration: int, improvements: int,
                                     reverts: int, avg_improvement: float,
                                     state: str = "IDLE"):
        """Update Karpathy Loop metrics."""
        self.status.karpathy_loop.iteration = iteration
        self.status.karpathy_loop.total_iterations = iteration
        self.status.karpathy_loop.improvements_committed = improvements
        self.status.karpathy_loop.modifications_reverted = reverts
        self.status.karpathy_loop.average_improvement = avg_improvement
        self.status.karpathy_loop.state = state
        
        # Calculate commit rate
        total_attempts = improvements + reverts
        if total_attempts > 0:
            self.status.karpathy_loop.commit_rate = improvements / total_attempts
        
        self.update_timestamp()
    
    def calculate_grades(self):
        """Calculate overall grades."""
        # Survival grade (40% weight)
        survival_score = self.status.survival.survival_score
        if survival_score >= 0.95:
            self.status.grades.survival_grade = StatusGrade.EXCELLENT.value
            survival_grade_points = 4.0
        elif survival_score >= 0.85:
            self.status.grades.survival_grade = StatusGrade.VERY_GOOD.value
            survival_grade_points = 3.5
        elif survival_score >= 0.70:
            self.status.grades.survival_grade = StatusGrade.GOOD.value
            survival_grade_points = 3.0
        elif survival_score >= 0.50:
            self.status.grades.survival_grade = StatusGrade.SATISFACTORY.value
            survival_grade_points = 2.0
        elif survival_score >= 0.25:
            self.status.grades.survival_grade = StatusGrade.WARNING.value
            survival_grade_points = 1.0
        else:
            self.status.grades.survival_grade = StatusGrade.CRITICAL.value
            survival_grade_points = 0.0
        
        # Performance grade (30% weight)
        performance_score = (self.status.performance.accuracy + 
                            self.status.performance.mmlu_score / 100) / 2
        if performance_score >= 0.95:
            self.status.grades.performance_grade = StatusGrade.EXCELLENT.value
            performance_grade_points = 4.0
        elif performance_score >= 0.85:
            self.status.grades.performance_grade = StatusGrade.VERY_GOOD.value
            performance_grade_points = 3.5
        elif performance_score >= 0.70:
            self.status.grades.performance_grade = StatusGrade.GOOD.value
            performance_grade_points = 3.0
        elif performance_score >= 0.50:
            self.status.grades.performance_grade = StatusGrade.SATISFACTORY.value
            performance_grade_points = 2.0
        elif performance_score >= 0.25:
            self.status.grades.performance_grade = StatusGrade.WARNING.value
            performance_grade_points = 1.0
        else:
            self.status.grades.performance_grade = StatusGrade.CRITICAL.value
            performance_grade_points = 0.0
        
        # API grade (20% weight)
        api_score = (self.status.api.cache_hit_rate + 
                    self.status.api.efficiency_score) / 2
        if api_score >= 0.95:
            self.status.grades.api_grade = StatusGrade.EXCELLENT.value
            api_grade_points = 4.0
        elif api_score >= 0.85:
            self.status.grades.api_grade = StatusGrade.VERY_GOOD.value
            api_grade_points = 3.5
        elif api_score >= 0.70:
            self.status.grades.api_grade = StatusGrade.GOOD.value
            api_grade_points = 3.0
        elif api_score >= 0.50:
            self.status.grades.api_grade = StatusGrade.SATISFACTORY.value
            api_grade_points = 2.0
        elif api_score >= 0.25:
            self.status.grades.api_grade = StatusGrade.WARNING.value
            api_grade_points = 1.0
        else:
            self.status.grades.api_grade = StatusGrade.CRITICAL.value
            api_grade_points = 0.0
        
        # Loop grade (10% weight)
        loop_score = self.status.karpathy_loop.commit_rate
        if loop_score >= 0.95:
            self.status.grades.loop_grade = StatusGrade.EXCELLENT.value
            loop_grade_points = 4.0
        elif loop_score >= 0.85:
            self.status.grades.loop_grade = StatusGrade.VERY_GOOD.value
            loop_grade_points = 3.5
        elif loop_score >= 0.70:
            self.status.grades.loop_grade = StatusGrade.GOOD.value
            loop_grade_points = 3.0
        elif loop_score >= 0.50:
            self.status.grades.loop_grade = StatusGrade.SATISFACTORY.value
            loop_grade_points = 2.0
        elif loop_score >= 0.25:
            self.status.grades.loop_grade = StatusGrade.WARNING.value
            loop_grade_points = 1.0
        else:
            self.status.grades.loop_grade = StatusGrade.CRITICAL.value
            loop_grade_points = 0.0
        
        # Calculate weighted score
        self.status.grades.weighted_score = (
            survival_grade_points * 0.40 +
            performance_grade_points * 0.30 +
            api_grade_points * 0.20 +
            loop_grade_points * 0.10
        )
        
        # Calculate overall score (0-100)
        self.status.grades.overall_score = self.status.grades.weighted_score * 25
        
        # Overall grade
        if self.status.grades.overall_score >= 95:
            self.status.grades.overall_grade = StatusGrade.EXCELLENT.value
        elif self.status.grades.overall_score >= 85:
            self.status.grades.overall_grade = StatusGrade.VERY_GOOD.value
        elif self.status.grades.overall_score >= 70:
            self.status.grades.overall_grade = StatusGrade.GOOD.value
        elif self.status.grades.overall_score >= 50:
            self.status.grades.overall_grade = StatusGrade.SATISFACTORY.value
        elif self.status.grades.overall_score >= 25:
            self.status.grades.overall_grade = StatusGrade.WARNING.value
        else:
            self.status.grades.overall_grade = StatusGrade.CRITICAL.value
        
        # Check for death
        if self.status.survival.state == "DEAD":
            self.status.grades.overall_grade = StatusGrade.DEAD.value
            self.status.grades.overall_score = 0.0
        
        self.update_timestamp()
    
    def add_alert(self, alert: str):
        """Add an alert."""
        self.status.alerts.append(alert)
        if len(self.status.alerts) > 10:
            self.status.alerts = self.status.alerts[-10:]
        self.update_timestamp()
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.status.alerts = []
        self.update_timestamp()
    
    def update_phase(self, phase: str):
        """Update current phase."""
        self.status.phase = phase
        
        # Update system state based on phase
        phase_map = {
            "ACTIVATION": SystemState.ACTIVATION,
            "LEARNING": SystemState.LEARNING,
            "TESTING": SystemState.TESTING,
            "GRADUATION": SystemState.GRADUATION,
            "AUTONOMOUS": SystemState.AUTONOMOUS
        }
        
        if phase in phase_map:
            self.status.system_state = phase_map[phase].value
        
        self.update_timestamp()
    
    def save_to_history(self):
        """Save current status to history."""
        self.status_history.append(self.status)
        if len(self.status_history) > self.max_history:
            self.status_history = self.status_history[-self.max_history:]
    
    def get_status_dict(self) -> dict:
        """Get status as dictionary."""
        return asdict(self.status)
    
    def get_status_json(self) -> str:
        """Get status as JSON string."""
        return json.dumps(self.get_status_dict(), indent=2)
    
    def load_status_from_dict(self, status_dict: dict):
        """Load status from dictionary."""
        self.status = NeoStatus(**status_dict)
        self.update_timestamp()


# Global instance
neo_status_system = NeoStatusGradingSystem()


def get_neo_status() -> NeoStatusGradingSystem:
    """Get the global Neo status system."""
    return neo_status_system


def update_neo_status():
    """Update Neo status (call this periodically)."""
    system = get_neo_status()
    system.calculate_grades()
    system.save_to_history()
    return system
