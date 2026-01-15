"""
Security Scoring Module

This module provides functionality to adjust security scores based on security levels.
"""

from enum import Enum


class SecurityLevel(Enum):
    """Enumeration of security levels for score adjustment."""
    CRITICAL = "critical"
    ELEVATED = "elevated"
    NORMAL = "normal"


# Score multipliers for each security level
SECURITY_LEVEL_MULTIPLIERS = {
    SecurityLevel.CRITICAL: 0.7,
    SecurityLevel.ELEVATED: 0.9,
    SecurityLevel.NORMAL: 1.0,
}


class SecurityScorer:
    """
    A class to calculate security scores based on security levels.
    
    Attributes:
        security_level (SecurityLevel): The current security level.
    """
    
    def __init__(self, security_level: SecurityLevel):
        """
        Initialize the SecurityScorer with a security level.
        
        Args:
            security_level (SecurityLevel): The security level to use for scoring.
        """
        self.security_level = security_level
    
    def calculate_score(self, base_score: float) -> float:
        """
        Calculate the adjusted score based on the security level.
        
        Args:
            base_score (float): The base score before adjustment.
        
        Returns:
            float: The adjusted score based on security level.
        
        Raises:
            ValueError: If base_score is negative.
        """
        if base_score < 0:
            raise ValueError("base_score must be non-negative")
        
        multiplier = SECURITY_LEVEL_MULTIPLIERS.get(self.security_level, 1.0)
        return base_score * multiplier
