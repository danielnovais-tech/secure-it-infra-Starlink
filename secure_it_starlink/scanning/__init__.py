"""
Vulnerability Scanning Module
==============================

Provides vulnerability scanning and security assessment capabilities
for Starlink-connected infrastructures.
"""

import socket
from datetime import datetime
from typing import Dict, List, Optional, Any, Set


class VulnerabilityScanner:
    """
    Scan for common security vulnerabilities.
    
    Identifies potential security issues in configurations, services,
    and infrastructure components.
    """

    def __init__(self):
        """Initialize the Vulnerability Scanner."""
        self.scan_results: List[Dict[str, Any]] = []
        self.known_vulnerabilities = {
            "weak_cipher": {
                "severity": "HIGH",
                "description": "Weak encryption cipher detected",
                "recommendation": "Use AES-256 or stronger encryption"
            },
            "open_port": {
                "severity": "MEDIUM",
                "description": "Unnecessary open port detected",
                "recommendation": "Close unused ports or restrict access"
            },
            "outdated_protocol": {
                "severity": "HIGH",
                "description": "Outdated protocol version in use",
                "recommendation": "Update to latest secure protocol version"
            },
            "default_credentials": {
                "severity": "CRITICAL",
                "description": "Default credentials detected",
                "recommendation": "Change default passwords immediately"
            },
            "missing_encryption": {
                "severity": "CRITICAL",
                "description": "Unencrypted data transmission detected",
                "recommendation": "Enable encryption for all data in transit"
            }
        }

    def scan_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan a configuration for vulnerabilities.
        
        Args:
            config: Configuration dictionary to scan
            
        Returns:
            Scan results with identified vulnerabilities
        """
        vulnerabilities = []
        timestamp = datetime.now().isoformat()

        # Check for encryption settings
        if not config.get("encryption_enabled", False):
            vulnerabilities.append({
                **self.known_vulnerabilities["missing_encryption"],
                "location": "encryption_enabled",
                "detected_value": config.get("encryption_enabled")
            })

        # Check for weak ciphers
        cipher = config.get("cipher_suite", "")
        if cipher and ("DES" in cipher or "RC4" in cipher or "MD5" in cipher):
            vulnerabilities.append({
                **self.known_vulnerabilities["weak_cipher"],
                "location": "cipher_suite",
                "detected_value": cipher
            })

        # Check for default credentials
        if config.get("username") == "admin" and config.get("password") == "admin":
            vulnerabilities.append({
                **self.known_vulnerabilities["default_credentials"],
                "location": "credentials"
            })

        scan_result = {
            "scan_id": f"SCAN-{len(self.scan_results) + 1:06d}",
            "timestamp": timestamp,
            "scan_type": "configuration",
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "status": "completed"
        }

        self.scan_results.append(scan_result)
        return scan_result

    def get_scan_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get scan results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of scan results
        """
        if limit:
            return self.scan_results[-limit:]
        return self.scan_results.copy()

    def get_vulnerability_summary(self) -> Dict[str, Any]:
        """
        Get summary of all vulnerabilities found.
        
        Returns:
            Summary statistics of vulnerabilities
        """
        all_vulnerabilities = []
        for result in self.scan_results:
            all_vulnerabilities.extend(result["vulnerabilities"])

        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in all_vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN")
            if severity in severity_counts:
                severity_counts[severity] += 1

        return {
            "total_scans": len(self.scan_results),
            "total_vulnerabilities": len(all_vulnerabilities),
            "by_severity": severity_counts
        }


class PortScanner:
    """
    Scan network ports for security assessment.
    
    Identifies open ports and potentially vulnerable services.
    """

    def __init__(self):
        """Initialize the Port Scanner."""
        self.scan_history: List[Dict[str, Any]] = []
        self.common_ports = {
            20: "FTP Data",
            21: "FTP Control",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP Proxy"
        }

    def scan_port(self, host: str, port: int, timeout: float = 1.0) -> Dict[str, Any]:
        """
        Scan a single port.
        
        Args:
            host: Target host
            port: Port number to scan
            timeout: Connection timeout in seconds
            
        Returns:
            Port scan result
        """
        result = {
            "host": host,
            "port": port,
            "service": self.common_ports.get(port, "Unknown"),
            "status": "closed",
            "timestamp": datetime.now().isoformat()
        }

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            connection_result = sock.connect_ex((host, port))
            sock.close()

            if connection_result == 0:
                result["status"] = "open"
        except socket.gaierror:
            result["status"] = "error"
            result["error"] = "Host resolution failed"
        except socket.error as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def scan_ports(
        self,
        host: str,
        ports: Optional[List[int]] = None,
        timeout: float = 1.0
    ) -> Dict[str, Any]:
        """
        Scan multiple ports on a host.
        
        Args:
            host: Target host
            ports: List of ports to scan. If None, scans common ports.
            timeout: Connection timeout in seconds
            
        Returns:
            Comprehensive scan results
        """
        if ports is None:
            ports = list(self.common_ports.keys())

        scan_results = []
        open_ports = []

        for port in ports:
            result = self.scan_port(host, port, timeout)
            scan_results.append(result)
            if result["status"] == "open":
                open_ports.append(port)

        scan_record = {
            "scan_id": f"PORTSCAN-{len(self.scan_history) + 1:06d}",
            "timestamp": datetime.now().isoformat(),
            "host": host,
            "ports_scanned": len(ports),
            "open_ports": open_ports,
            "scan_results": scan_results
        }

        self.scan_history.append(scan_record)
        return scan_record

    def get_scan_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get port scan history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of scan records
        """
        if limit:
            return self.scan_history[-limit:]
        return self.scan_history.copy()

    def get_open_ports_summary(self) -> Dict[str, Set[int]]:
        """
        Get summary of all open ports by host.
        
        Returns:
            Dictionary mapping hosts to sets of open ports
        """
        summary: Dict[str, Set[int]] = {}
        
        for scan in self.scan_history:
            host = scan["host"]
            if host not in summary:
                summary[host] = set()
            summary[host].update(scan["open_ports"])

        return {host: sorted(list(ports)) for host, ports in summary.items()}
