"""
Automated response system for threat containment, policy enforcement, and failover.

Provides automated and configurable responses to security threats, policy violations,
and infrastructure failures.
"""

import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ResponseStatus(Enum):
    """Status of an automated response."""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(Enum):
    """Severity levels for threats and incidents."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AutomatedAction:
    """Represents an automated action to be taken."""
    action_type: str
    severity: SeverityLevel
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    status: ResponseStatus = ResponseStatus.PENDING
    auto_execute: bool = False
    cooldown: int = 300  # seconds
    result: Optional[str] = None


class ThreatContainment:
    """
    Threat containment system for isolating and mitigating security threats.
    
    Handles threat isolation, IP blocking, and traffic quarantine with
    configurable severity thresholds and cooldown periods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize threat containment.
        
        Args:
            config: Threat containment configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_execute = config.get('auto_execute', False)
        self.actions_config = config.get('actions', [])
        self.active_containments: List[AutomatedAction] = []
        self.containment_history: List[AutomatedAction] = []
    
    def isolate_device(self, device_id: str, severity: SeverityLevel, reason: str) -> AutomatedAction:
        """
        Isolate a device from the network.
        
        Args:
            device_id: ID of the device to isolate
            severity: Severity level of the threat
            reason: Reason for isolation
            
        Returns:
            AutomatedAction instance
        """
        action = AutomatedAction(
            action_type='isolate_device',
            severity=severity,
            target=device_id,
            parameters={'reason': reason},
            auto_execute=self.auto_execute,
            cooldown=self._get_cooldown('isolate_device')
        )
        
        self.active_containments.append(action)
        return action
    
    def block_ip(self, ip_address: str, severity: SeverityLevel, reason: str) -> AutomatedAction:
        """
        Block an IP address.
        
        Args:
            ip_address: IP address to block
            severity: Severity level of the threat
            reason: Reason for blocking
            
        Returns:
            AutomatedAction instance
        """
        action = AutomatedAction(
            action_type='block_ip',
            severity=severity,
            target=ip_address,
            parameters={'reason': reason},
            auto_execute=self.auto_execute,
            cooldown=self._get_cooldown('block_ip')
        )
        
        self.active_containments.append(action)
        return action
    
    def quarantine_traffic(self, source: str, severity: SeverityLevel, reason: str) -> AutomatedAction:
        """
        Quarantine traffic from a source.
        
        Args:
            source: Source to quarantine (IP, device, etc.)
            severity: Severity level of the threat
            reason: Reason for quarantine
            
        Returns:
            AutomatedAction instance
        """
        action = AutomatedAction(
            action_type='quarantine_traffic',
            severity=severity,
            target=source,
            parameters={'reason': reason},
            auto_execute=self.auto_execute,
            cooldown=self._get_cooldown('quarantine_traffic')
        )
        
        self.active_containments.append(action)
        return action
    
    def _get_cooldown(self, action_type: str) -> int:
        """Get cooldown period for an action type."""
        for action_config in self.actions_config:
            if action_config.get('type') == action_type:
                return action_config.get('cooldown', 300)
        return 300
    
    def execute_action(self, action: AutomatedAction) -> bool:
        """
        Execute a containment action.
        
        Args:
            action: Action to execute
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            action.status = ResponseStatus.FAILED
            action.result = "Threat containment is disabled"
            return False
        
        action.status = ResponseStatus.EXECUTING
        
        # Simulate execution (in real implementation, this would perform actual containment)
        try:
            # Log the action
            print(f"Executing {action.action_type} on {action.target} (severity: {action.severity.value})")
            
            action.status = ResponseStatus.COMPLETED
            action.result = f"Successfully executed {action.action_type}"
            self.containment_history.append(action)
            return True
        except Exception as e:
            action.status = ResponseStatus.FAILED
            action.result = f"Failed to execute: {str(e)}"
            return False


class PolicyEnforcement:
    """
    Policy enforcement system for ensuring compliance with security policies.
    
    Monitors and enforces policies related to bandwidth limits, authentication,
    and malware detection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize policy enforcement.
        
        Args:
            config: Policy enforcement configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_execute = config.get('auto_execute', True)
        self.policies = config.get('policies', [])
        self.active_enforcements: List[AutomatedAction] = []
        self.enforcement_history: List[AutomatedAction] = []
    
    def check_policies(self, context: Dict[str, Any]) -> List[AutomatedAction]:
        """
        Check all policies against current context.
        
        Args:
            context: Current system context with relevant metrics
            
        Returns:
            List of actions to be taken
        """
        actions = []
        
        for policy in self.policies:
            if self._evaluate_policy(policy, context):
                action = self._create_policy_action(policy, context)
                actions.append(action)
                self.active_enforcements.append(action)
        
        return actions
    
    def _evaluate_policy(self, policy: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate if a policy condition is met.
        
        Args:
            policy: Policy configuration
            context: Current context
            
        Returns:
            True if policy condition is met
        """
        condition = policy.get('condition', '')
        threshold = policy.get('threshold', 0)
        
        # Simple condition evaluation (in real implementation, use proper expression parser)
        if 'bandwidth_usage' in condition:
            return context.get('bandwidth_usage', 0) > threshold
        elif 'failed_auth_attempts' in condition:
            return context.get('failed_auth_attempts', 0) > threshold
        elif 'malware_detected' in condition:
            return context.get('malware_detected', False)
        
        return False
    
    def _create_policy_action(self, policy: Dict[str, Any], context: Dict[str, Any]) -> AutomatedAction:
        """Create an action based on policy violation."""
        return AutomatedAction(
            action_type=policy.get('action', 'alert'),
            severity=SeverityLevel.MEDIUM,
            target=policy.get('name', 'unknown'),
            parameters={'policy': policy, 'context': context},
            auto_execute=self.auto_execute
        )
    
    def execute_action(self, action: AutomatedAction) -> bool:
        """
        Execute a policy enforcement action.
        
        Args:
            action: Action to execute
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            action.status = ResponseStatus.FAILED
            action.result = "Policy enforcement is disabled"
            return False
        
        action.status = ResponseStatus.EXECUTING
        
        try:
            print(f"Enforcing policy: {action.target} with action {action.action_type}")
            
            action.status = ResponseStatus.COMPLETED
            action.result = f"Policy enforcement completed: {action.action_type}"
            self.enforcement_history.append(action)
            return True
        except Exception as e:
            action.status = ResponseStatus.FAILED
            action.result = f"Failed to enforce: {str(e)}"
            return False


class FailoverActivation:
    """
    Failover activation system for switching to backup links.
    
    Handles automatic failover to backup connections based on triggers
    like connection loss, performance degradation, or security breaches.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize failover activation.
        
        Args:
            config: Failover configuration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.auto_execute = config.get('auto_execute', True)
        self.triggers = config.get('triggers', [])
        self.backup_links = config.get('backup_links', [])
        self.active_link = None
        self.failover_history: List[Dict[str, Any]] = []
    
    def check_triggers(self, metrics: Dict[str, Any]) -> Optional[AutomatedAction]:
        """
        Check if any failover triggers are activated.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            AutomatedAction if failover needed, None otherwise
        """
        for trigger in self.triggers:
            if self._evaluate_trigger(trigger, metrics):
                return self._create_failover_action(trigger, metrics)
        
        return None
    
    def _evaluate_trigger(self, trigger: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """
        Evaluate if a trigger condition is met.
        
        Args:
            trigger: Trigger configuration
            metrics: Current metrics
            
        Returns:
            True if trigger condition is met
        """
        trigger_type = trigger.get('type')
        threshold = trigger.get('threshold')
        
        if trigger_type == 'connection_loss':
            return metrics.get('connection_down_time', 0) > threshold
        elif trigger_type == 'performance_degradation':
            return metrics.get('performance_score', 100) < threshold
        elif trigger_type == 'security_breach':
            return metrics.get('security_level') == threshold
        
        return False
    
    def _create_failover_action(self, trigger: Dict[str, Any], metrics: Dict[str, Any]) -> AutomatedAction:
        """Create a failover action based on trigger."""
        return AutomatedAction(
            action_type=trigger.get('action', 'switch_to_backup'),
            severity=SeverityLevel.HIGH,
            target='failover',
            parameters={'trigger': trigger, 'metrics': metrics},
            auto_execute=self.auto_execute
        )
    
    def execute_failover(self, action: AutomatedAction) -> bool:
        """
        Execute a failover action.
        
        Args:
            action: Failover action to execute
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            action.status = ResponseStatus.FAILED
            action.result = "Failover is disabled"
            return False
        
        action.status = ResponseStatus.EXECUTING
        
        try:
            # Select backup link based on priority
            backup_link = self._select_backup_link()
            
            if backup_link:
                print(f"Activating failover to: {backup_link['name']}")
                self.active_link = backup_link
                
                self.failover_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': action.action_type,
                    'backup_link': backup_link,
                    'trigger': action.parameters.get('trigger')
                })
                
                action.status = ResponseStatus.COMPLETED
                action.result = f"Failover to {backup_link['name']} completed"
                return True
            else:
                action.status = ResponseStatus.FAILED
                action.result = "No backup link available"
                return False
        except Exception as e:
            action.status = ResponseStatus.FAILED
            action.result = f"Failover failed: {str(e)}"
            return False
    
    def _select_backup_link(self) -> Optional[Dict[str, Any]]:
        """Select the highest priority available backup link."""
        if not self.backup_links:
            return None
        
        # Sort by priority and return the first one
        sorted_links = sorted(self.backup_links, key=lambda x: x.get('priority', 999))
        return sorted_links[0] if sorted_links else None


class AutomatedResponseCoordinator:
    """
    Coordinates all automated response systems.
    
    Main coordinator that manages threat containment, policy enforcement,
    and failover activation systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize automated response coordinator.
        
        Args:
            config: Complete automated responses configuration
        """
        self.config = config
        self.threat_containment = ThreatContainment(config.get('threat_containment', {}))
        self.policy_enforcement = PolicyEnforcement(config.get('policy_enforcement', {}))
        self.failover_activation = FailoverActivation(config.get('failover', {}))
        
        self.pending_actions: List[AutomatedAction] = []
        self.action_history: List[AutomatedAction] = []
    
    def process_event(self, event: Dict[str, Any]) -> List[AutomatedAction]:
        """
        Process an event and determine appropriate responses.
        
        Args:
            event: Event data including type, severity, and context
            
        Returns:
            List of automated actions to be taken
        """
        actions = []
        
        event_type = event.get('type')
        severity = event.get('severity', 'low')
        
        # Check for threat containment needs
        if event_type in ['security_threat', 'malware_detected', 'intrusion_attempt']:
            # Safely convert severity to enum with fallback
            try:
                severity_level = SeverityLevel[severity.upper()]
            except (KeyError, AttributeError):
                severity_level = SeverityLevel.LOW
            
            if event.get('device_id'):
                action = self.threat_containment.isolate_device(
                    event['device_id'],
                    severity_level,
                    event.get('reason', 'Security threat detected')
                )
                actions.append(action)
            
            if event.get('source_ip'):
                action = self.threat_containment.block_ip(
                    event['source_ip'],
                    severity_level,
                    event.get('reason', 'Malicious IP detected')
                )
                actions.append(action)
        
        # Check for policy violations
        policy_actions = self.policy_enforcement.check_policies(event.get('context', {}))
        actions.extend(policy_actions)
        
        # Check for failover triggers
        failover_action = self.failover_activation.check_triggers(event.get('metrics', {}))
        if failover_action:
            actions.append(failover_action)
        
        # Add to pending actions
        self.pending_actions.extend(actions)
        
        # Auto-execute if configured
        for action in actions:
            if action.auto_execute:
                self.execute_action(action)
        
        return actions
    
    def execute_action(self, action: AutomatedAction) -> bool:
        """
        Execute an automated action.
        
        Args:
            action: Action to execute
            
        Returns:
            True if successful, False otherwise
        """
        if action.action_type in ['isolate_device', 'block_ip', 'quarantine_traffic']:
            result = self.threat_containment.execute_action(action)
        elif action.action_type in ['throttle_connection', 'block_source', 'isolate_and_alert']:
            result = self.policy_enforcement.execute_action(action)
        elif action.action_type in ['switch_to_backup', 'load_balance', 'emergency_shutdown']:
            result = self.failover_activation.execute_failover(action)
        else:
            action.status = ResponseStatus.FAILED
            action.result = f"Unknown action type: {action.action_type}"
            result = False
        
        self.action_history.append(action)
        
        if action in self.pending_actions:
            self.pending_actions.remove(action)
        
        return result
    
    def get_pending_actions(self) -> List[AutomatedAction]:
        """Get all pending actions."""
        return self.pending_actions.copy()
    
    def get_action_history(self, limit: int = 100) -> List[AutomatedAction]:
        """
        Get action history.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent actions
        """
        return self.action_history[-limit:]
