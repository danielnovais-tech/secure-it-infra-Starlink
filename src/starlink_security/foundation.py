"""Main Starlink Security Foundation class."""

import asyncio
import copy
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, Optional

import yaml
from cryptography.fernet import Fernet

from .modules import (
    BackupManager,
    IncidentResponder,
    NetworkMonitor,
    PolicyEnforcer,
    ThreatDetector,
    VPNManager,
)

# Logger for this module
logger = logging.getLogger(__name__)

# Default directories
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [CONFIG_DIR, DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class StarlinkSecurityFoundation:
    """Core security foundation for Starlink enterprise infrastructure."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Starlink Security Foundation."""
        self.config = self._load_config(config_path)
        self.encryption = self._initialize_encryption()
        self.security_modules = {}
        self.running = False
        self._cleaned_up = False
        
        # Initialize security modules
        self._initialize_modules()
        
        # Initialize event handlers
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        signal.signal(signal.SIGINT, self._shutdown_handler)
        
        logger.info("Starlink Security Foundation initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or defaults."""
        default_config = {
            "security": {
                "encryption_enabled": True,
                "vpn_required": True,
                "minimum_tls_version": "TLSv1.3",
                "threat_intelligence_feeds": [
                    "https://feeds.dshield.org/block.txt",
                    "https://rules.emergingthreats.net/blockrules/compromised-ips.txt"
                ]
            },
            "monitoring": {
                "network_scan_interval": 300,  # seconds
                "threat_check_interval": 60,
                "log_retention_days": 90
            },
            "starlink": {
                "gateway_ip": "192.168.100.1",
                "api_endpoint": "http://192.168.100.1:9200",
                "performance_thresholds": {
                    "max_latency": 100,  # ms
                    "max_jitter": 20,  # ms
                    "max_packet_loss": 2,  # %
                    "min_throughput": 10  # Mbps
                }
            },
            "enterprise": {
                "critical_services": ["vpn", "authentication", "database"],
                "backup_connections": ["cellular", "satellite_backup"],
                "recovery_procedures": ["failover", "degraded_mode"]
            }
        }
        
        config_file = Path(config_path) if config_path else CONFIG_DIR / "config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                    # Deep merge configurations
                    merged = copy.deepcopy(default_config)
                    self._deep_update(merged, user_config)
                    return merged
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        return default_config
    
    def _deep_update(self, target: Dict, source: Dict):
        """Deep update nested dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def _initialize_encryption(self) -> Optional[Fernet]:
        """Initialize encryption system."""
        try:
            key_file = DATA_DIR / "encryption.key"
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                key_file.chmod(0o600)
            
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            return None
    
    def _initialize_modules(self):
        """Initialize security modules."""
        modules = {
            'network_monitor': NetworkMonitor(self),
            'threat_detector': ThreatDetector(self),
            'policy_enforcer': PolicyEnforcer(self),
            'incident_responder': IncidentResponder(self),
            'vpn_manager': VPNManager(self),
            'backup_manager': BackupManager(self)
        }
        
        for name, module in modules.items():
            if module.initialize():
                self.security_modules[name] = module
                logger.info(f"Initialized module: {name}")
    
    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received shutdown signal {signum}")
        self.running = False
        # Don't call cleanup here - let async_main's finally block handle it
        raise SystemExit(0)
    
    def _handle_module_task_result(self, task: asyncio.Task) -> None:
        """Handle completion of background module tasks and log exceptions."""
        try:
            exception = task.exception()
        except asyncio.CancelledError:
            # Task was cancelled as part of shutdown; no further action needed.
            return
        except Exception as e:
            # Unexpected error while retrieving the exception from the task.
            logger.error(f"Unexpected error retrieving task exception: {e}")
            return

        if exception is not None:
            logger.error("Module task raised an exception", exc_info=exception)
    
    async def run(self):
        """Main event loop for the security foundation."""
        logger.info("Starting Starlink Security Foundation")
        self.running = True
        
        # Start all security modules
        for name, module in self.security_modules.items():
            task = asyncio.create_task(module.start())
            task.add_done_callback(self._handle_module_task_result)
            logger.info(f"Started module: {name}")
        
        try:
            # Keep running until shutdown
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown all modules gracefully."""
        logger.info("Shutting down Starlink Security Foundation")
        self.running = False
        
        # Stop all modules
        for name, module in self.security_modules.items():
            try:
                await module.stop()
                logger.info(f"Stopped module: {name}")
            except Exception as e:
                logger.error(f"Error stopping module {name}: {e}")
    
    def cleanup(self):
        """Cleanup resources. Idempotent - safe to call multiple times."""
        if self._cleaned_up:
            return
        
        logger.info("Cleaning up resources")
        self._cleaned_up = True
        
        for module in self.security_modules.values():
            try:
                module.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def configure_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def async_main(config_path: Optional[str] = None):
    """Main async entry point."""
    logger.info("Starting Starlink Security Foundation")
    foundation = StarlinkSecurityFoundation(config_path=config_path)
    try:
        await foundation.run()
    except asyncio.CancelledError:
        # Handle Ctrl+C or shutdown signals
        logger.info("Received cancellation signal")
        await foundation.shutdown()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        raise
    finally:
        # Ensure resources are released
        logger.info("Cleaning up resources")
        foundation.cleanup()


def main():
    """Main synchronous entry point for console script."""
    import argparse
    
    configure_logging()
    
    parser = argparse.ArgumentParser(
        description="Starlink Security Foundation - Enterprise security for Starlink infrastructure"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(async_main(config_path=args.config))
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
