"""
Metrics collection and monitoring module.

Provides comprehensive metrics for security scoring, connection stability,
and performance monitoring.
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MetricData:
    """Data class for storing metric information."""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecurityScoring:
    """
    Security scoring system for evaluating security posture.
    
    Calculates security scores based on multiple security checks including
    firewall status, encryption level, authentication strength, and more.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize security scoring.
        
        Args:
            config: Security configuration dictionary
        """
        self.config = config
        self.weight = config.get('weight', 0.4)
        self.thresholds = config.get('thresholds', {})
        self.checks = config.get('checks', [])
    
    def calculate_score(self, security_data: Dict[str, Any]) -> float:
        """
        Calculate overall security score.
        
        Args:
            security_data: Dictionary containing security check results
            
        Returns:
            Security score (0-100)
        """
        if not security_data:
            return 0.0
        
        total_score = 0.0
        check_count = 0
        
        for check in self.checks:
            if check in security_data:
                # Validate that the value is numeric
                value = security_data[check]
                if isinstance(value, (int, float)):
                    total_score += value
                    check_count += 1
        
        if check_count == 0:
            return 0.0
        
        return total_score / check_count
    
    def get_severity_level(self, score: float) -> str:
        """
        Determine severity level based on score.
        
        Args:
            score: Security score (0-100)
            
        Returns:
            Severity level string
        """
        if score >= self.thresholds.get('critical', 90):
            return 'critical'
        elif score >= self.thresholds.get('high', 70):
            return 'high'
        elif score >= self.thresholds.get('medium', 50):
            return 'medium'
        else:
            return 'low'


class ConnectionStability:
    """
    Connection stability monitoring system.
    
    Tracks connection metrics including uptime, packet loss, latency,
    jitter, and signal strength.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connection stability monitoring.
        
        Args:
            config: Connection configuration dictionary
        """
        self.config = config
        self.weight = config.get('weight', 0.3)
        self.thresholds = config.get('thresholds', {})
        self.metrics = config.get('metrics', [])
        self.check_interval = config.get('check_interval', 60)
    
    def calculate_stability_score(self, connection_data: Dict[str, Any]) -> float:
        """
        Calculate connection stability score.
        
        Args:
            connection_data: Dictionary containing connection metrics
            
        Returns:
            Stability score (0-100)
        """
        if not connection_data:
            return 0.0
        
        # Calculate weighted score based on different metrics
        uptime = connection_data.get('uptime_percentage', 0)
        packet_loss = 100 - connection_data.get('packet_loss', 0)
        latency_score = max(0, 100 - connection_data.get('latency', 0) / 10)
        signal_strength = connection_data.get('signal_strength', 0)
        
        # Weighted average
        score = (
            uptime * 0.4 +
            packet_loss * 0.3 +
            latency_score * 0.2 +
            signal_strength * 0.1
        )
        
        return min(100.0, max(0.0, score))
    
    def get_stability_level(self, score: float) -> str:
        """
        Determine stability level based on score.
        
        Args:
            score: Stability score (0-100)
            
        Returns:
            Stability level string
        """
        if score >= self.thresholds.get('excellent', 99.5):
            return 'excellent'
        elif score >= self.thresholds.get('good', 98.0):
            return 'good'
        elif score >= self.thresholds.get('fair', 95.0):
            return 'fair'
        else:
            return 'poor'


class PerformanceMonitoring:
    """
    Performance monitoring system.
    
    Monitors system performance including throughput, bandwidth utilization,
    CPU usage, memory usage, and disk I/O.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize performance monitoring.
        
        Args:
            config: Performance configuration dictionary
        """
        self.config = config
        self.weight = config.get('weight', 0.3)
        self.thresholds = config.get('thresholds', {})
        self.metrics = config.get('metrics', [])
        self.check_interval = config.get('check_interval', 30)
    
    def calculate_performance_score(self, performance_data: Dict[str, Any]) -> float:
        """
        Calculate overall performance score.
        
        Args:
            performance_data: Dictionary containing performance metrics
            
        Returns:
            Performance score (0-100)
        """
        if not performance_data:
            return 0.0
        
        # Calculate inverse scores for resource usage (lower is better)
        cpu_score = 100 - performance_data.get('cpu_usage', 0)
        memory_score = 100 - performance_data.get('memory_usage', 0)
        
        # Calculate direct scores for throughput and bandwidth
        throughput_score = performance_data.get('throughput_score', 0)
        bandwidth_score = 100 - performance_data.get('bandwidth_utilization', 0)
        disk_io_score = 100 - performance_data.get('disk_io_usage', 0)
        
        # Weighted average
        score = (
            throughput_score * 0.3 +
            bandwidth_score * 0.2 +
            cpu_score * 0.2 +
            memory_score * 0.2 +
            disk_io_score * 0.1
        )
        
        return min(100.0, max(0.0, score))
    
    def get_performance_level(self, score: float) -> str:
        """
        Determine performance level based on score.
        
        Args:
            score: Performance score (0-100)
            
        Returns:
            Performance level string
        """
        if score >= self.thresholds.get('excellent', 90):
            return 'excellent'
        elif score >= self.thresholds.get('good', 75):
            return 'good'
        elif score >= self.thresholds.get('fair', 60):
            return 'fair'
        else:
            return 'poor'


class MetricsCollector:
    """
    Main metrics collector that aggregates all monitoring subsystems.
    
    Collects and manages metrics from security scoring, connection stability,
    and performance monitoring systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize metrics collector.
        
        Args:
            config: Complete metrics configuration dictionary
        """
        self.config = config
        self.security_scoring = SecurityScoring(config.get('security', {}))
        self.connection_stability = ConnectionStability(config.get('connection', {}))
        self.performance_monitoring = PerformanceMonitoring(config.get('performance', {}))
        
        self.collection_interval = config.get('collection', {}).get('interval', 60)
        self.metrics_history: List[Dict[str, Any]] = []
    
    def collect_metrics(
        self,
        security_data: Optional[Dict[str, Any]] = None,
        connection_data: Optional[Dict[str, Any]] = None,
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect all metrics and calculate composite score.
        
        Args:
            security_data: Security check results
            connection_data: Connection metrics
            performance_data: Performance metrics
            
        Returns:
            Dictionary containing all collected metrics and scores
        """
        timestamp = datetime.now().isoformat()
        
        # Calculate individual scores
        security_score = self.security_scoring.calculate_score(security_data or {})
        connection_score = self.connection_stability.calculate_stability_score(connection_data or {})
        performance_score = self.performance_monitoring.calculate_performance_score(performance_data or {})
        
        # Calculate composite score
        composite_score = (
            security_score * self.security_scoring.weight +
            connection_score * self.connection_stability.weight +
            performance_score * self.performance_monitoring.weight
        )
        
        metrics = {
            'timestamp': timestamp,
            'security': {
                'score': security_score,
                'level': self.security_scoring.get_severity_level(security_score),
                'weight': self.security_scoring.weight,
                'data': security_data or {}
            },
            'connection': {
                'score': connection_score,
                'level': self.connection_stability.get_stability_level(connection_score),
                'weight': self.connection_stability.weight,
                'data': connection_data or {}
            },
            'performance': {
                'score': performance_score,
                'level': self.performance_monitoring.get_performance_level(performance_score),
                'weight': self.performance_monitoring.weight,
                'data': performance_data or {}
            },
            'composite_score': composite_score
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent metrics.
        
        Returns:
            Latest metrics dictionary or None if no metrics collected
        """
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_summary(self, timeframe: int = 3600) -> Dict[str, Any]:
        """
        Get aggregated metrics summary for a given timeframe.
        
        Args:
            timeframe: Timeframe in seconds (default: 1 hour)
            
        Returns:
            Summary of metrics including averages and trends
        """
        if not self.metrics_history:
            return {}
        
        current_time = time.time()
        recent_metrics = [
            m for m in self.metrics_history
            if current_time - time.mktime(
                time.strptime(m['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
            ) <= timeframe
        ]
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        avg_security = sum(m['security']['score'] for m in recent_metrics) / len(recent_metrics)
        avg_connection = sum(m['connection']['score'] for m in recent_metrics) / len(recent_metrics)
        avg_performance = sum(m['performance']['score'] for m in recent_metrics) / len(recent_metrics)
        avg_composite = sum(m['composite_score'] for m in recent_metrics) / len(recent_metrics)
        
        return {
            'timeframe_seconds': timeframe,
            'sample_count': len(recent_metrics),
            'averages': {
                'security_score': avg_security,
                'connection_score': avg_connection,
                'performance_score': avg_performance,
                'composite_score': avg_composite
            },
            'latest': recent_metrics[-1] if recent_metrics else None
        }
