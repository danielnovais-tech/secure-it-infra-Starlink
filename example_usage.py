"""
Example usage of Starlink Security Monitoring System
"""

from starlink_monitor import StarlinkMonitor
from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    monitor_connection
)


def starlink_security_monitor_demo():
    """Demonstrate the usage of StarlinkMonitor."""
    
    print("=== Starlink Security Monitoring System Demo ===\n")
    
    # Initialize the monitor
    monitor = StarlinkMonitor()
    print("Monitor initialized with default metrics")
    print(f"Initial security score: {monitor.metrics.security_score}")
    print(f"Initial connection stability: {monitor.metrics.connection_stability}\n")
    
    # Scenario 1: Perfect conditions
    print("--- Scenario 1: Perfect Network Conditions ---")
    monitor.update_metrics(
        signal_quality=100.0,
        latency_ms=20.0,
        packet_loss_rate=0.0,
        uptime_percentage=100.0,
        failed_auth_attempts=0,
        encryption_strength=100.0
    )
    
    report = monitor.get_status_report()
    print(f"Security Score: {report['security_score']:.2f}")
    print(f"Connection Stability: {report['connection_stability']:.2f}")
    print()
    
    # Scenario 2: Typical good connection
    print("--- Scenario 2: Typical Good Connection ---")
    monitor.update_metrics(
        signal_quality=92.0,
        latency_ms=35.0,
        packet_loss_rate=0.5,
        uptime_percentage=99.0,
        failed_auth_attempts=1,
        encryption_strength=98.0
    )
    
    report = monitor.get_status_report()
    print(f"Security Score: {report['security_score']:.2f}")
    print(f"Connection Stability: {report['connection_stability']:.2f}")
    print(f"Signal Quality: {report['signal_quality']:.2f}%")
    print(f"Latency: {report['latency_ms']:.2f}ms")
    print(f"Packet Loss: {report['packet_loss_rate']:.2f}%")
    print()
    
    # Scenario 3: Degraded conditions
    print("--- Scenario 3: Degraded Network Conditions ---")
    monitor.update_metrics(
        signal_quality=75.0,
        latency_ms=120.0,
        packet_loss_rate=3.5,
        uptime_percentage=95.0,
        failed_auth_attempts=3,
        encryption_strength=85.0
    )
    
    report = monitor.get_status_report()
    print(f"Security Score: {report['security_score']:.2f}")
    print(f"Connection Stability: {report['connection_stability']:.2f}")
    print(f"Signal Quality: {report['signal_quality']:.2f}%")
    print(f"Latency: {report['latency_ms']:.2f}ms")
    print(f"Packet Loss: {report['packet_loss_rate']:.2f}%")
    print(f"Failed Auth Attempts: {report['failed_auth_attempts']}")
    print()
    
    # Scenario 4: Security incident
    print("--- Scenario 4: Security Incident (Multiple Failed Auth) ---")
    monitor.update_metrics(
        signal_quality=90.0,
        latency_ms=30.0,
        packet_loss_rate=0.8,
        uptime_percentage=99.5,
        failed_auth_attempts=10,
        encryption_strength=95.0
    )
    
    report = monitor.get_status_report()
    print(f"Security Score: {report['security_score']:.2f} (⚠️  Low due to failed auth)")
    print(f"Connection Stability: {report['connection_stability']:.2f}")
    print(f"Failed Auth Attempts: {report['failed_auth_attempts']}")
    print()
    
    print("=== Demo Complete ===")


def security_monitor_demo():
    """Backward-compatible alias for the StarlinkMonitor demo."""
    # Kept for compatibility if external code imports and calls this name.
    starlink_security_monitor_demo()


def _starlink_monitor_demo():
    """Demonstrate the usage of StarlinkMonitor."""
    # Backward-compatible name used by the connection metrics demo below.
    starlink_security_monitor_demo()

"""Example usage of the Starlink Connection Metrics module.

This script demonstrates how to use the metrics module to monitor
and evaluate Starlink connection quality.
"""


def main():
    """Demonstrate usage of the connection metrics module."""

    # Run the security monitoring demo first.
    _starlink_monitor_demo()
    
    print("=" * 60)
    print("Starlink Connection Quality Monitor - Examples")
    print("=" * 60)
    
    # Example 1: Excellent connection
    print("\n1. Excellent Connection:")
    print("-" * 40)
    status = monitor_connection(packet_loss=0.5, latency=25.0)
    print_status(status)
    
    # Example 2: Good connection
    print("\n2. Good Connection:")
    print("-" * 40)
    status = monitor_connection(packet_loss=3.0, latency=120.0)
    print_status(status)
    
    # Example 3: Fair connection (high packet loss)
    print("\n3. Fair Connection (High Packet Loss):")
    print("-" * 40)
    status = monitor_connection(packet_loss=8.0, latency=180.0)
    print_status(status)
    
    # Example 4: Poor connection
    print("\n4. Poor Connection:")
    print("-" * 40)
    status = monitor_connection(packet_loss=15.0, latency=350.0)
    print_status(status)
    
    # Example 5: Using the class directly
    print("\n5. Using StarlinkConnectionQuality class directly:")
    print("-" * 40)
    metrics = ConnectionMetrics(packet_loss=6.0, latency=160.0)
    quality = StarlinkConnectionQuality(metrics)
    
    print(f"Packet Loss: {metrics.packet_loss}%")
    print(f"Latency: {metrics.latency}ms")
    print(f"Quality Score: {quality.calculate_quality_score():.1f}/100")
    print(f"Stability Score: {quality.calculate_stability_score():.3f}")
    
    status = quality.get_connection_status()
    print(f"Overall Status: {status['status']}")
    
    print("\n" + "=" * 60)


def print_status(status: dict):
    """Print connection status in a formatted way."""
    print(f"Status: {status['status']}")
    print(f"Packet Loss: {status['packet_loss']}%")
    print(f"Latency: {status['latency']}ms")
    print(f"Quality Score: {status['quality_score']:.1f}/100")
    print(f"Stability Score: {status['stability_score']:.3f}")


if __name__ == "__main__":
    main()
