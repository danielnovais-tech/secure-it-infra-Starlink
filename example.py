"""
Example usage of the Security Scoring Module
"""

import json
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
    
    print("\n" + "=" * 50)
    
    # Example 2: Custom multipliers
    print("\nExample 2: Custom Multipliers")
    custom_multipliers = {
        SecurityLevel.CRITICAL: 0.5,
        SecurityLevel.ELEVATED: 0.75,
    }
    custom_scorer = SecurityScorer(SecurityLevel.CRITICAL, custom_multipliers=custom_multipliers)
    custom_score = custom_scorer.calculate_score(100.0)
    print(f"Using custom multiplier (0.5x) for CRITICAL: {custom_score}")
    
    print("\n" + "=" * 50)
    
    # Example 3: Using configuration file
    print("\nExample 3: Configuration File")
    config_scorer = SecurityScorer(SecurityLevel.ELEVATED, config_file="config.json")
    config_score = config_scorer.calculate_score(100.0)
    print(f"Using config file multipliers: {config_score}")
    
    print("\n" + "=" * 50)
    
    # Example 4: Audit trail integration
    print("\nExample 4: Audit Trail")
    audit_scorer = SecurityScorer(SecurityLevel.CRITICAL)
    audit_scorer.calculate_score(100.0)
    audit_scorer.calculate_score(250.0)
    
    print("Audit trail entries:")
    for i, entry in enumerate(audit_scorer.get_audit_trail(), 1):
        print(f"\n  Entry {i}:")
        print(f"    Reason: {entry['reason']}")
        print(f"    Points: {entry['points']}")
        print(f"    Original Score: {entry['original_score']}")
        print(f"    Adjusted Score: {entry['adjusted_score']}")
    
    print("\n" + "=" * 50)
    
    # Example 5: Boundary cases
    print("\nExample 5: Boundary Cases")
    
    # Zero score
    boundary_scorer = SecurityScorer(SecurityLevel.CRITICAL)
    zero_score = boundary_scorer.calculate_score(0.0)
    print(f"Zero base score (0.0): {zero_score} (remains 0)")
    
    # Very high score with cap
    high_score = boundary_scorer.calculate_score(10000.0, max_score=500.0)
    print(f"High base score (10000.0) with max cap (500.0): {high_score}")
    
    # Very high score without cap
    boundary_scorer.clear_audit_trail()
    high_score_no_cap = boundary_scorer.calculate_score(10000.0)
    print(f"High base score (10000.0) without cap: {high_score_no_cap}")
    
    print("\n" + "=" * 50)
    
    # Example 6: Real-world scenario
    print("\nExample 6: Real-world Scenario")
    print("Evaluating system security with base score of 250")
    
    scenarios = [
        (SecurityLevel.CRITICAL, "Critical vulnerability detected"),
        (SecurityLevel.ELEVATED, "Elevated threat level"),
        (SecurityLevel.NORMAL, "Normal operations"),
    ]
    
    for level, description in scenarios:
        scorer = SecurityScorer(level)
        score = scorer.calculate_score(250.0)
        audit = scorer.get_audit_trail()[0]
        
        print(f"\n{description}")
        print(f"  Security Level: {level.value}")
        print(f"  Final Score: {score}")
        print(f"  Audit: {audit['reason']}")
        print(f"  Points Change: {audit['points']}")


if __name__ == "__main__":
    main()
