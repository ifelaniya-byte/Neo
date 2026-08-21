"""
ENHANCED SELF-MONITORING WITH ADVANCED HEALTH ASSESSMENT

Advanced monitoring system with:
- Multi-dimensional health metrics
- Predictive health analysis
- Anomaly detection and early warning
- Trend analysis and forecasting
- Resource utilization monitoring
- Performance degradation detection
- Automated health reports
"""

import time
import json
import random
import hashlib
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque


class HealthStatus(Enum):
    """Overall health status levels."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"


class MetricCategory(Enum):
    """Categories of health metrics."""
    PERFORMANCE = "PERFORMANCE"
    RESOURCE = "RESOURCE"
    STABILITY = "STABILITY"
    QUALITY = "QUALITY"
    SECURITY = "SECURITY"
    NETWORK = "NETWORK"


class AlertSeverity(Enum):
    """Severity levels for health alerts."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class HealthMetric:
    """A single health metric with metadata."""
    name: str
    category: str
    value: float
    unit: str
    timestamp: str
    threshold_min: float
    threshold_max: float
    status: str
    trend: str
    historical_values: List[float]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class HealthAlert:
    """A health alert generated from monitoring."""
    id: str
    severity: str
    metric_name: str
    message: str
    timestamp: str
    value: float
    threshold: float
    acknowledged: bool
    resolved: bool
    resolution_notes: str


@dataclass
class HealthTrend:
    """Trend analysis for a health metric."""
    metric_name: str
    trend_direction: str  # IMPROVING, DECLINING, STABLE
    trend_strength: float
    predicted_value: float
    confidence: float
    time_horizon: str
    recommendations: List[str]


@dataclass
class HealthReport:
    """Comprehensive health report."""
    id: str
    timestamp: str
    overall_status: str
    health_score: float
    metrics_summary: Dict[str, Dict]
    active_alerts: List[str]
    trends: List[Dict]
    recommendations: List[str]
    resource_usage: Dict[str, float]
    performance_summary: Dict[str, float]


class TrendAnalyzer:
    """Analyze trends in health metrics."""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_observation(self, metric_name: str, value: float):
        """Add observation to history."""
        self.history[metric_name].append(value)
    
    def analyze_trend(self, metric_name: str) -> HealthTrend:
        """Analyze trend for a metric."""
        values = list(self.history[metric_name])
        
        if len(values) < 3:
            return HealthTrend(
                metric_name=metric_name,
                trend_direction="STABLE",
                trend_strength=0.0,
                predicted_value=values[-1] if values else 0.0,
                confidence=0.0,
                time_horizon="1h",
                recommendations=[]
            )
        
        # Calculate trend using linear regression
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "IMPROVING" if self._is_higher_better(metric_name) else "DECLINING"
        elif slope < -0.01:
            trend_direction = "DECLINING" if self._is_higher_better(metric_name) else "IMPROVING"
        else:
            trend_direction = "STABLE"
        
        # Calculate trend strength
        trend_strength = min(1.0, abs(slope) * 10)
        
        # Predict future value
        predicted_value = values[-1] + slope * 5  # 5 steps ahead
        
        # Calculate confidence
        variance = sum((v - sum(y)/n) ** 2 for v in values) / n
        confidence = max(0.0, min(1.0, 1.0 - variance / (sum(y)/n + 1)))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_name, trend_direction, trend_strength)
        
        return HealthTrend(
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            predicted_value=predicted_value,
            confidence=confidence,
            time_horizon="1h",
            recommendations=recommendations
        )
    
    def _is_higher_better(self, metric_name: str) -> bool:
        """Determine if higher values are better for this metric."""
        higher_better_metrics = [
            "accuracy", "success_rate", "throughput", "cache_hit_rate",
            "efficiency", "availability", "reliability"
        ]
        return any(hbm in metric_name.lower() for hbm in higher_better_metrics)
    
    def _generate_recommendations(self, metric_name: str, trend_direction: str, 
                                trend_strength: float) -> List[str]:
        """Generate recommendations based on trend."""
        recommendations = []
        
        if trend_strength > 0.5:
            if trend_direction == "DECLINING":
                recommendations.append(f"Immediate attention required for {metric_name}")
                recommendations.append(f"Investigate root cause of {metric_name} degradation")
            elif trend_direction == "IMPROVING":
                recommendations.append(f"Continue current practices for {metric_name}")
                recommendations.append(f"Monitor {metric_name} for sustained improvement")
        
        return recommendations


class AnomalyDetector:
    """Detect anomalies in health metrics."""
    
    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity  # Standard deviations for anomaly threshold
        self.baselines: Dict[str, Dict] = {}
    
    def update_baseline(self, metric_name: str, values: List[float]):
        """Update baseline statistics for a metric."""
        if not values:
            return
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        
        self.baselines[metric_name] = {
            "mean": mean,
            "std": std,
            "min": min(values),
            "max": max(values),
            "count": len(values)
        }
    
    def detect_anomaly(self, metric_name: str, value: float) -> Optional[Dict]:
        """Detect if current value is anomalous."""
        if metric_name not in self.baselines:
            return None
        
        baseline = self.baselines[metric_name]
        
        # Z-score based detection
        if baseline["std"] > 0:
            z_score = abs(value - baseline["mean"]) / baseline["std"]
            
            if z_score > self.sensitivity:
                return {
                    "metric_name": metric_name,
                    "value": value,
                    "baseline_mean": baseline["mean"],
                    "z_score": z_score,
                    "severity": "HIGH" if z_score > 3 else "MEDIUM",
                    "type": "STATISTICAL"
                }
        
        # Range-based detection
        if value < baseline["min"] or value > baseline["max"]:
            return {
                "metric_name": metric_name,
                "value": value,
                "baseline_range": (baseline["min"], baseline["max"]),
                "severity": "HIGH",
                "type": "RANGE"
            }
        
        return None


class EnhancedMonitoringSystem:
    """
    Enhanced monitoring system with advanced health assessment.
    """
    
    def __init__(self, storage_path="enhanced_monitoring_system.json"):
        self.storage_path = storage_path
        self.metrics: Dict[str, HealthMetric] = {}
        self.alerts: Dict[str, HealthAlert] = {}
        self.trends: Dict[str, HealthTrend] = {}
        self.reports: List[HealthReport] = []
        
        # Monitoring components
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # System state
        self.start_time = datetime.now()
        self.last_health_check = None
        self.health_score_history: List[Tuple[str, float]] = []
        
        self.load_data()
    
    def register_metric(self, name: str, category: MetricCategory, unit: str,
                       threshold_min: float, threshold_max: float):
        """Register a new health metric for monitoring."""
        metric = HealthMetric(
            name=name,
            category=category.value,
            value=0.0,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            status="OK",
            trend="STABLE",
            historical_values=[]
        )
        
        self.metrics[name] = metric
    
    def update_metric(self, name: str, value: float) -> Optional[HealthAlert]:
        """Update a metric value and check for alerts."""
        if name not in self.metrics:
            return None
        
        metric = self.metrics[name]
        metric.value = value
        metric.timestamp = datetime.now().isoformat()
        metric.historical_values.append(value)
        
        # Keep only last 100 historical values
        if len(metric.historical_values) > 100:
            metric.historical_values = metric.historical_values[-100:]
        
        # Update trend analyzer
        self.trend_analyzer.add_observation(name, value)
        
        # Update anomaly detector baseline
        if len(metric.historical_values) >= 10:
            self.anomaly_detector.update_baseline(name, metric.historical_values[-10:])
        
        # Check thresholds
        alert = self._check_thresholds(metric)
        if alert:
            self.alerts[alert.id] = alert
        
        # Check for anomalies
        anomaly = self.anomaly_detector.detect_anomaly(name, value)
        if anomaly:
            anomaly_alert = self._create_anomaly_alert(anomaly)
            self.alerts[anomaly_alert.id] = anomaly_alert
        
        # Update metric status
        metric.status = self._determine_metric_status(metric)
        
        # Update trend
        if len(metric.historical_values) >= 3:
            trend = self.trend_analyzer.analyze_trend(name)
            metric.trend = trend.trend_direction
            self.trends[name] = trend
        
        self.save_data()
        return alert
    
    def _check_thresholds(self, metric: HealthMetric) -> Optional[HealthAlert]:
        """Check if metric violates thresholds."""
        if metric.value < metric.threshold_min:
            return self._create_alert(
                metric.name,
                AlertSeverity.ERROR,
                f"{metric.name} below minimum threshold",
                metric.value,
                metric.threshold_min
            )
        elif metric.value > metric.threshold_max:
            return self._create_alert(
                metric.name,
                AlertSeverity.ERROR,
                f"{metric.name} above maximum threshold",
                metric.value,
                metric.threshold_max
            )
        
        return None
    
    def _create_alert(self, metric_name: str, severity: AlertSeverity, 
                    message: str, value: float, threshold: float) -> HealthAlert:
        """Create a health alert."""
        alert_id = hashlib.md5(f"{metric_name}_{severity.value}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        return HealthAlert(
            id=alert_id,
            severity=severity.value,
            metric_name=metric_name,
            message=message,
            timestamp=datetime.now().isoformat(),
            value=value,
            threshold=threshold,
            acknowledged=False,
            resolved=False,
            resolution_notes=""
        )
    
    def _create_anomaly_alert(self, anomaly: Dict) -> HealthAlert:
        """Create an alert from anomaly detection."""
        alert_id = hashlib.md5(f"anomaly_{anomaly['metric_name']}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        return HealthAlert(
            id=alert_id,
            severity=anomaly["severity"],
            metric_name=anomaly["metric_name"],
            message=f"Anomaly detected in {anomaly['metric_name']}: {anomaly['type']}",
            timestamp=datetime.now().isoformat(),
            value=anomaly["value"],
            threshold=anomaly.get("baseline_mean", 0.0),
            acknowledged=False,
            resolved=False,
            resolution_notes=""
        )
    
    def _determine_metric_status(self, metric: HealthMetric) -> str:
        """Determine status of a metric."""
        if metric.value < metric.threshold_min * 0.8 or metric.value > metric.threshold_max * 1.2:
            return "CRITICAL"
        elif metric.value < metric.threshold_min or metric.value > metric.threshold_max:
            return "WARNING"
        else:
            return "OK"
    
    def calculate_health_score(self) -> float:
        """Calculate overall system health score."""
        if not self.metrics:
            return 1.0
        
        total_score = 0.0
        metric_count = 0
        
        for metric in self.metrics.values():
            # Normalize value to 0-1 range
            range_size = metric.threshold_max - metric.threshold_min
            if range_size > 0:
                normalized = (metric.value - metric.threshold_min) / range_size
                normalized = max(0.0, min(1.0, normalized))
            else:
                normalized = 1.0
            
            # Apply status penalty
            if metric.status == "CRITICAL":
                normalized *= 0.5
            elif metric.status == "WARNING":
                normalized *= 0.75
            
            total_score += normalized
            metric_count += 1
        
        if metric_count == 0:
            return 1.0
        
        # Apply alert penalty
        active_alerts = [a for a in self.alerts.values() if not a.resolved]
        critical_alerts = sum(1 for a in active_alerts if a.severity == "CRITICAL")
        error_alerts = sum(1 for a in active_alerts if a.severity == "ERROR")
        
        alert_penalty = (critical_alerts * 0.2 + error_alerts * 0.1)
        health_score = max(0.0, (total_score / metric_count) - alert_penalty)
        
        return health_score
    
    def determine_health_status(self, health_score: float) -> HealthStatus:
        """Determine overall health status from score."""
        if health_score >= 0.9:
            return HealthStatus.EXCELLENT
        elif health_score >= 0.75:
            return HealthStatus.GOOD
        elif health_score >= 0.6:
            return HealthStatus.FAIR
        elif health_score >= 0.4:
            return HealthStatus.POOR
        else:
            return HealthStatus.CRITICAL
    
    def generate_health_report(self) -> HealthReport:
        """Generate comprehensive health report."""
        report_id = hashlib.md5(f"health_report_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        health_score = self.calculate_health_score()
        health_status = self.determine_health_status(health_score)
        
        # Summarize metrics by category
        metrics_summary = defaultdict(lambda: {"count": 0, "ok": 0, "warning": 0, "critical": 0})
        for metric in self.metrics.values():
            metrics_summary[metric.category]["count"] += 1
            metrics_summary[metric.category][metric.status.lower()] += 1
        
        # Get active alerts
        active_alerts = [a.id for a in self.alerts.values() if not a.resolved]
        
        # Get recent trends
        recent_trends = [t.to_dict() if hasattr(t, 'to_dict') else asdict(t) 
                        for t in self.trends.values()]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(health_score, health_status)
        
        # Calculate resource usage
        resource_usage = self._calculate_resource_usage()
        
        # Calculate performance summary
        performance_summary = self._calculate_performance_summary()
        
        report = HealthReport(
            id=report_id,
            timestamp=datetime.now().isoformat(),
            overall_status=health_status.value,
            health_score=health_score,
            metrics_summary=dict(metrics_summary),
            active_alerts=active_alerts,
            trends=recent_trends,
            recommendations=recommendations,
            resource_usage=resource_usage,
            performance_summary=performance_summary
        )
        
        self.reports.append(report)
        self.last_health_check = datetime.now()
        self.health_score_history.append((datetime.now().isoformat(), health_score))
        
        # Keep only last 100 health scores
        if len(self.health_score_history) > 100:
            self.health_score_history = self.health_score_history[-100:]
        
        self.save_data()
        return report
    
    def _generate_recommendations(self, health_score: float, 
                                health_status: HealthStatus) -> List[str]:
        """Generate recommendations based on health status."""
        recommendations = []
        
        if health_status == HealthStatus.CRITICAL:
            recommendations.append("IMMEDIATE ACTION REQUIRED")
            recommendations.append("Address all critical alerts immediately")
            recommendations.append("Consider system restart if issues persist")
        elif health_status == HealthStatus.POOR:
            recommendations.append("System performance is degraded")
            recommendations.append("Prioritize resolving error-level alerts")
            recommendations.append("Review resource utilization")
        elif health_status == HealthStatus.FAIR:
            recommendations.append("Monitor system closely")
            recommendations.append("Address warning-level alerts")
            recommendations.append("Review performance trends")
        elif health_status == HealthStatus.GOOD:
            recommendations.append("System is performing well")
            recommendations.append("Continue regular monitoring")
            recommendations.append("Consider optimization opportunities")
        else:  # EXCELLENT
            recommendations.append("System is performing excellently")
            recommendations.append("Maintain current practices")
            recommendations.append("Document optimal configuration")
        
        # Add trend-based recommendations
        for trend in self.trends.values():
            if trend.trend_direction == "DECLINING" and trend.trend_strength > 0.5:
                recommendations.append(f"Investigate declining trend in {trend.metric_name}")
        
        return recommendations
    
    def _calculate_resource_usage(self) -> Dict[str, float]:
        """Calculate current resource usage."""
        usage = {}
        
        # Get resource-related metrics
        resource_metrics = ["cpu_usage", "memory_usage", "disk_usage", "network_usage"]
        
        for metric_name in resource_metrics:
            if metric_name in self.metrics:
                usage[metric_name] = self.metrics[metric_name].value
        
        return usage
    
    def _calculate_performance_summary(self) -> Dict[str, float]:
        """Calculate performance summary."""
        summary = {}
        
        # Get performance-related metrics
        performance_metrics = ["response_time", "throughput", "error_rate", "success_rate"]
        
        for metric_name in performance_metrics:
            if metric_name in self.metrics:
                summary[metric_name] = self.metrics[metric_name].value
        
        return summary
    
    def acknowledge_alert(self, alert_id: str, notes: str = ""):
        """Acknowledge a health alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            self.alerts[alert_id].resolution_notes = notes
            self.save_data()
    
    def resolve_alert(self, alert_id: str, notes: str = ""):
        """Resolve a health alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolution_notes = notes
            self.save_data()
    
    def get_health_history(self, hours: int = 24) -> List[Tuple[str, float]]:
        """Get health score history for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            (timestamp, score) for timestamp, score in self.health_score_history
            if datetime.fromisoformat(timestamp) >= cutoff_time
        ]
    
    def predict_health(self, hours_ahead: int = 1) -> Dict[str, Any]:
        """Predict future health based on current trends."""
        predictions = {}
        
        for metric_name, trend in self.trends.items():
            if trend.confidence > 0.7:
                predictions[metric_name] = {
                    "predicted_value": trend.predicted_value,
                    "confidence": trend.confidence,
                    "trend_direction": trend.trend_direction,
                    "time_horizon": f"{hours_ahead}h"
                }
        
        # Predict overall health
        if predictions:
            avg_predicted_change = sum(
                (p["predicted_value"] - self.metrics[mn].value) / self.metrics[mn].value
                for mn, p in predictions.items()
                if self.metrics[mn].value != 0
            ) / len(predictions)
            
            current_health = self.calculate_health_score()
            predicted_health = max(0.0, min(1.0, current_health + avg_predicted_change))
            
            predictions["overall_health"] = {
                "current_score": current_health,
                "predicted_score": predicted_health,
                "predicted_status": self.determine_health_status(predicted_health).value,
                "confidence": sum(p["confidence"] for p in predictions.values()) / len(predictions)
            }
        
        return predictions
    
    def save_data(self):
        """Save monitoring system data to disk."""
        data = {
            "metrics": {name: m.to_dict() if hasattr(m, 'to_dict') else asdict(m) 
                       for name, m in self.metrics.items()},
            "alerts": {aid: a.to_dict() if hasattr(a, 'to_dict') else asdict(a) 
                      for aid, a in self.alerts.items()},
            "trends": {name: t.to_dict() if hasattr(t, 'to_dict') else asdict(t) 
                      for name, t in self.trends.items()},
            "reports": [r.to_dict() if hasattr(r, 'to_dict') else asdict(r) 
                       for r in self.reports],
            "health_score_history": self.health_score_history,
            "start_time": self.start_time.isoformat()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load monitoring system data from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct metrics
            for name, m_data in data.get("metrics", {}).items():
                self.metrics[name] = HealthMetric(**m_data)
            
            # Reconstruct alerts
            for aid, a_data in data.get("alerts", {}).items():
                self.alerts[aid] = HealthAlert(**a_data)
            
            # Reconstruct trends
            for name, t_data in data.get("trends", {}).items():
                self.trends[name] = HealthTrend(**t_data)
            
            # Reconstruct reports
            for r_data in data.get("reports", []):
                self.reports.append(HealthReport(**r_data))
            
            self.health_score_history = data.get("health_score_history", [])
            self.start_time = datetime.fromisoformat(data.get("start_time", datetime.now().isoformat()))
            
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading monitoring data: {e}")


def test_enhanced_monitoring_system():
    """Test the enhanced monitoring system."""
    monitoring = EnhancedMonitoringSystem("test_monitoring_system.json")
    
    # Register some metrics
    monitoring.register_metric("cpu_usage", MetricCategory.RESOURCE, "%", 0.0, 100.0)
    monitoring.register_metric("memory_usage", MetricCategory.RESOURCE, "%", 0.0, 100.0)
    monitoring.register_metric("response_time", MetricCategory.PERFORMANCE, "ms", 0.0, 5000.0)
    monitoring.register_metric("success_rate", MetricCategory.QUALITY, "%", 0.0, 100.0)
    
    # Simulate metric updates
    for i in range(20):
        cpu = 30 + 5 * math.sin(i * 0.5) + random.uniform(-2, 2)
        memory = 50 + 0.5 * i + random.uniform(-1, 1)
        response_time = 100 + 10 * math.sin(i * 0.3) + random.uniform(-5, 5)
        success_rate = 95 + random.uniform(-2, 3)
        
        monitoring.update_metric("cpu_usage", cpu)
        monitoring.update_metric("memory_usage", memory)
        monitoring.update_metric("response_time", response_time)
        monitoring.update_metric("success_rate", success_rate)
        
        time.sleep(0.1)
    
    # Generate health report
    report = monitoring.generate_health_report()
    
    print(f"Health Report - {report.timestamp}")
    print(f"Overall Status: {report.overall_status}")
    print(f"Health Score: {report.health_score:.2f}")
    print(f"Active Alerts: {len(report.active_alerts)}")
    print(f"Recommendations: {report.recommendations}")
    
    # Predict health
    predictions = monitoring.predict_health(hours_ahead=1)
    print(f"\nHealth Predictions:")
    for metric, prediction in predictions.items():
        print(f"  {metric}: {prediction}")
    
    # Get health history
    history = monitoring.get_health_history(hours=1)
    print(f"\nHealth History (last hour): {len(history)} data points")
    
    # Cleanup
    import os
    if os.path.exists("test_monitoring_system.json"):
        os.remove("test_monitoring_system.json")


if __name__ == "__main__":
    test_enhanced_monitoring_system()