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
        """
        if self.security_level == SecurityLevel.CRITICAL:
            base_score *= 0.7
        elif self.security_level == SecurityLevel.ELEVATED:
            base_score *= 0.9
        
        return base_score
