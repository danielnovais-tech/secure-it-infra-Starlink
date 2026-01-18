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

__version__ = "1.0.0"

# Public symbols expected by legacy tests (e.g. `test_security.py`).
StarlinkSecurityFoundation: Any
PolicyEnforcer: Any
IncidentResponder: Any
VPNManager: Any
BackupManager: Any
SecurityEvent: Any


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
    PolicyEnforcer = getattr(_legacy, "PolicyEnforcer")
    IncidentResponder = getattr(_legacy, "IncidentResponder")
    VPNManager = getattr(_legacy, "VPNManager")
    BackupManager = getattr(_legacy, "BackupManager")
    SecurityEvent = getattr(_legacy, "SecurityEvent")


__all__ = [
    "StarlinkSecurityFoundation",
    "PolicyEnforcer",
    "IncidentResponder",
    "VPNManager",
    "BackupManager",
    "SecurityEvent",
]
