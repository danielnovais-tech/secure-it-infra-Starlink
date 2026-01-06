"""
VPN Manager Module
Manages VPN connectivity with YAML-based configuration, status monitoring, 
and auto-connection capabilities for Starlink infrastructure security.
"""

import os
import time
import logging
import subprocess
import yaml
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path


class VPNManager:
    """
    VPN Manager for ensuring VPN connectivity with monitoring and auto-reconnection.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize VPN Manager with configuration file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.connection_attempts = 0
        self.consecutive_failures = 0
        self.is_running = False
        
    def _load_config(self) -> Dict:
        """Load VPN configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            raise ValueError(f"Failed to load config from {self.config_path}: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging based on configuration."""
        logger = logging.getLogger('VPNManager')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if logging is enabled
        if self.config.get('vpn', {}).get('monitoring', {}).get('enable_logging', False):
            log_file = self.config['vpn']['monitoring'].get('log_file', '/var/log/vpn_manager.log')
            try:
                # Create log directory if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not setup file logging: {e}")
        
        return logger
    
    def get_vpn_status(self) -> Dict[str, any]:
        """
        Get current VPN connection status.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'connected': False,
            'timestamp': datetime.now().isoformat(),
            'connection_name': self.config['vpn']['connection']['name'],
            'healthy': False
        }
        
        vpn_type = self.config['vpn']['connection']['type']
        
        try:
            if vpn_type == 'openvpn':
                status['connected'] = self._check_openvpn_status()
            elif vpn_type == 'wireguard':
                status['connected'] = self._check_wireguard_status()
            else:
                self.logger.error(f"Unsupported VPN type: {vpn_type}")
                return status
            
            # Perform health check if connected
            if status['connected'] and self.config['vpn'].get('health_check', {}).get('enabled', False):
                status['healthy'] = self._perform_health_check()
            else:
                status['healthy'] = status['connected']
            
        except Exception as e:
            self.logger.error(f"Error checking VPN status: {e}")
        
        return status
    
    def _check_openvpn_status(self) -> bool:
        """Check if OpenVPN is connected."""
        try:
            # Check if OpenVPN process is running
            result = subprocess.run(
                ['pgrep', '-f', 'openvpn'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"Error checking OpenVPN status: {e}")
            return False
    
    def _check_wireguard_status(self) -> bool:
        """Check if WireGuard is connected."""
        try:
            # Check WireGuard interface status
            result = subprocess.run(
                ['wg', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and len(result.stdout) > 0
        except Exception as e:
            self.logger.debug(f"Error checking WireGuard status: {e}")
            return False
    
    def _perform_health_check(self) -> bool:
        """
        Perform health check by pinging test hosts.
        
        Returns:
            True if VPN connection is healthy, False otherwise
        """
        test_hosts = self.config['vpn']['health_check'].get('test_hosts', ['8.8.8.8'])
        timeout = self.config['vpn']['health_check'].get('timeout', 5)
        
        for host in test_hosts:
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout), host],
                    capture_output=True,
                    timeout=timeout + 1
                )
                if result.returncode == 0:
                    return True
            except Exception as e:
                self.logger.debug(f"Ping to {host} failed: {e}")
                continue
        
        return False
    
    def connect_vpn(self) -> bool:
        """
        Attempt to connect to VPN.
        
        Returns:
            True if connection successful, False otherwise
        """
        vpn_type = self.config['vpn']['connection']['type']
        config_file = self.config['vpn']['connection']['config_file']
        
        self.logger.info(f"Attempting to connect to VPN ({vpn_type})...")
        
        try:
            if vpn_type == 'openvpn':
                return self._connect_openvpn(config_file)
            elif vpn_type == 'wireguard':
                return self._connect_wireguard(config_file)
            else:
                self.logger.error(f"Unsupported VPN type: {vpn_type}")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to VPN: {e}")
            return False
    
    def _connect_openvpn(self, config_file: str) -> bool:
        """Connect to OpenVPN."""
        try:
            # Check if config file exists
            if not os.path.exists(config_file):
                self.logger.error(f"OpenVPN config file not found: {config_file}")
                return False
            
            # Start OpenVPN in background
            subprocess.Popen(
                ['openvpn', '--config', config_file, '--daemon'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit for connection to establish
            time.sleep(3)
            
            # Check if connection was successful
            return self._check_openvpn_status()
        except Exception as e:
            self.logger.error(f"Failed to connect OpenVPN: {e}")
            return False
    
    def _connect_wireguard(self, config_file: str) -> bool:
        """Connect to WireGuard."""
        try:
            # Extract interface name from config file
            interface_name = os.path.splitext(os.path.basename(config_file))[0]
            
            result = subprocess.run(
                ['wg-quick', 'up', interface_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to connect WireGuard: {e}")
            return False
    
    def disconnect_vpn(self) -> bool:
        """
        Disconnect from VPN.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        vpn_type = self.config['vpn']['connection']['type']
        
        self.logger.info(f"Disconnecting from VPN ({vpn_type})...")
        
        try:
            if vpn_type == 'openvpn':
                return self._disconnect_openvpn()
            elif vpn_type == 'wireguard':
                return self._disconnect_wireguard()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error disconnecting from VPN: {e}")
            return False
    
    def _disconnect_openvpn(self) -> bool:
        """Disconnect OpenVPN."""
        try:
            subprocess.run(['pkill', '-f', 'openvpn'], timeout=5)
            time.sleep(1)
            return not self._check_openvpn_status()
        except Exception as e:
            self.logger.error(f"Failed to disconnect OpenVPN: {e}")
            return False
    
    def _disconnect_wireguard(self) -> bool:
        """Disconnect WireGuard."""
        try:
            config_file = self.config['vpn']['connection']['config_file']
            interface_name = os.path.splitext(os.path.basename(config_file))[0]
            
            result = subprocess.run(
                ['wg-quick', 'down', interface_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to disconnect WireGuard: {e}")
            return False
    
    def auto_reconnect(self) -> bool:
        """
        Attempt to reconnect to VPN with configured retry logic.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        max_attempts = self.config['vpn']['monitoring'].get('max_reconnect_attempts', 5)
        delay = self.config['vpn']['monitoring'].get('reconnect_delay', 10)
        
        for attempt in range(1, max_attempts + 1):
            self.logger.info(f"Reconnection attempt {attempt}/{max_attempts}")
            
            if self.connect_vpn():
                self.logger.info("VPN reconnected successfully")
                self.connection_attempts = 0
                self.consecutive_failures = 0
                return True
            
            if attempt < max_attempts:
                self.logger.warning(f"Reconnection failed, waiting {delay}s before retry...")
                time.sleep(delay)
        
        self.logger.error(f"Failed to reconnect after {max_attempts} attempts")
        return False
    
    def monitor(self) -> None:
        """
        Start monitoring VPN connection with auto-reconnection.
        This is a blocking call that runs until stopped.
        """
        if not self.config['vpn'].get('enabled', False):
            self.logger.warning("VPN management is disabled in configuration")
            return
        
        check_interval = self.config['vpn']['monitoring'].get('check_interval', 30)
        auto_reconnect_enabled = self.config['vpn']['monitoring'].get('auto_reconnect', True)
        failure_threshold = self.config['vpn'].get('health_check', {}).get('failure_threshold', 3)
        
        self.is_running = True
        self.logger.info("Starting VPN monitoring...")
        
        try:
            while self.is_running:
                status = self.get_vpn_status()
                
                if status['connected'] and status['healthy']:
                    self.logger.info(f"VPN status: Connected and healthy")
                    self.consecutive_failures = 0
                elif status['connected'] and not status['healthy']:
                    self.consecutive_failures += 1
                    self.logger.warning(
                        f"VPN connected but unhealthy "
                        f"({self.consecutive_failures}/{failure_threshold})"
                    )
                    
                    if self.consecutive_failures >= failure_threshold:
                        self.logger.error("VPN health check failed threshold reached")
                        if auto_reconnect_enabled:
                            self.disconnect_vpn()
                            self.auto_reconnect()
                else:
                    self.logger.warning("VPN is disconnected")
                    if auto_reconnect_enabled:
                        self.auto_reconnect()
                    else:
                        self.logger.info("Auto-reconnect is disabled")
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error during monitoring: {e}")
        finally:
            self.is_running = False
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring loop."""
        self.is_running = False
        self.logger.info("Stopping VPN monitoring...")
