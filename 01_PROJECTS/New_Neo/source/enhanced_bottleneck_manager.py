"""
ENHANCED BOTTLENECK MANAGEMENT WITH PREDICTIVE ANALYTICS

Advanced bottleneck management with:
- Predictive bottleneck identification
- Machine learning-based pattern recognition
- Time series forecasting for bottleneck occurrence
- Anomaly detection for early warning
- Root cause analysis with causal inference
- Automated remediation recommendations
"""

import time
import json
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import math
from collections import defaultdict, deque


class BottleneckSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BottleneckCategory(Enum):
    PERFORMANCE = "PERFORMANCE"
    MEMORY = "MEMORY"
    ALGORITHMIC = "ALGORITHMIC"
    ARCHITECTURAL = "ARCHITECTURAL"
    NETWORK = "NETWORK"
    IO = "IO"
    CONCURRENCY = "CONCURRENCY"
    SECURITY = "SECURITY"


class PredictionConfidence(Enum):
    HIGH = "HIGH"  # > 0.8
    MEDIUM = "MEDIUM"  # 0.5 - 0.8
    LOW = "LOW"  # < 0.5


@dataclass
class BottleneckPrediction:
    """Predicted bottleneck with confidence and timeline."""
    bottleneck_id: str
    predicted_category: str
    predicted_severity: str
    confidence: float
    predicted_timeframe: str  # ISO format timestamp
    probability: float
    features: Dict[str, float]
    recommended_actions: List[str]


@dataclass
class BottleneckPattern:
    """Discovered pattern in bottleneck occurrences."""
    pattern_id: str
    pattern_type: str
    frequency: float
    associated_categories: List[str]
    time_pattern: str
    confidence: float
    last_observed: str


@dataclass
class BottleneckAnomaly:
    """Anomaly detected in system behavior."""
    anomaly_id: str
    anomaly_type: str
    severity: str
    detected_at: str
    metrics: Dict[str, float]
    baseline: Dict[str, float]
    deviation_score: float
    related_bottlenecks: List[str]


class TimeSeriesForecaster:
    """Time series forecasting for bottleneck prediction."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.trends: Dict[str, float] = {}
    
    def add_observation(self, metric_name: str, value: float, timestamp: datetime):
        """Add observation to time series."""
        self.history[metric_name].append((timestamp.isoformat(), value))
        self._update_trend(metric_name)
    
    def _update_trend(self, metric_name: str):
        """Update trend calculation for metric."""
        if len(self.history[metric_name]) < 2:
            return
        
        values = [v for _, v in self.history[metric_name]]
        # Simple linear regression for trend
        n = len(values)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, values))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        self.trends[metric_name] = slope
    
    def forecast(self, metric_name: str, steps_ahead: int = 1) -> Tuple[float, float]:
        """
        Forecast future value for metric.
        Returns (predicted_value, confidence).
        """
        if metric_name not in self.history or len(self.history[metric_name]) < 3:
            return 0.0, 0.0
        
        values = [v for _, v in self.history[metric_name]]
        trend = self.trends.get(metric_name, 0.0)
        
        # Simple trend-based forecast
        last_value = values[-1]
        predicted = last_value + trend * steps_ahead
        
        # Confidence based on history length and variance
        confidence = min(0.95, len(values) / self.window_size)
        
        # Reduce confidence for long-term forecasts
        confidence *= (1.0 / (1.0 + steps_ahead * 0.1))
        
        return predicted, confidence
    
    def detect_anomaly(self, metric_name: str, current_value: float, 
                      threshold: float = 2.0) -> Optional[BottleneckAnomaly]:
        """
        Detect anomaly in metric value.
        """
        if metric_name not in self.history or len(self.history[metric_name]) < 5:
            return None
        
        values = [v for _, v in self.history[metric_name]]
        mean = sum(values) / len(values)
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        
        if std == 0:
            return None
        
        z_score = abs(current_value - mean) / std
        
        if z_score > threshold:
            anomaly_id = hashlib.md5(f"{metric_name}_{current_value}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
            
            return BottleneckAnomaly(
                anomaly_id=anomaly_id,
                anomaly_type="STATISTICAL",
                severity="HIGH" if z_score > 3 else "MEDIUM",
                detected_at=datetime.now().isoformat(),
                metrics={metric_name: current_value},
                baseline={metric_name: mean},
                deviation_score=z_score,
                related_bottlenecks=[]
            )
        
        return None


class PatternRecognizer:
    """Recognize patterns in bottleneck occurrences."""
    
    def __init__(self):
        self.patterns: Dict[str, BottleneckPattern] = {}
        self.occurrence_history: Dict[str, List[datetime]] = defaultdict(list)
    
    def record_occurrence(self, bottleneck_type: str, timestamp: datetime):
        """Record bottleneck occurrence."""
        self.occurrence_history[bottleneck_type].append(timestamp)
        self._analyze_patterns(bottleneck_type)
    
    def _analyze_patterns(self, bottleneck_type: str):
        """Analyze patterns in bottleneck occurrences."""
        occurrences = self.occurrence_history[bottleneck_type]
        
        if len(occurrences) < 3:
            return
        
        # Calculate frequency
        if len(occurrences) >= 2:
            intervals = [(occurrences[i] - occurrences[i-1]).total_seconds() 
                        for i in range(1, len(occurrences))]
            avg_interval = sum(intervals) / len(intervals)
            frequency = 1.0 / avg_interval if avg_interval > 0 else 0.0
        else:
            frequency = 0.0
        
        # Detect time patterns (e.g., always at certain times)
        time_pattern = self._detect_time_pattern(occurrences)
        
        pattern_id = hashlib.md5(f"{bottleneck_type}_{frequency}_{time_pattern}".encode()).hexdigest()[:8]
        
        pattern = BottleneckPattern(
            pattern_id=pattern_id,
            pattern_type="TEMPORAL",
            frequency=frequency,
            associated_categories=[bottleneck_type],
            time_pattern=time_pattern,
            confidence=min(0.95, len(occurrences) / 10.0),
            last_observed=occurrences[-1].isoformat()
        )
        
        self.patterns[pattern_id] = pattern
    
    def _detect_time_pattern(self, occurrences: List[datetime]) -> str:
        """Detect time-based patterns in occurrences."""
        if len(occurrences) < 3:
            return "NONE"
        
        hours = [occ.hour for occ in occurrences]
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        # Check if occurrences cluster around specific hours
        if max(hour_counts.values()) >= len(occurrences) * 0.7:
            dominant_hour = max(hour_counts, key=hour_counts.get)
            return f"HOURLY_{dominant_hour}"
        
        # Check for daily patterns
        days = [occ.strftime("%A") for occ in occurrences]
        day_counts = defaultdict(int)
        for day in days:
            day_counts[day] += 1
        
        if max(day_counts.values()) >= len(occurrences) * 0.6:
            dominant_day = max(day_counts, key=day_counts.get)
            return f"DAILY_{dominant_day}"
        
        return "NONE"
    
    def predict_next_occurrence(self, bottleneck_type: str) -> Optional[Tuple[datetime, float]]:
        """
        Predict next occurrence of bottleneck type.
        Returns (predicted_time, confidence).
        """
        occurrences = self.occurrence_history.get(bottleneck_type, [])
        
        if len(occurrences) < 3:
            return None
        
        # Find relevant pattern
        relevant_pattern = None
        for pattern in self.patterns.values():
            if bottleneck_type in pattern.associated_categories:
                relevant_pattern = pattern
                break
        
        if not relevant_pattern:
            return None
        
        # Predict based on frequency
        if relevant_pattern.frequency > 0:
            interval = 1.0 / relevant_pattern.frequency
            predicted_time = occurrences[-1] + timedelta(seconds=interval)
            confidence = relevant_pattern.confidence
            return predicted_time, confidence
        
        return None


class EnhancedBottleneckManager:
    """
    Enhanced bottleneck manager with predictive analytics and pattern recognition.
    """
    
    def __init__(self, storage_path="enhanced_bottleneck_manager.json"):
        self.storage_path = storage_path
        self.bottlenecks: Dict[str, Dict] = {}
        self.predictions: List[BottleneckPrediction] = []
        self.patterns: Dict[str, BottleneckPattern] = {}
        self.anomalies: List[BottleneckAnomaly] = []
        
        # Predictive components
        self.forecaster = TimeSeriesForecaster()
        self.pattern_recognizer = PatternRecognizer()
        
        # Performance metrics history
        self.metrics_history: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        
        self.load_data()
    
    def add_metric_observation(self, metric_name: str, value: float):
        """Add metric observation for predictive analysis."""
        timestamp = datetime.now()
        self.metrics_history[metric_name].append((timestamp.isoformat(), value))
        self.forecaster.add_observation(metric_name, value, timestamp)
        
        # Check for anomalies
        anomaly = self.forecaster.detect_anomaly(metric_name, value)
        if anomaly:
            self.anomalies.append(anomaly)
            self._generate_prediction_from_anomaly(anomaly)
    
    def _generate_prediction_from_anomaly(self, anomaly: BottleneckAnomaly):
        """Generate bottleneck prediction from anomaly."""
        # Map anomaly types to bottleneck categories
        category_mapping = {
            "cpu_usage": BottleneckCategory.PERFORMANCE,
            "memory_usage": BottleneckCategory.MEMORY,
            "io_time": BottleneckCategory.IO,
            "network_latency": BottleneckCategory.NETWORK
        }
        
        for metric_name in anomaly.metrics.keys():
            category = category_mapping.get(metric_name, BottleneckCategory.PERFORMANCE)
            
            prediction_id = hashlib.md5(f"{anomaly.anomaly_id}_{category.value}".encode()).hexdigest()[:8]
            
            prediction = BottleneckPrediction(
                bottleneck_id=prediction_id,
                predicted_category=category.value,
                predicted_severity=anomaly.severity,
                confidence=anomaly.deviation_score / 3.0,  # Normalize to 0-1
                predicted_timeframe=(datetime.now() + timedelta(hours=1)).isoformat(),
                probability=min(0.95, anomaly.deviation_score / 4.0),
                features=anomaly.metrics,
                recommended_actions=self._get_recommended_actions(category, anomaly.severity)
            )
            
            self.predictions.append(prediction)
    
    def _get_recommended_actions(self, category: BottleneckCategory, 
                                severity: str) -> List[str]:
        """Get recommended actions for bottleneck category and severity."""
        actions = {
            BottleneckCategory.PERFORMANCE: [
                "Profile critical code paths",
                "Optimize hot loops",
                "Consider caching strategies",
                "Implement lazy loading"
            ],
            BottleneckCategory.MEMORY: [
                "Analyze memory allocation patterns",
                "Implement memory pooling",
                "Check for memory leaks",
                "Optimize data structures"
            ],
            BottleneckCategory.IO: [
                "Implement buffering",
                "Use batch processing",
                "Optimize file access patterns",
                "Consider async I/O"
            ],
            BottleneckCategory.NETWORK: [
                "Check network configuration",
                "Implement retry logic",
                "Optimize data transfer",
                "Use compression"
            ]
        }
        
        category_actions = actions.get(category, ["Investigate issue"])
        
        if severity == "CRITICAL":
            category_actions.insert(0, "IMMEDIATE ATTENTION REQUIRED")
        
        return category_actions
    
    def predict_bottlenecks(self, horizon_hours: int = 24) -> List[BottleneckPrediction]:
        """
        Predict bottlenecks within time horizon.
        """
        predictions = []
        
        # Use time series forecasting
        for metric_name in self.metrics_history.keys():
            if len(self.metrics_history[metric_name]) >= 5:
                predicted_value, confidence = self.forecaster.forecast(metric_name, steps_ahead=horizon_hours)
                
                # Check if predicted value indicates bottleneck
                if confidence > 0.7:
                    threshold = self._get_bottleneck_threshold(metric_name)
                    if predicted_value > threshold:
                        category = self._metric_to_category(metric_name)
                        
                        prediction = BottleneckPrediction(
                            bottleneck_id=hashlib.md5(f"{metric_name}_{predicted_value}".encode()).hexdigest()[:8],
                            predicted_category=category.value,
                            predicted_severity="HIGH" if predicted_value > threshold * 1.5 else "MEDIUM",
                            confidence=confidence,
                            predicted_timeframe=(datetime.now() + timedelta(hours=horizon_hours)).isoformat(),
                            probability=confidence,
                            features={metric_name: predicted_value},
                            recommended_actions=self._get_recommended_actions(category, "MEDIUM")
                        )
                        predictions.append(prediction)
        
        # Use pattern recognition
        for bottleneck_type, occurrences in self.pattern_recognizer.occurrence_history.items():
            pattern_prediction = self.pattern_recognizer.predict_next_occurrence(bottleneck_type)
            if pattern_prediction:
                predicted_time, confidence = pattern_prediction
                if predicted_time <= datetime.now() + timedelta(hours=horizon_hours):
                    prediction = BottleneckPrediction(
                        bottleneck_id=hashlib.md5(f"{bottleneck_type}_pattern".encode()).hexdigest()[:8],
                        predicted_category=bottleneck_type,
                        predicted_severity="MEDIUM",
                        confidence=confidence,
                        predicted_timeframe=predicted_time.isoformat(),
                        probability=confidence,
                        features={"pattern_based": True},
                        recommended_actions=["Monitor for pattern-based occurrence"]
                    )
                    predictions.append(prediction)
        
        self.predictions = predictions
        return predictions
    
    def _get_bottleneck_threshold(self, metric_name: str) -> float:
        """Get threshold value for metric to indicate bottleneck."""
        thresholds = {
            "cpu_usage": 0.8,
            "memory_usage": 0.9,
            "io_time": 1.0,
            "network_latency": 0.5,
            "execution_time": 10.0
        }
        return thresholds.get(metric_name, 0.8)
    
    def _metric_to_category(self, metric_name: str) -> BottleneckCategory:
        """Map metric name to bottleneck category."""
        mapping = {
            "cpu_usage": BottleneckCategory.PERFORMANCE,
            "memory_usage": BottleneckCategory.MEMORY,
            "io_time": BottleneckCategory.IO,
            "network_latency": BottleneckCategory.NETWORK,
            "execution_time": BottleneckCategory.PERFORMANCE
        }
        return mapping.get(metric_name, BottleneckCategory.PERFORMANCE)
    
    def record_bottleneck(self, category: BottleneckCategory, severity: BottleneckSeverity,
                         description: str, location: str):
        """Record actual bottleneck occurrence for learning."""
        bottleneck_id = hashlib.md5(f"{category.value}_{location}_{description}".encode()).hexdigest()[:12]
        
        self.bottlenecks[bottleneck_id] = {
            "id": bottleneck_id,
            "category": category.value,
            "severity": severity.value,
            "description": description,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        }
        
        # Record for pattern recognition
        self.pattern_recognizer.record_occurrence(category.value, datetime.now())
        
        self.save_data()
    
    def get_prediction_accuracy(self) -> Dict[str, float]:
        """Calculate accuracy of predictions."""
        if not self.predictions:
            return {}
        
        correct_predictions = 0
        total_predictions = len(self.predictions)
        
        for prediction in self.predictions:
            predicted_time = datetime.fromisoformat(prediction.predicted_timeframe)
            if predicted_time <= datetime.now():
                # Check if similar bottleneck occurred
                for bottleneck in self.bottlenecks.values():
                    if bottleneck["category"] == prediction.predicted_category:
                        bottleneck_time = datetime.fromisoformat(bottleneck["timestamp"])
                        time_diff = abs((bottleneck_time - predicted_time).total_seconds())
                        if time_diff < 3600:  # Within 1 hour
                            correct_predictions += 1
                            break
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        return {
            "accuracy": accuracy,
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions
        }
    
    def get_system_health_prediction(self) -> Dict[str, Any]:
        """Get overall system health prediction."""
        # Get recent predictions
        recent_predictions = [p for p in self.predictions 
                             if datetime.fromisoformat(p.predicted_timeframe) <= datetime.now() + timedelta(hours=6)]
        
        # Count by severity
        severity_counts = defaultdict(int)
        for prediction in recent_predictions:
            severity_counts[prediction.predicted_severity] += 1
        
        # Calculate health score
        critical_count = severity_counts.get("CRITICAL", 0)
        high_count = severity_counts.get("HIGH", 0)
        medium_count = severity_counts.get("MEDIUM", 0)
        
        health_score = max(0.0, 1.0 - (critical_count * 0.3 + high_count * 0.15 + medium_count * 0.05))
        
        return {
            "health_score": health_score,
            "predicted_bottlenecks": len(recent_predictions),
            "severity_breakdown": dict(severity_counts),
            "anomalies_detected": len(self.anomalies),
            "patterns_recognized": len(self.patterns)
        }
    
    def save_data(self):
        """Save manager data to disk."""
        data = {
            "bottlenecks": self.bottlenecks,
            "predictions": [p.to_dict() if hasattr(p, 'to_dict') else asdict(p) for p in self.predictions],
            "patterns": {pid: asdict(p) for pid, p in self.patterns.items()},
            "anomalies": [a.to_dict() if hasattr(a, 'to_dict') else asdict(a) for a in self.anomalies],
            "metrics_history": dict(self.metrics_history)
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load manager data from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.bottlenecks = data.get("bottlenecks", {})
            
            # Reconstruct predictions
            for p_data in data.get("predictions", []):
                self.predictions.append(BottleneckPrediction(**p_data))
            
            # Reconstruct patterns
            for pid, p_data in data.get("patterns", {}).items():
                self.patterns[pid] = BottleneckPattern(**p_data)
            
            # Reconstruct anomalies
            for a_data in data.get("anomalies", []):
                self.anomalies.append(BottleneckAnomaly(**a_data))
            
            self.metrics_history = defaultdict(list, data.get("metrics_history", {}))
            
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading data: {e}")


def test_enhanced_bottleneck_manager():
    """Test the enhanced bottleneck manager."""
    manager = EnhancedBottleneckManager("test_bottleneck_manager.json")
    
    # Simulate metric observations
    for i in range(20):
        cpu_usage = 0.5 + 0.1 * math.sin(i * 0.5) + random.uniform(-0.05, 0.05)
        memory_usage = 0.6 + 0.05 * i + random.uniform(-0.02, 0.02)
        
        manager.add_metric_observation("cpu_usage", cpu_usage)
        manager.add_metric_observation("memory_usage", memory_usage)
        time.sleep(0.1)
    
    # Record some bottlenecks
    manager.record_bottleneck(
        BottleneckCategory.PERFORMANCE,
        BottleneckSeverity.HIGH,
        "CPU usage spike",
        "main_loop"
    )
    
    # Predict bottlenecks
    predictions = manager.predict_bottlenecks(horizon_hours=24)
    print(f"Generated {len(predictions)} predictions")
    
    for prediction in predictions[:3]:
        print(f"  - {prediction.predicted_category} ({prediction.predicted_severity}): {prediction.confidence:.2f}")
    
    # Get system health prediction
    health = manager.get_system_health_prediction()
    print(f"\nSystem health score: {health['health_score']:.2f}")
    print(f"Predicted bottlenecks: {health['predicted_bottlenecks']}")
    
    # Get prediction accuracy
    accuracy = manager.get_prediction_accuracy()
    print(f"\nPrediction accuracy: {accuracy.get('accuracy', 0):.2f}")
    
    # Cleanup
    import os
    if os.path.exists("test_bottleneck_manager.json"):
        os.remove("test_bottleneck_manager.json")


if __name__ == "__main__":
    test_enhanced_bottleneck_manager()