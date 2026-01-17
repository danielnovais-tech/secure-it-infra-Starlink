"""
Unit tests for SESF Network Security Module
"""

import unittest
from sesf.modules.network_security import NetworkSecurityModule


class TestNetworkSecurityModule(unittest.TestCase):
    """Test cases for NetworkSecurityModule."""
    
    def setUp(self):
        """Set up test network security module."""
        self.network = NetworkSecurityModule({
            "firewall_enabled": True,
            "intrusion_detection": True,
            "rate_limiting": True,
            "allowed_protocols": ["HTTPS", "SSH"]
        })
    
    def test_add_firewall_rule(self):
        """Test adding firewall rules."""
        rule = {
            "action": "allow",
            "protocol": "HTTPS",
            "port": 443
        }
        result = self.network.add_firewall_rule(rule)
        self.assertTrue(result)
        self.assertEqual(len(self.network.firewall_rules), 1)
    
    def test_firewall_allow(self):
        """Test firewall allowing traffic."""
        # Add allow rule
        self.network.add_firewall_rule({
            "action": "allow",
            "protocol": "HTTPS",
            "port": 443
        })
        
        result = self.network.check_firewall("10.0.0.1", "192.168.1.1", "HTTPS", 443)
        self.assertTrue(result["allowed"])
    
    def test_firewall_deny(self):
        """Test firewall denying traffic."""
        # Add deny rule
        self.network.add_firewall_rule({
            "action": "deny",
            "protocol": "HTTP",
            "port": 80
        })
        
        result = self.network.check_firewall("10.0.0.1", "192.168.1.1", "HTTP", 80)
        self.assertFalse(result["allowed"])
    
    def test_ip_blocking(self):
        """Test IP address blocking."""
        ip = "192.168.1.100"
        self.network.block_ip(ip, "Test block")
        
        self.assertIn(ip, self.network.blocked_ips)
        
        # Traffic from blocked IP should be denied
        result = self.network.check_firewall(ip, "10.0.0.1", "HTTPS", 443)
        self.assertFalse(result["allowed"])
    
    def test_ip_unblocking(self):
        """Test IP address unblocking."""
        ip = "192.168.1.100"
        self.network.block_ip(ip)
        self.network.unblock_ip(ip)
        
        self.assertNotIn(ip, self.network.blocked_ips)
    
    def test_rate_limiting(self):
        """Test rate limiting."""
        identifier = "test_user"
        
        # Should allow within limit
        result = self.network.check_rate_limit(identifier, limit=5, window_seconds=60)
        self.assertTrue(result["allowed"])
        
        # Exceed limit
        for i in range(10):
            result = self.network.check_rate_limit(identifier, limit=5, window_seconds=60)
        
        self.assertFalse(result["allowed"])
    
    def test_intrusion_detection(self):
        """Test intrusion detection."""
        # Suspicious event
        event = {
            "source_ip": "203.0.113.42",
            "failed_auth_attempts": 10,
            "port_scan_detected": True
        }
        
        result = self.network.detect_intrusion(event)
        self.assertTrue(result["threat_detected"])
        self.assertGreater(result["threat_score"], 50)
    
    def test_get_security_status(self):
        """Test getting security status."""
        status = self.network.get_security_status()
        
        self.assertIn("firewall_enabled", status)
        self.assertIn("intrusion_detection_enabled", status)
        self.assertIn("rate_limiting_enabled", status)


if __name__ == "__main__":
    unittest.main()
