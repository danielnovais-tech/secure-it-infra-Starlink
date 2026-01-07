"""Starlink Security Infrastructure Package."""

from starlink_security.config import CONFIG_DIR, DATA_DIR, LOG_DIR

__all__ = ["CONFIG_DIR", "DATA_DIR", "LOG_DIR"]
"""
Starlink Security Infrastructure Package

A comprehensive security solution for managed enterprise infrastructures
supporting Starlink satellite connectivity with specialized adaptations for:
- Latency-aware security policies
- Connection resilience and failover
- Remote management capabilities
- Bandwidth-optimized security operations
"""

__version__ = "1.0.0"

from .connection_monitor import ConnectionMonitor
from .policy_manager import LatencyAwarePolicyManager
from .resilience import ConnectionResilience
from .remote_manager import RemoteManager
from .bandwidth_optimizer import BandwidthOptimizer

__all__ = [
    "ConnectionMonitor",
    "LatencyAwarePolicyManager",
    "ConnectionResilience",
    "RemoteManager",
    "BandwidthOptimizer",
]
