"""
Common types and enumerations for Starlink Security Foundation
"""

from enum import Enum


class SecurityLevel(Enum):
    """Security level enumeration."""
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


# Constants
THREAT_INTELLIGENCE_FEED_LIMIT = 100  # Maximum number of indicators to process per feed
THREAT_SIMULATION_PROBABILITY = 0.1  # Probability of simulated threat (10%)
NETWORK_SCAN_INTERVAL = 300  # Default network scan interval in seconds
THREAT_CHECK_INTERVAL = 60  # Default threat check interval in seconds
