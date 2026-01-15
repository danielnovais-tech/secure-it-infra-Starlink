"""Security level definitions for the infrastructure."""

from enum import Enum, auto


class SecurityLevel(Enum):
    """Structured security levels for infrastructure management.
    
    Attributes:
        NORMAL: Standard operational security level
        ELEVATED: Increased security monitoring and controls
        CRITICAL: Maximum security protocols activated
        RECOVERY: System recovery mode with restricted access
    """
    
    NORMAL = auto()
    ELEVATED = auto()
    CRITICAL = auto()
    RECOVERY = auto()
    
    def __str__(self) -> str:
        """Return string representation of security level."""
        return self.name
    
    def __repr__(self) -> str:
        """Return detailed representation of security level."""
        return f"SecurityLevel.{self.name}"
    
    @property
    def priority(self) -> int:
        """Return numeric priority of security level (higher is more severe)."""
        priority_map = {
            SecurityLevel.NORMAL: 0,
            SecurityLevel.ELEVATED: 1,
            SecurityLevel.CRITICAL: 2,
            SecurityLevel.RECOVERY: 3,
        }
        return priority_map[self]
    
    def is_higher_than(self, other: "SecurityLevel") -> bool:
        """Check if this security level has higher priority than another.
        
        Args:
            other: Another SecurityLevel to compare against
            
        Returns:
            True if this level has higher priority
        """
        return self.priority > other.priority
    
    def is_lower_than(self, other: "SecurityLevel") -> bool:
        """Check if this security level has lower priority than another.
        
        Args:
            other: Another SecurityLevel to compare against
            
        Returns:
            True if this level has lower priority
        """
        return self.priority < other.priority
