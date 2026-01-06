"""
Secure IT Starlink - Comprehensive Security Tool Foundation
=====================================================

A security toolkit for Starlink-connected enterprise infrastructures.

This package provides:
- Network security monitoring for Starlink connections
- Encryption and key management utilities
- Security event logging and alerting
- Vulnerability scanning framework
- Access control and authentication
- Configuration security scanner
"""

__version__ = "0.1.0"
__author__ = "Daniel Novais Tech"

from secure_it_starlink.network import NetworkMonitor, ConnectionValidator
from secure_it_starlink.crypto import EncryptionManager, KeyManager
from secure_it_starlink.logging import SecurityLogger, AlertManager
from secure_it_starlink.scanning import VulnerabilityScanner, PortScanner
from secure_it_starlink.access import AccessController, AuthenticationManager
from secure_it_starlink.config import ConfigScanner, SecurityConfig

__all__ = [
    "NetworkMonitor",
    "ConnectionValidator",
    "EncryptionManager",
    "KeyManager",
    "SecurityLogger",
    "AlertManager",
    "VulnerabilityScanner",
    "PortScanner",
    "AccessController",
    "AuthenticationManager",
    "ConfigScanner",
    "SecurityConfig",
]
