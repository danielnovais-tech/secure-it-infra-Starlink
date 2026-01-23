"""
Enhanced examples demonstrating new features of the Starlink Connection Metrics module.

This script demonstrates:
1. Configurable thresholds
2. Alert integration
3. Service level mapping
4. Historical smoothing
"""

from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    QualityThresholds,
    StabilityThresholds,
    AlertThresholds
)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_configurable_thresholds():
    """Demonstrate configurable thresholds for different environments."""
    print_section("Example 1: Configurable Thresholds")
    
    metrics = ConnectionMetrics(packet_loss=7.0, latency=180.0)
    
    # Default thresholds
    print("\n1a. Default Thresholds:")
    quality_default = StarlinkConnectionQuality(metrics)
    status = quality_default.get_connection_status()
    print(f"  Packet Loss: {metrics.packet_loss}%")
    print(f"  Latency: {metrics.latency}ms")
    print(f"  Quality Score: {status['quality_score']}/100")
    print(f"  Service Level: {status['service_level']}")
    
    # Custom thresholds for more lenient environment
    print("\n1b. Lenient Thresholds (for remote/satellite environments):")
    lenient_quality = QualityThresholds(
        packet_loss_threshold=10.0,  # Allow up to 10% loss
        latency_threshold=250.0  # Allow up to 250ms latency
    )
    quality_lenient = StarlinkConnectionQuality(
        metrics,
        quality_thresholds=lenient_quality
    )
    status = quality_lenient.get_connection_status()
    print(f"  Quality Score: {status['quality_score']}/100 (vs {quality_default.calculate_quality_score()}/100 default)")
    print(f"  Service Level: {status['service_level']}")
    
    # Custom thresholds for strict environment
    print("\n1c. Strict Thresholds (for critical applications):")
    strict_quality = QualityThresholds(
        packet_loss_threshold=2.0,  # Very low tolerance
        packet_loss_penalty=20.0,  # Heavy penalty
        latency_threshold=100.0,  # Low latency required
        latency_penalty=10.0
    )
    quality_strict = StarlinkConnectionQuality(
        metrics,
        quality_thresholds=strict_quality
    )
    status = quality_strict.get_connection_status()
    print(f"  Quality Score: {status['quality_score']}/100 (vs {quality_default.calculate_quality_score()}/100 default)")
    print(f"  Service Level: {status['service_level']}")


def example_2_alert_integration():
    """Demonstrate alert callback integration for monitoring."""
    print_section("Example 2: Alert Integration")
    
    alerts_log = []
    
    def alert_handler(level, data):
        """Custom alert handler that logs alerts."""
        alerts_log.append({
            'level': level,
            'stability': data['stability'],
            'service_level': data['service_level'],
            'packet_loss': data['packet_loss'],
            'latency': data['latency']
        })
        print(f"\n  🚨 ALERT [{level.upper()}]: Stability={data['stability']:.3f}")
        print(f"     Service Level: {data['service_level']}")
        print(f"     Metrics: {data['packet_loss']}% loss, {data['latency']}ms latency")
    
    scenarios = [
        (2.0, 80.0, "Stable Connection"),
        (15.0, 250.0, "Degraded Connection"),
        (35.0, 420.0, "Critical Connection"),
    ]
    
    for packet_loss, latency, description in scenarios:
        print(f"\n{description}:")
        metrics = ConnectionMetrics(packet_loss=packet_loss, latency=latency)
        quality = StarlinkConnectionQuality(
            metrics,
            alert_callback=alert_handler
        )
        status = quality.get_connection_status()
        
        if 'alert_level' not in status:
            print("  ✓ No alerts - Connection is stable")
        print(f"  Status: {status['status']}, Stability: {status['stability_score']:.3f}")
    
    print(f"\n  Total alerts triggered: {len(alerts_log)}")


def example_3_service_levels():
    """Demonstrate service level classification and governance."""
    print_section("Example 3: Service Level Mapping")
    
    print("\nService Level Thresholds:")
    print("  - STABLE:   Stability >= 0.7")
    print("  - DEGRADED: Stability >= 0.5")
    print("  - CRITICAL: Stability >= 0.3")
    print("  - OFFLINE:  Stability < 0.3")
    
    test_cases = [
        (1.0, 30.0),
        (8.0, 150.0),
        (18.0, 300.0),
        (30.0, 400.0),
        (55.0, 550.0)
    ]
    
    print("\nConnection Quality Assessment:")
    print("-" * 70)
    print(f"{'PL%':<6} {'Lat(ms)':<9} {'Stability':<12} {'Service Level':<15} {'Status'}")
    print("-" * 70)
    
    for packet_loss, latency in test_cases:
        metrics = ConnectionMetrics(packet_loss=packet_loss, latency=latency)
        quality = StarlinkConnectionQuality(metrics)
        status = quality.get_connection_status()
        
        print(f"{packet_loss:<6.1f} {latency:<9.0f} {status['stability_score']:<12.3f} "
              f"{status['service_level']:<15} {status['status']}")


def example_4_historical_smoothing():
    """Demonstrate historical smoothing to reduce false positives."""
    print_section("Example 4: Historical Smoothing")
    
    print("\nSimulating connection metrics over time with a momentary spike...")
    
    # Create quality monitor with 5-point smoothing window
    quality = StarlinkConnectionQuality(
        ConnectionMetrics(packet_loss=3.0, latency=90.0),
        history_window_size=5
    )
    
    # Simulate metrics over time
    time_series = [
        (3.0, 90.0, "Normal"),
        (4.0, 95.0, "Normal"),
        (3.5, 88.0, "Normal"),
        (18.0, 280.0, "SPIKE!"),  # Momentary spike
        (3.0, 92.0, "Normal"),
        (3.5, 90.0, "Normal"),
    ]
    
    print(f"\n{'Time':<6} {'PL%':<7} {'Lat(ms)':<9} {'Raw Stab':<11} {'Smoothed':<11} {'Note'}")
    print("-" * 70)
    
    for i, (pl, lat, note) in enumerate(time_series):
        quality.metrics = ConnectionMetrics(packet_loss=pl, latency=lat)
        raw_stability = quality.calculate_stability_score(use_smoothing=False)
        smoothed_stability = quality.calculate_stability_score(use_smoothing=True)
        
        marker = " ⚠️ " if "SPIKE" in note else "   "
        print(f"{i+1:<6} {pl:<7.1f} {lat:<9.0f} {raw_stability:<11.3f} "
              f"{smoothed_stability:<11.3f} {marker}{note}")
    
    print("\nNote: Smoothing reduces the impact of momentary spikes,")
    print("      preventing false alarms from temporary fluctuations.")


def example_5_dynamic_scaling():
    """Demonstrate custom stability calculation for different environments."""
    print_section("Example 5: Dynamic Scaling")
    
    metrics = ConnectionMetrics(packet_loss=8.0, latency=200.0)
    
    # Default (satellite-optimized): 500ms ceiling
    print("\n5a. Default (Satellite Environment):")
    default_stability = StabilityThresholds(max_latency=500.0)
    quality_default = StarlinkConnectionQuality(
        metrics,
        stability_thresholds=default_stability
    )
    print("  Max Latency Threshold: 500ms")
    print(f"  Stability Score: {quality_default.calculate_stability_score():.3f}")
    
    # Fiber-optimized: lower latency expectations
    print("\n5b. Fiber Environment (Lower Latency Expected):")
    fiber_stability = StabilityThresholds(
        max_latency=100.0,  # Fiber has much lower latency
        packet_loss_weight=0.6,
        latency_weight=0.4  # Latency more important for fiber
    )
    quality_fiber = StarlinkConnectionQuality(
        metrics,
        stability_thresholds=fiber_stability
    )
    print("  Max Latency Threshold: 100ms")
    print(f"  Stability Score: {quality_fiber.calculate_stability_score():.3f}")
    print("  (Lower score reflects that 200ms is poor for fiber)")
    
    # Long-distance satellite: higher latency tolerance
    print("\n5c. Long-Distance Satellite:")
    satellite_stability = StabilityThresholds(
        max_latency=800.0,  # Higher tolerance
        packet_loss_weight=0.8,  # Even more weight on packet loss
        latency_weight=0.2
    )
    quality_satellite = StarlinkConnectionQuality(
        metrics,
        stability_thresholds=satellite_stability
    )
    print("  Max Latency Threshold: 800ms")
    print(f"  Stability Score: {quality_satellite.calculate_stability_score():.3f}")
    print("  (Higher score reflects that 200ms is acceptable)")


def example_6_complete_monitoring_solution():
    """Demonstrate a complete monitoring solution combining all features."""
    print_section("Example 6: Complete Monitoring Solution")
    
    print("\nSetting up comprehensive monitoring with:")
    print("  - Custom thresholds for satellite environment")
    print("  - Alert integration")
    print("  - Service level tracking")
    print("  - 10-point smoothing window")
    
    def monitoring_alert_handler(level, data):
        print(f"\n  📊 Monitoring Alert [{level.upper()}]")
        print(f"     Service Level: {data['service_level']}")
        print(f"     Stability: {data['stability']:.3f}")
        print("     Recommendation: ", end="")
        if level == "critical":
            print("Immediate attention required - Consider failover")
        else:
            print("Monitor closely - May need intervention")
    
    # Configure for satellite environment
    quality = StarlinkConnectionQuality(
        ConnectionMetrics(packet_loss=12.0, latency=220.0),
        quality_thresholds=QualityThresholds(
            packet_loss_threshold=8.0,
            latency_threshold=200.0
        ),
        stability_thresholds=StabilityThresholds(
            max_latency=600.0
        ),
        alert_thresholds=AlertThresholds(
            critical_stability=0.4,
            degraded_stability=0.6,
            stable_stability=0.8
        ),
        alert_callback=monitoring_alert_handler,
        history_window_size=10
    )
    
    status = quality.get_connection_status()
    
    print("\nCurrent Status Report:")
    print(f"  Connection Status: {status['status']}")
    print(f"  Service Level: {status['service_level']}")
    print(f"  Quality Score: {status['quality_score']}/100")
    print(f"  Stability Score: {status['stability_score']:.3f}")
    print(f"  Packet Loss: {status['packet_loss']}%")
    print(f"  Latency: {status['latency']}ms")
    if 'stability_history_size' in status:
        print(f"  History Buffer: {status['stability_history_size']} measurements")


def main():
    """Run all examples."""
    print("\n" + "🛰️ " * 25)
    print("STARLINK CONNECTION METRICS - ENHANCED FEATURES DEMONSTRATION")
    print("🛰️ " * 25)
    
    example_1_configurable_thresholds()
    example_2_alert_integration()
    example_3_service_levels()
    example_4_historical_smoothing()
    example_5_dynamic_scaling()
    example_6_complete_monitoring_solution()
    
    print("\n" + "=" * 70)
    print("  All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
