"""
Security Logging and Alerting Module

Provides comprehensive logging and alerting for security events
in Starlink-connected infrastructures.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from .structured_logger import StructuredLogger, EventCorrelator


__all__ = ["StructuredLogger", "EventCorrelator"]


class LogLevel(Enum):
    """Security log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityLogger:
    """
    Comprehensive security event logger.
    
    Logs security events with context, severity, and timestamps.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the Security Logger.
        
        Args:
            log_file: Optional file path for persistent logging
        """
        self.log_file = log_file
        self.logs: List[Dict[str, Any]] = []
        self.min_level = LogLevel.INFO

    def log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a security event.
        
        Args:
            level: Log severity level
            message: Log message
            context: Additional context data
            
        Returns:
            The created log entry
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
            "context": context or {}
        }

        self.logs.append(log_entry)

        if self.log_file:
            self._write_to_file(log_entry)

        return log_entry

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log a debug message."""
        return self.log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log an info message."""
        return self.log(LogLevel.INFO, message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log a warning message."""
        return self.log(LogLevel.WARNING, message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log an error message."""
        return self.log(LogLevel.ERROR, message, context)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log a critical message."""
        return self.log(LogLevel.CRITICAL, message, context)

    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve logs, optionally filtered by level.
        
        Args:
            level: Optional level filter
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        filtered_logs = self.logs
        if level:
            filtered_logs = [log for log in self.logs if log["level"] == level.value]

        if limit:
            return filtered_logs[-limit:]
        return filtered_logs.copy()

    def clear_logs(self) -> None:
        """Clear all logs."""
        self.logs.clear()

    def _write_to_file(self, log_entry: Dict[str, Any]) -> None:
        """Write log entry to file."""
        if self.log_file:
            try:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception:
                # Fail silently to avoid breaking the application
                pass


class AlertManager:
    """
    Manage security alerts and notifications.
    
    Creates, tracks, and manages security alerts based on events.
    """

    def __init__(self, alert_threshold: Optional[int] = None):
        """
        Initialize the Alert Manager.
        
        Args:
            alert_threshold: Minimum number of events to trigger an alert
        """
        self.alerts: List[Dict[str, Any]] = []
        self.alert_threshold = alert_threshold or 3
        self.active_alerts = 0

    def create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new security alert.
        
        Args:
            severity: Alert severity level
            title: Alert title
            description: Detailed description
            context: Additional context data
            
        Returns:
            The created alert
        """
        alert = {
            "alert_id": f"ALERT-{len(self.alerts) + 1:06d}",
            "timestamp": datetime.now().isoformat(),
            "severity": severity.value,
            "title": title,
            "description": description,
            "context": context or {},
            "status": "active",
            "acknowledged": False
        }

        self.alerts.append(alert)
        self.active_alerts += 1

        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            True if alert was acknowledged, False otherwise
        """
        for alert in self.alerts:
            if alert["alert_id"] == alert_id and not alert["acknowledged"]:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                return True
        return False

    def resolve_alert(self, alert_id: str, resolution: str = "") -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert identifier
            resolution: Resolution notes
            
        Returns:
            True if alert was resolved, False otherwise
        """
        for alert in self.alerts:
            if alert["alert_id"] == alert_id and alert["status"] == "active":
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolution"] = resolution
                self.active_alerts -= 1
                return True
        return False

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alerts, optionally filtered by severity and status.
        
        Args:
            severity: Optional severity filter
            status: Optional status filter (active, resolved)
            
        Returns:
            List of alerts
        """
        filtered_alerts = self.alerts

        if severity:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert["severity"] == severity.value
            ]

        if status:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert["status"] == status
            ]

        return filtered_alerts.copy()

    def get_active_alert_count(self) -> int:
        """
        Get the count of active alerts.
        
        Returns:
            Number of active alerts
        """
        return self.active_alerts

    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Dictionary containing alert statistics
        """
        stats = {
            "total_alerts": len(self.alerts),
            "active_alerts": self.active_alerts,
            "resolved_alerts": len([a for a in self.alerts if a["status"] == "resolved"]),
            "by_severity": {}
        }

        for severity in AlertSeverity:
            count = len([a for a in self.alerts if a["severity"] == severity.value])
            stats["by_severity"][severity.value] = count

        return stats
