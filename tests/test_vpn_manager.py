"""
Unit tests for VPN Manager
Tests core functionality of VPN management, monitoring, and auto-reconnection
"""

import unittest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock, call
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_manager.vpn_manager import VPNManager


class TestVPNManager(unittest.TestCase):
    """Test cases for VPN Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary config file
        self.test_config = {
            'vpn': {
                'enabled': True,
                'connection': {
                    'name': 'test-vpn',
                    'type': 'openvpn',
                    'config_file': '/etc/openvpn/test.conf'
                },
                'monitoring': {
                    'check_interval': 5,
                    'auto_reconnect': True,
                    'max_reconnect_attempts': 3,
                    'reconnect_delay': 2,
                    'enable_logging': False
                },
                'health_check': {
                    'enabled': True,
                    'test_hosts': ['8.8.8.8'],
                    'timeout': 5,
                    'failure_threshold': 2
                }
            }
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        )
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_load_config(self):
        """Test configuration loading"""
        manager = VPNManager(self.temp_config.name)
        self.assertEqual(manager.config['vpn']['connection']['name'], 'test-vpn')
        self.assertTrue(manager.config['vpn']['enabled'])
    
    def test_invalid_config_path(self):
        """Test handling of invalid config path"""
        with self.assertRaises(ValueError):
            VPNManager('/nonexistent/config.yaml')
    
    @patch('subprocess.run')
    def test_check_openvpn_status_connected(self, mock_run):
        """Test OpenVPN status check when connected"""
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = VPNManager(self.temp_config.name)
        self.assertTrue(manager._check_openvpn_status())
    
    @patch('subprocess.run')
    def test_check_openvpn_status_disconnected(self, mock_run):
        """Test OpenVPN status check when disconnected"""
        mock_run.return_value = MagicMock(returncode=1)
        
        manager = VPNManager(self.temp_config.name)
        self.assertFalse(manager._check_openvpn_status())
    
    @patch('subprocess.run')
    def test_perform_health_check_success(self, mock_run):
        """Test health check with successful ping"""
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = VPNManager(self.temp_config.name)
        self.assertTrue(manager._perform_health_check())
    
    @patch('subprocess.run')
    def test_perform_health_check_failure(self, mock_run):
        """Test health check with failed ping"""
        mock_run.return_value = MagicMock(returncode=1)
        
        manager = VPNManager(self.temp_config.name)
        self.assertFalse(manager._perform_health_check())
    
    @patch('subprocess.run')
    def test_get_vpn_status_connected_and_healthy(self, mock_run):
        """Test VPN status when connected and healthy"""
        # Mock both pgrep and ping to succeed
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = VPNManager(self.temp_config.name)
        status = manager.get_vpn_status()
        
        self.assertTrue(status['connected'])
        self.assertTrue(status['healthy'])
        self.assertEqual(status['connection_name'], 'test-vpn')
    
    @patch('subprocess.run')
    def test_get_vpn_status_disconnected(self, mock_run):
        """Test VPN status when disconnected"""
        # Mock pgrep to fail (VPN not running)
        mock_run.return_value = MagicMock(returncode=1)
        
        manager = VPNManager(self.temp_config.name)
        status = manager.get_vpn_status()
        
        self.assertFalse(status['connected'])
        self.assertFalse(status['healthy'])
    
    @patch('os.path.exists')
    @patch('subprocess.Popen')
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_connect_openvpn_success(self, mock_sleep, mock_run, mock_popen, mock_exists):
        """Test successful OpenVPN connection"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = VPNManager(self.temp_config.name)
        result = manager.connect_vpn()
        
        self.assertTrue(result)
        mock_popen.assert_called_once()
    
    @patch('os.path.exists')
    def test_connect_openvpn_config_not_found(self, mock_exists):
        """Test OpenVPN connection with missing config file"""
        mock_exists.return_value = False
        
        manager = VPNManager(self.temp_config.name)
        result = manager.connect_vpn()
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_disconnect_openvpn(self, mock_sleep, mock_run):
        """Test OpenVPN disconnection"""
        # First call to pkill succeeds, second call to check status returns not running
        mock_run.side_effect = [
            MagicMock(returncode=0),  # pkill
            MagicMock(returncode=1)   # status check
        ]
        
        manager = VPNManager(self.temp_config.name)
        result = manager.disconnect_vpn()
        
        self.assertTrue(result)
    
    @patch('vpn_manager.vpn_manager.VPNManager.connect_vpn')
    @patch('time.sleep')
    def test_auto_reconnect_success(self, mock_sleep, mock_connect):
        """Test successful auto-reconnection"""
        mock_connect.return_value = True
        
        manager = VPNManager(self.temp_config.name)
        result = manager.auto_reconnect()
        
        self.assertTrue(result)
        mock_connect.assert_called_once()
    
    @patch('vpn_manager.vpn_manager.VPNManager.connect_vpn')
    @patch('time.sleep')
    def test_auto_reconnect_failure(self, mock_sleep, mock_connect):
        """Test auto-reconnection after max attempts"""
        mock_connect.return_value = False
        
        manager = VPNManager(self.temp_config.name)
        result = manager.auto_reconnect()
        
        self.assertFalse(result)
        # Should try max_reconnect_attempts times
        self.assertEqual(mock_connect.call_count, 3)
    
    @patch('vpn_manager.vpn_manager.VPNManager.connect_vpn')
    @patch('time.sleep')
    def test_auto_reconnect_success_on_retry(self, mock_sleep, mock_connect):
        """Test auto-reconnection succeeds on second attempt"""
        # Fail first, succeed second
        mock_connect.side_effect = [False, True]
        
        manager = VPNManager(self.temp_config.name)
        result = manager.auto_reconnect()
        
        self.assertTrue(result)
        self.assertEqual(mock_connect.call_count, 2)
    
    def test_wireguard_config(self):
        """Test VPN manager with WireGuard configuration"""
        config = self.test_config.copy()
        config['vpn']['connection']['type'] = 'wireguard'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name
        
        try:
            manager = VPNManager(temp_path)
            self.assertEqual(manager.config['vpn']['connection']['type'], 'wireguard')
        finally:
            os.unlink(temp_path)
    
    @patch('subprocess.run')
    def test_check_wireguard_status_connected(self, mock_run):
        """Test WireGuard status check when connected"""
        # Modify config for WireGuard
        config = self.test_config.copy()
        config['vpn']['connection']['type'] = 'wireguard'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name
        
        try:
            mock_run.return_value = MagicMock(returncode=0, stdout='interface: wg0')
            
            manager = VPNManager(temp_path)
            self.assertTrue(manager._check_wireguard_status())
        finally:
            os.unlink(temp_path)
    
    def test_stop_monitoring(self):
        """Test stopping the monitoring loop"""
        manager = VPNManager(self.temp_config.name)
        manager.is_running = True
        manager.stop_monitoring()
        self.assertFalse(manager.is_running)


class TestVPNManagerConfiguration(unittest.TestCase):
    """Test VPN Manager configuration handling"""
    
    def test_disabled_vpn(self):
        """Test VPN manager with disabled VPN"""
        config = {
            'vpn': {
                'enabled': False,
                'connection': {
                    'name': 'test-vpn',
                    'type': 'openvpn',
                    'config_file': '/etc/openvpn/test.conf'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name
        
        try:
            manager = VPNManager(temp_path)
            self.assertFalse(manager.config['vpn']['enabled'])
        finally:
            os.unlink(temp_path)
    
    def test_custom_intervals(self):
        """Test custom monitoring intervals"""
        config = {
            'vpn': {
                'enabled': True,
                'connection': {
                    'name': 'test-vpn',
                    'type': 'openvpn',
                    'config_file': '/etc/openvpn/test.conf'
                },
                'monitoring': {
                    'check_interval': 60,
                    'reconnect_delay': 30,
                    'max_reconnect_attempts': 10
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name
        
        try:
            manager = VPNManager(temp_path)
            self.assertEqual(manager.config['vpn']['monitoring']['check_interval'], 60)
            self.assertEqual(manager.config['vpn']['monitoring']['reconnect_delay'], 30)
            self.assertEqual(manager.config['vpn']['monitoring']['max_reconnect_attempts'], 10)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
