"""Tests for the vulnerability scanning module."""

import pytest
from secure_it_starlink.scanning import VulnerabilityScanner, PortScanner


class TestVulnerabilityScanner:
    """Test the VulnerabilityScanner class."""

    def test_initialization(self):
        """Test scanner initialization."""
        scanner = VulnerabilityScanner()
        assert len(scanner.scan_results) == 0
        assert len(scanner.known_vulnerabilities) > 0

    def test_scan_configuration_with_vulnerabilities(self):
        """Test scanning configuration with vulnerabilities."""
        scanner = VulnerabilityScanner()
        config = {
            "encryption_enabled": False,
            "cipher_suite": "DES",
            "username": "admin",
            "password": "admin"
        }
        
        result = scanner.scan_configuration(config)
        
        assert result["scan_type"] == "configuration"
        assert result["vulnerabilities_found"] > 0
        assert result["status"] == "completed"
        assert "scan_id" in result
        assert len(result["vulnerabilities"]) > 0

    def test_scan_configuration_secure(self):
        """Test scanning secure configuration."""
        scanner = VulnerabilityScanner()
        config = {
            "encryption_enabled": True,
            "cipher_suite": "AES-256-GCM",
            "username": "custom_user",
            "password": "SecureP@ssw0rd123"
        }
        
        result = scanner.scan_configuration(config)
        
        assert result["vulnerabilities_found"] == 0
        assert len(result["vulnerabilities"]) == 0

    def test_get_scan_results(self):
        """Test getting scan results."""
        scanner = VulnerabilityScanner()
        scanner.scan_configuration({"encryption_enabled": False})
        scanner.scan_configuration({"cipher_suite": "DES"})
        
        results = scanner.get_scan_results()
        assert len(results) == 2
        
        # Test with limit
        limited_results = scanner.get_scan_results(limit=1)
        assert len(limited_results) == 1

    def test_get_vulnerability_summary(self):
        """Test getting vulnerability summary."""
        scanner = VulnerabilityScanner()
        scanner.scan_configuration({
            "encryption_enabled": False,
            "cipher_suite": "DES"
        })
        
        summary = scanner.get_vulnerability_summary()
        
        assert "total_scans" in summary
        assert "total_vulnerabilities" in summary
        assert "by_severity" in summary
        assert summary["total_scans"] >= 1


class TestPortScanner:
    """Test the PortScanner class."""

    def test_initialization(self):
        """Test port scanner initialization."""
        scanner = PortScanner()
        assert len(scanner.scan_history) == 0
        assert len(scanner.common_ports) > 0

    def test_scan_port(self):
        """Test scanning a single port."""
        scanner = PortScanner()
        
        # Test with localhost (should work)
        result = scanner.scan_port("127.0.0.1", 80, timeout=0.5)
        
        assert result["host"] == "127.0.0.1"
        assert result["port"] == 80
        assert "status" in result
        assert result["status"] in ["open", "closed", "error"]
        assert "timestamp" in result

    def test_scan_ports(self):
        """Test scanning multiple ports."""
        scanner = PortScanner()
        
        # Scan common ports on localhost
        result = scanner.scan_ports("127.0.0.1", ports=[22, 80, 443], timeout=0.5)
        
        assert result["host"] == "127.0.0.1"
        assert result["ports_scanned"] == 3
        assert "open_ports" in result
        assert "scan_id" in result
        assert len(result["scan_results"]) == 3

    def test_scan_ports_default(self):
        """Test scanning with default common ports."""
        scanner = PortScanner()
        
        result = scanner.scan_ports("127.0.0.1", timeout=0.5)
        
        assert result["ports_scanned"] == len(scanner.common_ports)

    def test_get_scan_history(self):
        """Test getting scan history."""
        scanner = PortScanner()
        scanner.scan_ports("127.0.0.1", ports=[80], timeout=0.5)
        scanner.scan_ports("127.0.0.1", ports=[443], timeout=0.5)
        
        history = scanner.get_scan_history()
        assert len(history) == 2
        
        # Test with limit
        limited_history = scanner.get_scan_history(limit=1)
        assert len(limited_history) == 1

    def test_get_open_ports_summary(self):
        """Test getting open ports summary."""
        scanner = PortScanner()
        scanner.scan_ports("127.0.0.1", ports=[80, 443], timeout=0.5)
        
        summary = scanner.get_open_ports_summary()
        
        assert isinstance(summary, dict)
        # Summary should have entries for scanned hosts
        if "127.0.0.1" in summary:
            assert isinstance(summary["127.0.0.1"], list)
