"""
Network Security Module for SESF

Provides network security controls including firewall rules,
intrusion detection, and rate limiting for Starlink infrastructure.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict


class NetworkSecurityModule:
    """
    Handles network security for SESF.
    
    Implements firewall rules, intrusion detection,
    rate limiting, and protocol filtering.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize network security module.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.firewall_enabled = self.config.get("firewall_enabled", True)
        self.ids_enabled = self.config.get("intrusion_detection", True)
        self.rate_limiting_enabled = self.config.get("rate_limiting", True)
        
        self.firewall_rules = []
        self.blocked_ips = set()
        self.allowed_protocols = set(self.config.get("allowed_protocols", ["HTTPS", "SSH"]))
        self.rate_limit_data = defaultdict(list)
        self.intrusion_attempts = []
    
    def add_firewall_rule(self, rule: Dict) -> bool:
        """
        Add a firewall rule.
        
        Args:
            rule: Firewall rule dictionary with action, protocol, source, destination
            
        Returns:
            bool: True if rule was added
        """
        if not self.firewall_enabled:
            return False
        
        rule["created_at"] = datetime.now()
        rule["id"] = len(self.firewall_rules) + 1
        self.firewall_rules.append(rule)
        
        return True
    
    def check_firewall(self, source_ip: str, dest_ip: str, protocol: str, port: int) -> Dict:
        """
        Check if traffic is allowed by firewall rules.
        
        Args:
            source_ip: Source IP address
            dest_ip: Destination IP address
            protocol: Network protocol
            port: Destination port
            
        Returns:
            Dict with allow/deny decision and reason
        """
        if not self.firewall_enabled:
            return {"allowed": True, "reason": "Firewall disabled"}
        
        # Check if IP is blocked
        if source_ip in self.blocked_ips:
            return {"allowed": False, "reason": "Source IP blocked"}
        
        # Check protocol whitelist
        if protocol not in self.allowed_protocols:
            return {"allowed": False, "reason": f"Protocol {protocol} not allowed"}
        
        # Check firewall rules
        for rule in self.firewall_rules:
            if self._match_rule(rule, source_ip, dest_ip, protocol, port):
                if rule.get("action") == "deny":
                    return {"allowed": False, "reason": f"Denied by rule {rule['id']}"}
                elif rule.get("action") == "allow":
                    return {"allowed": True, "reason": f"Allowed by rule {rule['id']}"}
        
        # Default deny
        return {"allowed": False, "reason": "No matching allow rule"}
    
    def _match_rule(self, rule: Dict, source_ip: str, dest_ip: str, protocol: str, port: int) -> bool:
        """Check if traffic matches a firewall rule."""
        if "protocol" in rule and rule["protocol"] != protocol:
            return False
        if "port" in rule and rule["port"] != port:
            return False
        # Simplified matching - in production would handle CIDR, ranges, etc.
        return True
    
    def block_ip(self, ip_address: str, reason: str = "Manual block") -> bool:
        """
        Block an IP address.
        
        Args:
            ip_address: IP address to block
            reason: Reason for blocking
            
        Returns:
            bool: True if IP was blocked
        """
        self.blocked_ips.add(ip_address)
        self.intrusion_attempts.append({
            "ip": ip_address,
            "action": "blocked",
            "reason": reason,
            "timestamp": datetime.now()
        })
        return True
    
    def unblock_ip(self, ip_address: str) -> bool:
        """
        Unblock an IP address.
        
        Args:
            ip_address: IP address to unblock
            
        Returns:
            bool: True if IP was unblocked
        """
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            return True
        return False
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window_seconds: int = 60) -> Dict:
        """
        Check if request exceeds rate limit.
        
        Args:
            identifier: Identifier for rate limiting (IP, user, etc.)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Dict with allowed status and current count
        """
        if not self.rate_limiting_enabled:
            return {"allowed": True, "count": 0}
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old entries
        self.rate_limit_data[identifier] = [
            timestamp for timestamp in self.rate_limit_data[identifier]
            if timestamp > window_start
        ]
        
        # Add current request
        self.rate_limit_data[identifier].append(now)
        
        current_count = len(self.rate_limit_data[identifier])
        
        if current_count > limit:
            return {
                "allowed": False,
                "count": current_count,
                "limit": limit,
                "retry_after": window_seconds
            }
        
        return {
            "allowed": True,
            "count": current_count,
            "limit": limit
        }
    
    def detect_intrusion(self, event: Dict) -> Dict:
        """
        Analyze event for potential intrusion.
        
        Args:
            event: Event data to analyze
            
        Returns:
            Dict with detection results
        """
        if not self.ids_enabled:
            return {"threat_detected": False}
        
        threat_score = 0
        threats = []
        
        # Check for suspicious patterns
        if event.get("failed_auth_attempts", 0) > 5:
            threat_score += 30
            threats.append("Multiple failed authentication attempts")
        
        if event.get("port_scan_detected"):
            threat_score += 50
            threats.append("Port scanning detected")
        
        if event.get("unusual_traffic_pattern"):
            threat_score += 40
            threats.append("Unusual traffic pattern")
        
        # Record intrusion attempt
        if threat_score >= 50:
            self.intrusion_attempts.append({
                "event": event,
                "threat_score": threat_score,
                "threats": threats,
                "timestamp": datetime.now()
            })
            
            # Auto-block if severe
            if threat_score >= 70 and "source_ip" in event:
                self.block_ip(event["source_ip"], "Automatic block - intrusion detected")
        
        return {
            "threat_detected": threat_score >= 50,
            "threat_score": threat_score,
            "threats": threats,
            "action_taken": "blocked" if threat_score >= 70 else "logged"
        }
    
    def get_security_status(self) -> Dict:
        """
        Get current network security status.
        
        Returns:
            Dict with security metrics
        """
        return {
            "firewall_enabled": self.firewall_enabled,
            "firewall_rules": len(self.firewall_rules),
            "blocked_ips": len(self.blocked_ips),
            "intrusion_detection_enabled": self.ids_enabled,
            "intrusion_attempts": len(self.intrusion_attempts),
            "rate_limiting_enabled": self.rate_limiting_enabled,
            "allowed_protocols": list(self.allowed_protocols)
        }
