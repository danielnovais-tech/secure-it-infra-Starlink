"""Connection type management for Starlink infrastructure."""

from enum import Enum, auto


class ConnectionType(Enum):
    """Connection type definitions for network management.
    
    Attributes:
        STARLINK_ONLY: Exclusive Starlink satellite connection
        HYBRID: Combined Starlink and terrestrial connection
        FAILOVER: Automatic failover between connection types
    """
    
    STARLINK_ONLY = auto()
    HYBRID = auto()
    FAILOVER = auto()
    
    def __str__(self) -> str:
        """Return string representation of connection type."""
        return self.name.replace("_", "-")
    
    def __repr__(self) -> str:
        """Return detailed representation of connection type."""
        return f"ConnectionType.{self.name}"
    
    @property
    def supports_redundancy(self) -> bool:
        """Check if connection type supports redundancy.
        
        Returns:
            True if connection type has redundancy capabilities
        """
        return self in (ConnectionType.HYBRID, ConnectionType.FAILOVER)
    
    @property
    def is_satellite_only(self) -> bool:
        """Check if connection type uses only satellite.
        
        Returns:
            True if connection type is satellite-only
        """
        return self == ConnectionType.STARLINK_ONLY
