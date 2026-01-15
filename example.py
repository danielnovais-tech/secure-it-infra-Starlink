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
"""Example usage of the SecurityMonitor class."""
import asyncio
import logging
from src.security_monitor import SecurityMonitor

# Configure logging to see the output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Demonstrate SecurityMonitor functionality."""
    # Create a security monitor instance
    monitor = SecurityMonitor()
    
    logger.info("=== Starting Security Monitor Demo ===\n")
    
    # Simulate initial metrics
    logger.info("Step 1: Setting initial metrics")
    initial_metrics = {
        "failed_login_attempts": 2,
        "unauthorized_access_attempts": 0,
        "network_intrusion_attempts": 0,
        "active_connections": 100,
        "encrypted_connections": 95
    }
    await monitor.update_metrics(initial_metrics)
    
    # Calculate initial security score
    score = monitor.get_security_score()
    logger.info(f"Initial Security Score: {score}\n")
    
    # Simulate a significant change in metrics
    logger.info("Step 2: Simulating significant changes in security metrics")
    updated_metrics = {
        "failed_login_attempts": 25,  # Significant increase
        "unauthorized_access_attempts": 0,
        "network_intrusion_attempts": 0,
        "active_connections": 150,  # 50% increase
        "encrypted_connections": 145
    }
    await monitor.update_metrics(updated_metrics)
    
    # Calculate security score after changes
    score = monitor.get_security_score()
    logger.info(f"Security Score after changes: {score}\n")
    
    # Simulate critical security issues
    logger.info("Step 3: Simulating critical security incidents")
    critical_metrics = {
        "failed_login_attempts": 30,
        "unauthorized_access_attempts": 3,  # Critical!
        "network_intrusion_attempts": 2,  # Critical!
        "active_connections": 200,
        "encrypted_connections": 150
    }
    await monitor.update_metrics(critical_metrics)
    
    # Check anomalies
    anomalies = monitor.get_anomalies()
    logger.info(f"\nTotal anomalies detected: {len(anomalies)}")
    
    # Show critical anomalies
    critical_anomalies = monitor.get_anomalies(severity="critical")
    logger.info(f"Critical anomalies: {len(critical_anomalies)}")
    for anomaly in critical_anomalies:
        logger.warning(f"  - {anomaly['type']}: {anomaly['metric']} = {anomaly['value']}")
    
    # Calculate final security score
    score = monitor.get_security_score()
    logger.info(f"\nFinal Security Score: {score}")
    
    # Demonstrate clearing anomalies
    logger.info("\nStep 4: Clearing anomalies")
    monitor.clear_anomalies()
    logger.info(f"Anomalies after clearing: {len(monitor.get_anomalies())}\n")
    
    logger.info("=== Security Monitor Demo Complete ===")


if __name__ == "__main__":
#!/usr/bin/env python3
"""
Example usage of the Starlink Network Monitoring System
"""
import asyncio
import json
from starlink_monitor import StarlinkMonitor, NetworkMetrics


async def main():
    """Main example function."""
    # Load configuration
    with open('config.example.json', 'r') as f:
        config = json.load(f)
    
    # Create monitor instance
    monitor = StarlinkMonitor(config)
    
    # Register event handler
    async def handle_event(event):
        print(f"\n{'='*60}")
        print(f"EVENT: {event['type']}")
        print(f"Severity: {event['severity']}")
        print(f"Source: {event['source']}")
        print(f"Message: {event['message']}")
        if event['data']:
            print(f"Data: {json.dumps(event['data'], indent=2)}")
        print(f"{'='*60}\n")
    
    monitor.event_handlers.append(handle_event)
    
    # Scenario 1: Normal operation
    print("\n>>> Scenario 1: Normal Operation")
    print("-" * 60)
    metrics = NetworkMetrics(
        latency=45.0,
        jitter=8.0,
        packet_loss=1.5,
        throughput=120.0,
        security_score=90.0
    )
    monitor.update_metrics(metrics)
    stability = monitor.calculate_stability()
    print(f"Metrics: latency={metrics.latency}ms, jitter={metrics.jitter}ms, "
          f"packet_loss={metrics.packet_loss}%, throughput={metrics.throughput}Mbps")
    print(f"Stability Score: {stability:.1f}%")
    print(f"Security Score: {metrics.security_score:.1f}")
    await monitor.monitor()
    
    # Scenario 2: High jitter and packet loss
    print("\n>>> Scenario 2: High Jitter and Packet Loss")
    print("-" * 60)
    metrics = NetworkMetrics(
        latency=65.0,
        jitter=25.0,  # High jitter
        packet_loss=8.0,  # High packet loss
        throughput=95.0,
        security_score=75.0
    )
    monitor.update_metrics(metrics)
    stability = monitor.calculate_stability()
    print(f"Metrics: latency={metrics.latency}ms, jitter={metrics.jitter}ms, "
          f"packet_loss={metrics.packet_loss}%, throughput={metrics.throughput}Mbps")
    print(f"Stability Score: {stability:.1f}%")
    print(f"Jitter deduction: {min(metrics.jitter * 2, 30):.1f} points")
    print(f"Packet loss deduction: {min(metrics.packet_loss * 10, 40):.1f} points")
    await monitor.monitor()
    
    # Scenario 3: Multiple anomalies detected
    print("\n>>> Scenario 3: Multiple Anomalies Detected")
    print("-" * 60)
    metrics = NetworkMetrics(
        latency=150.0,  # High latency
        jitter=30.0,    # High jitter
        packet_loss=10.0,  # High packet loss
        throughput=35.0,   # Low throughput
        security_score=55.0
    )
    monitor.update_metrics(metrics)
    stability = monitor.calculate_stability()
    print(f"Metrics: latency={metrics.latency}ms, jitter={metrics.jitter}ms, "
          f"packet_loss={metrics.packet_loss}%, throughput={metrics.throughput}Mbps")
    print(f"Stability Score: {stability:.1f}%")
    await monitor.monitor()
    
    # Scenario 4: Critical security level
    print("\n>>> Scenario 4: Critical Security Level")
    print("-" * 60)
    metrics = NetworkMetrics(
        latency=80.0,
        jitter=12.0,
        packet_loss=3.0,
        throughput=75.0,
        security_score=35.0  # Critical level
    )
    monitor.update_metrics(metrics)
    stability = monitor.calculate_stability()
    print(f"Metrics: latency={metrics.latency}ms, jitter={metrics.jitter}ms, "
          f"packet_loss={metrics.packet_loss}%, throughput={metrics.throughput}Mbps")
    print(f"Stability Score: {stability:.1f}%")
    print(f"Security Score: {metrics.security_score:.1f}")
    await monitor.monitor()
    
    # Scenario 5: Extreme conditions
    print("\n>>> Scenario 5: Extreme Conditions")
    print("-" * 60)
    metrics = NetworkMetrics(
        latency=200.0,
        jitter=50.0,  # Very high jitter (will be capped at 30 points deduction)
        packet_loss=15.0,  # Very high packet loss (will be capped at 40 points deduction)
        throughput=20.0,
        security_score=25.0
    )
    monitor.update_metrics(metrics)
    stability = monitor.calculate_stability()
    print(f"Metrics: latency={metrics.latency}ms, jitter={metrics.jitter}ms, "
          f"packet_loss={metrics.packet_loss}%, throughput={metrics.throughput}Mbps")
    print(f"Stability Score: {stability:.1f}%")
    print(f"Jitter deduction (capped): {min(metrics.jitter * 2, 30):.1f} points")
    print(f"Packet loss deduction (capped): {min(metrics.packet_loss * 10, 40):.1f} points")
    await monitor.monitor()


if __name__ == '__main__':
    asyncio.run(main())
