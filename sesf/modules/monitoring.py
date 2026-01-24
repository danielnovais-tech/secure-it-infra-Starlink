"""
Monitoring Module for SESF

Provides real-time monitoring, logging, and alerting capabilities
for Starlink infrastructure security.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque


class MonitoringModule:
    """
    Handles monitoring and logging for SESF.
    
    Provides real-time monitoring, event logging,
    metrics collection, and alerting.
    """
    
    ALERT_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize monitoring module.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.log_level = self.config.get("log_level", "INFO")
        self.alert_threshold = self.config.get("alert_threshold", "HIGH")
        self.metrics_enabled = self.config.get("metrics_collection", True)
        
        self.logger = self._setup_logger()
        self.events = deque(maxlen=10000)
        self.alerts = []
        self.metrics = {
            "requests_total": 0,
            "requests_blocked": 0,
            "authentication_success": 0,
            "authentication_failure": 0,
            "encryption_operations": 0,
            "intrusion_attempts": 0
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup monitoring logger."""
        logger = logging.getLogger("SESF.Monitoring")
        logger.setLevel(getattr(logging, self.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def log_event(self, event_type: str, details: Dict, level: str = "INFO"):
        """
        Log a security event.
        
        Args:
            event_type: Type of event (auth, network, encryption, etc.)
            details: Event details
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if not self.enabled:
            return
        
        event = {
            "timestamp": datetime.now(),
            "type": event_type,
            "level": level,
            "details": details
        }
        
        self.events.append(event)
        
        # Log to standard logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"{event_type}: {details}")
        
        # Check if alert should be triggered
        if self._should_alert(level):
            self._create_alert(event)
    
    def _should_alert(self, level: str) -> bool:
        """Determine if event level warrants an alert."""
        level_priority = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
        
        threshold_priority = level_priority.get(self.alert_threshold, 2)
        event_priority = level_priority.get(level, 0)
        
        return event_priority >= threshold_priority
    
    def _create_alert(self, event: Dict):
        """Create an alert for significant events."""
        alert = {
            "id": len(self.alerts) + 1,
            "timestamp": event["timestamp"],
            "type": event["type"],
            "level": event["level"],
            "message": f"{event['type']} event: {event['details']}",
            "status": "open",
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"ALERT CREATED: {alert['message']}")
    
    def update_metric(self, metric_name: str, value: int = 1):
        """
        Update a metric counter.
        
        Args:
            metric_name: Name of the metric
            value: Value to add (default 1)
        """
        if not self.metrics_enabled:
            return
        
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
        else:
            self.metrics[metric_name] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dict with all metrics
        """
        return self.metrics.copy()
    
    def get_events(self, 
                   event_type: Optional[str] = None, 
                   level: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """
        Retrieve logged events.
        
        Args:
            event_type: Filter by event type
            level: Filter by level
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = list(self.events)
        
        # Apply filters
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        if level:
            events = [e for e in events if e["level"] == level]
        
        # Return most recent events first
        events.reverse()
        
        return events[:limit]
    
    def get_alerts(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get alerts.
        
        Args:
            status: Filter by status (open, closed)
            
        Returns:
            List of alerts
        """
        if status:
            return [a for a in self.alerts if a["status"] == status]
        return self.alerts.copy()
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            bool: True if alert was acknowledged
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now()
                return True
        return False
    
    def close_alert(self, alert_id: int) -> bool:
        """
        Close an alert.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            bool: True if alert was closed
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["status"] = "closed"
                alert["closed_at"] = datetime.now()
                return True
        return False
    
    def generate_report(self, time_period: str = "24h") -> Dict:
        """
        Generate a security monitoring report.
        
        Args:
            time_period: Time period for report (24h, 7d, 30d)
            
        Returns:
            Dict with report data
        """
        return {
            "period": time_period,
            "generated_at": datetime.now().isoformat(),
            "metrics": self.get_metrics(),
            "total_events": len(self.events),
            "total_alerts": len(self.alerts),
            "open_alerts": len([a for a in self.alerts if a["status"] == "open"]),
            "critical_events": len([e for e in self.events if e["level"] == "CRITICAL"]),
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> str:
        """Generate a text summary of monitoring data."""
        open_alerts = len([a for a in self.alerts if a["status"] == "open"])
        critical_events = len([e for e in self.events if e["level"] == "CRITICAL"])
        
        summary = "Monitoring Status: "
        if critical_events > 0 or open_alerts > 0:
            summary += f"ATTENTION REQUIRED - {open_alerts} open alerts, {critical_events} critical events"
        else:
            summary += "NORMAL - No critical issues detected"
        
        return summary
