"""
Secure IT Starlink - Enterprise-grade security solutions for managed Starlink infrastructures.
"""

__version__ = "1.0.0"
__author__ = "Secure IT Team"

from .config.config_loader import ConfigurationManager
from .metrics.collector import MetricsCollector
from .automated_responses.coordinator import AutomatedResponseCoordinator
from .logging.structured_logger import StructuredLogger

__all__ = [
    "ConfigurationManager",
    "MetricsCollector",
    "AutomatedResponseCoordinator",
    "StructuredLogger",
]
