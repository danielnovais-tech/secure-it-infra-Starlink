"""
Starlink Connection Metrics Module

This module provides functionality to monitor and calculate quality metrics
for Starlink satellite internet connections based on packet loss and latency.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any, Union
from enum import Enum
from collections import deque
from statistics import mean

logger = logging.getLogger(__name__)

# Threat severity multipliers for weighted deductions
THREAT_SEVERITY_MULTIPLIERS = {
    'low': 0.5,
    'medium': 1.0,
    'high': 2.0
}


class ServiceLevel(Enum):
    """Service level classification for connection quality."""
    STABLE = "Stable"
    DEGRADED = "Degraded"
    CRITICAL = "Critical"
    OFFLINE = "Offline"


@dataclass
class QualityThresholds:
    """Configurable thresholds for quality score calculation."""
    packet_loss_threshold: float = 5.0  # Percentage
    packet_loss_penalty: float = 10.0  # Points to deduct
    latency_threshold: float = 150.0  # Milliseconds
    latency_penalty: float = 5.0  # Points to deduct
    threat_penalty: float = 5.0  # Points to deduct per active threat
    
    def __post_init__(self):
        """Validate threshold values."""
        if not 0 <= self.packet_loss_threshold <= 100:
            raise ValueError("packet_loss_threshold must be between 0 and 100")
        if self.packet_loss_penalty < 0:
            raise ValueError("packet_loss_penalty must be non-negative")
        if self.latency_threshold < 0:
            raise ValueError("latency_threshold must be non-negative")
        if self.latency_penalty < 0:
            raise ValueError("latency_penalty must be non-negative")
        if self.threat_penalty < 0:
            raise ValueError("threat_penalty must be non-negative")


@dataclass
class StabilityThresholds:
    """Configurable thresholds for stability score calculation."""
    max_latency: float = 500.0  # Milliseconds - latency ceiling
    packet_loss_weight: float = 0.7  # Weight for packet loss factor (0.0-1.0)
    latency_weight: float = 0.3  # Weight for latency factor (0.0-1.0)
    packet_loss_multiplier: float = 2.0  # Multiplier for packet loss penalty
    
    def __post_init__(self):
        """Validate threshold values."""
        if not 0.0 <= self.packet_loss_weight <= 1.0:
            raise ValueError("packet_loss_weight must be between 0.0 and 1.0")
        if not 0.0 <= self.latency_weight <= 1.0:
            raise ValueError("latency_weight must be between 0.0 and 1.0")
        if abs(self.packet_loss_weight + self.latency_weight - 1.0) > 0.01:
            raise ValueError("packet_loss_weight and latency_weight must sum to 1.0")
        if self.max_latency <= 0:
            raise ValueError("max_latency must be positive")
        if self.packet_loss_multiplier <= 0:
            raise ValueError("packet_loss_multiplier must be positive")


@dataclass
class AlertThresholds:
    """Thresholds for triggering alerts."""
    critical_stability: float = 0.3  # Trigger alert when stability falls below
    degraded_stability: float = 0.5  # Trigger warning when stability falls below
    stable_stability: float = 0.7  # Stable connection threshold
    
    def __post_init__(self):
        """Validate threshold values."""
        if not 0.0 <= self.critical_stability <= 1.0:
            raise ValueError("critical_stability must be between 0.0 and 1.0")
        if not 0.0 <= self.degraded_stability <= 1.0:
            raise ValueError("degraded_stability must be between 0.0 and 1.0")
        if not 0.0 <= self.stable_stability <= 1.0:
            raise ValueError("stable_stability must be between 0.0 and 1.0")
        if not (self.critical_stability < self.degraded_stability < self.stable_stability):
            raise ValueError("Thresholds must be in ascending order: critical < degraded < stable")


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
    providing stability scores and overall quality assessments with configurable
    thresholds and alert capabilities.
    """
    
    def __init__(
        self,
        metrics: ConnectionMetrics,
        quality_thresholds: Optional[QualityThresholds] = None,
        stability_thresholds: Optional[StabilityThresholds] = None,
        alert_thresholds: Optional[AlertThresholds] = None,
        alert_callback: Optional[Callable[[str, Dict], None]] = None,
        history_window_size: int = 0,
        active_threats: Optional[List[Any]] = None
    ):
        """
        Initialize the connection quality calculator.
        
        Args:
            metrics: ConnectionMetrics object containing packet_loss and latency
            quality_thresholds: Optional custom quality thresholds
            stability_thresholds: Optional custom stability thresholds
            alert_thresholds: Optional custom alert thresholds
            alert_callback: Optional callback function for alerts (receives alert_level, data)
            history_window_size: Size of sliding window for historical smoothing (0 = disabled)
            active_threats: Optional list of active security threats. Can be:
                - List of strings (each deducts threat_penalty points)
                - List of dicts with 'severity' key for weighted deduction:
                  {'id': 'threat1', 'severity': 'high'} where severity can be
                  'low' (50% of threat_penalty), 'medium' (100%), 'high' (200%)
        """
        self.metrics = metrics
        self.quality_thresholds = quality_thresholds or QualityThresholds()
        self.stability_thresholds = stability_thresholds or StabilityThresholds()
        self.alert_thresholds = alert_thresholds or AlertThresholds()
        self.alert_callback = alert_callback
        self.active_threats = active_threats or []
        
        # Historical tracking for smoothing
        if history_window_size < 0:
            raise ValueError("history_window_size must be non-negative")
        self.history_window_size = history_window_size
        self.stability_history: deque = deque(maxlen=history_window_size if history_window_size > 0 else None)
    
    def calculate_quality_score(self, return_details: bool = False) -> Union[float, Dict[str, Any]]:
        """
        Calculate overall connection quality score (0-100).
        
        The base score starts at 100 and is reduced based on configurable thresholds.
        Default penalties:
        - Packet loss > 5%: -10 points
        - Latency > 150ms: -5 points
        - Each active threat: -5 points (configurable via threat_penalty)
          - Threats can have weighted severity: low (50%), medium (100%), high (200%)
        
        Args:
            return_details: If True, returns a dict with audit trail of deductions.
                          If False (default), returns just the final score for backward compatibility.
        
        Returns:
            If return_details=False: Quality score between 0 and 100
            If return_details=True: Dict with keys:
                - final_score: Final quality score (0-100)
                - base_score: Starting score before deductions (100)
                - deductions: List of dicts with 'reason' and 'points' for each deduction
                - summary: Human-readable summary of deductions (e.g., "Score reduced by 17.5 points due to 3 active threats (1 high, 1 medium, 1 low).")
        """
        base_score = 100.0
        deductions_list = []
        
        if self.metrics.packet_loss > self.quality_thresholds.packet_loss_threshold:
            deduction = self.quality_thresholds.packet_loss_penalty
            base_score -= deduction
            deductions_list.append({
                "reason": f"Packet loss above {self.quality_thresholds.packet_loss_threshold}% threshold",
                "points": -deduction
            })
            
        if self.metrics.latency > self.quality_thresholds.latency_threshold:
            deduction = self.quality_thresholds.latency_penalty
            base_score -= deduction
            deductions_list.append({
                "reason": f"Latency above {self.quality_thresholds.latency_threshold}ms threshold",
                "points": -deduction
            })
            
        if len(self.active_threats) > 0:
            threat_deductions = self._calculate_threat_deduction_with_details()
            for threat_deduction in threat_deductions:
                penalty = threat_deduction['points']
                base_score -= penalty
                deductions_list.append({
                    "reason": threat_deduction['reason'],
                    "points": -penalty
                })
            
            total_threat_deduction = sum(d['points'] for d in threat_deductions)
            logger.info(
                "Quality score impacted by %d active threat(s), deducting %s points",
                len(self.active_threats), total_threat_deduction
            )
        
        final_score = max(0, min(100, base_score))
        
        if deductions_list and logger.isEnabledFor(logging.DEBUG):
            deduction_summary = ', '.join(f"{d['reason']}: {d['points']}" for d in deductions_list)
            logger.debug("Quality score deductions: %s. Final score: %s", deduction_summary, final_score)
        
        if return_details:
            # Generate human-readable summary
            total_deduction = sum(abs(d['points']) for d in deductions_list)
            summary_parts = []
            
            if total_deduction > 0:
                summary_parts.append(f"Score reduced by {total_deduction:g} points")
                
                # Count threats by severity
                threat_counts = {'low': 0, 'medium': 0, 'high': 0}
                for d in deductions_list:
                    reason_lower = d['reason'].lower()
                    if 'threat' in reason_lower:
                        if 'low severity' in reason_lower:
                            threat_counts['low'] += 1
                        elif 'high severity' in reason_lower:
                            threat_counts['high'] += 1
                        elif 'medium severity' in reason_lower:
                            threat_counts['medium'] += 1
                
                total_threats = sum(threat_counts.values())
                if total_threats > 0:
                    threat_breakdown = []
                    if threat_counts['high'] > 0:
                        threat_breakdown.append(f"{threat_counts['high']} high")
                    if threat_counts['medium'] > 0:
                        threat_breakdown.append(f"{threat_counts['medium']} medium")
                    if threat_counts['low'] > 0:
                        threat_breakdown.append(f"{threat_counts['low']} low")
                    
                    summary_parts.append(f"due to {total_threats} active threat{'s' if total_threats > 1 else ''}")
                    if threat_breakdown:
                        summary_parts.append(f"({', '.join(threat_breakdown)})")
                
                summary = ' '.join(summary_parts) + '.'
            else:
                summary = "No deductions applied."
            
            return {
                "final_score": final_score,
                "base_score": 100.0,
                "deductions": deductions_list,
                "summary": summary
            }
        
        return final_score
    
    def _calculate_threat_deduction(self) -> float:
        """
        Calculate total deduction for active threats, supporting weighted severity.
        
        Supports severity levels: 'low' (50%), 'medium' (100%), 'high' (200%).
        Invalid severity values will raise a ValueError.
        
        Returns:
            Total points to deduct for all active threats
            
        Raises:
            ValueError: If an invalid severity level is provided
        """
        threat_deductions = self._calculate_threat_deduction_with_details()
        return sum(d['points'] for d in threat_deductions)
    
    def _calculate_threat_deduction_with_details(self) -> List[Dict[str, Any]]:
        """
        Calculate deduction for each active threat with details, supporting weighted severity.
        
        Supports severity levels: 'low' (50%), 'medium' (100%), 'high' (200%).
        Invalid severity values will raise a ValueError.
        
        Returns:
            List of dicts with 'reason' and 'points' for each threat
            
        Raises:
            ValueError: If an invalid severity level is provided
        """
        deductions = []
        for threat in self.active_threats:
            if isinstance(threat, dict) and 'severity' in threat:
                # Weighted threat based on severity
                severity = str(threat.get('severity', 'medium')).lower()
                
                if severity not in THREAT_SEVERITY_MULTIPLIERS:
                    raise ValueError(
                        f"Invalid threat severity '{severity}'. "
                        f"Valid values are: {', '.join(THREAT_SEVERITY_MULTIPLIERS.keys())}"
                    )
                
                multiplier = THREAT_SEVERITY_MULTIPLIERS[severity]
                penalty = self.quality_thresholds.threat_penalty * multiplier
                threat_id = threat.get('id', 'unknown')
                deductions.append({
                    "reason": f"{severity.capitalize()} severity threat ({threat_id})",
                    "points": penalty
                })
            else:
                # Default threat (string or dict without severity)
                penalty = self.quality_thresholds.threat_penalty
                if isinstance(threat, str):
                    threat_id = threat
                elif isinstance(threat, dict):
                    threat_id = threat.get('id', 'unknown')
                else:
                    threat_id = str(threat)
                deductions.append({
                    "reason": f"Medium severity threat ({threat_id})",
                    "points": penalty
                })
        
        return deductions
    
    def _calculate_stability(self, packet_loss: float, latency: float) -> float:
        """
        Calculate connection stability score based on packet loss and latency.
        
        Uses configurable weights and thresholds for flexible calculation.
        Default: heavily penalizes packet loss (70% weight) and considers
        latency (30% weight) with a 500ms threshold.
        
        Args:
            packet_loss: Packet loss as a decimal (0.0-1.0, where 1.0 = 100%)
            latency: Latency in milliseconds
            
        Returns:
            Stability score between 0.0 and 1.0
        """
        # Heavily penalize packet loss
        loss_factor = max(
            0,
            1 - packet_loss * self.stability_thresholds.packet_loss_multiplier
        )
        # Latency factor based on configurable maximum
        latency_factor = max(
            0,
            1 - latency / self.stability_thresholds.max_latency
        )
        
        return (
            loss_factor * self.stability_thresholds.packet_loss_weight +
            latency_factor * self.stability_thresholds.latency_weight
        )
    
    def calculate_stability_score(self, use_smoothing: bool = True) -> float:
        """
        Calculate stability score using stored metrics.
        
        Args:
            use_smoothing: If True and history is enabled, return smoothed average
        
        Returns:
            Stability score between 0.0 and 1.0
        """
        # Convert percentage to decimal for calculation
        packet_loss_decimal = self.metrics.packet_loss / 100.0
        current_stability = self._calculate_stability(
            packet_loss_decimal,
            self.metrics.latency
        )
        
        # Add to history if enabled
        if self.history_window_size > 0:
            self.stability_history.append(current_stability)
            
            # Return smoothed average if requested and we have history
            if use_smoothing and len(self.stability_history) > 0:
                return mean(self.stability_history)
        
        return current_stability
    
    def get_service_level(self, stability: float) -> ServiceLevel:
        """
        Map stability score to service level classification.
        
        Args:
            stability: Stability score (0.0-1.0)
            
        Returns:
            ServiceLevel enum value
        """
        if stability >= self.alert_thresholds.stable_stability:
            return ServiceLevel.STABLE
        elif stability >= self.alert_thresholds.degraded_stability:
            return ServiceLevel.DEGRADED
        elif stability >= self.alert_thresholds.critical_stability:
            return ServiceLevel.CRITICAL
        else:
            return ServiceLevel.OFFLINE
    
    def _trigger_alert(self, alert_level: str, data: Dict) -> None:
        """
        Trigger an alert if callback is configured.
        
        Args:
            alert_level: Level of alert ("critical", "degraded", "warning")
            data: Dictionary with alert context
        """
        if self.alert_callback:
            self.alert_callback(alert_level, data)
    
    def check_and_alert(self, stability: float) -> Optional[str]:
        """
        Check stability against alert thresholds and trigger alerts if needed.
        
        Args:
            stability: Current stability score
            
        Returns:
            Alert level if triggered, None otherwise
        """
        alert_level = None
        
        if stability < self.alert_thresholds.critical_stability:
            alert_level = "critical"
        elif stability < self.alert_thresholds.degraded_stability:
            alert_level = "degraded"
        
        if alert_level:
            self._trigger_alert(alert_level, {
                "stability": stability,
                "packet_loss": self.metrics.packet_loss,
                "latency": self.metrics.latency,
                "service_level": self.get_service_level(stability).value
            })
        
        return alert_level
    
    def get_connection_status(self) -> dict:
        """
        Get comprehensive connection status information.
        
        Returns:
            Dictionary containing quality score, stability score, service level, and metrics
        """
        quality = self.calculate_quality_score()
        stability = self.calculate_stability_score()
        service_level = self.get_service_level(stability)
        
        # Check for alerts
        alert_level = self.check_and_alert(stability)
        
        # Determine connection status based on scores (legacy compatibility)
        if quality >= 90 and stability >= 0.9:
            status = "Excellent"
        elif quality >= 75 and stability >= 0.7:
            status = "Good"
        elif quality >= 50 and stability >= 0.5:
            status = "Fair"
        else:
            status = "Poor"
        
        result = {
            "status": status,
            "quality_score": quality,
            "stability_score": stability,
            "service_level": service_level.value,
            "packet_loss": self.metrics.packet_loss,
            "latency": self.metrics.latency
        }
        
        if alert_level:
            result["alert_level"] = alert_level
        
        if self.history_window_size > 0 and len(self.stability_history) > 0:
            result["stability_history_size"] = len(self.stability_history)
        
        return result


def monitor_connection(
    packet_loss: float,
    latency: float,
    active_threats: Optional[List[Any]] = None
) -> dict:
    """
    Convenience function to monitor connection quality.
    
    Args:
        packet_loss: Packet loss percentage (0-100)
        latency: Latency in milliseconds
        active_threats: Optional list of active security threats
        
    Returns:
        Dictionary with connection status information
    """
    metrics = ConnectionMetrics(packet_loss=packet_loss, latency=latency)
    quality = StarlinkConnectionQuality(metrics, active_threats=active_threats)
    return quality.get_connection_status()
