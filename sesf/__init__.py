"""
SESF - Starlink Enterprise Security Framework

A comprehensive security framework for managing enterprise infrastructures
supporting Starlink satellite communications.

This framework provides:
- Authentication and authorization
- End-to-end encryption
- Network security controls
- Real-time monitoring and logging
- Compliance and audit capabilities
"""

__version__ = "1.0.0"
__author__ = "Secure IT Infrastructure Team"

from .core.framework import SESFFramework
from .core.config import SESFConfig

__all__ = ["SESFFramework", "SESFConfig"]
