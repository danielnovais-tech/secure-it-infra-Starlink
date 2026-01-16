"""
Main Starlink monitoring application.
Implements a running instance with dynamic metrics updates based on network conditions.
Ensures Linux OS compatibility with proper signal handling.
"""
import sys
import signal
import time
import logging
import json
from datetime import datetime, timezone
from typing import Optional

from src.config import UPDATE_INTERVAL, LOG_DIR, DATA_DIR
from src.starlink_api import StarlinkAPIClient
from src.metrics_collector import MetricsCollector

# Configure logging only when run as a script
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_DIR / 'starlink_monitor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
logger = logging.getLogger(__name__)


class StarlinkMonitor:
    """Main monitoring application for Starlink network."""
    
    def __init__(self):
        """Initialize the Starlink monitor."""
        self.running = False
        self.api_client: Optional[StarlinkAPIClient] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        self.update_interval = UPDATE_INTERVAL
        
        # Setup signal handlers for graceful shutdown (Linux compatibility)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Starlink Monitor initialized")
    
    def _signal_handler(self, signum, frame):
        """
        Handle termination signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.info(f"Received signal {signal_name}, shutting down gracefully...")
        self.stop()
    
    def start(self):
        """Start the monitoring service."""
        logger.info("Starting Starlink monitoring service...")
        
        # Initialize components
        self.api_client = StarlinkAPIClient()
        self.metrics_collector = MetricsCollector()
        self.running = True
        
        logger.info(f"Monitoring started with {self.update_interval}s update interval")
        
        # Main monitoring loop
        try:
            while self.running:
                self._update_cycle()
                time.sleep(self.update_interval)
        except Exception as e:
            logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)
        finally:
            self._cleanup()
    
    def _update_cycle(self):
        """Perform a single update cycle: fetch metrics and detect events."""
        try:
            # Fetch current status from Starlink API
            status = self.api_client.get_status()
            
            if status:
                # Update metrics and detect events
                self.metrics_collector.update_metrics(status)
                
                # Log current status
                summary = self.metrics_collector.get_metrics_summary()
                logger.info(f"Status: {summary['status']}")
                
                # Save metrics to file
                self._save_metrics(summary)
            else:
                logger.warning("Failed to retrieve status from API")
        
        except Exception as e:
            logger.error(f"Error during update cycle: {e}", exc_info=True)
    
    def _save_metrics(self, summary: dict):
        """
        Save metrics summary to JSON file.
        
        Args:
            summary: Metrics summary dictionary
        """
        try:
            metrics_file = DATA_DIR / 'current_metrics.json'
            with open(metrics_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Also append to history file
            history_file = DATA_DIR / 'metrics_history.jsonl'
            with open(history_file, 'a') as f:
                json.dump({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metrics': summary['current_metrics']
                }, f)
                f.write('\n')
        
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def stop(self):
        """Stop the monitoring service."""
        logger.info("Stopping monitoring service...")
        self.running = False
    
    def _cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        
        if self.api_client:
            self.api_client.close()
        
        logger.info("Starlink Monitor stopped")
    
    def get_status(self) -> dict:
        """
        Get current monitoring status.
        
        Returns:
            Dictionary containing current status
        """
        if self.metrics_collector:
            return self.metrics_collector.get_metrics_summary()
        return {'status': 'not_started'}


def main():
    """Main entry point for the application."""
    logger.info("=" * 60)
    logger.info("Starlink Monitoring System")
    logger.info("=" * 60)
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Update interval: {UPDATE_INTERVAL} seconds")
    
    monitor = StarlinkMonitor()
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
