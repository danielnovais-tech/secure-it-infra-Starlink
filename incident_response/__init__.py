"""
Incident Response System

A YAML-based incident response handler for high-severity security events
such as malware detection and security breaches.

Features:
- YAML-configured incident definitions
- Automated action execution (isolation, scanning, notifications, logging)
- Priority-based action ordering
- Event condition matching
- Extensible action framework
"""

from .handler import IncidentResponseHandler

__version__ = '1.0.0'
__all__ = ['IncidentResponseHandler']
