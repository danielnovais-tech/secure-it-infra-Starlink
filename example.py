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
