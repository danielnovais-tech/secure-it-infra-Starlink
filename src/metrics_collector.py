"""
Metrics collector and event detector for Starlink monitoring.
Dynamically updates metrics based on network conditions and detected events.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from src.config import (
    LATENCY_THRESHOLD,
    DOWNLINK_THRESHOLD,
    UPLINK_THRESHOLD,
    OBSTRUCTION_THRESHOLD
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and analyzes Starlink metrics, detecting network events."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.current_metrics: Optional[Dict[str, Any]] = None
        self.previous_metrics: Optional[Dict[str, Any]] = None
        self.events: List[Dict[str, Any]] = []
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update current metrics and detect events.
        
        Args:
            metrics: New metrics data from API
        """
        self.previous_metrics = self.current_metrics
        self.current_metrics = metrics
        
        # Add to history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        
        # Detect events based on metrics
        self._detect_events()
    
    def _detect_events(self):
        """Detect network events based on current metrics and thresholds."""
        if not self.current_metrics:
            return
        
        events_detected = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # High latency event
        latency = self.current_metrics.get('latency_ms', 0)
        if latency > LATENCY_THRESHOLD:
            event = {
                'timestamp': timestamp,
                'type': 'HIGH_LATENCY',
                'severity': 'WARNING',
                'message': f'High latency detected: {latency:.2f}ms (threshold: {LATENCY_THRESHOLD}ms)',
                'metrics': {'latency_ms': latency}
            }
            events_detected.append(event)
            logger.warning(event['message'])
        
        # Low downlink throughput event
        downlink = self.current_metrics.get('downlink_mbps', 0)
        if downlink < DOWNLINK_THRESHOLD and downlink > 0:
            event = {
                'timestamp': timestamp,
                'type': 'LOW_DOWNLINK',
                'severity': 'WARNING',
                'message': f'Low downlink throughput: {downlink:.2f}Mbps (threshold: {DOWNLINK_THRESHOLD}Mbps)',
                'metrics': {'downlink_mbps': downlink}
            }
            events_detected.append(event)
            logger.warning(event['message'])
        
        # Low uplink throughput event
        uplink = self.current_metrics.get('uplink_mbps', 0)
        if uplink < UPLINK_THRESHOLD and uplink > 0:
            event = {
                'timestamp': timestamp,
                'type': 'LOW_UPLINK',
                'severity': 'WARNING',
                'message': f'Low uplink throughput: {uplink:.2f}Mbps (threshold: {UPLINK_THRESHOLD}Mbps)',
                'metrics': {'uplink_mbps': uplink}
            }
            events_detected.append(event)
            logger.warning(event['message'])
        
        # Obstruction event
        obstruction = self.current_metrics.get('obstruction_percent', 0)
        if obstruction > OBSTRUCTION_THRESHOLD:
            event = {
                'timestamp': timestamp,
                'type': 'OBSTRUCTION_DETECTED',
                'severity': 'WARNING',
                'message': f'Obstruction detected: {obstruction:.2f}% (threshold: {OBSTRUCTION_THRESHOLD}%)',
                'metrics': {'obstruction_percent': obstruction}
            }
            events_detected.append(event)
            logger.warning(event['message'])
        
        # State change event
        if self.previous_metrics:
            prev_state = self.previous_metrics.get('state', 'UNKNOWN')
            curr_state = self.current_metrics.get('state', 'UNKNOWN')
            if prev_state != curr_state:
                event = {
                    'timestamp': timestamp,
                    'type': 'STATE_CHANGE',
                    'severity': 'INFO',
                    'message': f'State changed from {prev_state} to {curr_state}',
                    'metrics': {'previous_state': prev_state, 'current_state': curr_state}
                }
                events_detected.append(event)
                logger.info(event['message'])
        
        # Add detected events
        self.events.extend(events_detected)
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the current metrics."""
        return self.current_metrics
    
    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent events.
        
        Args:
            count: Number of recent events to retrieve
            
        Returns:
            List of recent events
        """
        return self.events[-count:] if self.events else []
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current metrics and recent events.
        
        Returns:
            Dictionary containing metrics summary
        """
        summary = {
            'current_metrics': self.current_metrics,
            'recent_events': self.get_recent_events(5),
            'total_events': len(self.events),
            'metrics_count': len(self.metrics_history)
        }
        
        if self.current_metrics:
            summary['status'] = {
                'state': self.current_metrics.get('state', 'UNKNOWN'),
                'latency_ms': self.current_metrics.get('latency_ms', 0),
                'downlink_mbps': self.current_metrics.get('downlink_mbps', 0),
                'uplink_mbps': self.current_metrics.get('uplink_mbps', 0),
                'obstruction_percent': self.current_metrics.get('obstruction_percent', 0)
            }
        
        return summary
