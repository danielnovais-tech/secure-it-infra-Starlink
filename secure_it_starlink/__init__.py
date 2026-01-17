"""Secure IT Infrastructure - Starlink.

Enterprise-grade security solutions for managed Starlink infrastructures.
"""

__version__ = "1.0.0"
__author__ = "Secure IT Team"

from .access import AccessController, AuthenticationManager
from .automated_responses.coordinator import AutomatedResponseCoordinator
from .config import ConfigScanner, SecurityConfig
from .config.config_loader import ConfigurationManager
from .crypto import EncryptionManager, KeyManager
from .logging import AlertManager, SecurityLogger
from .logging.structured_logger import StructuredLogger
from .metrics.collector import MetricsCollector
from .network import ConnectionValidator, NetworkMonitor
from .scanning import PortScanner, VulnerabilityScanner

__all__ = [
    "AccessController",
    "AlertManager",
    "AuthenticationManager",
    "AutomatedResponseCoordinator",
    "ConfigScanner",
    "ConfigurationManager",
    "ConnectionValidator",
    "EncryptionManager",
    "KeyManager",
    "MetricsCollector",
    "NetworkMonitor",
    "PortScanner",
    "SecurityConfig",
    "SecurityLogger",
    "StructuredLogger",
    "VulnerabilityScanner",
]
