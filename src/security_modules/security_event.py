"""Security Event data class."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class SecurityEvent:
    """Represents a security event in the system."""
    
    event_type: str
    severity: str  # critical, high, medium, low
    source: str
    timestamp: datetime
    description: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate severity level."""
        valid_severities = ["critical", "high", "medium", "low"]
        if self.severity not in valid_severities:
            raise ValueError(f"Invalid severity: {self.severity}. Must be one of {valid_severities}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type,
            "severity": self.severity,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metadata": self.metadata or {}
        }
