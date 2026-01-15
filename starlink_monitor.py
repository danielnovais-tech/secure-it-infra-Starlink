"""
Starlink Network Monitoring and Security System
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable, Awaitable
import logging


class SecurityLevel(Enum):
    """Security level enumeration."""
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"


@dataclass
class NetworkMetrics:
    """Network performance metrics."""
    latency: float = 0.0
    jitter: float = 0.0
    packet_loss: float = 0.0
    throughput: float = 0.0
    security_score: float = 100.0
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'latency': self.latency,
            'jitter': self.jitter,
            'packet_loss': self.packet_loss,
            'throughput': self.throughput,
            'security_score': self.security_score
        }


class StarlinkMonitor:
    """Starlink network monitoring and security management."""
    
    # Stability calculation constants
    JITTER_MULTIPLIER = 2
    JITTER_MAX_DEDUCTION = 30
    PACKET_LOSS_MULTIPLIER = 10
    PACKET_LOSS_MAX_DEDUCTION = 40
    
    # Default performance thresholds
    DEFAULT_MAX_LATENCY = 100.0
    DEFAULT_MAX_JITTER = 20.0
    DEFAULT_MAX_PACKET_LOSS = 5.0
    DEFAULT_MIN_THROUGHPUT = 50.0
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Starlink monitor.
        
        Args:
            config: Configuration dictionary containing Starlink settings
        """
        self.config = config
        self.metrics = NetworkMetrics()
        self.security_level = SecurityLevel.NORMAL
        self.logger = logging.getLogger(__name__)
        self.event_handlers: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
    
    async def trigger_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Trigger a monitoring event.
        
        Args:
            event_type: Type of the event
            severity: Severity level (info, warning, critical)
            source: Source component
            message: Event message
            data: Additional event data
        """
        event = {
            'type': event_type,
            'severity': severity,
            'source': source,
            'message': message,
            'data': data or {}
        }
        self.logger.info(f"Event triggered: {event_type} - {message}")
        
        # Notify all registered event handlers
        for handler in self.event_handlers:
            await handler(event)
    
    def calculate_stability(self) -> float:
        """
        Calculate network stability score.
        
        Returns:
            Stability score (0-100)
        """
        # Start with perfect stability
        stability = 100.0
        
        # Deduct for high jitter and packet loss
        stability -= min(self.metrics.jitter * self.JITTER_MULTIPLIER, self.JITTER_MAX_DEDUCTION)
        stability -= min(self.metrics.packet_loss * self.PACKET_LOSS_MULTIPLIER, self.PACKET_LOSS_MAX_DEDUCTION)
        
        return max(0, min(100, stability))
    
    async def _detect_anomalies(self):
        """Detect anomalies in network behavior."""
        # Validate configuration structure
        if 'starlink' not in self.config or 'performance_thresholds' not in self.config['starlink']:
            self.logger.warning("Missing performance_thresholds configuration")
            return
        
        thresholds = self.config['starlink']['performance_thresholds']
        
        # Get thresholds with defaults
        max_latency = thresholds.get('max_latency', self.DEFAULT_MAX_LATENCY)
        max_jitter = thresholds.get('max_jitter', self.DEFAULT_MAX_JITTER)
        max_packet_loss = thresholds.get('max_packet_loss', self.DEFAULT_MAX_PACKET_LOSS)
        min_throughput = thresholds.get('min_throughput', self.DEFAULT_MIN_THROUGHPUT)
        
        anomalies = []
        
        if self.metrics.latency > max_latency:
            anomalies.append(f"High latency: {self.metrics.latency:.1f}ms")
        
        if self.metrics.jitter > max_jitter:
            anomalies.append(f"High jitter: {self.metrics.jitter:.1f}ms")
        
        if self.metrics.packet_loss > max_packet_loss:
            anomalies.append(f"High packet loss: {self.metrics.packet_loss:.1f}%")
        
        if self.metrics.throughput < min_throughput:
            anomalies.append(f"Low throughput: {self.metrics.throughput:.1f}Mbps")
        
        if anomalies:
            await self.trigger_event(
                "network_anomaly_detected",
                "warning",
                "network_monitor",
                f"Network anomalies detected: {', '.join(anomalies)}",
                {"metrics": self.metrics.to_dict(), "anomalies": anomalies}
            )
    
    async def _check_security_status(self):
        """Check overall security status and adjust security level."""
        if self.metrics.security_score < 50:
            new_level = SecurityLevel.CRITICAL
        elif self.metrics.security_score < 70:
            new_level = SecurityLevel.ELEVATED
        else:
            new_level = SecurityLevel.NORMAL
        
        if new_level != self.security_level:
            old_level = self.security_level
            self.security_level = new_level
            await self.trigger_event(
                "security_level_changed",
                "info",
                "foundation",
                f"Security level changed from {old_level.value} to {new_level.value}",
                {"old_level": old_level.value, "new_level": new_level.value}
            )
    
    async def monitor(self):
        """Main monitoring loop."""
        await self._detect_anomalies()
        await self._check_security_status()
    
    def update_metrics(self, metrics: NetworkMetrics):
        """
        Update network metrics.
        
        Args:
            metrics: New network metrics
        """
        self.metrics = metrics
