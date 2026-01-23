"""
Threat Detection Module - Intrusion Detection System
Real-time threat monitoring and detection for enterprise infrastructure
"""

import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

class IntrusionDetectionSystem:
    """IDS for monitoring and detecting security threats"""
    
    def __init__(self, connection_threshold=10000, baseline_multiplier=2.0):
        """
        Initialize IDS with configurable thresholds
        
        Args:
            connection_threshold: Default threshold for high connection volume
            baseline_multiplier: Multiplier for baseline-based anomaly detection
        """
        self.alerts = []
        self.threat_signatures = []
        self.monitoring_enabled = True
        self.connection_threshold = connection_threshold
        self.baseline_multiplier = baseline_multiplier
        self.traffic_baseline = None
        
    def configure_ids_rules(self):
        """
        Configure IDS rules for Starlink-enabled networks
        
        Includes rules specific to satellite connectivity patterns
        """
        rules = {
            'network_anomalies': {
                'unexpected_port_scanning': 'high',
                'unusual_traffic_patterns': 'medium',
                'bandwidth_anomalies': 'medium',  # Important for Starlink
                'connection_from_blacklisted_ip': 'critical'
            },
            'application_attacks': {
                'sql_injection_attempts': 'critical',
                'xss_attempts': 'high',
                'csrf_attempts': 'high',
                'ddos_patterns': 'critical'
            },
            'authentication_anomalies': {
                'brute_force_attempts': 'high',
                'credential_stuffing': 'high',
                'impossible_travel': 'critical',
                'multiple_failed_mfa': 'high'
            },
            'starlink_specific': {
                'satellite_handoff_anomalies': 'medium',
                'unexpected_latency_spikes': 'low',
                'beam_switching_irregularities': 'low'
            }
        }
        return rules
    
    def detect_anomaly(self, event_type, severity, description):
        """
        Detect and log security anomaly
        
        Args:
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            description: Event description
        """
        alert = {
            'timestamp': time.time(),
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'status': 'open'
        }
        self.alerts.append(alert)
        return alert
    
    def set_traffic_baseline(self, baseline_connections):
        """
        Set baseline for normal traffic patterns
        
        Args:
            baseline_connections: Expected normal connection count
            
        Note:
            This enables adaptive anomaly detection based on learned behavior
        """
        self.traffic_baseline = baseline_connections
        logger.info(
            "Traffic baseline established",
            extra={
                'baseline_connections': baseline_connections,
                'anomaly_threshold': baseline_connections * self.baseline_multiplier
            }
        )
    
    def analyze_traffic_patterns(self, traffic_data):
        """
        Analyze network traffic for suspicious patterns
        
        Args:
            traffic_data: Network traffic data to analyze
            
        Returns:
            Dictionary with analysis results including threat level
        """
        analysis = {
            'total_connections': len(traffic_data) if isinstance(traffic_data, list) else 0,
            'suspicious_patterns': [],
            'threat_level': 'low',
            'recommendations': []
        }
        
        # Use baseline-based detection if baseline is set
        if self.traffic_baseline is not None:
            threshold = self.traffic_baseline * self.baseline_multiplier
            if analysis['total_connections'] > threshold:
                analysis['suspicious_patterns'].append(
                    f'Traffic volume {analysis["total_connections"]} exceeds baseline threshold {threshold:.0f}'
                )
                analysis['threat_level'] = 'medium'
                analysis['recommendations'].append('Review traffic sources and patterns')
                logger.warning(
                    "Baseline-based anomaly detected",
                    extra={
                        'total_connections': analysis['total_connections'],
                        'baseline': self.traffic_baseline,
                        'threshold': threshold,
                        'multiplier': self.baseline_multiplier
                    }
                )
        else:
            # Fallback to configurable static threshold
            if analysis['total_connections'] > self.connection_threshold:
                analysis['suspicious_patterns'].append(
                    f'High connection volume: {analysis["total_connections"]} (threshold: {self.connection_threshold})'
                )
                analysis['threat_level'] = 'medium'
                analysis['recommendations'].append('Consider establishing traffic baseline for adaptive detection')
                logger.warning(
                    "Static threshold anomaly detected",
                    extra={
                        'total_connections': analysis['total_connections'],
                        'threshold': self.connection_threshold
                    }
                )
            
        return analysis
    
    def enable_behavioral_analysis(self):
        """
        Enable AI-powered behavioral analysis
        
        Detects zero-day threats through behavior patterns
        """
        return {
            'enabled': True,
            'ml_models': ['anomaly_detection', 'threat_classification'],
            'learning_mode': 'continuous',
            'baseline_period_days': 30,
            'confidence_threshold': 0.85
        }
    
    def get_threat_intelligence_feed(self):
        """
        Configure threat intelligence feeds
        
        Integrates with external threat databases
        """
        return {
            'feeds': [
                'cisa_known_exploited_vulnerabilities',
                'mitre_attack_framework',
                'commercial_threat_intelligence',
                'community_threat_sharing'
            ],
            'update_frequency': 'hourly',
            'auto_block_critical': True
        }
    
    def get_active_alerts(self, severity_filter=None):
        """
        Get active security alerts
        
        Args:
            severity_filter: Optional filter by severity level
        """
        if severity_filter:
            return [a for a in self.alerts if a['severity'] == severity_filter and a['status'] == 'open']
        return [a for a in self.alerts if a['status'] == 'open']
