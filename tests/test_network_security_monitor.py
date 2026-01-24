"""
Tests for Network Security Monitor
"""

import asyncio
import sys
from pathlib import Path
import importlib.util

# Add src to path (runtime) and load the module explicitly (helps IDEs/linters too)
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_SRC_DIR))

_MODULE_PATH = _SRC_DIR / "network_security_monitor.py"
_spec = importlib.util.spec_from_file_location("network_security_monitor", _MODULE_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load network_security_monitor from {_MODULE_PATH}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

NetworkSecurityMonitor = _module.NetworkSecurityMonitor
NetworkMetrics = _module.NetworkMetrics


async def test_metrics_initialization():
    """Test that metrics are initialized correctly."""
    monitor = NetworkSecurityMonitor()
    assert monitor.metrics.latency == 0.0
    assert monitor.metrics.jitter == 0.0
    assert monitor.metrics.packet_loss == 0.0
    assert monitor.metrics.throughput == 0.0
    print("✓ Metrics initialization test passed")


async def test_update_metrics():
    """Test that metrics update correctly."""
    monitor = NetworkSecurityMonitor()
    await monitor._update_metrics()
    
    # Check that metrics are within expected ranges
    assert 20 <= monitor.metrics.latency <= 80
    assert 5 <= monitor.metrics.jitter <= 15
    assert 0.1 <= monitor.metrics.packet_loss <= 1.5
    assert 50 <= monitor.metrics.throughput <= 200
    print("✓ Metrics update test passed")


async def test_start_stop():
    """Test starting and stopping the monitor."""
    monitor = NetworkSecurityMonitor()
    
    # Start the monitor
    start_task = asyncio.create_task(monitor.start())
    
    # Wait a bit for modules to start
    await asyncio.sleep(0.5)
    
    # Verify modules are running
    assert len(monitor.modules) == 3
    assert "metrics_updater" in monitor.modules
    assert "security_scanner" in monitor.modules
    assert "alert_monitor" in monitor.modules
    
    # Stop the monitor
    await monitor.stop()
    
    # Wait for start task to complete
    try:
        await asyncio.wait_for(start_task, timeout=2.0)
    except asyncio.TimeoutError:
        pass
    
    print("✓ Start/stop test passed")


async def test_get_metrics():
    """Test getting current metrics."""
    monitor = NetworkSecurityMonitor()
    await monitor._update_metrics()
    
    metrics = monitor.get_metrics()
    assert isinstance(metrics, NetworkMetrics)
    assert metrics.latency > 0
    print("✓ Get metrics test passed")


async def run_tests():
    """Run all tests."""
    print("Running Network Security Monitor tests...\n")
    
    await test_metrics_initialization()
    await test_update_metrics()
    await test_start_stop()
    await test_get_metrics()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests())
