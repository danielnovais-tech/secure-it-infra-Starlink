"""
Example usage of the Security Scoring Module
"""

import json
import tempfile
from security_scoring import SecurityLevel, SecurityScorer


def main():
    """Demonstrate the usage of SecurityScorer with different security levels."""
    
    print("Security Scoring System - Example Usage\n")
    print("=" * 50)
    
    # Example 1: Basic usage with different security levels
    base_score = 100.0
    
    # CRITICAL security level
    critical_scorer = SecurityScorer(SecurityLevel.CRITICAL)
    critical_score = critical_scorer.calculate_score(base_score)
    print(f"\nExample 1: Basic Usage")
    print(f"Base Score: {base_score}")
    print(f"Security Level: CRITICAL")
    print(f"Adjusted Score: {critical_score} (70% of base)")
    
    # ELEVATED security level
    elevated_scorer = SecurityScorer(SecurityLevel.ELEVATED)
    elevated_score = elevated_scorer.calculate_score(base_score)
    print(f"\nBase Score: {base_score}")
    print(f"Security Level: ELEVATED")
    print(f"Adjusted Score: {elevated_score} (90% of base)")
    
    # NORMAL security level
    normal_scorer = SecurityScorer(SecurityLevel.NORMAL)
    normal_score = normal_scorer.calculate_score(base_score)
    print(f"\nBase Score: {base_score}")
    print(f"Security Level: NORMAL")
    print(f"Adjusted Score: {normal_score} (100% of base)")



if __name__ == "__main__":
    main()
