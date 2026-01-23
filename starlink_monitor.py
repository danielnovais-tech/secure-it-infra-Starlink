"""
Starlink Security Monitoring System

This module provides security monitoring capabilities for Starlink infrastructure,
including security score calculation and connection stability metrics.
"""

from dataclasses import dataclass
import time


# Constants for security score calculation
AUTH_PENALTY_MULTIPLIER = 3  # Penalty multiplier per failed auth attempt
PACKET_LOSS_PENALTY_MULTIPLIER = 6  # Penalty multiplier for packet loss
LATENCY_DIVISOR = 5  # Divisor for latency score calculation


@dataclass
class SecurityMetrics:
    """Data class to hold security and connection metrics."""
    security_score: float = 0.0
    connection_stability: float = 0.0
    signal_quality: float = 100.0
    latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    uptime_percentage: float = 100.0
    failed_auth_attempts: int = 0
    encryption_strength: float = 100.0
    last_updated: float = 0.0


class StarlinkMonitor:
    """
    Monitor for Starlink infrastructure security and stability.
    
    This class calculates security scores and connection stability based on
    various network and security factors.
    """
    
    def __init__(self):
        """Initialize the Starlink monitor with default metrics."""
        self.metrics = SecurityMetrics()
        self.metrics.last_updated = time.time()
        
    def update_metrics(self, **kwargs):
        """
        Update individual metrics.
        
        Args:
            **kwargs: Metric values to update (e.g., signal_quality=95.5)
        """
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        self.metrics.last_updated = time.time()
        
        # Calculate connection stability first, as it's used in security score
        self.metrics.connection_stability = self._calculate_stability()
        
        # Update security score based on various factors
        self.metrics.security_score = self._calculate_security_score()
    
    def _calculate_security_score(self) -> float:
        """
        Calculate security score based on multiple security factors.
        
        The security score is calculated from:
        - Encryption strength (40% weight)
        - Failed authentication attempts (30% weight)
        - Connection stability (20% weight)
        - Signal quality (10% weight)
        
        Returns:
            float: Security score between 0.0 and 100.0
        """
        # Base score starts at 100
        score = 100.0
        
        # Factor 1: Encryption strength (40% weight)
        # Reduce score if encryption is weak
        encryption_factor = (self.metrics.encryption_strength / 100.0) * 40.0
        
        # Factor 2: Failed authentication attempts (30% weight)
        # More failed attempts = lower score
        # Penalize heavily for failed auth attempts (max penalty at 10+ attempts)
        auth_penalty = min(self.metrics.failed_auth_attempts * AUTH_PENALTY_MULTIPLIER, 30)
        auth_factor = max(0, 30.0 - auth_penalty)
        
        # Factor 3: Connection stability (20% weight)
        # Use current stability metric
        stability_factor = (self.metrics.connection_stability / 100.0) * 20.0
        
        # Factor 4: Signal quality (10% weight)
        # Better signal = better security posture
        signal_factor = (self.metrics.signal_quality / 100.0) * 10.0
        
        # Calculate final score
        score = encryption_factor + auth_factor + stability_factor + signal_factor
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))
    
    def _calculate_stability(self) -> float:
        """
        Calculate connection stability based on network metrics.
        
        The stability score is calculated from:
        - Uptime percentage (40% weight)
        - Packet loss rate (30% weight)
        - Signal quality (20% weight)
        - Latency (10% weight)
        
        Returns:
            float: Stability score between 0.0 and 100.0
        """
        # Factor 1: Uptime percentage (40% weight)
        uptime_factor = (self.metrics.uptime_percentage / 100.0) * 40.0
        
        # Factor 2: Packet loss rate (30% weight)
        # Lower packet loss = higher stability
        # Assume packet loss > 5% is very bad
        packet_loss_penalty = min(self.metrics.packet_loss_rate * PACKET_LOSS_PENALTY_MULTIPLIER, 30)
        packet_loss_factor = max(0, 30.0 - packet_loss_penalty)
        
        # Factor 3: Signal quality (20% weight)
        signal_factor = (self.metrics.signal_quality / 100.0) * 20.0
        
        # Factor 4: Latency (10% weight)
        # Lower latency = higher stability
        # Assume latency > 100ms starts to degrade stability
        # Latency > 500ms is very poor
        latency_score = max(0, 100 - (self.metrics.latency_ms / LATENCY_DIVISOR))
        latency_factor = (latency_score / 100.0) * 10.0
        
        # Calculate final stability score
        stability = uptime_factor + packet_loss_factor + signal_factor + latency_factor
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, stability))
    
    def get_status_report(self) -> dict:
        """
        Get a comprehensive status report of all metrics.
        
        Returns:
            dict: Dictionary containing all current metrics and calculated scores
        """
        return {
            'security_score': self.metrics.security_score,
            'connection_stability': self.metrics.connection_stability,
            'signal_quality': self.metrics.signal_quality,
            'latency_ms': self.metrics.latency_ms,
            'packet_loss_rate': self.metrics.packet_loss_rate,
            'uptime_percentage': self.metrics.uptime_percentage,
            'failed_auth_attempts': self.metrics.failed_auth_attempts,
            'encryption_strength': self.metrics.encryption_strength,
            'last_updated': self.metrics.last_updated,
        }
