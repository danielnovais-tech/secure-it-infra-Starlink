#!/usr/bin/env python3
"""
Starlink Metrics CLI

Command-line interface for querying connection metrics, running diagnostics,
and generating reports.

Usage:
    starlink-cli status              - Show current connection status
    starlink-cli check               - Run diagnostics and show detailed metrics
    starlink-cli report              - Generate and display recent metrics report
    starlink-cli monitor             - Monitor connection in real-time
    starlink-cli export              - Export metrics to various formats
    starlink-cli config              - View or update configuration
"""

import argparse
import json
import sys
import time
from datetime import datetime

from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    QualityThresholds,
    StabilityThresholds,
    AlertThresholds,
)
from observability import MetricsExporter, PeriodicReporter


def get_current_metrics() -> ConnectionMetrics:
    """
    Get current connection metrics.
    
    In production, this would interface with actual network monitoring tools.
    For now, this is a placeholder that returns sample data.
    """
    # TODO: Implement actual metrics collection from system
    # This could integrate with:
    # - ping/traceroute utilities
    # - network interface statistics
    # - Starlink dish API
    print("Note: Using sample data. Implement actual metrics collection for production.", file=sys.stderr)
    return ConnectionMetrics(packet_loss=3.5, latency=95.0)


def cmd_status(args):
    """Display current connection status."""
    metrics = get_current_metrics()
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("=" * 60)
        print("STARLINK CONNECTION STATUS")
        print("=" * 60)
        print(f"Status:           {status['status']}")
        print(f"Service Level:    {status['service_level']}")
        print(f"Quality Score:    {status['quality_score']}/100")
        print(f"Stability Score:  {status['stability_score']:.3f}")
        print("\nMetrics:")
        print(f"  Packet Loss:    {status['packet_loss']}%")
        print(f"  Latency:        {status['latency']}ms")
        print("=" * 60)


def cmd_check(args):
    """Run comprehensive diagnostics."""
    print("Running connection diagnostics...\n")
    
    metrics = get_current_metrics()
    quality = StarlinkConnectionQuality(
        metrics,
        quality_thresholds=QualityThresholds(),
        stability_thresholds=StabilityThresholds(),
        alert_thresholds=AlertThresholds()
    )
    
    status = quality.get_connection_status()
    
    print("=" * 60)
    print("DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    # Connection metrics
    print("\n1. CONNECTION METRICS")
    print(f"   Packet Loss: {status['packet_loss']}%")
    if status['packet_loss'] > 5:
        print("   ⚠️  WARNING: Packet loss above threshold (>5%)")
    else:
        print("   ✅ Packet loss within acceptable range")
    
    print(f"\n   Latency: {status['latency']}ms")
    if status['latency'] > 150:
        print("   ⚠️  WARNING: High latency detected (>150ms)")
    else:
        print("   ✅ Latency within acceptable range")
    
    # Quality assessment
    print("\n2. QUALITY ASSESSMENT")
    print(f"   Quality Score: {status['quality_score']}/100")
    if status['quality_score'] >= 90:
        print("   ✅ Excellent connection quality")
    elif status['quality_score'] >= 75:
        print("   ✅ Good connection quality")
    elif status['quality_score'] >= 50:
        print("   ⚠️  Fair connection quality")
    else:
        print("   ❌ Poor connection quality")
    
    # Stability assessment
    print("\n3. STABILITY ASSESSMENT")
    print(f"   Stability Score: {status['stability_score']:.3f}")
    print(f"   Service Level: {status['service_level']}")
    
    if status['service_level'] == 'Stable':
        print("   ✅ Connection is stable")
    elif status['service_level'] == 'Degraded':
        print("   ⚠️  Connection is degraded")
    elif status['service_level'] == 'Critical':
        print("   ❌ Connection is critical")
    else:
        print("   ❌ Connection is offline")
    
    # Recommendations
    print("\n4. RECOMMENDATIONS")
    if status['packet_loss'] > 10:
        print("   • Check for physical obstructions to satellite dish")
        print("   • Verify dish alignment")
    if status['latency'] > 200:
        print("   • High latency detected - check for network congestion")
        print("   • Consider traffic prioritization")
    if status['service_level'] in ['Critical', 'Offline']:
        print("   • Immediate action required")
        print("   • Consider failover to backup connection")
    
    if status['quality_score'] >= 90 and status['stability_score'] >= 0.9:
        print("   ✅ No issues detected - connection is performing optimally")
    
    print("=" * 60)


def cmd_report(args):
    """Generate metrics report."""
    print(f"Generating metrics report for the last {args.hours} hour(s)...\n")
    
    reporter = PeriodicReporter()
    
    # Simulate collecting some metrics
    # In production, this would read from a time-series database
    for i in range(10):
        metrics = get_current_metrics()
        quality = StarlinkConnectionQuality(metrics)
        status = quality.get_connection_status()
        reporter.record_metrics(status)
    
    # Generate report
    sla_thresholds = {
        "quality_score": args.sla_quality,
        "stability_score": args.sla_stability
    }
    
    report = reporter.generate_report(sla_thresholds=sla_thresholds)
    
    if args.json:
        print(json.dumps(report, indent=2))
    elif args.export:
        filename = args.export
        reporter.export_report_json(report, filename)
        print(f"✅ Report exported to {filename}")
    else:
        print("=" * 60)
        print("METRICS REPORT")
        print("=" * 60)
        print(f"Period: Last {args.hours} hour(s)")
        print(f"Measurements: {report['total_measurements']}")
        print("\nQuality Metrics:")
        print(f"  Avg Quality Score: {report['summary']['quality_score']['avg']:.1f}/100")
        print(f"  Avg Stability: {report['summary']['stability_score']['avg']:.3f}")
        print(f"  Avg Packet Loss: {report['summary']['packet_loss']['avg']:.2f}%")
        print(f"  Avg Latency: {report['summary']['latency']['avg']:.1f}ms")
        
        print("\nService Level Distribution:")
        for level, count in report['service_level_distribution'].items():
            if count > 0:
                pct = (count / report['total_measurements']) * 100
                print(f"  {level}: {count} ({pct:.1f}%)")
        
        print(f"\nUptime: {report['uptime_percentage']:.2f}%")
        
        print("\nSLA Compliance:")
        for metric, compliance in report['sla_compliance'].items():
            icon = "✅" if compliance['compliant'] else "❌"
            print(f"  {icon} {metric}: {compliance['actual']:.2f} (threshold: {compliance['threshold']})")
        
        print("=" * 60)


def cmd_monitor(args):
    """Monitor connection in real-time."""
    print("Starting real-time monitoring (Press Ctrl+C to stop)...\n")
    print(f"{'Time':<12} {'Status':<12} {'Quality':<10} {'Stability':<12} {'Packet Loss':<12} {'Latency':<10}")
    print("-" * 80)
    
    try:
        while True:
            metrics = get_current_metrics()
            quality = StarlinkConnectionQuality(metrics)
            status = quality.get_connection_status()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{timestamp:<12} "
                  f"{status['status']:<12} "
                  f"{status['quality_score']:<10.0f} "
                  f"{status['stability_score']:<12.3f} "
                  f"{status['packet_loss']:<12.1f}% "
                  f"{status['latency']:<10.0f}ms")
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def cmd_export(args):
    """Export metrics to various formats."""
    metrics = get_current_metrics()
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    exporter = MetricsExporter()
    
    if args.format == 'prometheus':
        output = exporter.export_prometheus(status, labels={"instance": args.instance})
        print(output)
    
    elif args.format == 'cloudwatch':
        output = exporter.export_cloudwatch(status, namespace=args.namespace)
        print(json.dumps(output, indent=2, default=str))
    
    elif args.format == 'json':
        print(json.dumps(status, indent=2))
    
    else:
        print(f"Error: Unknown format '{args.format}'", file=sys.stderr)
        sys.exit(1)


def cmd_config(args):
    """View or update configuration."""
    if args.show:
        config = {
            "quality_thresholds": {
                "packet_loss_threshold": 5.0,
                "latency_threshold": 150.0,
                "packet_loss_penalty": 10,
                "latency_penalty": 5
            },
            "stability_thresholds": {
                "max_latency": 500.0,
                "packet_loss_weight": 0.7,
                "latency_weight": 0.3
            },
            "alert_thresholds": {
                "critical_stability": 0.3,
                "degraded_stability": 0.5,
                "stable_stability": 0.7
            }
        }
        print(json.dumps(config, indent=2))
    else:
        print("Configuration management not yet implemented.")
        print("Use --show to view current configuration.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Starlink Connection Metrics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  starlink-cli status                    # Show current status
  starlink-cli status --json             # Show status in JSON format
  starlink-cli check                     # Run diagnostics
  starlink-cli report --hours 24         # Generate 24-hour report
  starlink-cli monitor --interval 5      # Monitor every 5 seconds
  starlink-cli export --format prometheus # Export to Prometheus format
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current connection status')
    status_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    status_parser.set_defaults(func=cmd_status)
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Run comprehensive diagnostics')
    check_parser.set_defaults(func=cmd_check)
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate metrics report')
    report_parser.add_argument('--hours', type=int, default=24, help='Hours of history to include (default: 24)')
    report_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    report_parser.add_argument('--export', type=str, help='Export to file')
    report_parser.add_argument('--sla-quality', type=float, default=85.0, help='SLA quality threshold (default: 85.0)')
    report_parser.add_argument('--sla-stability', type=float, default=0.75, help='SLA stability threshold (default: 0.75)')
    report_parser.set_defaults(func=cmd_report)
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor connection in real-time')
    monitor_parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds (default: 5)')
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export metrics to various formats')
    export_parser.add_argument('--format', choices=['json', 'prometheus', 'cloudwatch'], default='json',
                               help='Export format (default: json)')
    export_parser.add_argument('--instance', default='default', help='Instance label for Prometheus')
    export_parser.add_argument('--namespace', default='Starlink/Metrics', help='CloudWatch namespace')
    export_parser.set_defaults(func=cmd_export)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='View or update configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.set_defaults(func=cmd_config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
