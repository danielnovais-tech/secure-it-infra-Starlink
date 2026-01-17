"""Utility functions for Secure IT Starlink."""

import time
from typing import Dict, Any


def format_timestamp(timestamp: float = None) -> str:
    """
    Format timestamp to ISO format.
    
    Args:
        timestamp: Unix timestamp (defaults to current time)
        
    Returns:
        ISO formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).isoformat()


def calculate_uptime_percentage(total_time: float, down_time: float) -> float:
    """
    Calculate uptime percentage.
    
    Args:
        total_time: Total time period
        down_time: Time the system was down
        
    Returns:
        Uptime percentage
    """
    if total_time <= 0:
        return 0.0
    
    uptime = total_time - down_time
    return (uptime / total_time) * 100


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_sections = ['metrics', 'automated_responses', 'logging']
    
    for section in required_sections:
        if section not in config:
            return False
    
    return True


def get_severity_score(severity: str) -> int:
    """
    Convert severity level to numeric score.
    
    Args:
        severity: Severity level string
        
    Returns:
        Numeric severity score
    """
    severity_map = {
        'low': 1,
        'medium': 2,
        'high': 3,
        'critical': 4
    }
    
    return severity_map.get(severity.lower(), 0)
