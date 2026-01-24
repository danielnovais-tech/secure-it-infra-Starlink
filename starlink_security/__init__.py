"""Starlink Security Infrastructure.

This repo currently contains multiple historical implementations that share the
same top-level name ("starlink_security"). Some legacy tests import high-level
symbols directly from this package.

To keep those tests and editor tooling working, this package provides a
compatibility layer that re-exports symbols from the legacy script
`starlink_security.py` when present.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Optional
from .bandwidth_optimizer import BandwidthOptimizer as _BandwidthOptimizer
from .connection_monitor import ConnectionMonitor as _ConnectionMonitor
from .policy_manager import LatencyAwarePolicyManager as _LatencyAwarePolicyManager
from .remote_manager import RemoteManager as _RemoteManager
from .resilience import ConnectionResilience as _ConnectionResilience

__version__ = "1.0.0"

# Public symbols expected by legacy tests (e.g. `test_security.py`).
StarlinkSecurityFoundation: Any
LegacyStarlinkSecurityFoundation: Any
PolicyEnforcer: Any
IncidentResponder: Any
VPNManager: Any
BackupManager: Any
SecurityEvent: Any
NetworkMonitor: Any
SecurityLevel: Any
ConnectionType: Any
NetworkMetrics: Any

# Public symbols used by the newer `starlink_security/*.py` implementation.
ConnectionMonitor: Any
LatencyAwarePolicyManager: Any
ConnectionResilience: Any
RemoteManager: Any
BandwidthOptimizer: Any


# Import the modern package-level implementation first (keeps examples working).
BandwidthOptimizer = _BandwidthOptimizer
ConnectionMonitor = _ConnectionMonitor
LatencyAwarePolicyManager = _LatencyAwarePolicyManager
RemoteManager = _RemoteManager
ConnectionResilience = _ConnectionResilience


def _load_legacy_script() -> Optional[object]:
    legacy_path = Path(__file__).resolve().parent.parent / "starlink_security.py"
    if not legacy_path.exists():
        return None

    spec = spec_from_file_location("_starlink_security_legacy", legacy_path)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_legacy = _load_legacy_script()
if _legacy is not None:
    StarlinkSecurityFoundation = getattr(_legacy, "StarlinkSecurityFoundation")
    if hasattr(_legacy, "LegacyStarlinkSecurityFoundation"):
        LegacyStarlinkSecurityFoundation = getattr(_legacy, "LegacyStarlinkSecurityFoundation")
    PolicyEnforcer = getattr(_legacy, "PolicyEnforcer")
    IncidentResponder = getattr(_legacy, "IncidentResponder")
    VPNManager = getattr(_legacy, "VPNManager")
    BackupManager = getattr(_legacy, "BackupManager")
    SecurityEvent = getattr(_legacy, "SecurityEvent")
    NetworkMonitor = getattr(_legacy, "NetworkMonitor")
    SecurityLevel = getattr(_legacy, "SecurityLevel")
    ConnectionType = getattr(_legacy, "ConnectionType")
    NetworkMetrics = getattr(_legacy, "NetworkMetrics")


__all__ = [
    "StarlinkSecurityFoundation",
    "LegacyStarlinkSecurityFoundation",
    "PolicyEnforcer",
    "IncidentResponder",
    "VPNManager",
    "BackupManager",
    "SecurityEvent",
    "NetworkMonitor",
    "SecurityLevel",
    "ConnectionType",
    "NetworkMetrics",

    "ConnectionMonitor",
    "LatencyAwarePolicyManager",
    "ConnectionResilience",
    "RemoteManager",
    "BandwidthOptimizer",
]
