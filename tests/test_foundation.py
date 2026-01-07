"""Tests for Starlink Security Foundation."""

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from starlink_security import StarlinkSecurityFoundation


class TestStarlinkSecurityFoundation:
    """Test cases for StarlinkSecurityFoundation."""
    
    def test_initialization(self):
        """Test that the foundation initializes correctly."""
        foundation = StarlinkSecurityFoundation()
        assert foundation is not None
        assert foundation.config is not None
        assert foundation.security_modules is not None
        assert not foundation.running
    
    def test_default_config_loaded(self):
        """Test that default configuration is loaded."""
        foundation = StarlinkSecurityFoundation()
        
        # Check security config
        assert 'security' in foundation.config
        assert foundation.config['security']['encryption_enabled'] is True
        assert foundation.config['security']['vpn_required'] is True
        assert foundation.config['security']['minimum_tls_version'] == "TLSv1.3"
        
        # Check monitoring config
        assert 'monitoring' in foundation.config
        assert foundation.config['monitoring']['network_scan_interval'] == 300
        assert foundation.config['monitoring']['threat_check_interval'] == 60
        
        # Check starlink config
        assert 'starlink' in foundation.config
        assert foundation.config['starlink']['gateway_ip'] == "192.168.100.1"
        
        # Check enterprise config
        assert 'enterprise' in foundation.config
        assert 'vpn' in foundation.config['enterprise']['critical_services']
    
    def test_modules_initialized(self):
        """Test that security modules are initialized."""
        foundation = StarlinkSecurityFoundation()
        
        expected_modules = [
            'network_monitor',
            'threat_detector',
            'policy_enforcer',
            'incident_responder',
            'vpn_manager',
            'backup_manager'
        ]
        
        for module_name in expected_modules:
            assert module_name in foundation.security_modules
    
    def test_encryption_initialization(self):
        """Test that encryption is initialized."""
        foundation = StarlinkSecurityFoundation()
        assert foundation.encryption is not None
    
    def test_deep_update(self):
        """Test deep dictionary update."""
        foundation = StarlinkSecurityFoundation()
        
        target = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            }
        }
        
        source = {
            'b': {
                'c': 20,
                'e': 4
            },
            'f': 5
        }
        
        foundation._deep_update(target, source)
        
        assert target['a'] == 1
        assert target['b']['c'] == 20
        assert target['b']['d'] == 3
        assert target['b']['e'] == 4
        assert target['f'] == 5
    
    def test_custom_config_loading(self):
        """Test loading a custom configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
security:
  encryption_enabled: false
  vpn_required: false
monitoring:
  network_scan_interval: 600
""")
            config_path = f.name
        
        try:
            foundation = StarlinkSecurityFoundation(config_path=config_path)
            
            # Check that custom values override defaults
            assert foundation.config['security']['encryption_enabled'] is False
            assert foundation.config['security']['vpn_required'] is False
            assert foundation.config['monitoring']['network_scan_interval'] == 600
            
            # Check that unspecified defaults are preserved
            assert foundation.config['security']['minimum_tls_version'] == "TLSv1.3"
            assert foundation.config['monitoring']['threat_check_interval'] == 60
        finally:
            Path(config_path).unlink()
    
    @pytest.mark.asyncio
    async def test_shutdown(self):
        """Test graceful shutdown."""
        foundation = StarlinkSecurityFoundation()
        foundation.running = True
        
        await foundation.shutdown()
        
        assert foundation.running is False
    
    def test_cleanup(self):
        """Test cleanup method."""
        foundation = StarlinkSecurityFoundation()
        foundation.cleanup()
        # Should not raise any exceptions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
