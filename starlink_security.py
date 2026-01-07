#!/usr/bin/env python3
"""
Starlink Enterprise Security Foundation

A comprehensive security management system for Starlink enterprise connections
with automatic failover, monitoring, and threat detection capabilities.
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
# Use local logs directory if /var/log is not writable
try:
    LOG_DIR = Path("/var/log/starlink_security")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    LOG_DIR = Path.home() / ".starlink_security" / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'starlink_security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Types of network connections."""
    STARLINK_ONLY = "starlink_only"
    FAILOVER = "failover"
    DUAL_WAN = "dual_wan"
    LOAD_BALANCED = "load_balanced"


class SecurityLevel(Enum):
    """Security threat levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityMetrics:
    """Security and connection metrics."""
    security_score: float = 100.0
    connection_stability: float = 100.0
    packet_loss: float = 0.0
    latency: float = 0.0
    bandwidth_usage: float = 0.0
    threat_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ThreatInfo:
    """Information about a detected threat."""
    threat_id: str
    severity: str
    source: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)


class BackupConnectionManager:
    """Manages backup connections and failover logic."""
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation'):
        """Initialize backup connection manager.
        
        Args:
            foundation: Reference to the main StarlinkSecurityFoundation instance
        """
        self.foundation = foundation
        self.backup_connections: Dict[str, Dict[str, Any]] = {
            "lte_backup": {
                "available": True,
                "priority": 1,
                "type": "LTE"
            },
            "cable_backup": {
                "available": True,
                "priority": 2,
                "type": "Cable"
            },
            "satellite_backup": {
                "available": False,
                "priority": 3,
                "type": "Satellite"
            }
        }
        self.active_backup: Optional[str] = None
        
    async def monitor_connection(self):
        """Monitor primary connection and trigger failover if needed."""
        logger.info("Monitoring connection status")
        
        metrics = self.foundation.metrics
        
        # Check if primary connection is degraded
        if (metrics.packet_loss > 10 or 
            metrics.latency > 200 or
            metrics.connection_stability < 50):
            
            if self.foundation.connection_type == ConnectionType.STARLINK_ONLY:
                await self.activate_failover()
    
    async def activate_failover(self):
        """Activate backup connection."""
        logger.info("Activating failover to backup connection")
        
        # Find best available backup
        best_backup = None
        best_priority = float('inf')
        
        for name, info in self.backup_connections.items():
            if info["available"] and info["priority"] < best_priority:
                best_backup = name
                best_priority = info["priority"]
        
        if best_backup:
            self.active_backup = best_backup
            self.foundation.connection_type = ConnectionType.FAILOVER
            
            await self.foundation.trigger_event(
                "failover_activated",
                "info",
                "backup_manager",
                f"Failover activated to {best_backup}",
                {"backup_connection": best_backup}
            )
        else:
            await self.foundation.trigger_event(
                "failover_failed",
                "critical",
                "backup_manager",
                "No backup connections available for failover",
                {"available_backups": []}
            )


class StarlinkSecurityFoundation:
    """Main security foundation class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the security foundation.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.security_level = SecurityLevel.MINIMAL
        self.connection_type = ConnectionType.STARLINK_ONLY
        self.metrics = SecurityMetrics()
        self.active_threats: List[ThreatInfo] = []
        self.running = False
        self.backup_manager = BackupConnectionManager(self)
        self.events: List[Dict[str, Any]] = []
        
        logger.info("Starlink Security Foundation initialized")
        
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Configuration loaded from {config_path}")
                # Process configuration here
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
    
    async def trigger_event(self, event_type: str, severity: str, 
                           source: str, message: str, metadata: Dict[str, Any]):
        """Trigger and log a security event.
        
        Args:
            event_type: Type of event
            severity: Event severity level (info, warning, error, critical)
            source: Source of the event
            message: Event message
            metadata: Additional event metadata
        """
        event = {
            "type": event_type,
            "severity": severity,
            "source": source,
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        
        # Map severity to logging level safely
        severity_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        log_level = severity_mapping.get(severity.lower(), logging.INFO)
        logger.log(log_level, f"{event_type}: {message}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate a comprehensive security report.
        
        Returns:
            Dictionary containing security metrics and status
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "security_level": self.security_level.value,
            "connection_type": self.connection_type.value,
            "metrics": {
                "security_score": self.metrics.security_score,
                "connection_stability": self.metrics.connection_stability,
                "packet_loss": self.metrics.packet_loss,
                "latency": self.metrics.latency,
                "bandwidth_usage": self.metrics.bandwidth_usage,
                "threat_count": self.metrics.threat_count
            },
            "active_threats": [
                {
                    "id": threat.threat_id,
                    "severity": threat.severity,
                    "source": threat.source,
                    "description": threat.description,
                    "timestamp": threat.timestamp.isoformat()
                }
                for threat in self.active_threats
            ],
            "events": self.events[-10:],  # Last 10 events
            "backup_status": {
                "active": self.backup_manager.active_backup,
                "available": {
                    name: info["available"]
                    for name, info in self.backup_manager.backup_connections.items()
                }
            }
        }
    
    async def update_metrics(self):
        """Update security metrics periodically."""
        # Simulate metric updates
        # In a real implementation, this would collect actual metrics
        import random
        
        self.metrics.packet_loss = random.uniform(0, 15)
        self.metrics.latency = random.uniform(10, 250)
        self.metrics.connection_stability = random.uniform(40, 100)
        self.metrics.bandwidth_usage = random.uniform(0, 100)
        self.metrics.security_score = max(0, 100 - len(self.active_threats) * 10)
        self.metrics.threat_count = len(self.active_threats)
        self.metrics.last_updated = datetime.now()
        
        logger.debug(f"Metrics updated: loss={self.metrics.packet_loss:.1f}%, "
                    f"latency={self.metrics.latency:.1f}ms, "
                    f"stability={self.metrics.connection_stability:.1f}%")
    
    async def run(self):
        """Main run loop for the security foundation."""
        self.running = True
        logger.info("Starting Starlink Security Foundation main loop")
        
        try:
            while self.running:
                # Update metrics
                await self.update_metrics()
                
                # Monitor connection
                await self.backup_manager.monitor_connection()
                
                # Sleep before next iteration
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            raise
        finally:
            logger.info("Main loop stopped")
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up resources")
        self.running = False


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Starlink Enterprise Security Foundation')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--report', '-r', action='store_true', help='Generate security report')
    parser.add_argument('--status', '-s', action='store_true', help='Show current status')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Initialize foundation
    foundation = StarlinkSecurityFoundation(args.config)
    
    if args.report:
        # Generate and print report
        report = foundation.get_security_report()
        print(json.dumps(report, indent=2))
        return
    
    if args.status:
        # Show current status
        metrics = foundation.metrics
        print(f"Security Level: {foundation.security_level.value}")
        print(f"Connection Type: {foundation.connection_type.value}")
        print(f"Security Score: {metrics.security_score:.1f}/100")
        print(f"Connection Stability: {metrics.connection_stability:.1f}/100")
        print(f"Active Threats: {len(foundation.active_threats)}")
        return
    
    if args.daemon:
        # Run as daemon (Unix/Linux only)
        # Note: This implementation uses os.fork() which is not available on Windows
        if sys.platform == "win32":
            print("Error: Daemon mode is not supported on Windows")
            print("Please run the application in the foreground instead")
            sys.exit(1)
        
        print(f"Starting Starlink Security Foundation (PID: {os.getpid()})")
        print(f"Log file: {LOG_DIR}/starlink_security.log")
        
        # Daemonize (simplified)
        if os.fork() > 0:
            sys.exit(0)
        
        os.setsid()
        
        if os.fork() > 0:
            sys.exit(0)
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open('/dev/null', 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(LOG_DIR / 'daemon.log', 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
    
    # Run the foundation
    try:
        await foundation.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        foundation.running = False
        foundation.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
