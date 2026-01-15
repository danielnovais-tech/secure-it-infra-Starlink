"""
Security Scoring Module

This module provides functionality to adjust security scores based on security levels.
"""

import json
import logging
import os
from enum import Enum
from typing import Dict, Optional, List


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Enumeration of security levels for score adjustment."""
    CRITICAL = "critical"
    ELEVATED = "elevated"
    NORMAL = "normal"


# Default score multipliers for each security level
DEFAULT_SECURITY_LEVEL_MULTIPLIERS = {
    SecurityLevel.CRITICAL: 0.7,
    SecurityLevel.ELEVATED: 0.9,
    SecurityLevel.NORMAL: 1.0,
}


class AuditEntry:
    """
    Represents an audit trail entry for a security scoring operation.
    
    Attributes:
        reason (str): Description of the scoring adjustment.
        points (str): Points adjustment details.
        security_level (str): The security level applied.
        original_score (float): The original score before adjustment.
        adjusted_score (float): The score after adjustment.
    """
    
    def __init__(self, reason: str, points: str, security_level: str, 
                 original_score: float, adjusted_score: float):
        self.reason = reason
        self.points = points
        self.security_level = security_level
        self.original_score = original_score
        self.adjusted_score = adjusted_score
    
    def to_dict(self) -> dict:
        """Convert audit entry to dictionary format."""
        return {
            "reason": self.reason,
            "points": self.points,
            "security_level": self.security_level,
            "original_score": self.original_score,
            "adjusted_score": self.adjusted_score
        }
    
    def __repr__(self) -> str:
        return f"AuditEntry({self.to_dict()})"


class SecurityScorer:
    """
    A class to calculate security scores based on security levels.
    
    Attributes:
        security_level (SecurityLevel): The current security level.
        multipliers (Dict[SecurityLevel, float]): Custom multipliers for each security level.
        audit_trail (List[AuditEntry]): List of audit entries for scoring operations.
    """
    
    def __init__(
        self, 
        security_level: SecurityLevel, 
        custom_multipliers: Optional[Dict[SecurityLevel, float]] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize the SecurityScorer with a security level.
        
        Args:
            security_level (SecurityLevel): The security level to use for scoring.
            custom_multipliers (Optional[Dict[SecurityLevel, float]]): Custom multiplier overrides.
            config_file (Optional[str]): Path to JSON configuration file with multipliers.
        """
        self.security_level = security_level
        self.audit_trail: List[AuditEntry] = []
        
        # Load multipliers from config file if provided
        if config_file and os.path.exists(config_file):
            self.multipliers = self._load_multipliers_from_config(config_file)
        elif custom_multipliers:
            self.multipliers = {**DEFAULT_SECURITY_LEVEL_MULTIPLIERS, **custom_multipliers}
        else:
            self.multipliers = DEFAULT_SECURITY_LEVEL_MULTIPLIERS.copy()
    
    def _load_multipliers_from_config(self, config_file: str) -> Dict[SecurityLevel, float]:
        """
        Load multipliers from a JSON configuration file.
        
        Args:
            config_file (str): Path to the JSON configuration file.
        
        Returns:
            Dict[SecurityLevel, float]: Multipliers loaded from config.
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            multipliers = DEFAULT_SECURITY_LEVEL_MULTIPLIERS.copy()
            
            # Map string keys to SecurityLevel enum
            for level_str, multiplier in config.get('multipliers', {}).items():
                try:
                    level = SecurityLevel(level_str.lower())
                    multipliers[level] = float(multiplier)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid security level '{level_str}' in config file: {e}")
            
            logger.info(f"Loaded multipliers from {config_file}")
            return multipliers
            
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config from {config_file}: {e}. Using defaults.")
            return DEFAULT_SECURITY_LEVEL_MULTIPLIERS.copy()
    
    def calculate_score(self, base_score: float, max_score: Optional[float] = None) -> float:
        """
        Calculate the adjusted score based on the security level.
        
        Args:
            base_score (float): The base score before adjustment.
            max_score (Optional[float]): Maximum score cap. If None, no cap is applied.
        
        Returns:
            float: The adjusted score based on security level.
        
        Raises:
            ValueError: If base_score is negative.
        """
        if base_score < 0:
            raise ValueError("base_score must be non-negative")
        
        # Get multiplier, default to 1.0 if security level is unknown
        multiplier = self.multipliers.get(self.security_level, 1.0)
        
        # Log warning for unknown security levels
        if self.security_level not in self.multipliers:
            logger.warning(f"Unknown security level {self.security_level}. Using default multiplier of 1.0")
        
        adjusted_score = base_score * multiplier
        
        # Apply max score cap if specified
        if max_score is not None and adjusted_score > max_score:
            adjusted_score = max_score
        
        # Create audit trail entry
        points_change = adjusted_score - base_score
        audit_entry = AuditEntry(
            reason=f"{self.security_level.value.upper()} security level multiplier",
            points=f"{points_change:+.1f} ({multiplier}x applied)",
            security_level=self.security_level.value,
            original_score=base_score,
            adjusted_score=adjusted_score
        )
        self.audit_trail.append(audit_entry)
        
        return adjusted_score
    
    def get_audit_trail(self) -> List[Dict]:
        """
        Get the audit trail of all scoring operations.
        
        Returns:
            List[Dict]: List of audit entries as dictionaries.
        """
        return [entry.to_dict() for entry in self.audit_trail]
    
    def clear_audit_trail(self) -> None:
        """Clear the audit trail."""
        self.audit_trail.clear()
