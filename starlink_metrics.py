"""
Starlink Connection Metrics Module

This module provides functionality to monitor and calculate quality metrics
for Starlink satellite internet connections based on packet loss and latency.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConnectionMetrics:
    """Data class to hold connection metrics."""
    packet_loss: float  # Packet loss percentage (0-100)
    latency: float  # Latency in milliseconds
    
    def __post_init__(self):
        """Validate metrics values."""
        if self.packet_loss < 0 or self.packet_loss > 100:
            raise ValueError("packet_loss must be between 0 and 100")
        if self.latency < 0:
            raise ValueError("latency must be non-negative")


class StarlinkConnectionQuality:
    """
    Calculate and monitor Starlink connection quality metrics.
    
    This class evaluates connection quality based on packet loss and latency,
    providing stability scores and overall quality assessments.
    """
    
    def __init__(self, metrics: ConnectionMetrics):
        """
        Initialize the connection quality calculator.
        
        Args:
            metrics: ConnectionMetrics object containing packet_loss and latency
        """
        self.metrics = metrics
    
    def calculate_quality_score(self) -> float:
        """
        Calculate overall connection quality score (0-100).
        
        The base score starts at 100 and is reduced based on:
        - Packet loss > 5%: -10 points
        - Latency > 150ms: -5 points
        
        Returns:
            Quality score between 0 and 100
        """
        base_score = 100.0
        
        if self.metrics.packet_loss > 5:
            base_score -= 10
        if self.metrics.latency > 150:
            base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _calculate_stability(self, packet_loss: float, latency: float) -> float:
        """
        Calculate connection stability score based on packet loss and latency.
        
        This method heavily penalizes packet loss (70% weight) and considers
        latency (30% weight) with a 500ms threshold.
        
        Args:
            packet_loss: Packet loss as a decimal (0.0-1.0, where 1.0 = 100%)
            latency: Latency in milliseconds
            
        Returns:
            Stability score between 0.0 and 1.0
        """
        # penaliza fortemente packet loss
        loss_factor = max(0, 1 - packet_loss * 2)
        latency_factor = max(0, 1 - latency / 500)  # 500ms como limite
        return (loss_factor * 0.7 + latency_factor * 0.3)
    
    def calculate_stability_score(self) -> float:
        """
        Calculate stability score using stored metrics.
        
        Returns:
            Stability score between 0.0 and 1.0
        """
        # Convert percentage to decimal for calculation
        packet_loss_decimal = self.metrics.packet_loss / 100.0
        return self._calculate_stability(packet_loss_decimal, self.metrics.latency)
    
    def get_connection_status(self) -> dict:
        """
        Get comprehensive connection status information.
        
        Returns:
            Dictionary containing quality score, stability score, and metrics
        """
        quality = self.calculate_quality_score()
        stability = self.calculate_stability_score()
        
        # Determine connection status based on scores
        if quality >= 90 and stability >= 0.9:
            status = "Excellent"
        elif quality >= 75 and stability >= 0.7:
            status = "Good"
        elif quality >= 50 and stability >= 0.5:
            status = "Fair"
        else:
            status = "Poor"
        
        return {
            "status": status,
            "quality_score": quality,
            "stability_score": stability,
            "packet_loss": self.metrics.packet_loss,
            "latency": self.metrics.latency
        }


def monitor_connection(packet_loss: float, latency: float) -> dict:
    """
    Convenience function to monitor connection quality.
    
    Args:
        packet_loss: Packet loss percentage (0-100)
        latency: Latency in milliseconds
        
    Returns:
        Dictionary with connection status information
    """
    metrics = ConnectionMetrics(packet_loss=packet_loss, latency=latency)
    quality = StarlinkConnectionQuality(metrics)
    return quality.get_connection_status()
