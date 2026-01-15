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
