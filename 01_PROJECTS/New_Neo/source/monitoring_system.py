"""
PROJECT APEX: REAL-TIME MONITORING & ANOMALY DETECTION SYSTEM
Provides continuous monitoring, anomaly detection, and alerting.
Detects performance regressions, memory leaks, and unusual patterns.
"""

import time
import json
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import threading

class AnomalySeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class MetricType(Enum):
    EXECUTION_TIME = "EXECUTION_TIME"
    MEMORY_USAGE = "MEMORY_USAGE"
    CPU_USAGE = "CPU_USAGE"
    IO_OPERATIONS = "IO_OPERATIONS"
    ERROR_RATE = "ERROR_RATE"
    NETWORK_LATENCY = "NETWORK_LATENCY"

@dataclass
class MetricData:
    timestamp: float
    value: float
    metric_type: MetricType
    context: Dict
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Anomaly:
    id: str
    severity: AnomalySeverity
    metric_type: MetricType
    description: str
    detected_at: float
    value: float
    expected_range: Tuple[float, float]
    confidence: float
    resolved: bool
    
    def to_dict(self):
        return asdict(self)

class MonitoringSystem:
    """
    Real-time monitoring system with anomaly detection.
    Uses statistical analysis and machine learning for pattern recognition.
    """
    
    def __init__(self, history_size=1000, alert_threshold=2.0):
        self.history_size = history_size
        self.alert_threshold = alert_threshold  # Standard deviations
        
        self.metrics_history = {
            metric_type: deque(maxlen=history_size) 
            for metric_type in MetricType
        }
        
        self.anomalies = []
        self.baseline_metrics = {}
        self.trend_data = {}
        
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.Lock()
    
    def start_monitoring(self, check_interval=1.0):
        """Start continuous monitoring in background thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
    
    def _monitoring_loop(self, check_interval):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                self.check_system_health()
                time.sleep(check_interval)
            except Exception as e:
                print(f"[MONITOR] Error in monitoring loop: {e}")
    
    def record_metric(self, metric_type: MetricType, value: float, context: Dict = None):
        """
        Record a metric value with timestamp.
        Automatically checks for anomalies.
        """
        if context is None:
            context = {}
        
        metric = MetricData(
            timestamp=time.time(),
            value=value,
            metric_type=metric_type,
            context=context
        )
        
        with self.lock:
            self.metrics_history[metric_type].append(metric)
            
            # Check for anomaly
            anomaly = self.detect_anomaly(metric_type, value)
            if anomaly:
                self.anomalies.append(anomaly)
                self.trigger_alert(anomaly)
    
    def detect_anomaly(self, metric_type: MetricType, value: float) -> Optional[Anomaly]:
        """
        Detect if a metric value is anomalous using statistical analysis.
        Uses z-score analysis and trend detection.
        """
        history = list(self.metrics_history[metric_type])
        
        if len(history) < 10:
            return None  # Not enough data for analysis
        
        values = [m.value for m in history]
        
        # Calculate statistics
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        if stdev == 0:
            return None
        
        # Calculate z-score
        z_score = abs(value - mean) / stdev
        
        if z_score > self.alert_threshold:
            # Determine severity based on deviation
            if z_score > 4.0:
                severity = AnomalySeverity.CRITICAL
            elif z_score > 3.0:
                severity = AnomalySeverity.HIGH
            elif z_score > 2.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
            
            # Calculate expected range
            expected_range = (mean - 2*stdev, mean + 2*stdev)
            
            return Anomaly(
                id=f"{metric_type.value}_{int(time.time())}",
                severity=severity,
                metric_type=metric_type,
                description=f"{metric_type.value} value {value:.2f} deviates {z_score:.2f}σ from mean {mean:.2f}",
                detected_at=time.time(),
                value=value,
                expected_range=expected_range,
                confidence=min(0.99, z_score / 5.0),
                resolved=False
            )
        
        return None
    
    def check_system_health(self):
        """
        Perform comprehensive system health check.
        Monitors key metrics and detects patterns.
        """
        import psutil
        import os
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.record_metric(MetricType.CPU_USAGE, cpu_percent)
        
        # Memory Usage
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        self.record_metric(MetricType.MEMORY_USAGE, memory_percent)
        
        # Disk I/O (simplified)
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                io_operations = disk_io.read_count + disk_io.write_count
                self.record_metric(MetricType.IO_OPERATIONS, io_operations)
        except:
            pass
        
        # Check for memory leaks (trend analysis)
        self.detect_memory_leaks()
        
        # Check for performance degradation
        self.detect_performance_degradation()
    
    def detect_memory_leaks(self) -> Optional[Anomaly]:
        """
        Detect memory leaks by analyzing memory usage trends.
        Uses linear regression to identify upward trends.
        """
        history = list(self.metrics_history[MetricType.MEMORY_USAGE])
        
        if len(history) < 20:
            return None
        
        # Calculate trend
        values = [m.value for m in history[-20:]]
        timestamps = [m.timestamp for m in history[-20:]]
        
        # Simple linear regression
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(t * v for t, v in zip(timestamps, values))
        sum_x2 = sum(t * t for t in timestamps)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # If slope is positive and significant, indicate potential leak
        if slope > 0.1:  # Threshold for significant upward trend
            return Anomaly(
                id=f"memory_leak_{int(time.time())}",
                severity=AnomalySeverity.HIGH,
                metric_type=MetricType.MEMORY_USAGE,
                description=f"Potential memory leak detected: upward trend of {slope:.4f} per second",
                detected_at=time.time(),
                value=values[-1],
                expected_range=(values[0], values[-1]),
                confidence=0.7,
                resolved=False
            )
        
        return None
    
    def detect_performance_degradation(self) -> Optional[Anomaly]:
        """
        Detect performance degradation by comparing recent performance to baseline.
        """
        history = list(self.metrics_history[MetricType.EXECUTION_TIME])
        
        if len(history) < 30:
            return None
        
        # Compare recent 10 measurements to baseline (first 20)
        recent_values = [m.value for m in history[-10:]]
        baseline_values = [m.value for m in history[:20]]
        
        recent_mean = statistics.mean(recent_values)
        baseline_mean = statistics.mean(baseline_values)
        
        # If recent performance is significantly worse than baseline
        if recent_mean > baseline_mean * 1.5:  # 50% degradation
            return Anomaly(
                id=f"performance_degradation_{int(time.time())}",
                severity=AnomalySeverity.HIGH,
                metric_type=MetricType.EXECUTION_TIME,
                description=f"Performance degradation detected: {recent_mean:.2f}s vs baseline {baseline_mean:.2f}s",
                detected_at=time.time(),
                value=recent_mean,
                expected_range=(baseline_mean * 0.8, baseline_mean * 1.2),
                confidence=0.8,
                resolved=False
            )
        
        return None
    
    def trigger_alert(self, anomaly: Anomaly):
        """Trigger alert for detected anomaly."""
        alert_message = f"[ALERT] {anomaly.severity.value}: {anomaly.description}"
        print(alert_message)
        
        # In production, this would send to monitoring service, slack, etc.
        # For now, just log to file
        self.log_alert(anomaly)
    
    def log_alert(self, anomaly: Anomaly):
        """Log anomaly to file for analysis."""
        try:
            with open("anomaly_log.jsonl", "a") as f:
                f.write(json.dumps(anomaly.to_dict()) + "\n")
        except Exception as e:
            print(f"[MONITOR] Error logging alert: {e}")
    
    def get_metrics_summary(self, metric_type: MetricType) -> Dict:
        """Get statistical summary for a metric type."""
        history = list(self.metrics_history[metric_type])
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'latest': values[-1] if values else None
        }
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of detected anomalies."""
        unresolved = [a for a in self.anomalies if not a.resolved]
        
        severity_counts = {}
        for anomaly in unresolved:
            severity_counts[anomaly.severity.value] = severity_counts.get(anomaly.severity.value, 0) + 1
        
        return {
            'total_anomalies': len(self.anomalies),
            'unresolved_anomalies': len(unresolved),
            'severity_breakdown': severity_counts,
            'recent_anomalies': [a.to_dict() for a in unresolved[-10:]]
        }
    
    def resolve_anomaly(self, anomaly_id: str):
        """Mark an anomaly as resolved."""
        for anomaly in self.anomalies:
            if anomaly.id == anomaly_id:
                anomaly.resolved = True
                break
    
    def export_monitoring_data(self, filepath: str):
        """Export monitoring data for analysis."""
        data = {
            'metrics_history': {
                metric_type.value: [m.to_dict() for m in history]
                for metric_type, history in self.metrics_history.items()
            },
            'anomalies': [a.to_dict() for a in self.anomalies],
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_health_score(self) -> float:
        """
        Calculate overall system health score.
        Considers anomaly count, severity, and metric stability.
        """
        if not self.anomalies:
            return 1.0
        
        unresolved = [a for a in self.anomalies if not a.resolved]
        
        if not unresolved:
            return 1.0
        
        # Penalty based on severity
        severity_penalty = {
            AnomalySeverity.CRITICAL: 0.4,
            AnomalySeverity.HIGH: 0.2,
            AnomalySeverity.MEDIUM: 0.1,
            AnomalySeverity.LOW: 0.05
        }
        
        total_penalty = sum(severity_penalty.get(a.severity, 0) for a in unresolved)
        health_score = max(0.0, 1.0 - total_penalty)
        
        return health_score