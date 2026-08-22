"""
PROJECT APEX: BENCHMARK COMPARISON SYSTEM
Enables micro-LLM to compare itself against flagship 700B+ models.
Tracks progress and provides detailed comparison metrics.
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

from flagship_llm_database import FlagshipModelDatabase, FlagshipModel, ModelPerformance, ModelEfficiency

class ComparisonMetric(Enum):
    """Metrics for comparison."""
    MMLU = "MMLU"
    HUMAN_EVAL = "HUMAN_EVAL"
    MATH = "MATH"
    GSM8K = "GSM8K"
    HELLASWAG = "HELLASWAG"
    ARC_CHALLENGE = "ARC_CHALLENGE"
    TRUTHFULQA = "TRUTHFULQA"
    WINOGRANDE = "WINOGRANDE"
    OVERALL = "OVERALL"
    EFFICIENCY = "EFFICIENCY"
    PARAMETER_EFFICIENCY = "PARAMETER_EFFICIENCY"

class ComparisonType(Enum):
    """Types of comparisons."""
    ABSOLUTE = "ABSOLUTE"  # Direct score comparison
    NORMALIZED = "NORMALIZED"  # Normalized by parameter count
    EFFICIENCY = "EFFICIENCY"  # Performance per parameter
    PROGRESS = "PROGRESS"  # Progress over time

@dataclass
class ComparisonResult:
    """Result of a comparison between micro-LLM and flagship model."""
    micro_llm_score: float
    flagship_score: float
    flagship_model_id: str
    flagship_model_name: str
    metric: ComparisonMetric
    difference: float
    percentage_of_flagship: float
    improvement_needed: float
    parameter_ratio: float  # micro_params / flagship_params
    efficiency_ratio: float  # performance per parameter
    timestamp: str
    
    def to_dict(self):
        return self.__dict__

@dataclass
class ProgressTracker:
    """Tracks micro-LLM progress against flagship models."""
    baseline_score: float
    current_score: float
    target_score: float
    flagship_model_id: str
    metric: ComparisonMetric
    start_date: str
    last_update: str
    improvements: List[float]
    progress_percentage: float
    estimated_time_to_target: float  # days
    
    def to_dict(self):
        return self.__dict__

class BenchmarkComparisonSystem:
    """
    System for comparing micro-LLM against flagship models.
    Provides detailed metrics and progress tracking.
    """
    
    def __init__(self, micro_llm_params: int = 500_000_000):
        self.micro_llm_params = micro_llm_params
        self.flagship_database = FlagshipModelDatabase()
        self.comparison_history = []
        self.progress_trackers = {}
        self.benchmark_results = {}
        
    def compare_to_flagship(self, micro_llm_score: float, 
                          flagship_model_id: str,
                          metric: ComparisonMetric) -> ComparisonResult:
        """
        Compare micro-LLM performance to a flagship model.
        Returns detailed comparison result.
        """
        flagship_model = self.flagship_database.get_model(flagship_model_id)
        if not flagship_model:
            raise ValueError(f"Flagship model {flagship_model_id} not found")
        
        # Get flagship score for metric
        flagship_score = self.get_flagship_score(flagship_model, metric)
        
        # Calculate comparison metrics
        difference = micro_llm_score - flagship_score
        percentage_of_flagship = (micro_llm_score / flagship_score) * 100 if flagship_score > 0 else 0
        improvement_needed = flagship_score - micro_llm_score
        parameter_ratio = self.micro_llm_params / flagship_model.weights.total_parameters
        efficiency_ratio = (micro_llm_score / self.micro_llm_params) / (flagship_score / flagship_model.weights.total_parameters) if flagship_score > 0 else 0
        
        result = ComparisonResult(
            micro_llm_score=micro_llm_score,
            flagship_score=flagship_score,
            flagship_model_id=flagship_model_id,
            flagship_model_name=flagship_model.model_name,
            metric=metric,
            difference=difference,
            percentage_of_flagship=percentage_of_flagship,
            improvement_needed=improvement_needed,
            parameter_ratio=parameter_ratio,
            efficiency_ratio=efficiency_ratio,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.comparison_history.append(result)
        return result
    
    def get_flagship_score(self, model: FlagshipModel, metric: ComparisonMetric) -> float:
        """Get flagship model score for a specific metric."""
        performance = model.performance
        
        metric_map = {
            ComparisonMetric.MMLU: performance.mmlu_score,
            ComparisonMetric.HUMAN_EVAL: performance.human_eval_score,
            ComparisonMetric.MATH: performance.math_score,
            ComparisonMetric.GSM8K: performance.gsm8k_score,
            ComparisonMetric.HELLASWAG: performance.hellaswag_score,
            ComparisonMetric.ARC_CHALLENGE: performance.arc_challenge_score,
            ComparisonMetric.TRUTHFULQA: performance.truthfulqa_score,
            ComparisonMetric.WINOGRANDE: performance.winogrande_score,
            ComparisonMetric.OVERALL: performance.custom_benchmark,
            ComparisonMetric.EFFICIENCY: performance.custom_benchmark,  # Placeholder
            ComparisonMetric.PARAMETER_EFFICIENCY: performance.custom_benchmark / (model.weights.total_parameters / 1e9)
        }
        
        return metric_map.get(metric, 0.0)
    
    def compare_to_all_flagships(self, micro_llm_score: float,
                                 metric: ComparisonMetric) -> List[ComparisonResult]:
        """Compare micro-LLM to all flagship models."""
        results = []
        
        for model in self.flagship_database.get_all_models():
            result = self.compare_to_flagship(micro_llm_score, model.model_id, metric)
            results.append(result)
        
        return results
    
    def calculate_efficiency_score(self, micro_llm_score: float,
                                   flagship_model_id: str,
                                   metric: ComparisonMetric) -> float:
        """
        Calculate efficiency score (performance per billion parameters).
        This shows how efficient the micro-LLM is compared to flagship models.
        """
        flagship_model = self.flagship_database.get_model(flagship_model_id)
        if not flagship_model:
            return 0.0
        
        flagship_score = self.get_flagship_score(flagship_model, metric)
        
        # Performance per billion parameters
        micro_efficiency = micro_llm_score / (self.micro_llm_params / 1e9)
        flagship_efficiency = flagship_score / (flagship_model.weights.total_parameters / 1e9)
        
        # Efficiency ratio
        efficiency_ratio = micro_efficiency / flagship_efficiency if flagship_efficiency > 0 else 0
        
        return efficiency_ratio
    
    def track_progress(self, metric: ComparisonMetric, 
                      current_score: float,
                      target_model_id: str = "claude-3.5-sonnet") -> ProgressTracker:
        """
        Track progress of micro-LLM against a target flagship model.
        """
        target_model = self.flagship_database.get_model(target_model_id)
        if not target_model:
            raise ValueError(f"Target model {target_model_id} not found")
        
        target_score = self.get_flagship_score(target_model, metric)
        
        # Get or create progress tracker
        tracker_key = f"{metric.value}_{target_model_id}"
        
        if tracker_key not in self.progress_trackers:
            tracker = ProgressTracker(
                baseline_score=current_score,
                current_score=current_score,
                target_score=target_score,
                flagship_model_id=target_model_id,
                metric=metric,
                start_date=time.strftime("%Y-%m-%d %H:%M:%S"),
                last_update=time.strftime("%Y-%m-%d %H:%M:%S"),
                improvements=[],
                progress_percentage=0.0,
                estimated_time_to_target=0.0
            )
            self.progress_trackers[tracker_key] = tracker
        else:
            tracker = self.progress_trackers[tracker_key]
            improvement = current_score - tracker.current_score
            tracker.improvements.append(improvement)
            tracker.current_score = current_score
            tracker.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate progress percentage
        progress_range = target_score - tracker.baseline_score
        if progress_range > 0:
            current_progress = current_score - tracker.baseline_score
            tracker.progress_percentage = (current_progress / progress_range) * 100
        
        # Estimate time to target based on improvement rate
        if len(tracker.improvements) > 1:
            avg_improvement = sum(tracker.improvements[-10:]) / min(len(tracker.improvements), 10)
            if avg_improvement > 0:
                remaining_improvement = target_score - current_score
                iterations_needed = remaining_improvement / avg_improvement
                tracker.estimated_time_to_target = iterations_needed  # In iterations
        
        return tracker
    
    def get_efficiency_comparison(self) -> Dict:
        """
        Get efficiency comparison across all flagship models.
        Shows how well micro-LLM performs per parameter compared to flagships.
        """
        efficiency_comparison = {}
        
        for model in self.flagship_database.get_all_models():
            overall_score = model.performance.custom_benchmark
            
            # Calculate efficiency metrics
            micro_efficiency = overall_score / (self.micro_llm_params / 1e9)
            flagship_efficiency = overall_score / (model.weights.total_parameters / 1e9)
            
            efficiency_ratio = micro_efficiency / flagship_efficiency if flagship_efficiency > 0 else 0
            
            efficiency_comparison[model.model_id] = {
                'model_name': model.model_name,
                'flagship_params': model.weights.total_parameters,
                'micro_params': self.micro_llm_params,
                'parameter_ratio': self.micro_llm_params / model.weights.total_parameters,
                'flagship_efficiency': flagship_efficiency,
                'micro_efficiency': micro_efficiency,
                'efficiency_ratio': efficiency_ratio,
                'efficiency_score': efficiency_ratio * 100  # Percentage
            }
        
        return efficiency_comparison
    
    def get_parameter_equivalent_performance(self, micro_llm_score: float) -> Dict:
        """
        Calculate what a flagship model would score if scaled to micro-LLM parameter count.
        This shows how much the micro-LLM outperforms parameter-based expectations.
        """
        equivalent_performance = {}
        
        for model in self.flagship_database.get_all_models():
            flagship_score = model.performance.custom_benchmark
            flagship_params = model.weights.total_parameters
            
            # Assume scaling follows Chinchilla scaling laws
            # Performance scales with params^alpha where alpha ~ 0.076
            scaling_factor = (self.micro_llm_params / flagship_params) ** 0.076
            expected_score = flagship_score * scaling_factor
            
            equivalent_performance[model.model_id] = {
                'model_name': model.model_name,
                'flagship_score': flagship_score,
                'expected_scaled_score': expected_score,
                'micro_llm_score': micro_llm_score,
                'outperformance': micro_llm_score - expected_score,
                'outperformance_percentage': ((micro_llm_score / expected_score) - 1) * 100 if expected_score > 0 else 0
            }
        
        return equivalent_performance
    
    def generate_comparison_report(self, micro_llm_scores: Dict[str, float]) -> str:
        """
        Generate comprehensive comparison report.
        micro_llm_scores: dict of metric names to scores
        """
        report = []
        report.append("=" * 80)
        report.append("PROJECT APEX: BENCHMARK COMPARISON REPORT")
        report.append("=" * 80)
        report.append(f"Micro-LLM Parameters: {self.micro_llm_params:,} ({self.micro_llm_params / 1e9:.2f}B)")
        report.append(f"Report Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall comparison to top models
        report.append("OVERALL COMPARISON TO TOP FLAGSHIP MODELS")
        report.append("-" * 80)
        
        top_models = self.flagship_database.get_top_n_models(5)
        for model in top_models:
            overall_score = micro_llm_scores.get('overall', 0.0)
            comparison = self.compare_to_flagship(overall_score, model.model_id, ComparisonMetric.OVERALL)
            
            report.append(f"\n{model.model_name} ({model.company})")
            report.append(f"  Parameters: {model.weights.total_parameters:,} ({model.weights.total_parameters / 1e9:.1f}B)")
            report.append(f"  Flagship Score: {comparison.flagship_score:.2f}")
            report.append(f"  Micro-LLM Score: {comparison.micro_llm_score:.2f}")
            report.append(f"  Percentage of Flagship: {comparison.percentage_of_flagship:.1f}%")
            report.append(f"  Parameter Ratio: {comparison.parameter_ratio:.6f}")
            report.append(f"  Efficiency Ratio: {comparison.efficiency_ratio:.2f}x")
        
        # Efficiency comparison
        report.append("\n" + "=" * 80)
        report.append("EFFICIENCY COMPARISON (Performance per Billion Parameters)")
        report.append("-" * 80)
        
        efficiency_comparison = self.get_efficiency_comparison()
        
        for model_id, metrics in sorted(efficiency_comparison.items(), 
                                       key=lambda x: x[1]['efficiency_ratio'], 
                                       reverse=True):
            report.append(f"\n{metrics['model_name']}")
            report.append(f"  Parameter Ratio: {metrics['parameter_ratio']:.6f}")
            report.append(f"  Flagship Efficiency: {metrics['flagship_efficiency']:.4f}")
            report.append(f"  Micro-LLM Efficiency: {metrics['micro_efficiency']:.4f}")
            report.append(f"  Efficiency Score: {metrics['efficiency_score']:.1f}%")
        
        # Parameter equivalent performance
        report.append("\n" + "=" * 80)
        report.append("PARAMETER-EQUIVALENT PERFORMANCE ANALYSIS")
        report.append("-" * 80)
        report.append("(Shows how micro-LLM compares to expected performance based on parameter count)")
        
        equivalent_performance = self.get_parameter_equivalent_performance(micro_llm_scores.get('overall', 0.0))
        
        for model_id, metrics in equivalent_performance.items():
            report.append(f"\n{metrics['model_name']}")
            report.append(f"  Flagship Score: {metrics['flagship_score']:.2f}")
            report.append(f"  Expected Scaled Score: {metrics['expected_scaled_score']:.2f}")
            report.append(f"  Micro-LLM Score: {metrics['micro_llm_score']:.2f}")
            report.append(f"  Outperformance: {metrics['outperformance']:+.2f}")
            report.append(f"  Outperformance Percentage: {metrics['outperformance_percentage']:+.1f}%")
        
        # Detailed metric comparisons
        report.append("\n" + "=" * 80)
        report.append("DETAILED METRIC COMPARISONS")
        report.append("-" * 80)
        
        metric_names = {
            'mmlu': 'MMLU (Massive Multitask Language Understanding)',
            'human_eval': 'HumanEval (Python Coding)',
            'math': 'Math (Mathematical Reasoning)',
            'gsm8k': 'GSM8K (Grade School Math)',
            'hellaswag': 'HellaSwag (Common Sense Reasoning)',
            'arc_challenge': 'ARC Challenge (Science Reasoning)'
        }
        
        for metric_key, metric_name in metric_names.items():
            if metric_key in micro_llm_scores:
                report.append(f"\n{metric_name}")
                report.append("-" * 40)
                
                metric_enum = ComparisonMetric(metric_key.upper())
                comparisons = self.compare_to_all_flagships(micro_llm_scores[metric_key], metric_enum)
                
                for comp in comparisons[:3]:  # Top 3
                    report.append(f"  {comp.flagship_model_name}: {comp.micro_llm_score:.2f} vs {comp.flagship_score:.2f} ({comp.percentage_of_flagship:.1f}%)")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def get_comparison_summary(self) -> Dict:
        """Get summary of comparison data."""
        return {
            'micro_llm_params': self.micro_llm_params,
            'total_comparisons': len(self.comparison_history),
            'flagship_models_count': len(self.flagship_database.models),
            'active_progress_trackers': len(self.progress_trackers),
            'top_flagship_model': self.flagship_database.get_top_n_models(1)[0].model_name if self.flagship_database.models else None
        }
    
    def export_comparison_data(self, filepath: str):
        """Export comparison data to JSON file."""
        data = {
            'summary': self.get_comparison_summary(),
            'comparisons': [c.to_dict() for c in self.comparison_history],
            'progress_trackers': {k: v.to_dict() for k, v in self.progress_trackers.items()},
            'efficiency_comparison': self.get_efficiency_comparison()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)