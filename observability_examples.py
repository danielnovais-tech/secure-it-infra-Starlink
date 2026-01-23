"""
Observability and Integration Examples

This script demonstrates observability features including:
- Prometheus metrics export
- CloudWatch metrics export  
- Structured JSON logging for SIEM integration
- Periodic reporting for governance
- Integration with alert callbacks
"""

from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    AlertThresholds
)
from observability import (
    MetricsExporter,
    StructuredLogger,
    PeriodicReporter
)


def example_prometheus_export():
    """Demonstrate Prometheus metrics export."""
    print("=" * 70)
    print("PROMETHEUS METRICS EXPORT")
    print("=" * 70)
    
    # Create connection status
    metrics = ConnectionMetrics(packet_loss=5.5, latency=135.0)
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    # Export to Prometheus format
    exporter = MetricsExporter()
    prometheus_metrics = exporter.export_prometheus(
        status,
        labels={"datacenter": "us-west-1", "satellite": "starlink-42"}
    )
    
    print("\nPrometheus Format Output:")
    print(prometheus_metrics)
    print("\nThese metrics can be scraped by Prometheus for monitoring dashboards.")


def example_cloudwatch_export():
    """Demonstrate CloudWatch metrics export."""
    print("\n" + "=" * 70)
    print("CLOUDWATCH METRICS EXPORT")
    print("=" * 70)
    
    # Create connection status
    metrics = ConnectionMetrics(packet_loss=8.0, latency=175.0)
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    # Export to CloudWatch format
    exporter = MetricsExporter()
    cloudwatch_data = exporter.export_cloudwatch(
        status,
        namespace="Production/Starlink"
    )
    
    print("\nCloudWatch Format Output:")
    print(f"Namespace: {cloudwatch_data['Namespace']}")
    print(f"Metrics Count: {len(cloudwatch_data['MetricData'])}")
    for metric in cloudwatch_data['MetricData']:
        print(f"  - {metric['MetricName']}: {metric['Value']} {metric['Unit']}")
    
    print("\nThis data can be sent to AWS CloudWatch using boto3:")
    print("  cloudwatch.put_metric_data(**cloudwatch_data)")


def example_structured_logging():
    """Demonstrate structured logging for SIEM integration."""
    print("\n" + "=" * 70)
    print("STRUCTURED LOGGING FOR SIEM")
    print("=" * 70)
    
    # Setup logger
    logger = StructuredLogger("production_starlink")
    
    # Create quality monitor with alert callback that logs
    def logging_alert_handler(level, data):
        logger.log_alert(level, data)
    
    quality = StarlinkConnectionQuality(
        ConnectionMetrics(packet_loss=28.0, latency=390.0),
        alert_callback=logging_alert_handler
    )
    
    print("\nTriggering connection monitoring with alerts...")
    status = quality.get_connection_status()
    
    print("\nAlerts are logged in JSON format for SIEM integration.")
    print("Log entries include: timestamp, event_type, severity, metrics")
    
    # Log a status change
    logger.log_status_change("Good", "Poor", status)
    print("\nStatus changes are also logged for audit trails.")
    
    # Log current metrics
    logger.log_metrics(status)
    print("\nMetrics snapshots can be logged periodically for analysis.")


def example_periodic_reporting():
    """Demonstrate periodic reporting for governance."""
    print("\n" + "=" * 70)
    print("PERIODIC REPORTING FOR GOVERNANCE")
    print("=" * 70)
    
    # Create reporter
    reporter = PeriodicReporter()
    
    # Simulate collecting metrics over time
    print("\nSimulating metric collection over 24 hours...")
    
    # Hour 0-8: Stable
    for _ in range(8):
        reporter.record_metrics({
            "quality_score": 95.0,
            "stability_score": 0.90,
            "packet_loss": 2.0,
            "latency": 85.0,
            "service_level": "Stable",
            "status": "Excellent"
        })
    
    # Hour 9-10: Degraded
    for _ in range(2):
        reporter.record_metrics({
            "quality_score": 75.0,
            "stability_score": 0.60,
            "packet_loss": 12.0,
            "latency": 220.0,
            "service_level": "Degraded",
            "status": "Fair"
        })
    
    # Hour 11-23: Stable again
    for _ in range(13):
        reporter.record_metrics({
            "quality_score": 92.0,
            "stability_score": 0.88,
            "packet_loss": 3.0,
            "latency": 95.0,
            "service_level": "Stable",
            "status": "Good"
        })
    
    # Generate report with SLA thresholds
    sla_thresholds = {
        "quality_score": 85.0,  # Require 85+ quality
        "stability_score": 0.75  # Require 0.75+ stability
    }
    
    report = reporter.generate_report(sla_thresholds=sla_thresholds)
    
    print("\nReport Summary:")
    print(f"  Period: {report['period_start']} to {report['period_end']}")
    print(f"  Total Measurements: {report['total_measurements']}")
    print("\nQuality Metrics:")
    print(f"  Average Quality Score: {report['summary']['quality_score']['avg']:.1f}/100")
    print(f"  Average Stability Score: {report['summary']['stability_score']['avg']:.3f}")
    print(f"  Average Packet Loss: {report['summary']['packet_loss']['avg']:.1f}%")
    print(f"  Average Latency: {report['summary']['latency']['avg']:.1f}ms")
    
    print("\nService Level Distribution:")
    for level, count in report['service_level_distribution'].items():
        if count > 0:
            percentage = (count / report['total_measurements']) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")
    
    print(f"\nUptime: {report['uptime_percentage']:.1f}%")
    
    print("\nSLA Compliance:")
    for metric, compliance in report['sla_compliance'].items():
        status_icon = "✓" if compliance['compliant'] else "✗"
        print(f"  {status_icon} {metric}: {compliance['actual']:.2f} (threshold: {compliance['threshold']})")
    
    # Export report
    report_filename = "/tmp/starlink_report.json"
    reporter.export_report_json(report, report_filename)
    print(f"\nReport exported to: {report_filename}")


def example_complete_monitoring_system():
    """Demonstrate a complete monitoring system with all features."""
    print("\n" + "=" * 70)
    print("COMPLETE MONITORING SYSTEM")
    print("=" * 70)
    
    # Setup components
    exporter = MetricsExporter()
    logger = StructuredLogger("production")
    reporter = PeriodicReporter()
    
    # Define comprehensive alert handler
    def comprehensive_alert_handler(level, data):
        # Log to SIEM
        logger.log_alert(level, data)
        
        # Print to console (in production, this might trigger notifications)
        severity = "🚨 CRITICAL" if level == "critical" else "⚠️  WARNING"
        print(f"\n{severity} Alert Triggered!")
        print(f"  Stability: {data['stability']:.3f}")
        print(f"  Service Level: {data['service_level']}")
        print(f"  Packet Loss: {data['packet_loss']}%")
        print(f"  Latency: {data['latency']}ms")
    
    # Create quality monitor
    quality = StarlinkConnectionQuality(
        ConnectionMetrics(packet_loss=5.0, latency=120.0),
        alert_callback=comprehensive_alert_handler,
        alert_thresholds=AlertThresholds(
            critical_stability=0.3,
            degraded_stability=0.5,
            stable_stability=0.7
        ),
        history_window_size=10
    )
    
    print("\nMonitoring connection...")
    
    # Simulate monitoring loop
    test_scenarios = [
        (3.0, 95.0, "Normal operation"),
        (5.0, 120.0, "Normal operation"),
        (25.0, 350.0, "Service degradation detected!"),
    ]
    
    for packet_loss, latency, description in test_scenarios:
        print(f"\n{description}")
        quality.metrics = ConnectionMetrics(packet_loss=packet_loss, latency=latency)
        status = quality.get_connection_status()
        
        # Record for reporting
        reporter.record_metrics(status)
        
        # Log metrics
        logger.log_metrics(status)
        
        # Export to Prometheus (would be scraped in production)
        exporter.export_prometheus(status, labels={"env": "prod"})
        
        print(f"  Quality: {status['quality_score']}/100")
        print(f"  Stability: {status['stability_score']:.3f}")
        print(f"  Service Level: {status['service_level']}")
    
    # Generate final report
    print("\n" + "-" * 70)
    report = reporter.generate_report()
    print("\nMonitoring Session Report:")
    print(f"  Measurements: {report['total_measurements']}")
    print(f"  Avg Quality: {report['summary']['quality_score']['avg']:.1f}/100")
    print(f"  Uptime: {report['uptime_percentage']:.1f}%")


def main():
    """Run all examples."""
    print("\n" + "🛰️ " * 25)
    print("STARLINK METRICS - OBSERVABILITY & INTEGRATION EXAMPLES")
    print("🛰️ " * 25 + "\n")
    
    example_prometheus_export()
    example_cloudwatch_export()
    example_structured_logging()
    example_periodic_reporting()
    example_complete_monitoring_system()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
