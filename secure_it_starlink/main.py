#!/usr/bin/env python3
"""
Main application for Secure IT Starlink.

Enterprise-grade security and monitoring for Starlink infrastructure.
"""

import sys
import time
import signal
from typing import Dict, Any, Optional

from secure_it_starlink.config import ConfigurationManager
from secure_it_starlink.metrics import MetricsCollector
from secure_it_starlink.automated_responses import AutomatedResponseCoordinator
from secure_it_starlink.logging import StructuredLogger


class SecureITStarlink:
    """
    Main application class for Secure IT Starlink monitoring system.
    
    Integrates all components: configuration, metrics, automated responses,
    and structured logging.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Secure IT Starlink application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config_manager = ConfigurationManager(config_path)
        self.config = self.config_manager.get_all()
        
        # Initialize logging
        logging_config = self.config.get('logging', {})
        self.logger = StructuredLogger(logging_config)
        
        # Initialize metrics collector
        metrics_config = self.config.get('metrics', {})
        self.metrics_collector = MetricsCollector(metrics_config)
        
        # Initialize automated response coordinator
        responses_config = self.config.get('automated_responses', {})
        self.response_coordinator = AutomatedResponseCoordinator(responses_config)
        
        # Application state
        self.running = False
        
        self.logger.info("Secure IT Starlink initialized", 
                        version=self.config.get('application', {}).get('version', '1.0.0'))
    
    def start(self):
        """Start the monitoring system."""
        self.running = True
        self.logger.info("Starting Secure IT Starlink monitoring system")
        
        try:
            self._run_monitoring_loop()
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fatal error in monitoring loop: {str(e)}", 
                            error=str(e), error_type=type(e).__name__)
            self.stop()
            raise
    
    def _run_monitoring_loop(self):
        """Main monitoring loop."""
        collection_interval = self.config.get('metrics', {}).get('collection', {}).get('interval', 60)
        
        while self.running:
            try:
                # Collect metrics
                metrics = self._collect_current_metrics()
                
                self.logger.info("Metrics collected", 
                               composite_score=metrics.get('composite_score'),
                               security_level=metrics.get('security', {}).get('level'),
                               connection_level=metrics.get('connection', {}).get('level'),
                               performance_level=metrics.get('performance', {}).get('level'))
                
                # Check for automated response triggers
                self._check_response_triggers(metrics)
                
                # Sleep until next collection
                time.sleep(collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop iteration: {str(e)}",
                                error=str(e), error_type=type(e).__name__)
                time.sleep(5)  # Brief pause before retrying
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """
        Collect current metrics from all sources.
        
        Returns:
            Dictionary of collected metrics
        """
        # In a real implementation, these would be collected from actual sources
        # For now, we'll use simulated data
        
        security_data = {
            'firewall_status': 95.0,
            'encryption_level': 90.0,
            'authentication_strength': 85.0,
            'vulnerability_count': 92.0,
            'patch_level': 88.0
        }
        
        connection_data = {
            'uptime_percentage': 99.8,
            'packet_loss': 0.1,
            'latency': 25.0,
            'jitter': 2.0,
            'signal_strength': 95.0
        }
        
        performance_data = {
            'throughput_score': 85.0,
            'bandwidth_utilization': 65.0,
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'disk_io_usage': 30.0
        }
        
        # Collect metrics
        metrics = self.metrics_collector.collect_metrics(
            security_data=security_data,
            connection_data=connection_data,
            performance_data=performance_data
        )
        
        return metrics
    
    def _check_response_triggers(self, metrics: Dict[str, Any]):
        """
        Check if metrics trigger any automated responses.
        
        Args:
            metrics: Current metrics
        """
        # Create event from metrics
        event = {
            'type': 'metrics_update',
            'timestamp': time.time(),
            'metrics': metrics,
            'context': {
                'security_score': metrics.get('security', {}).get('score', 0),
                'connection_score': metrics.get('connection', {}).get('score', 0),
                'performance_score': metrics.get('performance', {}).get('score', 0)
            }
        }
        
        # Process event through response coordinator
        actions = self.response_coordinator.process_event(event)
        
        if actions:
            self.logger.warning(f"Automated responses triggered: {len(actions)} actions",
                              action_count=len(actions),
                              actions=[a.action_type for a in actions])
    
    def stop(self):
        """Stop the monitoring system."""
        self.running = False
        self.logger.info("Stopping Secure IT Starlink monitoring system")
        
        # Log final metrics summary
        summary = self.metrics_collector.get_metrics_summary(3600)
        if summary:
            self.logger.info("Final metrics summary", **summary)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            System status dictionary
        """
        latest_metrics = self.metrics_collector.get_latest_metrics()
        pending_actions = self.response_coordinator.get_pending_actions()
        
        return {
            'running': self.running,
            'latest_metrics': latest_metrics,
            'pending_actions_count': len(pending_actions),
            'pending_actions': [
                {
                    'type': action.action_type,
                    'target': action.target,
                    'status': action.status.value,
                    'severity': action.severity.value
                }
                for action in pending_actions
            ]
        }


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\nReceived signal to shutdown...")
    sys.exit(0)


def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Secure IT Starlink - Enterprise Security Monitoring')
    parser.add_argument('-c', '--config', help='Path to configuration file', default=None)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--status', action='store_true', help='Display system status')
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize application
    app = SecureITStarlink(config_path=args.config)
    
    if args.status:
        # Display status and exit
        status = app.get_status()
        print("\n=== Secure IT Starlink Status ===")
        print(f"Running: {status['running']}")
        print(f"Pending Actions: {status['pending_actions_count']}")
        if status['latest_metrics']:
            print(f"Composite Score: {status['latest_metrics'].get('composite_score', 'N/A')}")
        print("=================================\n")
    else:
        # Start monitoring
        app.start()


if __name__ == '__main__':
    main()
