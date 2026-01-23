"""
Policy Enforcer Module
Provides dynamic policy application based on security level.
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class SecurityLevel(Enum):
    """Security level classifications."""
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    MAXIMUM = 5


class PolicyAction(Enum):
    """Available policy actions."""
    ALLOW = "allow"
    DENY = "deny"
    QUARANTINE = "quarantine"
    MONITOR = "monitor"
    ALERT = "alert"


class PolicyEnforcer:
    """
    Policy enforcement service for Starlink infrastructure.
    
    Features:
    - Dynamic policy application based on security level
    - Rule-based access control
    - Automated policy enforcement
    """
    
    def __init__(self, default_security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """
        Initialize the Policy Enforcer.
        
        Args:
            default_security_level: Default security level for the system
        """
        self.current_security_level = default_security_level
        self.active_policies = []
        self.policy_violations = []
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Policy Enforcer initialized with security level: {default_security_level.name}")
    
    def set_security_level(self, level: SecurityLevel) -> bool:
        """
        Set the current security level and apply corresponding policies.
        
        Args:
            level: New security level to apply
        
        Returns:
            True if security level was changed successfully
        """
        old_level = self.current_security_level
        self.current_security_level = level
        
        self.logger.info(f"Security level changed from {old_level.name} to {level.name}")
        
        # Apply policies based on new security level
        self._apply_level_policies(level)
        
        return True
    
    def _apply_level_policies(self, level: SecurityLevel) -> None:
        """
        Apply policies appropriate for the given security level.
        
        Args:
            level: Security level to apply policies for
        """
        # Clear existing policies
        self.active_policies.clear()
        
        # Base policies for all levels
        base_policies = [
            {"name": "log_all_access", "action": PolicyAction.MONITOR.value},
            {"name": "encrypt_data_at_rest", "action": PolicyAction.ALLOW.value}
        ]
        
        self.active_policies.extend(base_policies)
        
        # Additional policies based on security level
        if level.value >= SecurityLevel.LOW.value:
            self.active_policies.append({
                "name": "require_authentication",
                "action": PolicyAction.DENY.value,
                "condition": "no_auth"
            })
        
        if level.value >= SecurityLevel.MEDIUM.value:
            self.active_policies.extend([
                {"name": "require_mfa", "action": PolicyAction.DENY.value},
                {"name": "block_unknown_devices", "action": PolicyAction.QUARANTINE.value}
            ])
        
        if level.value >= SecurityLevel.HIGH.value:
            self.active_policies.extend([
                {"name": "restrict_network_access", "action": PolicyAction.DENY.value},
                {"name": "enable_strict_firewall", "action": PolicyAction.DENY.value},
                {"name": "mandatory_encryption", "action": PolicyAction.DENY.value}
            ])
        
        if level.value >= SecurityLevel.MAXIMUM.value:
            self.active_policies.extend([
                {"name": "lockdown_mode", "action": PolicyAction.DENY.value},
                {"name": "allow_only_whitelist", "action": PolicyAction.DENY.value},
                {"name": "continuous_monitoring", "action": PolicyAction.ALERT.value}
            ])
        
        self.logger.info(f"Applied {len(self.active_policies)} policies for {level.name} security level")
    
    def enforce_policy(self, resource: str, action: str, context: Optional[Dict] = None) -> Dict:
        """
        Enforce policy for a specific resource and action.
        
        Args:
            resource: Resource being accessed
            action: Action being attempted
            context: Additional context for policy evaluation
        
        Returns:
            Dictionary containing enforcement decision
        """
        if context is None:
            context = {}
        
        self.logger.info(f"Evaluating policy for {action} on {resource}")
        
        decision = {
            "allowed": True,
            "action": PolicyAction.ALLOW.value,
            "reason": "No matching policy",
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would:
        # - Match resource and action against active policies
        # - Evaluate conditions based on context
        # - Apply policy precedence rules
        # - Log policy decisions
        
        # Check for violations
        if not decision["allowed"]:
            self._record_violation(resource, action, decision)
        
        return decision
    
    def _record_violation(self, resource: str, action: str, decision: Dict) -> None:
        """
        Record a policy violation.
        
        Args:
            resource: Resource that was accessed
            action: Action that was attempted
            decision: Policy decision details
        """
        violation = {
            "resource": resource,
            "action": action,
            "decision": decision,
            "security_level": self.current_security_level.name,
            "timestamp": datetime.now().isoformat()
        }
        
        self.policy_violations.append(violation)
        self.logger.warning(f"Policy violation recorded for {action} on {resource}")
    
    def add_custom_policy(self, name: str, rules: Dict) -> bool:
        """
        Add a custom policy rule.
        
        Args:
            name: Name of the policy
            rules: Policy rules and conditions
        
        Returns:
            True if policy was added successfully
        """
        policy = {
            "name": name,
            "rules": rules,
            "created_at": datetime.now().isoformat()
        }
        
        self.active_policies.append(policy)
        self.logger.info(f"Custom policy added: {name}")
        
        return True
    
    def remove_policy(self, policy_name: str) -> bool:
        """
        Remove a policy by name.
        
        Args:
            policy_name: Name of the policy to remove
        
        Returns:
            True if policy was removed successfully
        """
        initial_count = len(self.active_policies)
        self.active_policies = [p for p in self.active_policies if p["name"] != policy_name]
        
        removed = len(self.active_policies) < initial_count
        
        if removed:
            self.logger.info(f"Policy removed: {policy_name}")
        else:
            self.logger.warning(f"Policy not found: {policy_name}")
        
        return removed
    
    def get_policy_status(self) -> Dict:
        """
        Get current policy enforcement status.
        
        Returns:
            Dictionary containing policy statistics
        """
        return {
            "security_level": self.current_security_level.name,
            "active_policies": len(self.active_policies),
            "violations": len(self.policy_violations),
            "timestamp": datetime.now().isoformat()
        }
