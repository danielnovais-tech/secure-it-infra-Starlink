"""
Anomaly Detection Module
Scans for anomalies in network traffic and system behavior
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class AnomalyDetector:
    """Detects anomalies based on configured thresholds"""
    
    def __init__(self, config: dict):
        """
        Initialize anomaly detector with configuration
        
        Args:
            config: Dictionary containing anomaly detection settings
        """
        self.config = config
        self.thresholds = config.get('thresholds', {})
        self.failed_logins = defaultdict(list)
        self.connections = defaultdict(list)
        self.bandwidth_usage = defaultdict(list)
        self.port_scans = defaultdict(list)
        
    def check_failed_login(self, ip_address: str) -> Tuple[bool, str]:
        """
        Check if failed login attempts exceed threshold
        
        Args:
            ip_address: IP address attempting login
            
        Returns:
            Tuple of (is_anomaly, description)
        """
        threshold = self.thresholds.get('failed_login_threshold', 5)
        window_minutes = self.thresholds.get('failed_login_window_minutes', 10)
        
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=window_minutes)
        
        # Add current attempt
        self.failed_logins[ip_address].append(now)
        
        # Remove old attempts
        self.failed_logins[ip_address] = [
            t for t in self.failed_logins[ip_address] if t > cutoff_time
        ]
        
        count = len(self.failed_logins[ip_address])
        
        if count >= threshold:
            return True, f"Failed login anomaly: {count} attempts from {ip_address} in {window_minutes} minutes"
        
        return False, ""
    
    def check_connection_rate(self, ip_address: str) -> Tuple[bool, str]:
        """
        Check if connection rate exceeds threshold
        
        Args:
            ip_address: IP address making connections
            
        Returns:
            Tuple of (is_anomaly, description)
        """
        threshold = self.thresholds.get('connection_rate_threshold', 100)
        window_seconds = self.thresholds.get('connection_rate_window_seconds', 60)
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_seconds)
        
        # Add current connection
        self.connections[ip_address].append(now)
        
        # Remove old connections
        self.connections[ip_address] = [
            t for t in self.connections[ip_address] if t > cutoff_time
        ]
        
        count = len(self.connections[ip_address])
        
        if count >= threshold:
            return True, f"Connection rate anomaly: {count} connections from {ip_address} in {window_seconds} seconds"
        
        return False, ""
    
    def check_bandwidth_usage(self, ip_address: str, bytes_transferred: int) -> Tuple[bool, str]:
        """
        Check if bandwidth usage exceeds threshold
        
        Args:
            ip_address: IP address using bandwidth
            bytes_transferred: Number of bytes transferred
            
        Returns:
            Tuple of (is_anomaly, description)
        """
        threshold_mb = self.thresholds.get('bandwidth_threshold_mb', 1000)
        window_minutes = self.thresholds.get('bandwidth_window_minutes', 5)
        
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=window_minutes)
        
        # Add current usage
        self.bandwidth_usage[ip_address].append((now, bytes_transferred))
        
        # Remove old usage records
        self.bandwidth_usage[ip_address] = [
            (t, b) for t, b in self.bandwidth_usage[ip_address] if t > cutoff_time
        ]
        
        total_bytes = sum(b for _, b in self.bandwidth_usage[ip_address])
        total_mb = total_bytes / (1024 * 1024)
        
        if total_mb >= threshold_mb:
            return True, f"Bandwidth anomaly: {total_mb:.2f}MB transferred from {ip_address} in {window_minutes} minutes"
        
        return False, ""
    
    def check_port_scan(self, ip_address: str, port: int) -> Tuple[bool, str]:
        """
        Check if port scanning is detected
        
        Args:
            ip_address: IP address scanning ports
            port: Port being accessed
            
        Returns:
            Tuple of (is_anomaly, description)
        """
        threshold = self.thresholds.get('port_scan_threshold', 10)
        window_seconds = self.thresholds.get('port_scan_window_seconds', 30)
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_seconds)
        
        # Add current port access
        self.port_scans[ip_address].append((now, port))
        
        # Remove old port accesses
        self.port_scans[ip_address] = [
            (t, p) for t, p in self.port_scans[ip_address] if t > cutoff_time
        ]
        
        # Count unique ports accessed
        unique_ports = len(set(p for _, p in self.port_scans[ip_address]))
        
        if unique_ports >= threshold:
            return True, f"Port scan anomaly: {unique_ports} unique ports accessed from {ip_address} in {window_seconds} seconds"
        
        return False, ""
    
    def analyze(self, event: Dict) -> List[Dict]:
        """
        Analyze an event for anomalies
        
        Args:
            event: Dictionary containing event data
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        ip_address = event.get('ip_address', '')
        event_type = event.get('type', '')
        
        if event_type == 'failed_login':
            is_anomaly, description = self.check_failed_login(ip_address)
            if is_anomaly:
                anomalies.append({
                    'type': 'failed_login_anomaly',
                    'ip_address': ip_address,
                    'description': description,
                    'timestamp': datetime.now().isoformat()
                })
        
        elif event_type == 'connection':
            is_anomaly, description = self.check_connection_rate(ip_address)
            if is_anomaly:
                anomalies.append({
                    'type': 'connection_rate_anomaly',
                    'ip_address': ip_address,
                    'description': description,
                    'timestamp': datetime.now().isoformat()
                })
        
        elif event_type == 'bandwidth':
            bytes_transferred = event.get('bytes', 0)
            is_anomaly, description = self.check_bandwidth_usage(ip_address, bytes_transferred)
            if is_anomaly:
                anomalies.append({
                    'type': 'bandwidth_anomaly',
                    'ip_address': ip_address,
                    'description': description,
                    'timestamp': datetime.now().isoformat()
                })
        
        elif event_type == 'port_access':
            port = event.get('port', 0)
            is_anomaly, description = self.check_port_scan(ip_address, port)
            if is_anomaly:
                anomalies.append({
                    'type': 'port_scan_anomaly',
                    'ip_address': ip_address,
                    'description': description,
                    'timestamp': datetime.now().isoformat()
                })
        
        return anomalies
