"""
Remote Management Module

Designed for managing security infrastructure in unmanned remote locations
with limited physical access and intermittent connectivity.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


class ManagementMode(Enum):
    """Remote management modes"""
    AUTONOMOUS = "autonomous"    # Fully autonomous operation
    SUPERVISED = "supervised"    # Periodic check-ins
    MANUAL = "manual"           # Requires manual intervention


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RemoteAlert:
    """Remote alert notification"""
    timestamp: datetime
    severity: AlertSeverity
    component: str
    message: str
    auto_resolved: bool
    requires_action: bool


@dataclass
class HealthStatus:
    """System health status"""
    timestamp: datetime
    overall_health: str  # "healthy", "degraded", "critical"
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    connection_quality: str
    uptime_hours: float
    alerts_count: int


@dataclass
class RemoteCommand:
    """Remote management command"""
    command_id: str
    timestamp: datetime
    command_type: str
    parameters: Dict[str, Any]
    status: str  # "pending", "executing", "completed", "failed"
    result: Optional[str]


class RemoteManager:
    """
    Manages security infrastructure for unmanned remote locations with
    autonomous operation capabilities and efficient remote administration.
    """
    
    def __init__(self, 
                 mode: ManagementMode = ManagementMode.SUPERVISED,
                 checkin_interval_minutes: int = 60,
                 autonomous_recovery: bool = True):
        """
        Initialize remote manager
        
        Args:
            mode: Management mode (autonomous, supervised, manual)
            checkin_interval_minutes: Minutes between check-ins
            autonomous_recovery: Enable autonomous error recovery
        """
        self.mode = mode
        self.checkin_interval = checkin_interval_minutes
        self.autonomous_recovery = autonomous_recovery
        
        self._alerts: List[RemoteAlert] = []
        self._command_queue: List[RemoteCommand] = []
        self._health_history: List[HealthStatus] = []
        self._configuration_cache: Dict[str, Any] = {}
        self._last_checkin: Optional[datetime] = None
    
    def add_alert(self, severity: AlertSeverity, component: str, 
                  message: str, auto_resolved: bool = False,
                  requires_action: bool = False) -> RemoteAlert:
        """
        Add a new alert
        
        Args:
            severity: Alert severity level
            component: Component that generated the alert
            message: Alert message
            auto_resolved: Whether alert was automatically resolved
            requires_action: Whether alert requires manual action
            
        Returns:
            Created alert
        """
        alert = RemoteAlert(
            timestamp=datetime.now(),
            severity=severity,
            component=component,
            message=message,
            auto_resolved=auto_resolved,
            requires_action=requires_action
        )
        self._alerts.append(alert)
        return alert
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None,
                   unresolved_only: bool = False) -> List[RemoteAlert]:
        """
        Get alerts filtered by criteria
        
        Args:
            severity: Filter by severity level
            unresolved_only: Only return unresolved alerts
            
        Returns:
            List of matching alerts
        """
        alerts = self._alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.auto_resolved]
        
        return alerts
    
    def clear_resolved_alerts(self) -> int:
        """
        Clear auto-resolved alerts
        
        Returns:
            Number of alerts cleared
        """
        before_count = len(self._alerts)
        self._alerts = [a for a in self._alerts if not a.auto_resolved]
        return before_count - len(self._alerts)
    
    def record_health_status(self, status: HealthStatus) -> None:
        """
        Record system health status
        
        Args:
            status: Current health status
        """
        self._health_history.append(status)
        
        # Keep only last 24 hours of history (assuming hourly checks)
        if len(self._health_history) > 24:
            self._health_history = self._health_history[-24:]
    
    def get_current_health(self) -> Optional[HealthStatus]:
        """Get most recent health status"""
        return self._health_history[-1] if self._health_history else None
    
    def get_health_trend(self, hours: int = 24) -> List[HealthStatus]:
        """
        Get health status trend
        
        Args:
            hours: Number of hours of history to return
            
        Returns:
            List of health status records
        """
        return self._health_history[-hours:]
    
    def queue_command(self, command_type: str, 
                     parameters: Dict[str, Any]) -> RemoteCommand:
        """
        Queue a remote command for execution
        
        Args:
            command_type: Type of command to execute
            parameters: Command parameters
            
        Returns:
            Queued command
        """
        command = RemoteCommand(
            command_id=f"cmd_{len(self._command_queue)}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            command_type=command_type,
            parameters=parameters,
            status="pending",
            result=None
        )
        self._command_queue.append(command)
        return command
    
    def execute_next_command(self) -> Optional[RemoteCommand]:
        """
        Execute the next pending command
        
        Returns:
            Executed command or None if queue is empty
        """
        pending_commands = [c for c in self._command_queue if c.status == "pending"]
        
        if not pending_commands:
            return None
        
        command = pending_commands[0]
        command.status = "executing"
        
        # Execute command based on type
        result = self._execute_command(command)
        
        command.status = "completed" if result else "failed"
        command.result = result
        
        return command
    
    def _execute_command(self, command: RemoteCommand) -> Optional[str]:
        """
        Execute a specific command
        
        Args:
            command: Command to execute
            
        Returns:
            Command result or None if failed
        """
        # Placeholder for command execution logic
        # In production, this would execute actual management commands
        command_handlers = {
            'update_config': self._handle_config_update,
            'restart_service': self._handle_service_restart,
            'collect_diagnostics': self._handle_diagnostics_collection,
            'update_policy': self._handle_policy_update,
        }
        
        handler = command_handlers.get(command.command_type)
        if handler:
            return handler(command.parameters)
        
        return f"Unknown command type: {command.command_type}"
    
    def _handle_config_update(self, params: Dict[str, Any]) -> str:
        """Handle configuration update command"""
        self._configuration_cache.update(params)
        return f"Configuration updated with {len(params)} parameters"
    
    def _handle_service_restart(self, params: Dict[str, Any]) -> str:
        """Handle service restart command"""
        service_name = params.get('service', 'unknown')
        return f"Service {service_name} restart initiated"
    
    def _handle_diagnostics_collection(self, params: Dict[str, Any]) -> str:
        """Handle diagnostics collection command"""
        return "Diagnostics collected successfully"
    
    def _handle_policy_update(self, params: Dict[str, Any]) -> str:
        """Handle policy update command"""
        policy_name = params.get('policy', 'unknown')
        return f"Policy {policy_name} updated"
    
    def perform_checkin(self) -> Dict[str, Any]:
        """
        Perform periodic check-in with management server
        
        Returns:
            Check-in data including health status and alerts
        """
        self._last_checkin = datetime.now()
        
        current_health = self.get_current_health()
        unresolved_alerts = self.get_alerts(unresolved_only=True)
        pending_commands = [c for c in self._command_queue if c.status == "pending"]
        
        checkin_data = {
            'timestamp': self._last_checkin.isoformat(),
            'mode': self.mode.value,
            'health': current_health.__dict__ if current_health else None,
            'alerts_count': len(unresolved_alerts),
            'critical_alerts': len([a for a in unresolved_alerts 
                                   if a.severity == AlertSeverity.CRITICAL]),
            'pending_commands': len(pending_commands),
            'autonomous_recovery_enabled': self.autonomous_recovery,
        }
        
        return checkin_data
    
    def get_last_checkin(self) -> Optional[datetime]:
        """Get timestamp of last check-in"""
        return self._last_checkin
    
    def enable_autonomous_mode(self) -> None:
        """Enable fully autonomous operation mode"""
        self.mode = ManagementMode.AUTONOMOUS
        self.autonomous_recovery = True
    
    def get_configuration_cache(self) -> Dict[str, Any]:
        """Get cached configuration for offline operation"""
        return self._configuration_cache.copy()
    
    def update_configuration_cache(self, config: Dict[str, Any]) -> None:
        """
        Update configuration cache for offline operation
        
        Args:
            config: Configuration data to cache
        """
        self._configuration_cache.update(config)
