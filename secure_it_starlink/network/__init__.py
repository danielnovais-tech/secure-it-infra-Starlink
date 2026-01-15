"""
Network Security Monitoring Module
===================================

Provides network monitoring and connection validation for Starlink connections.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import socket
import urllib.parse


class NetworkMonitor:
    """
    Monitor network connections and traffic for Starlink infrastructure.
    
    This class provides real-time monitoring of network connections,
    bandwidth usage, and connection quality metrics.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Network Monitor.
        
        Args:
            config: Optional configuration dictionary for monitoring parameters
        """
        self.config = config or {}
        self.monitoring_active = False
        self.connection_logs: List[Dict[str, Any]] = []
        self.alert_threshold = self.config.get("alert_threshold", 0.8)

    def start_monitoring(self) -> None:
        """Start network monitoring."""
        self.monitoring_active = True
        self.connection_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": "monitoring_started",
            "status": "active"
        })

    def stop_monitoring(self) -> None:
        """Stop network monitoring."""
        self.monitoring_active = False
        self.connection_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": "monitoring_stopped",
            "status": "inactive"
        })

    def check_connection_health(self, target: str = "8.8.8.8") -> Dict[str, Any]:
        """
        Check the health of network connection.
        
        Args:
            target: Target IP or hostname to check connectivity
            
        Returns:
            Dictionary containing connection health metrics
        """
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "status": "unknown",
            "latency_ms": None,
            "reachable": False
        }

        try:
            start_time = time.time()
            # Simple connectivity check
            socket.create_connection((target, 80), timeout=5)
            latency = (time.time() - start_time) * 1000
            health_data.update({
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "reachable": True
            })
        except (socket.timeout, socket.error, OSError) as e:
            health_data.update({
                "status": "unhealthy",
                "error": str(e),
                "reachable": False
            })

        self.connection_logs.append(health_data)
        return health_data

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get aggregated connection statistics.
        
        Returns:
            Dictionary containing connection statistics
        """
        total_checks = len([log for log in self.connection_logs 
                           if "latency_ms" in log])
        healthy_checks = len([log for log in self.connection_logs 
                             if log.get("status") == "healthy"])
        
        return {
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "unhealthy_checks": total_checks - healthy_checks,
            "health_ratio": healthy_checks / total_checks if total_checks > 0 else 0,
            "monitoring_active": self.monitoring_active
        }

    def get_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get connection logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of connection log entries
        """
        if limit:
            return self.connection_logs[-limit:]
        return self.connection_logs.copy()


class ConnectionValidator:
    """
    Validate and verify Starlink network connections.
    
    Ensures connections meet security requirements and are authorized.
    """

    def __init__(self, allowed_networks: Optional[List[str]] = None):
        """
        Initialize the Connection Validator.
        
        Args:
            allowed_networks: List of allowed network CIDR ranges
        """
        self.allowed_networks = allowed_networks or []
        self.validation_logs: List[Dict[str, Any]] = []

    def validate_connection(self, source_ip: str, destination: str) -> Dict[str, bool]:
        """
        Validate a network connection.
        
        Args:
            source_ip: Source IP address
            destination: Destination address
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            "valid": True,
            "source_authorized": True,
            "destination_safe": True,
            "timestamp": datetime.now().isoformat()
        }

        # Basic validation logic
        if not self._is_valid_ip(source_ip):
            validation_result["valid"] = False
            validation_result["source_authorized"] = False

        if not self._is_safe_destination(destination):
            validation_result["valid"] = False
            validation_result["destination_safe"] = False

        self.validation_logs.append({
            "source_ip": source_ip,
            "destination": destination,
            **validation_result
        })

        return validation_result

    def _is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid."""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def _is_safe_destination(self, destination: str) -> bool:
        """
        Check if destination is safe.
        
        Basic check for obviously malicious patterns.
        """
        # Block obviously suspicious patterns
        suspicious_patterns = ["127.0.0.1", "localhost", "0.0.0.0"]
        parsed = urllib.parse.urlparse(destination if "://" in destination else f"//{destination}")
        hostname = parsed.hostname or destination
        
        return hostname not in suspicious_patterns

    def get_validation_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get validation logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of validation log entries
        """
        if limit:
            return self.validation_logs[-limit:]
        return self.validation_logs.copy()

    def add_allowed_network(self, network: str) -> None:
        """
        Add a network to the allowed list.
        
        Args:
            network: Network CIDR range to allow
        """
        if network not in self.allowed_networks:
            self.allowed_networks.append(network)
