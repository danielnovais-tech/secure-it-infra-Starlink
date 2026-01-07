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
    asyncio.run(main())
