"""
Starlink Security Foundation Module

Foundation for securing enterprise infrastructures using Starlink connectivity.
Provides monitoring, enforcement, and response capabilities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    try:
        for directory in [CONFIG_DIR, DATA_DIR, LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create Starlink security directories due to insufficient permissions. "
            f"Failed at: {e.filename or 'unknown location'}"
        ) from e
    except OSError as e:
        raise OSError(
            f"Cannot create Starlink security directories due to filesystem error: "
            f"{e.strerror or 'unknown error'}. Failed at: {e.filename or 'unknown location'}"
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
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.NORMAL,
                 connection_type: ConnectionType = ConnectionType.STARLINK_ONLY):
        """
        Initialize the Starlink Security Foundation.
        
        Args:
            security_level: Initial security level
            connection_type: Type of Starlink connection
            
        Raises:
            PermissionError: If required directories cannot be created due to permissions.
            OSError: If required directories cannot be created due to other filesystem errors.
        """
        # Ensure required directories exist
        setup_directories()
        
        self.security_level = security_level
        self.connection_type = connection_type
        self.events: List[SecurityEvent] = []
        self.metrics: Optional[NetworkMetrics] = None
    
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
