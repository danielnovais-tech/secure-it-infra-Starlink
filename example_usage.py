"""
Example usage of the Starlink Connection Metrics module.

This script demonstrates how to use the metrics module to monitor
and evaluate Starlink connection quality.
"""

from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    monitor_connection
)


def main():
    """Demonstrate usage of the connection metrics module."""
    
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
