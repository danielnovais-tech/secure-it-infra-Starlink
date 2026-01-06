"""
Connection Monitor Module

Monitors Starlink connection quality including latency, packet loss,
and bandwidth metrics to inform security policy decisions.
"""

import time
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ConnectionQuality(Enum):
    """Connection quality levels based on measured metrics"""
    EXCELLENT = "excellent"  # < 20ms latency, < 0.1% loss
    GOOD = "good"            # 20-50ms latency, < 1% loss
    FAIR = "fair"            # 50-100ms latency, < 5% loss
    POOR = "poor"            # 100-200ms latency, < 10% loss
    CRITICAL = "critical"    # > 200ms latency or > 10% loss


@dataclass
class ConnectionMetrics:
    """Connection quality metrics"""
    latency_ms: float
    packet_loss_percent: float
    bandwidth_mbps: float
    jitter_ms: float
    timestamp: float
    quality: ConnectionQuality


class ConnectionMonitor:
    """
    Monitors Starlink connection quality and provides real-time metrics
    for adaptive security policy management.
    """
    
    def __init__(self, 
                 check_interval: int = 30,
                 latency_threshold_excellent: float = 20.0,
                 latency_threshold_good: float = 50.0,
                 latency_threshold_fair: float = 100.0,
                 latency_threshold_poor: float = 200.0):
        """
        Initialize connection monitor
        
        Args:
            check_interval: Seconds between connection checks
            latency_threshold_excellent: Max latency for excellent quality (ms)
            latency_threshold_good: Max latency for good quality (ms)
            latency_threshold_fair: Max latency for fair quality (ms)
            latency_threshold_poor: Max latency for poor quality (ms)
        """
        self.check_interval = check_interval
        self.thresholds = {
            'excellent': latency_threshold_excellent,
            'good': latency_threshold_good,
            'fair': latency_threshold_fair,
            'poor': latency_threshold_poor,
        }
        self._current_metrics: Optional[ConnectionMetrics] = None
        self._callbacks: list[Callable[[ConnectionMetrics], None]] = []
        self._monitoring = False
    
    def register_callback(self, callback: Callable[[ConnectionMetrics], None]) -> None:
        """Register a callback to be notified of metric updates"""
        self._callbacks.append(callback)
    
    def _determine_quality(self, latency: float, packet_loss: float) -> ConnectionQuality:
        """Determine connection quality based on metrics"""
        if latency < self.thresholds['excellent'] and packet_loss < 0.1:
            return ConnectionQuality.EXCELLENT
        elif latency < self.thresholds['good'] and packet_loss < 1.0:
            return ConnectionQuality.GOOD
        elif latency < self.thresholds['fair'] and packet_loss < 5.0:
            return ConnectionQuality.FAIR
        elif latency < self.thresholds['poor'] and packet_loss < 10.0:
            return ConnectionQuality.POOR
        else:
            return ConnectionQuality.CRITICAL
    
    def measure_connection(self) -> ConnectionMetrics:
        """
        Measure current connection metrics
        
        In production, this would perform actual network measurements.
        This is a placeholder for integration with network monitoring tools.
        
        Returns:
            ConnectionMetrics object with current measurements
        """
        # Placeholder implementation - in production this would:
        # - Ping Starlink gateway
        # - Measure bandwidth using iperf or similar
        # - Calculate jitter from packet timing
        # - Track packet loss
        
        # For now, return simulated metrics
        latency = 45.0  # Typical Starlink latency
        packet_loss = 0.5
        bandwidth = 150.0
        jitter = 5.0
        
        quality = self._determine_quality(latency, packet_loss)
        
        metrics = ConnectionMetrics(
            latency_ms=latency,
            packet_loss_percent=packet_loss,
            bandwidth_mbps=bandwidth,
            jitter_ms=jitter,
            timestamp=time.time(),
            quality=quality
        )
        
        self._current_metrics = metrics
        
        # Notify callbacks
        for callback in self._callbacks:
            callback(metrics)
        
        return metrics
    
    def get_current_metrics(self) -> Optional[ConnectionMetrics]:
        """Get the most recent connection metrics"""
        return self._current_metrics
    
    def get_quality(self) -> Optional[ConnectionQuality]:
        """Get current connection quality level"""
        if self._current_metrics:
            return self._current_metrics.quality
        return None
    
    def is_connection_stable(self, min_quality: ConnectionQuality = ConnectionQuality.FAIR) -> bool:
        """
        Check if connection meets minimum quality threshold
        
        Args:
            min_quality: Minimum acceptable connection quality
            
        Returns:
            True if connection meets or exceeds minimum quality
        """
        if not self._current_metrics:
            return False
        
        quality_levels = [
            ConnectionQuality.CRITICAL,
            ConnectionQuality.POOR,
            ConnectionQuality.FAIR,
            ConnectionQuality.GOOD,
            ConnectionQuality.EXCELLENT
        ]
        
        current_level = quality_levels.index(self._current_metrics.quality)
        min_level = quality_levels.index(min_quality)
        
        return current_level >= min_level
