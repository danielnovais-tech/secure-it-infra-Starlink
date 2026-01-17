"""
NetworkMonitor module - Monitors network for unauthorized devices and security issues
"""

import asyncio
import socket
from typing import Dict
from .logging_utils import StructuredLogger
from .metrics import PerformanceTimer


class NetworkMonitor:
    """Monitor network for unauthorized devices and security issues."""
    
    def __init__(self, foundation):
        self.foundation = foundation
        self.devices: Dict[str, Dict] = {}
        self.logger = StructuredLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize network monitor."""
        self.logger.info("Initializing Network Monitor", component="network_monitor")
        # Initialize trusted devices list
        self.devices = {
            "192.168.1.1": {"trusted": True, "name": "Gateway"},
            "192.168.1.10": {"trusted": True, "name": "Server"},
        }
        return True
    
    async def start(self):
        """Start network monitoring."""
        self.logger.info("Starting Network Monitor", component="network_monitor")
        
        while self.foundation.running:
            try:
                await self.scan_network()
                await self.check_ports()
                await asyncio.sleep(self.foundation.config['monitoring']['network_scan_interval'])
            except Exception as e:
                self.logger.error(f"Network monitor error: {e}", component="network_monitor")
                self.foundation.metrics.record_error('network_monitor_error')
                await asyncio.sleep(30)
    
    async def scan_network(self):
        """Scan network for devices with performance tracking."""
        try:
            with PerformanceTimer(self.foundation.metrics, 'network_scan'):
                # Check for unauthorized devices
                unauthorized = [ip for ip, info in self.devices.items() 
                              if not info["trusted"]]
                
                if unauthorized:
                    await self.foundation.trigger_event(
                        "unauthorized_device_detected",
                        "warning",
                        "network_monitor",
                        f"Unauthorized devices detected: {len(unauthorized)}",
                        {"unauthorized_devices": unauthorized}
                    )
                    
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}", component="network_monitor")
            self.foundation.metrics.record_error('network_scan_error')
    
    async def check_ports(self):
        """Check for open ports on critical systems with performance tracking."""
        critical_ports = [22, 23, 80, 443, 3389, 5900]
        
        try:
            with PerformanceTimer(self.foundation.metrics, 'port_check'):
                open_ports = []
                for port in critical_ports:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                
                if open_ports:
                    await self.foundation.trigger_event(
                        "open_ports_detected",
                        "info",
                        "network_monitor",
                        f"Open ports detected: {open_ports}",
                        {"open_ports": open_ports}
                    )
                    
        except Exception as e:
            self.logger.error(f"Port check failed: {e}", component="network_monitor")
            self.foundation.metrics.record_error('port_check_error')
