"""
Network Security Monitor for Starlink Infrastructure
Monitors network and security metrics for managed enterprise infrastructures.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple
import random


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class NetworkMetrics:
    """Network and security metrics."""
    latency: float = 0.0  # ms
    jitter: float = 0.0  # ms
    packet_loss: float = 0.0  # percentage
    throughput: float = 0.0  # Mbps


class NetworkSecurityMonitor:
    """Monitor network and security metrics for Starlink infrastructure."""
    
    def __init__(self):
        self.metrics = NetworkMetrics()
        self.running = False
        self.modules: Dict[str, asyncio.Task] = {}
        
    async def start(self):
        """Start the monitoring system."""
        logger.info("Starting Network Security Monitor")
        self.running = True
        
        # Start monitoring modules
        tasks = [
            ("metrics_updater", self._metrics_updater_loop()),
            ("security_scanner", self._security_scanner_loop()),
            ("alert_monitor", self._alert_monitor_loop()),
        ]
        
        for name, coro in tasks:
            self.modules[name] = asyncio.create_task(coro)
            logger.info(f"Started module: {name}")
        
        # Wait for all modules to complete (or until stopped)
        try:
            await asyncio.gather(*self.modules.values())
        except asyncio.CancelledError:
            logger.info("Monitor received cancellation signal")
            
    async def stop(self):
        """Stop the monitoring system."""
        logger.info("Stopping Network Security Monitor")
        self.running = False
        
        # Cancel all module tasks
        tasks: List[Tuple[str, asyncio.Task]] = []
        for name, task in self.modules.items():
            logger.info(f"Stopping module: {name}")
            task.cancel()
            tasks.append((name, task))
        
        # Wait for modules to shut down
        for name, task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                # Expected when cancelling tasks
                logger.debug(f"Module {name} cancelled successfully")
            except Exception as e:
                logger.error(f"Error stopping module {name}: {e}")
    
    async def _update_metrics(self):
        """Update network and security metrics."""
        try:
            # Simulate metric collection (in production, would use actual monitoring)
            self.metrics.latency = random.uniform(20, 80)
            self.metrics.jitter = random.uniform(5, 15)
            self.metrics.packet_loss = random.uniform(0.1, 1.5)
            self.metrics.throughput = random.uniform(50, 200)
            
            logger.debug(
                f"Metrics updated - Latency: {self.metrics.latency:.2f}ms, "
                f"Jitter: {self.metrics.jitter:.2f}ms, "
                f"Packet Loss: {self.metrics.packet_loss:.2f}%, "
                f"Throughput: {self.metrics.throughput:.2f}Mbps"
            )
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def _metrics_updater_loop(self):
        """Continuously update metrics."""
        logger.info("Metrics updater started")
        try:
            while self.running:
                await self._update_metrics()
                await asyncio.sleep(5)  # Update every 5 seconds
        except asyncio.CancelledError:
            logger.info("Metrics updater cancelled")
            raise
    
    async def _security_scanner_loop(self):
        """Scan for security threats."""
        logger.info("Security scanner started")
        try:
            while self.running:
                # Simulate security scanning
                await asyncio.sleep(10)
                logger.debug("Security scan completed")
        except asyncio.CancelledError:
            logger.info("Security scanner cancelled")
            raise
    
    async def _alert_monitor_loop(self):
        """Monitor for alerts and anomalies."""
        logger.info("Alert monitor started")
        try:
            while self.running:
                # Check for anomalies in metrics
                if self.metrics.latency > 70:
                    logger.warning(f"High latency detected: {self.metrics.latency:.2f}ms")
                if self.metrics.packet_loss > 1.0:
                    logger.warning(f"High packet loss detected: {self.metrics.packet_loss:.2f}%")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("Alert monitor cancelled")
            raise
    
    def get_metrics(self) -> NetworkMetrics:
        """Get current metrics."""
        return self.metrics


async def main():
    """Main entry point."""
    monitor = NetworkSecurityMonitor()
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await monitor.stop()
        logger.info("Network Security Monitor stopped")


if __name__ == "__main__":
    asyncio.run(main())
