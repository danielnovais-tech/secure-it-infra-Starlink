"""
Simple test script for the security monitoring loop.
Tests basic functionality without running indefinitely.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.security_monitor import SecurityMonitor
from datetime import datetime


async def test_monitoring_loop():
    """Test the monitoring loop with limited iterations."""
    print("Creating SecurityMonitor instance...")
    monitor = SecurityMonitor()
    
    # Test adding events
    print("Adding test events...")
    await monitor.add_event({
        'type': 'system_event',
        'message': 'Test system event',
        'timestamp': datetime.now().isoformat()
    })
    
    await monitor.add_event({
        'type': 'security_alert',
        'message': 'Test security alert',
        'timestamp': datetime.now().isoformat()
    })
    
    # Run a few iterations
    print("Running monitoring loop for 3 iterations...")
    monitor.running = True
    
    for i in range(3):
        print(f"\n--- Iteration {i+1} ---")
        await monitor._update_metrics()
        print(f"Metrics: {monitor.get_current_metrics()}")
        
        await monitor._check_security_status()
        print(f"Security Status: {monitor.get_security_status()}")
        
        await monitor._process_events()
        print(f"Event queue size: {monitor.event_queue.qsize()}")
        
        await asyncio.sleep(1)  # Shorter sleep for testing
    
    # Stop the monitor
    print("\nStopping monitor...")
    await monitor.stop()
    
    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_monitoring_loop())
