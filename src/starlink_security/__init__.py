"""Starlink Security Foundation package.

This repository contains both a newer package implementation (in this
directory) and a legacy single-file implementation at `src/starlink_security.py`.

The test suite and examples in this repo expect the legacy API surface to be
importable from `starlink_security`, so we load and re-export those symbols
here.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

try:
	from .foundation import StarlinkSecurityFoundation as ModernStarlinkSecurityFoundation
except Exception:  # pragma: no cover
	ModernStarlinkSecurityFoundation = None  # type: ignore[assignment]


def _load_legacy_module() -> Any:
	legacy_path = (Path(__file__).resolve().parent.parent / "starlink_security.py")
	spec = spec_from_file_location("_starlink_security_legacy_src", legacy_path)
	if spec is None or spec.loader is None:
		raise ImportError(f"Unable to load legacy module at {legacy_path}")
	module = module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


_legacy = _load_legacy_module()

StarlinkSecurityFoundation = _legacy.StarlinkSecurityFoundation
NetworkMonitor = _legacy.NetworkMonitor
SecurityEvent = _legacy.SecurityEvent
SecurityLevel = _legacy.SecurityLevel
ConnectionType = _legacy.ConnectionType
NetworkMetrics = _legacy.NetworkMetrics

__version__ = "0.1.0"
__all__ = [
	"StarlinkSecurityFoundation",
	"NetworkMonitor",
	"SecurityEvent",
	"SecurityLevel",
	"ConnectionType",
	"NetworkMetrics",
	"ModernStarlinkSecurityFoundation",
]
