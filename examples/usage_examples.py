#!/usr/bin/env python3
"""
Example usage of Secure IT Starlink.

This script demonstrates how to use the various components of the
Secure IT Starlink system.
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from secure_it_starlink.config import ConfigurationManager
from secure_it_starlink.metrics import MetricsCollector
from secure_it_starlink.automated_responses import (
    AutomatedResponseCoordinator,
    SeverityLevel
)
from secure_it_starlink.logging import StructuredLogger


def example_configuration():
    """Example: Configuration Management with Deep Merging."""
    print("\n" + "="*60)
    print("Example 1: Configuration Management")
    print("="*60)
    
    # Load default configuration
    config = ConfigurationManager()
    print(f"✓ Loaded default configuration")
    print(f"  - Security weight: {config.get('metrics.security.weight')}")
    print(f"  - Collection interval: {config.get('metrics.collection.interval')}s")
    
    # Load and merge custom configuration
    config.load_and_merge('configs/development_config.yaml')
    print(f"\n✓ Merged with development configuration")
    print(f"  - New collection interval: {config.get('metrics.collection.interval')}s")
    print(f"  - Log level: {config.get('logging.structured.level')}")


def example_metrics():
    """Example: Comprehensive Metrics Collection."""
    print("\n" + "="*60)
    print("Example 2: Comprehensive Metrics Collection")
    print("="*60)
    
    # Initialize metrics collector
    config = ConfigurationManager()
    collector = MetricsCollector(config.get('metrics'))
    
    # Simulate collecting metrics over time
    print("\nCollecting metrics for 3 cycles...")
    
    for i in range(3):
        # Simulate real-world data
        security_data = {
            'firewall_status': 95.0 - i,
            'encryption_level': 90.0,
            'authentication_strength': 85.0 + i,
            'vulnerability_count': 92.0,
            'patch_level': 88.0
        }
        
        connection_data = {
            'uptime_percentage': 99.8 - (i * 0.1),
            'packet_loss': 0.1 + (i * 0.05),
            'latency': 25.0 + (i * 2),
            'signal_strength': 95.0 - i
        }
        
        performance_data = {
            'throughput_score': 85.0 - (i * 2),
            'bandwidth_utilization': 65.0 + (i * 5),
            'cpu_usage': 45.0 + (i * 3),
            'memory_usage': 60.0 + i,
            'disk_io_usage': 30.0
        }
        
        metrics = collector.collect_metrics(
            security_data=security_data,
            connection_data=connection_data,
            performance_data=performance_data
        )
        
        print(f"\nCycle {i+1}:")
        print(f"  Composite Score: {metrics['composite_score']:.2f}")
        print(f"  Security: {metrics['security']['score']:.2f} ({metrics['security']['level']})")
        print(f"  Connection: {metrics['connection']['score']:.2f} ({metrics['connection']['level']})")
        print(f"  Performance: {metrics['performance']['score']:.2f} ({metrics['performance']['level']})")
        
        time.sleep(0.5)
    
    # Get metrics summary
    summary = collector.get_metrics_summary(3600)
    print(f"\n✓ Metrics Summary:")
    print(f"  Sample count: {summary['sample_count']}")
    print(f"  Average composite score: {summary['averages']['composite_score']:.2f}")


def example_automated_responses():
    """Example: Automated Threat Response."""
    print("\n" + "="*60)
    print("Example 3: Automated Responses")
    print("="*60)
    
    config = ConfigurationManager()
    coordinator = AutomatedResponseCoordinator(config.get('automated_responses'))
    
    # Example 1: Security threat
    print("\n--- Scenario 1: Security Threat Detected ---")
    event = {
        'type': 'security_threat',
        'severity': 'high',
        'device_id': 'starlink-gateway-001',
        'source_ip': '192.168.1.100',
        'reason': 'Malware detected in network traffic',
        'context': {},
        'metrics': {}
    }
    
    actions = coordinator.process_event(event)
    print(f"✓ Event processed: {len(actions)} automated actions triggered")
    
    for action in actions:
        print(f"  - {action.action_type}: {action.target}")
        print(f"    Status: {action.status.value}")
        print(f"    Severity: {action.severity.value}")
    
    # Example 2: Policy violation
    print("\n--- Scenario 2: Policy Violation ---")
    event = {
        'type': 'policy_violation',
        'severity': 'medium',
        'context': {
            'bandwidth_usage': 95,  # Above threshold
            'failed_auth_attempts': 3
        },
        'metrics': {}
    }
    
    actions = coordinator.process_event(event)
    print(f"✓ Policy check completed: {len(actions)} enforcement actions")
    
    for action in actions:
        print(f"  - {action.action_type}: {action.target}")
    
    # Example 3: Connection failure requiring failover
    print("\n--- Scenario 3: Connection Failure (Failover) ---")
    event = {
        'type': 'connection_failure',
        'severity': 'critical',
        'context': {},
        'metrics': {
            'connection_down_time': 35,  # Exceeds threshold
            'performance_score': 45  # Below threshold
        }
    }
    
    actions = coordinator.process_event(event)
    print(f"✓ Failover evaluation: {len(actions)} failover actions")
    
    for action in actions:
        print(f"  - {action.action_type}")


def example_logging():
    """Example: Structured Logging and Event Correlation."""
    print("\n" + "="*60)
    print("Example 4: Structured Logging & Event Correlation")
    print("="*60)
    
    config = ConfigurationManager()
    logger = StructuredLogger(config.get('logging'))
    
    print("\n--- Standard Logging ---")
    logger.info("System initialized", component="main", status="ready")
    logger.warning("High bandwidth usage detected", usage_percent=92)
    logger.error("Authentication failed", user="admin", source_ip="192.168.1.50")
    
    print("\n--- Event Correlation: Brute Force Detection ---")
    print("Simulating multiple failed login attempts...")
    
    # Simulate brute force attack
    for i in range(5):
        logger.warning(
            f"Failed login attempt {i+1}",
            event_type='failed_login',
            source_ip='192.168.1.100',
            user_id='admin',
            attempt_number=i+1
        )
        time.sleep(0.1)
    
    # Check for correlated incidents
    incidents = logger.get_correlated_events(300)
    
    if incidents:
        print(f"\n✓ Detected {len(incidents)} correlated incident(s):")
        for incident in incidents:
            print(f"  - Type: {incident['incident_type']}")
            print(f"    Events: {incident['event_count']}")
            print(f"    Severity: {incident['severity']}")


def example_integration():
    """Example: Full System Integration."""
    print("\n" + "="*60)
    print("Example 5: Full System Integration")
    print("="*60)
    
    # Initialize all components
    config = ConfigurationManager()
    logger = StructuredLogger(config.get('logging'))
    metrics = MetricsCollector(config.get('metrics'))
    responses = AutomatedResponseCoordinator(config.get('automated_responses'))
    
    print("\n✓ All components initialized")
    
    # Simulate a monitoring cycle
    print("\n--- Monitoring Cycle ---")
    
    # Collect metrics
    metrics_data = metrics.collect_metrics(
        security_data={'firewall_status': 95, 'encryption_level': 90},
        connection_data={'uptime_percentage': 99.5, 'latency': 25},
        performance_data={'cpu_usage': 45, 'memory_usage': 60}
    )
    
    logger.info(
        "Metrics collected",
        composite_score=metrics_data['composite_score'],
        security_level=metrics_data['security']['level']
    )
    
    # Process an event
    event = {
        'type': 'metrics_update',
        'metrics': metrics_data,
        'context': {
            'security_score': metrics_data['security']['score'],
            'connection_score': metrics_data['connection']['score']
        }
    }
    
    actions = responses.process_event(event)
    
    logger.info(
        "Monitoring cycle complete",
        actions_triggered=len(actions),
        composite_score=metrics_data['composite_score']
    )
    
    print(f"\n✓ Monitoring cycle completed")
    print(f"  - Composite score: {metrics_data['composite_score']:.2f}")
    print(f"  - Actions triggered: {len(actions)}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("Secure IT Starlink - Usage Examples")
    print("="*60)
    
    try:
        example_configuration()
        example_metrics()
        example_automated_responses()
        example_logging()
        example_integration()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
