"""Security monitoring module for Starlink infrastructure."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SecurityMonitor:
    """Monitor and track security metrics for Starlink infrastructure."""
    
    def __init__(self):
        """Initialize the security monitor."""
        self.metrics: Dict[str, Any] = {}
        self.previous_metrics: Dict[str, Any] = {}
        self.anomalies: List[Dict[str, Any]] = []
        self.security_score: float = 100.0
        
    async def update_metrics(self, new_metrics: Dict[str, Any]) -> None:
        """
        Update security metrics and detect anomalies.
        
        Args:
            new_metrics: Dictionary containing the latest security metrics
        """
        try:
            # Store previous metrics for comparison
            self.previous_metrics = self.metrics.copy()
            self.metrics = new_metrics
            
            # Log significant changes
            self._log_significant_changes()
            
            # Detect anomalies after logging changes
            await self._detect_anomalies()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def _log_significant_changes(self) -> None:
        """Log significant changes in security metrics."""
        if not self.previous_metrics:
            logger.info("Initial metrics recorded")
            return
            
        for key, value in self.metrics.items():
            if key in self.previous_metrics:
                prev_value = self.previous_metrics[key]
                
                # Check for numeric changes
                if isinstance(value, (int, float)) and isinstance(prev_value, (int, float)):
                    if prev_value != 0:
                        change_percent = abs((value - prev_value) / prev_value) * 100
                        if change_percent >= 10:  # Log changes >= 10%
                            logger.warning(
                                f"Significant change in {key}: {prev_value} -> {value} "
                                f"({change_percent:.1f}% change)"
                            )
                    elif value != prev_value:
                        logger.warning(f"Significant change in {key}: {prev_value} -> {value}")
                        
                # Check for non-numeric changes
                elif value != prev_value:
                    logger.info(f"Change in {key}: {prev_value} -> {value}")
            else:
                logger.info(f"New metric added: {key} = {value}")
    
    async def _detect_anomalies(self) -> None:
        """Detect anomalies in current metrics."""
        detected_anomalies = []
        
        # Check for critical thresholds
        if "failed_login_attempts" in self.metrics:
            if self.metrics["failed_login_attempts"] > 5:
                detected_anomalies.append({
                    "type": "authentication",
                    "severity": "high",
                    "metric": "failed_login_attempts",
                    "value": self.metrics["failed_login_attempts"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        if "unauthorized_access_attempts" in self.metrics:
            if self.metrics["unauthorized_access_attempts"] > 0:
                detected_anomalies.append({
                    "type": "access_control",
                    "severity": "critical",
                    "metric": "unauthorized_access_attempts",
                    "value": self.metrics["unauthorized_access_attempts"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        if "network_intrusion_attempts" in self.metrics:
            if self.metrics["network_intrusion_attempts"] > 0:
                detected_anomalies.append({
                    "type": "network_security",
                    "severity": "critical",
                    "metric": "network_intrusion_attempts",
                    "value": self.metrics["network_intrusion_attempts"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        # Store and log anomalies
        if detected_anomalies:
            self.anomalies.extend(detected_anomalies)
            for anomaly in detected_anomalies:
                logger.critical(
                    f"Anomaly detected - Type: {anomaly['type']}, "
                    f"Severity: {anomaly['severity']}, "
                    f"Metric: {anomaly['metric']}, "
                    f"Value: {anomaly['value']}"
                )
    
    def _calculate_security_score(self) -> float:
        """Calculate overall security score (0-100)."""
        base_score = 100.0
        
        # Deduct points for security issues
        deductions = 0.0
        
        # Failed login attempts reduce score
        if "failed_login_attempts" in self.metrics:
            failed_logins = self.metrics["failed_login_attempts"]
            deductions += min(failed_logins * 2, 20)  # Max 20 points for failed logins
        
        # Unauthorized access attempts significantly reduce score
        if "unauthorized_access_attempts" in self.metrics:
            unauth_attempts = self.metrics["unauthorized_access_attempts"]
            deductions += min(unauth_attempts * 10, 30)  # Max 30 points for unauthorized access
        
        # Network intrusion attempts critically reduce score
        if "network_intrusion_attempts" in self.metrics:
            intrusion_attempts = self.metrics["network_intrusion_attempts"]
            deductions += min(intrusion_attempts * 15, 40)  # Max 40 points for intrusions
        
        # Active anomalies reduce score
        if self.anomalies:
            critical_anomalies = sum(1 for a in self.anomalies if a.get("severity") == "critical")
            high_anomalies = sum(1 for a in self.anomalies if a.get("severity") == "high")
            deductions += critical_anomalies * 5 + high_anomalies * 2
        
        # Calculate final score
        final_score = max(0.0, base_score - deductions)
        self.security_score = final_score
        
        return final_score
    
    def get_security_score(self) -> float:
        """Get the current security score."""
        return self._calculate_security_score()
    
    def get_anomalies(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get detected anomalies, optionally filtered by severity.
        
        Args:
            severity: Optional severity filter ('critical', 'high', 'medium', 'low')
            
        Returns:
            List of anomaly dictionaries
        """
        if severity:
            return [a for a in self.anomalies if a.get("severity") == severity]
        return self.anomalies.copy()
    
    def clear_anomalies(self) -> None:
        """Clear all recorded anomalies."""
        self.anomalies.clear()
        logger.info("Anomalies cleared")
