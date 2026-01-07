"""
Example usage of Starlink Security Monitoring System
"""

from starlink_monitor import StarlinkMonitor


def main():
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


if __name__ == "__main__":
    main()
