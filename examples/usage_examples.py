"""
Example usage of Starlink Security Infrastructure

This module demonstrates how to use the various components
of the security infrastructure for Starlink-connected remote locations.
"""

from starlink_security import (
    ConnectionMonitor,
    LatencyAwarePolicyManager,
    ConnectionResilience,
    RemoteManager,
    BandwidthOptimizer
)
from starlink_security.config import (
    create_default_config,
    create_remote_location_config,
    create_high_security_config
)
from starlink_security.connection_monitor import ConnectionQuality
from starlink_security.resilience import BackupConnection, ConnectionState
from starlink_security.remote_manager import AlertSeverity, ManagementMode, HealthStatus
from starlink_security.bandwidth_optimizer import Priority, QueuedOperation, CompressionLevel
from datetime import datetime


def basic_usage_example():
    """Basic usage example - monitoring and adaptive policies"""
    print("=== Basic Usage Example ===\n")
    
    # Initialize components
    monitor = ConnectionMonitor(check_interval=30)
    policy_manager = LatencyAwarePolicyManager()
    
    # Measure connection quality
    metrics = monitor.measure_connection()
    print(f"Connection Quality: {metrics.quality.value}")
    print(f"Latency: {metrics.latency_ms}ms")
    print(f"Packet Loss: {metrics.packet_loss_percent}%")
    print(f"Bandwidth: {metrics.bandwidth_mbps} Mbps\n")
    
    # Update security policy based on connection quality
    policy = policy_manager.update_policy(metrics)
    print(f"Security Level: {policy.level.value}")
    print(f"Encryption Enabled: {policy.encryption_enabled}")
    print(f"Full Packet Inspection: {policy.full_packet_inspection}")
    print(f"Log Verbosity: {policy.log_verbosity}")
    print(f"Bandwidth Limit: {policy.bandwidth_limit_percent}%\n")


def resilience_example():
    """Connection resilience with failover example"""
    print("=== Connection Resilience Example ===\n")
    
    # Initialize resilience manager
    resilience = ConnectionResilience(
        reconnect_attempts=5,
        reconnect_delay_seconds=10,
        failover_threshold_seconds=30.0
    )
    
    # Configure backup connections
    cellular_backup = BackupConnection(
        name="cellular_4g",
        priority=1,
        connection_type="cellular",
        enabled=True,
        max_bandwidth_mbps=25.0,
        latency_ms=80.0
    )
    
    satellite_backup = BackupConnection(
        name="secondary_satellite",
        priority=2,
        connection_type="satellite",
        enabled=True,
        max_bandwidth_mbps=50.0,
        latency_ms=600.0
    )
    
    resilience.add_backup_connection(cellular_backup)
    resilience.add_backup_connection(satellite_backup)
    
    print(f"Current State: {resilience.get_state().value}")
    print(f"Backup Connections Configured: {len(resilience.get_backup_connections())}")
    print(f"Using Backup: {resilience.is_using_backup()}")
    print(f"Uptime: {resilience.get_uptime_percentage():.2f}%\n")


def remote_management_example():
    """Remote management for unmanned locations example"""
    print("=== Remote Management Example ===\n")
    
    # Initialize remote manager in autonomous mode
    manager = RemoteManager(
        mode=ManagementMode.AUTONOMOUS,
        checkin_interval_minutes=60,
        autonomous_recovery=True
    )
    
    # Record system health
    health = HealthStatus(
        timestamp=datetime.now(),
        overall_health="healthy",
        cpu_usage_percent=45.2,
        memory_usage_percent=62.1,
        disk_usage_percent=38.5,
        connection_quality="good",
        uptime_hours=168.5,
        alerts_count=2
    )
    manager.record_health_status(health)
    
    # Create alerts
    manager.add_alert(
        severity=AlertSeverity.WARNING,
        component="connection_monitor",
        message="Latency spike detected: 150ms",
        auto_resolved=True
    )
    
    manager.add_alert(
        severity=AlertSeverity.INFO,
        component="bandwidth_optimizer",
        message="Cache hit rate: 85%",
        auto_resolved=True
    )
    
    # Queue remote commands
    manager.queue_command('update_config', {'log_level': 'info'})
    manager.queue_command('collect_diagnostics', {})
    
    # Perform check-in
    checkin_data = manager.perform_checkin()
    print(f"Check-in Mode: {checkin_data['mode']}")
    print(f"Total Alerts: {checkin_data['alerts_count']}")
    print(f"Critical Alerts: {checkin_data['critical_alerts']}")
    print(f"Pending Commands: {checkin_data['pending_commands']}\n")


def bandwidth_optimization_example():
    """Bandwidth optimization for satellite constraints example"""
    print("=== Bandwidth Optimization Example ===\n")
    
    # Initialize bandwidth optimizer
    optimizer = BandwidthOptimizer(
        bandwidth_limit_mbps=100.0,
        enable_compression=True,
        enable_caching=True,
        enable_deferred_ops=True
    )
    
    # Set compression level
    optimizer.set_compression_level(CompressionLevel.HIGH)
    print(f"Compression Ratio: {optimizer.get_compression_ratio()}")
    
    # Cache frequently accessed data
    optimizer.cache_response("security_rules_v1", {"rules": [1, 2, 3]}, ttl_seconds=3600)
    
    # Try to retrieve from cache
    cached_data = optimizer.get_cached_response("security_rules_v1")
    print(f"Cache Hit: {cached_data is not None}")
    print(f"Cache Hit Rate: {optimizer.get_cache_hit_rate():.2%}")
    
    # Queue non-critical operation
    operation = QueuedOperation(
        operation_id="log_upload_1",
        priority=Priority.LOW,
        estimated_bandwidth_mb=50.0,
        queued_at=datetime.now(),
        execute_after=None,
        operation_type="log_upload"
    )
    optimizer.queue_operation(operation)
    
    # Calculate bandwidth budget
    budget = optimizer.calculate_bandwidth_budget(total_bandwidth_mbps=150.0)
    print(f"\nBandwidth Budget:")
    print(f"  Security Operations: {budget.security_ops_mbps:.2f} Mbps")
    print(f"  Logging: {budget.logging_mbps:.2f} Mbps")
    print(f"  Updates: {budget.updates_mbps:.2f} Mbps")
    print(f"  Monitoring: {budget.monitoring_mbps:.2f} Mbps")
    
    # Get optimization summary
    summary = optimizer.get_optimization_summary()
    print(f"\nOptimization Summary:")
    print(f"  Queued Operations: {summary['queued_operations']}")
    print(f"  Compression Level: {summary['compression_level']}\n")


def integrated_example():
    """Integrated example showing all components working together"""
    print("=== Integrated System Example ===\n")
    
    # Load configuration for remote location
    config = create_remote_location_config()
    print(f"Configuration: Remote Location Profile")
    print(f"  Management Mode: {config.management_mode}")
    print(f"  Bandwidth Limit: {config.bandwidth_limit_mbps} Mbps")
    print(f"  Compression: {config.compression_level}")
    print(f"  Security Level: {config.default_security_level}\n")
    
    # Initialize all components with config
    monitor = ConnectionMonitor(
        check_interval=config.connection_check_interval,
        latency_threshold_excellent=config.latency_threshold_excellent,
        latency_threshold_good=config.latency_threshold_good,
        latency_threshold_fair=config.latency_threshold_fair,
        latency_threshold_poor=config.latency_threshold_poor
    )
    
    policy_manager = LatencyAwarePolicyManager()
    
    resilience = ConnectionResilience(
        reconnect_attempts=config.reconnect_attempts,
        reconnect_delay_seconds=config.reconnect_delay_seconds,
        failover_threshold_seconds=config.failover_threshold_seconds
    )
    
    optimizer = BandwidthOptimizer(
        bandwidth_limit_mbps=config.bandwidth_limit_mbps,
        enable_compression=config.enable_compression,
        enable_caching=config.enable_caching,
        enable_deferred_ops=config.enable_deferred_ops
    )
    
    manager = RemoteManager(
        mode=ManagementMode.AUTONOMOUS if config.management_mode == "autonomous" else ManagementMode.SUPERVISED,
        checkin_interval_minutes=config.checkin_interval_minutes,
        autonomous_recovery=config.autonomous_recovery
    )
    
    # Simulate operation cycle
    print("Simulating operation cycle...\n")
    
    # 1. Monitor connection
    metrics = monitor.measure_connection()
    print(f"1. Connection measured: {metrics.quality.value} ({metrics.latency_ms}ms)")
    
    # 2. Update policy based on connection
    policy = policy_manager.update_policy(metrics)
    print(f"2. Policy updated: {policy.level.value}")
    
    # 3. Adjust bandwidth optimizer
    bandwidth_allowance = policy_manager.get_bandwidth_allowance(metrics.bandwidth_mbps)
    print(f"3. Bandwidth allowance: {bandwidth_allowance:.2f} Mbps")
    
    # 4. Check connection stability
    stable = monitor.is_connection_stable(ConnectionQuality.FAIR)
    print(f"4. Connection stable: {stable}")
    
    # 5. Record health for remote management
    health = HealthStatus(
        timestamp=datetime.now(),
        overall_health="healthy" if stable else "degraded",
        cpu_usage_percent=50.0,
        memory_usage_percent=65.0,
        disk_usage_percent=40.0,
        connection_quality=metrics.quality.value,
        uptime_hours=24.0,
        alerts_count=0
    )
    manager.record_health_status(health)
    print(f"5. Health recorded: {health.overall_health}\n")
    
    print("System operating normally with adaptive security policies.")


if __name__ == "__main__":
    print("Starlink Security Infrastructure - Usage Examples")
    print("=" * 60 + "\n")
    
    basic_usage_example()
    print("\n" + "=" * 60 + "\n")
    
    resilience_example()
    print("\n" + "=" * 60 + "\n")
    
    remote_management_example()
    print("\n" + "=" * 60 + "\n")
    
    bandwidth_optimization_example()
    print("\n" + "=" * 60 + "\n")
    
    integrated_example()
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
