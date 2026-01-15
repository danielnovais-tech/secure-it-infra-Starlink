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
    
    # Example 4: Audit trail integration with detail levels
    print("\nExample 4: Audit Trail with Detail Levels")
    audit_scorer = SecurityScorer(SecurityLevel.CRITICAL)
    audit_scorer.calculate_score(100.0)
    audit_scorer.calculate_score(250.0)
    
    print("\nSummary detail level:")
    for i, entry in enumerate(audit_scorer.get_audit_trail(detail_level="summary"), 1):
        print(f"  Entry {i}: {entry}")
    
    print("\nFull detail level:")
    for i, entry in enumerate(audit_scorer.get_audit_trail(detail_level="full"), 1):
        print(f"\n  Entry {i}:")
        for key, value in entry.items():
            print(f"    {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Example 5: Historical comparison
    print("\nExample 5: Historical Score Comparison")
    hist_scorer = SecurityScorer(SecurityLevel.ELEVATED)
    
    # First run (no previous score)
    score1 = hist_scorer.calculate_score(100.0)
    print(f"Run 1: Score = {score1}")
    
    # Second run (compare to previous)
    score2 = hist_scorer.calculate_score(120.0, previous_score=score1)
    print(f"Run 2: Score = {score2}")
    
    # Third run (compare to previous, score decreases)
    score3 = hist_scorer.calculate_score(80.0, previous_score=score2)
    print(f"Run 3: Score = {score3}")
    
    print("\nAudit trail with historical context:")
    for entry in hist_scorer.get_audit_trail():
        print(f"  {entry['reason']}")
        if 'historical_delta' in entry:
            print(f"    Delta from previous: {entry['historical_delta']:+.1f}")
    
    print("\n" + "=" * 50)
    
    # Example 6: Exporting audit trail
    print("\nExample 6: Exporting Audit Trail")
    export_scorer = SecurityScorer(SecurityLevel.CRITICAL)
    export_scorer.calculate_score(100.0, previous_score=120.0)
    export_scorer.calculate_score(250.0, previous_score=180.0)
    export_scorer.calculate_score(500.0, max_score=400.0, previous_score=300.0)
    
    # Export to JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_path = f.name
    export_scorer.export_audit_trail_json(json_path, detail_level="full")
    print(f"Exported audit trail to JSON: {json_path}")
    
    # Show JSON content
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    print(f"  Entries exported: {len(json_data['entries'])}")
    print(f"  Export timestamp: {json_data['export_timestamp']}")
    
    # Export to CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
    export_scorer.export_audit_trail_csv(csv_path)
    print(f"Exported audit trail to CSV: {csv_path}")
    
    print("\n" + "=" * 50)
    
    # Example 7: Boundary cases
    print("\nExample 7: Boundary Cases")
    
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
    
    # Example 8: Real-world scenario
    print("\nExample 8: Real-world Scenario with Full Pipeline")
    print("Simulating continuous security monitoring")
    
    scenarios = [
        (SecurityLevel.NORMAL, 250.0, None, "Normal operations"),
        (SecurityLevel.ELEVATED, 250.0, 250.0, "Threat detected - elevated level"),
        (SecurityLevel.CRITICAL, 250.0, 225.0, "Critical vulnerability - immediate action"),
    ]
    
    for level, base, previous, description in scenarios:
        scorer = SecurityScorer(level)
        score = scorer.calculate_score(base, previous_score=previous)
        audit = scorer.get_audit_trail()[0]
        
        print(f"\n{description}")
        print(f"  Security Level: {level.value}")
        print(f"  Base Score: {base}")
        print(f"  Final Score: {score}")
        print(f"  Audit: {audit['reason']}")
        print(f"  Points Change: {audit['points']}")
        if 'historical_delta' in audit:
            print(f"  Historical Delta: {audit['historical_delta']:+.1f}")


if __name__ == "__main__":
    main()
