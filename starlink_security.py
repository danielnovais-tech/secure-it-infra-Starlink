"""
Starlink Security Foundation Module

Foundation for securing enterprise infrastructures using Starlink connectivity.
Provides monitoring, enforcement, and response capabilities.
"""

import json
import queue
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from cryptography.fernet import Fernet

# Define directories
CONFIG_DIR = Path.home() / ".starlink_security" / "config"
DATA_DIR = Path.home() / ".starlink_security" / "data"
LOG_DIR = Path.home() / ".starlink_security" / "logs"


def setup_directories() -> None:
    """
    Create required directories if they don't exist.
    
    Raises:
        PermissionError: If directories cannot be created due to insufficient permissions.
        OSError: If directories cannot be created due to other filesystem errors.
    """
    for directory in [CONFIG_DIR, DATA_DIR, LOG_DIR]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(
                f"Cannot create Starlink security directory '{directory}' due to insufficient permissions. "
                f"Original error: {e}"
            ) from e
        except OSError as e:
            raise OSError(
                f"Cannot create Starlink security directory '{directory}' due to filesystem error. "
                f"Original error: {e}"
            ) from e


class SecurityLevel(Enum):
    """Security levels for different operational modes."""
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"
    RECOVERY = "recovery"


class ConnectionType(Enum):
    """Types of Starlink connections."""
    STARLINK_ONLY = "starlink_only"
    HYBRID = "hybrid"  # Starlink + backup connection
    FAILOVER = "failover"  # Primary failed, using Starlink


@dataclass
class SecurityEvent:
    """Security event data structure."""
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


@dataclass
class NetworkMetrics:
    """Network performance and security metrics."""
    latency: float
    jitter: float
    packet_loss: float
    throughput: float  # Mbps
    security_score: float  # 0-100
    connection_stability: float  # 0-100
    last_outage: Optional[datetime] = None
    threat_indicators: List[str] = field(default_factory=list)


class StarlinkSecurityFoundation:
    """
    Foundation for securing enterprise infrastructures using Starlink connectivity.
    Provides monitoring, enforcement, and response capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the security foundation.
        
        Args:
            config_path: Path to configuration file (optional)
            
        Raises:
            PermissionError: If required directories cannot be created due to permissions.
            OSError: If required directories cannot be created due to other filesystem errors.
        """
        # Ensure required directories exist
        setup_directories()
        
        self.config = self._load_config(config_path)
        self.security_level = SecurityLevel.NORMAL
        self.connection_type = ConnectionType.STARLINK_ONLY
        self.encryption_key = self._initialize_encryption()
        self.running = True
        self.events_queue: queue.Queue = queue.Queue()
        self.metrics = NetworkMetrics(0, 0, 0, 0, 100, 100)
        self.active_threats: Set[str] = set()
        self.security_modules: Dict[str, Any] = {}
        self.events: List[SecurityEvent] = []
        self._initialize_modules()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "security_level": "normal",
            "connection_type": "starlink_only",
            "monitoring_interval": 60,
            "max_events_queue": 1000,
            "encryption_enabled": True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                # Log error but continue with defaults
                pass
        
        return default_config
    
    def _initialize_encryption(self) -> bytes:
        """
        Initialize encryption key for secure communications.
        
        Returns:
            Encryption key
        """
        key_file = CONFIG_DIR / "encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _initialize_modules(self) -> None:
        """
        Initialize security modules.
        """
        self.security_modules = {
            "firewall": {"enabled": True, "status": "active"},
            "intrusion_detection": {"enabled": True, "status": "active"},
            "threat_analysis": {"enabled": True, "status": "active"},
            "encryption": {"enabled": self.config.get("encryption_enabled", True), "status": "active"}
        }
    
    def log_event(self, event: SecurityEvent) -> None:
        """
        Log a security event.
        
        Args:
            event: SecurityEvent to log
        """
        self.events.append(event)
    
    def update_metrics(self, metrics: NetworkMetrics) -> None:
        """
        Update network metrics.
        
        Args:
            metrics: NetworkMetrics to update
        """
        self.metrics = metrics
    
    def set_security_level(self, level: SecurityLevel) -> None:
        """
        Set the security level.
        
        Args:
            level: New security level
        """
        self.security_level = level
    
    def get_unresolved_events(self) -> List[SecurityEvent]:
        """
        Get all unresolved security events.
        
        Returns:
            List of unresolved SecurityEvent objects
        """
        return [event for event in self.events if not event.resolved]
