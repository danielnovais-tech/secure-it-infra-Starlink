#!/usr/bin/env python3
"""
Example: Basic Security Monitoring for Starlink Infrastructure
Demonstrates network monitoring, logging, and alerting capabilities.
"""

from secure_it_starlink.network import NetworkMonitor
from secure_it_starlink.logging import SecurityLogger, AlertManager, AlertSeverity


def main():
    print("=" * 70)
    print("Secure IT Starlink - Basic Security Monitoring Example")
    print("=" * 70)
    print()

    # Initialize components
    print("Initializing security components...")
    monitor = NetworkMonitor({"alert_threshold": 0.8})
    logger = SecurityLogger()
    alert_manager = AlertManager()
    
    # Start monitoring
    print("\n1. Starting Network Monitoring")
    print("-" * 70)
    monitor.start_monitoring()
    logger.info("Network monitoring started", {"component": "NetworkMonitor"})
    
    # Check connection health
    print("\n2. Checking Connection Health")
    print("-" * 70)
    targets = ["8.8.8.8", "1.1.1.1"]
    
    for target in targets:
        health = monitor.check_connection_health(target)
        print(f"Target: {target}")
        print(f"  Status: {health['status']}")
        print(f"  Reachable: {health['reachable']}")
        if health.get('latency_ms'):
            print(f"  Latency: {health['latency_ms']}ms")
        print()
        
        # Log the health check
        if health['status'] == 'healthy':
            logger.info(f"Connection to {target} is healthy", health)
        else:
            logger.warning(f"Connection to {target} is unhealthy", health)
            # Create alert for unhealthy connection
            alert_manager.create_alert(
                AlertSeverity.MEDIUM,
                f"Unhealthy Connection to {target}",
                f"Connection health check failed for {target}",
                health
            )
    
    # Get and display statistics
    print("\n3. Connection Statistics")
    print("-" * 70)
    stats = monitor.get_connection_stats()
    print(f"Total checks: {stats['total_checks']}")
    print(f"Healthy checks: {stats['healthy_checks']}")
    print(f"Unhealthy checks: {stats['unhealthy_checks']}")
    print(f"Health ratio: {stats['health_ratio']:.2%}")
    
    # Display security logs
    print("\n4. Recent Security Logs")
    print("-" * 70)
    logs = logger.get_logs(limit=5)
    for log in logs:
        print(f"[{log['level']}] {log['message']}")
    
    # Display alerts
    print("\n5. Active Alerts")
    print("-" * 70)
    alerts = alert_manager.get_alerts(status="active")
    if alerts:
        for alert in alerts:
            print(f"Alert ID: {alert['alert_id']}")
            print(f"  Severity: {alert['severity']}")
            print(f"  Title: {alert['title']}")
            print(f"  Description: {alert['description']}")
            print()
    else:
        print("No active alerts")
    
    # Alert statistics
    print("\n6. Alert Statistics")
    print("-" * 70)
    alert_stats = alert_manager.get_alert_stats()
    print(f"Total alerts: {alert_stats['total_alerts']}")
    print(f"Active alerts: {alert_stats['active_alerts']}")
    print(f"Resolved alerts: {alert_stats['resolved_alerts']}")
    print("\nBy Severity:")
    for severity, count in alert_stats['by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    # Stop monitoring
    print("\n7. Stopping Monitoring")
    print("-" * 70)
    monitor.stop_monitoring()
    logger.info("Network monitoring stopped", {"component": "NetworkMonitor"})
    print("Monitoring stopped successfully")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
