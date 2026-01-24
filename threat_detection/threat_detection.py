"""
Main Threat Detection System
Orchestrates anomaly detection, brute-force detection, and threat intelligence updates
"""

import os
import yaml
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Any, Dict, List, Optional

from threat_detection.modules.anomaly_detector import AnomalyDetector
from threat_detection.modules.brute_force_detector import BruteForceDetector
from threat_detection.modules.threat_intelligence import ThreatIntelligenceUpdater


class ThreatDetectionSystem:
    """Main threat detection system coordinating all components"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize threat detection system
        
        Args:
            config_path: Path to YAML configuration file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                'config',
                'threat_rules.yaml'
            )
        
        self.config_path: str = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.anomaly_detector = None
        self.brute_force_detector = None
        self.threat_intelligence = None
        
        self._initialize_components()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If configuration file has invalid YAML
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            print(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            raise
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging with configuration
        
        Returns:
            Configured logger
        """
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('log_file', 'threat_detection/logs/threat_detection.log')
        max_bytes = log_config.get('max_bytes', 10485760)
        backup_count = log_config.get('backup_count', 5)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logger
        logger = logging.getLogger('ThreatDetection')
        logger.setLevel(getattr(logging, log_level))
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_components(self):
        """Initialize all detection components"""
        # Initialize anomaly detector
        anomaly_config = self.config.get('anomaly_detection', {})
        if anomaly_config.get('enabled', True):
            self.anomaly_detector = AnomalyDetector(anomaly_config)
            self.logger.info("Anomaly detector initialized")
        
        # Initialize brute-force detector
        brute_force_config = self.config.get('brute_force_detection', {})
        if brute_force_config.get('enabled', True):
            self.brute_force_detector = BruteForceDetector(brute_force_config)
            self.logger.info("Brute-force detector initialized")
        
        # Initialize threat intelligence updater
        threat_intel_config = self.config.get('threat_intelligence', {})
        if threat_intel_config.get('enabled', True):
            self.threat_intelligence = ThreatIntelligenceUpdater(threat_intel_config)
            self.logger.info("Threat intelligence updater initialized")
    
    def update_threat_intelligence(self):
        """Update threat intelligence feeds"""
        if self.threat_intelligence:
            self.logger.info("Updating threat intelligence feeds...")
            threat_ips = self.threat_intelligence.update_all_feeds()
            
            # Save to file
            blocked_ips_config = self.config.get('blocked_ips', {})
            storage_file = blocked_ips_config.get('storage_file', 'threat_detection/config/blocked_ips.txt')
            self.threat_intelligence.save_threat_ips(storage_file)
            
            return threat_ips
        return set()
    
    def analyze_event(self, event: Dict) -> List[Dict]:
        """
        Analyze a single event for threats
        
        Args:
            event: Event dictionary with type, ip_address, etc.
            
        Returns:
            List of detected threats
        """
        threats = []
        
        # Check anomaly detection
        if self.anomaly_detector:
            anomalies = self.anomaly_detector.analyze(event)
            threats.extend(anomalies)
            
            for anomaly in anomalies:
                self.logger.warning(f"Anomaly detected: {anomaly['description']}")
        
        # Check against threat intelligence
        if self.threat_intelligence:
            ip_address = event.get('ip_address', '')
            if ip_address and self.threat_intelligence.is_threat_ip(ip_address):
                threat = {
                    'type': 'known_threat_ip',
                    'ip_address': ip_address,
                    'description': f"IP {ip_address} is in threat intelligence feeds",
                    'timestamp': datetime.now().isoformat()
                }
                threats.append(threat)
                self.logger.warning(f"Known threat IP detected: {ip_address}")
        
        return threats
    
    def analyze_log_file(self, log_file_path: str) -> List[Dict]:
        """
        Analyze a log file for brute-force attacks
        
        Args:
            log_file_path: Path to log file
            
        Returns:
            List of detected brute-force attacks
        """
        if self.brute_force_detector:
            self.logger.info(f"Analyzing log file: {log_file_path}")
            detections = self.brute_force_detector.analyze_log_file(log_file_path)
            
            for detection in detections:
                self.logger.warning(
                    f"Brute-force attack detected: {detection['pattern_name']} "
                    f"from {detection['ip_address']} ({detection['attempt_count']} attempts)"
                )
            
            return detections
        return []
    
    def get_blocked_ips(self) -> List[str]:
        """
        Get list of IPs that should be blocked
        
        Returns:
            List of IP addresses to block
        """
        blocked_ips = set()
        
        # Add IPs from brute-force detection
        if self.brute_force_detector:
            brute_force_ips = self.brute_force_detector.get_blocked_ips()
            blocked_ips.update(brute_force_ips)
        
        # Add IPs from threat intelligence
        if self.threat_intelligence:
            threat_ips = self.threat_intelligence.get_threat_ips()
            blocked_ips.update(threat_ips)
        
        return list(blocked_ips)
    
    def run_continuous_monitoring(self, log_files: Optional[List[str]] = None, interval_seconds: int = 60):
        """
        Run continuous monitoring mode
        
        Args:
            log_files: List of log files to monitor
            interval_seconds: Interval between checks
        """
        import time
        from datetime import datetime
        
        self.logger.info("Starting continuous threat monitoring...")
        
        # Initial threat intelligence update
        self.update_threat_intelligence()
        last_threat_update = datetime.now()
        
        if log_files is None:
            log_files = []
        
        # Get update interval from config
        threat_intel_config = self.config.get('threat_intelligence', {})
        update_interval_hours = threat_intel_config.get('update_interval_hours', 6)
        
        try:
            while True:
                # Analyze log files
                for log_file in log_files:
                    if os.path.exists(log_file):
                        self.analyze_log_file(log_file)
                
                # Periodic threat intelligence update (only if interval has passed)
                now = datetime.now()
                hours_since_update = (now - last_threat_update).total_seconds() / 3600
                
                if hours_since_update >= update_interval_hours:
                    self.update_threat_intelligence()
                    last_threat_update = now
                
                # Get and log current blocked IPs
                blocked_ips = self.get_blocked_ips()
                self.logger.info(f"Currently blocking {len(blocked_ips)} IPs")
                
                # Wait for next interval
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Threat Detection System')
    parser.add_argument(
        '--config',
        default=None,
        help='Path to configuration file (default: config/threat_rules.yaml)'
    )
    parser.add_argument(
        '--update-feeds',
        action='store_true',
        help='Update threat intelligence feeds and exit'
    )
    parser.add_argument(
        '--analyze-log',
        help='Analyze a specific log file and exit'
    )
    parser.add_argument(
        '--monitor',
        nargs='*',
        help='Monitor specified log files continuously'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    system = ThreatDetectionSystem(config_path=args.config)
    
    # Handle different modes
    if args.update_feeds:
        system.update_threat_intelligence()
    elif args.analyze_log:
        detections = system.analyze_log_file(args.analyze_log)
        print(f"\nDetected {len(detections)} brute-force attacks")
        for detection in detections:
            print(f"  - {detection['pattern_name']}: {detection['ip_address']} "
                  f"({detection['attempt_count']} attempts)")
    elif args.monitor is not None:
        system.run_continuous_monitoring(log_files=args.monitor)
    else:
        print("No action specified. Use --help for usage information.")
        print("\nExample commands:")
        print("  Update threat feeds: python threat_detection.py --update-feeds")
        print("  Analyze a log file: python threat_detection.py --analyze-log /var/log/auth.log")
        print("  Monitor logs: python threat_detection.py --monitor /var/log/auth.log /var/log/syslog")


if __name__ == '__main__':
    main()
