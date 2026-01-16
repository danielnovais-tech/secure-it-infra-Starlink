#!/usr/bin/env python3
"""
Demonstration script showing the Starlink monitor in action.
This creates a mock API server and runs the monitor for a few cycles.
"""
import sys
import os
import time
import signal
from unittest.mock import patch, Mock
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.starlink_api import StarlinkAPIClient
from src.metrics_collector import MetricsCollector

def create_mock_metrics(cycle: int):
    """Create mock metrics that change over time to demonstrate event detection."""
    base_latency = 45.0
    base_downlink = 150.0
    base_uplink = 25.0
    obstruction = 0.5  # Default obstruction value
    
    # Simulate different network conditions
    if cycle == 2:
        # High latency scenario
        latency = 120.0
        state = "CONNECTED"
    elif cycle == 3:
        # Low throughput scenario
        latency = 50.0
        base_downlink = 30.0  # Below threshold
        state = "CONNECTED"
    elif cycle == 4:
        # Obstruction scenario
        latency = 60.0
        base_downlink = 100.0
        obstruction = 8.0  # Above threshold
        state = "CONNECTED"
    elif cycle == 5:
        # State change
        state = "SEARCHING"
        latency = 0
        base_downlink = 0
        base_uplink = 0
    else:
        latency = base_latency
        state = "CONNECTED"
    
    return {
        'state': state,
        'uptime': 3600 * cycle,
        'popPingLatencyMs': latency,
        'downlinkThroughputBps': base_downlink * 1_000_000,
        'uplinkThroughputBps': base_uplink * 1_000_000,
        'obstructionStats': {
            'fractionObstructed': obstruction / 100,
            'avgProlongedObstructionDurationS': 2
        }
    }

def main():
    """Run the demonstration."""
    print("=" * 70)
    print("Starlink Monitor Demonstration")
    print("=" * 70)
    print("\nThis demo shows the monitor detecting various network events:")
    print("- Normal operation")
    print("- High latency detection")
    print("- Low throughput detection")
    print("- Obstruction detection")
    print("- State change detection")
    print("\n" + "=" * 70 + "\n")
    
    # Create components
    api_client = StarlinkAPIClient()
    metrics_collector = MetricsCollector()
    
    # Run for 6 cycles
    for cycle in range(1, 7):
        print(f"\n{'='*70}")
        print(f"Cycle {cycle} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 70)
        
        # Create mock response
        mock_data = create_mock_metrics(cycle)
        
        # Mock the API call
        with patch.object(api_client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Get status
            status = api_client.get_status()
            
            if status:
                # Update metrics
                metrics_collector.update_metrics(status)
                
                # Display current metrics
                print(f"\n📊 Current Metrics:")
                print(f"   State: {status.get('state', 'UNKNOWN')}")
                print(f"   Latency: {status.get('latency_ms', 0):.1f} ms")
                print(f"   Downlink: {status.get('downlink_mbps', 0):.1f} Mbps")
                print(f"   Uplink: {status.get('uplink_mbps', 0):.1f} Mbps")
                print(f"   Obstruction: {status.get('obstruction_percent', 0):.1f}%")
                print(f"   Uptime: {status.get('uptime', 0)} seconds")
                
                # Display recent events
                recent_events = metrics_collector.get_recent_events(5)
                if recent_events:
                    print(f"\n🚨 Events Detected:")
                    for event in recent_events[-3:]:  # Show last 3 events
                        severity_icon = "⚠️" if event['severity'] == 'WARNING' else "ℹ️"
                        print(f"   {severity_icon} [{event['type']}] {event['message']}")
        
        # Wait before next cycle (shortened for demo)
        if cycle < 6:
            time.sleep(1)
    
    # Show final summary
    print("\n" + "=" * 70)
    print("Final Summary")
    print("=" * 70)
    
    summary = metrics_collector.get_metrics_summary()
    print(f"\nTotal events detected: {summary['total_events']}")
    print(f"Total metrics collected: {summary['metrics_count']}")
    
    print("\n📋 All Events:")
    for i, event in enumerate(metrics_collector.events, 1):
        severity_icon = "⚠️" if event['severity'] == 'WARNING' else "ℹ️"
        print(f"{i}. {severity_icon} [{event['type']}] {event['message']}")
    
    print("\n" + "=" * 70)
    print("Demonstration Complete!")
    print("=" * 70)
    print("\nTo run the actual monitor with Starlink API:")
    print("  python3 run_monitor.py")
    print("  OR")
    print("  python3 -m src.starlink_monitor")
    print("\nConfiguration can be set via environment variables or .env file")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
