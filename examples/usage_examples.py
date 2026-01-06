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
