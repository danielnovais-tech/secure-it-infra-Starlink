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
        self.metric_history: List[Dict[str, Any]] = []
        self.security_score: float = 100.0
        self.audit_trail: List[Dict[str, Any]] = []
        
        # Configurable thresholds for anomaly detection
        self.thresholds = {
            "failed_login_attempts": 5,
            "unauthorized_access_attempts": 0,
            "network_intrusion_attempts": 0,
        }
        
        # Severity mapping for metrics
        self.severity_map = {
            "failed_login_attempts": "high",
            "unauthorized_access_attempts": "critical",
            "network_intrusion_attempts": "critical",
        }
        
        # Type mapping for metrics
        self.type_map = {
            "failed_login_attempts": "authentication",
            "unauthorized_access_attempts": "access_control",
            "network_intrusion_attempts": "network_security",
        }
        
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

            # Keep a timestamped history snapshot
            self.metric_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": new_metrics.copy()
            })

            # Log significant changes
            self._log_significant_changes()

            # Detect anomalies after logging changes
            await self._detect_anomalies()

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
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
        """Detect anomalies in current metrics using configurable thresholds."""
        detected_anomalies = []
        timestamp = datetime.now(timezone.utc).isoformat()

        # Check each metric against its threshold
        for metric, threshold in self.thresholds.items():
            if self.metrics.get(metric, 0) > threshold:
                anomaly = {
                    "type": self.type_map[metric],
                    "severity": self.severity_map[metric],
                    "metric": metric,
                    "value": self.metrics[metric],
                    "timestamp": timestamp,
                }
                detected_anomalies.append(anomaly)

        # Store and log anomalies with deduplication
        # Note: Anomalies are accumulated for historical tracking, but
        # logically duplicate anomalies (same type/metric/severity/value)
        # are not re-added on each detection cycle to avoid unbounded
        # growth and score degradation when conditions are unchanged.
        if detected_anomalies:
            existing_signatures = {
                (a.get("type"), a.get("metric"), a.get("severity"), a.get("value"))
                for a in self.anomalies
            }
            new_anomalies = [
                a
                for a in detected_anomalies
                if (a.get("type"), a.get("metric"), a.get("severity"), a.get("value"))
                not in existing_signatures
            ]
            if new_anomalies:
                self.anomalies.extend(new_anomalies)
                for anomaly in new_anomalies:
                    logger.critical(
                        f"Anomaly detected - Type: {anomaly['type']}, "
                        f"Severity: {anomaly['severity']}, "
                        f"Metric: {anomaly['metric']}, "
                        f"Value: {anomaly['value']}"
                    )
    
    def _calculate_security_score(self) -> float:
        """Calculate overall security score (0-100) with detailed audit trail."""
        base_score = 100.0
        deductions = 0.0
        audit_entries = []

        # Deduction rules for each metric
        deduction_rules = {
            "failed_login_attempts": {"multiplier": 2, "cap": 20, "severity": "high"},
            "unauthorized_access_attempts": {"multiplier": 10, "cap": 30, "severity": "critical"},
            "network_intrusion_attempts": {"multiplier": 15, "cap": 40, "severity": "critical"},
        }

        # Apply deductions based on metrics
        for metric, rules in deduction_rules.items():
            if metric in self.metrics:
                value = self.metrics[metric]
                points = min(value * rules["multiplier"], rules["cap"])
                deductions += points
                audit_entries.append({
                    "reason": f"{rules['severity'].capitalize()} issue: {metric}",
                    "points": -points,
                    "value": value
                })

        # Apply deductions for active anomalies
        if self.anomalies:
            critical = sum(1 for a in self.anomalies if a.get("severity") == "critical")
            high = sum(1 for a in self.anomalies if a.get("severity") == "high")
            anomaly_points = critical * 5 + high * 2
            deductions += anomaly_points
            audit_entries.append({
                "reason": "Active anomalies",
                "points": -anomaly_points,
                "critical_count": critical,
                "high_count": high
            })

        # Calculate final score (bounded 0-100)
        final_score = max(0.0, min(100.0, base_score - deductions))
        self.security_score = final_score

        # Store audit trail for transparency
        self.audit_trail = audit_entries

        return final_score
    
    def get_security_score(self) -> float:
        """Get the current security score."""
        return self._calculate_security_score()
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Get the audit trail showing how the security score was calculated.
        
        Returns:
            List of audit entry dictionaries with reasons and point deductions
        """
        return self.audit_trail.copy()
    
    def get_metric_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get historical metrics snapshots.
        
        Args:
            limit: Optional limit on number of history entries to return (most recent)
            
        Returns:
            List of historical metric snapshots with timestamps
        """
        if limit:
            return self.metric_history[-limit:]
        return self.metric_history.copy()
    
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
